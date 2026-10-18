"""QA by actually watching (guide section K + Prompt 6).

Automatic checks: length, loudness, black/empty frames, dead air, cut during the hook,
beats too short to read, text in the app's safe zones, captions 1-2 words, dark/light split,
CTA ending. Then it pulls 3 frames per second onto contact sheets so a reviewer
(Claude Code subagent, the Claude API vision pass, or you) can look at every frame."""
import re
from pathlib import Path

from common import (H, SAFE_TOP, SAFE_BOTTOM, SAFE_RIGHT, ffmpeg, duration, save_json)
from plan import tone_split, caption_chunks

SEV = {"high": 0, "medium": 1, "low": 2}


def loudness(path):
    out = ffmpeg(["-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"])
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", out)
    return float(m[-1]) if m else None


def black_frames(path):
    out = ffmpeg(["-i", path, "-vf", "blackdetect=d=0.15:pix_th=0.08", "-an", "-f", "null", "-"])
    return [(float(a), float(b)) for a, b in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", out)]


def dead_air(path, min_len=1.0):
    out = ffmpeg(["-i", path, "-af", f"silencedetect=noise=-40dB:d={min_len}", "-vn", "-f", "null", "-"])
    s = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    e = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    return list(zip(s, e))


def contact_sheets(path, out_dir, fps=3, cols=5, rows=4):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in list(out_dir.glob("sheet_*.jpg")) + list(out_dir.glob("frames/*.jpg")):
        old.unlink()
    (out_dir / "frames").mkdir(exist_ok=True)
    ffmpeg(["-i", path, "-vf", f"fps={fps},scale=540:960", "-q:v", "3", out_dir / "frames" / "f_%04d.jpg"])
    ffmpeg(["-i", path, "-vf",
            f"fps={fps},scale=216:384,drawtext=text='%{{pts\\:hms}}':x=6:y=6:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6,"
            f"tile={cols}x{rows}:padding=4:color=black",
            "-q:v", "3", out_dir / "sheet_%02d.jpg"])
    return sorted(str(p) for p in out_dir.glob("sheet_*.jpg"))


def run_qa(short_dir, final, plan, words, boxes, target=32, tolerance=(20, 60)):
    d = Path(short_dir)
    issues = []

    def add(sev, t, problem, fix=""):
        issues.append({"severity": sev, "time": None if t is None else round(t, 2), "problem": problem, "fix": fix})

    total = duration(final)
    lo, hi = tolerance
    if not lo <= total <= hi:
        add("high", None, f"length {total:.1f}s outside {lo}-{hi}s", "pick a tighter segment or trim the script")
    elif abs(total - target) > 6:
        add("low", None, f"length {total:.1f}s (target about {target}s)")

    lufs = loudness(final)
    if lufs is None or abs(lufs + 14) > 1.5:
        add("medium", None, f"loudness {lufs} LUFS (target -14)", "re-render (loudnorm)")

    for a, b in black_frames(final):
        add("high", a, f"black/empty frames {a:.2f}-{b:.2f}s", "fill the gap with the current graphic")
    for a, b in dead_air(final):
        add("medium", a, f"dead air {a:.2f}-{b:.2f}s", "trim the pause (cut --trim)")

    ms = plan["moments"]
    he = plan.get("hook_end", 0)
    if ms and ms[0]["end"] < he - 0.05:
        add("high", ms[0]["end"], "cut during the hook", "hook holds until the first sentence ends")
    for m in ms:
        if m["end"] - m["start"] < 0.5:
            add("medium", m["start"], f"beat too short to read ({m['end'] - m['start']:.2f}s)",
                "fold it into the previous graphic as a build step")
    if ms and ms[-1].get("graphic") != "cta":
        add("high", ms[-1]["start"], "no CTA ending card")
    if ms and ms[-1].get("tone") != "dark":
        add("medium", ms[-1]["start"], "ending must stay dark")
    if ms and ms[0].get("tone") != "dark":
        add("medium", 0, "hook must stay dark")
    split = tone_split(plan)
    if len([m for m in ms if m.get("graphic") not in ("face", "image")]) >= 5 and not 0.25 <= split <= 0.65:
        add("low", None, f"dark/light split is {100 - split * 100:.0f}/{split * 100:.0f}; aim for roughly 40-60% each",
            "flip one run of designed graphics to light on an idea change")

    for png, bbox in boxes:
        if not bbox:
            add("medium", None, f"empty graphic {Path(png).name}")
            continue
        x0, y0, x1, y1 = bbox
        if y0 < SAFE_TOP:
            add("high", None, f"{Path(png).name}: content in the top strip (y={y0})", "move it down")
        if y1 > SAFE_BOTTOM:
            add("high", None, f"{Path(png).name}: content in the bottom fifth (y={y1})", "move it up")
        if x1 > SAFE_RIGHT and y1 > H / 2:
            add("medium", None, f"{Path(png).name}: content under the right-edge buttons", "keep text in from the edge")

    long_caps = [c for c in caption_chunks(words) if len(c) > 2]
    if long_caps:
        add("medium", long_caps[0][0]["start"], "captions longer than 2 words")

    sheets = contact_sheets(final, d / "qa")
    issues.sort(key=lambda i: (SEV[i["severity"]], i["time"] or 0))
    report = {"length": round(total, 2), "lufs": lufs, "tone_split_light": round(split, 2),
              "issues": issues, "sheets": sheets, "frames_dir": str(d / "qa" / "frames")}
    save_json(d / "qa" / "report.json", report)
    md = [f"# QA report — {d.name}", "",
          f"- Length: {total:.1f}s (target {target}s)", f"- Loudness: {lufs} LUFS",
          f"- Dark/light split: {100 - split * 100:.0f}% / {split * 100:.0f}%",
          f"- Contact sheets: {len(sheets)} (3 frames per second) in `qa/`", "",
          "## Issues (worst first)", ""]
    md += [f"- **{i['severity']}** {'@' + str(i['time']) + 's ' if i['time'] is not None else ''}{i['problem']}"
           + (f" — fix: {i['fix']}" if i['fix'] else "") for i in issues] or ["- none"]
    (d / "qa" / "report.md").write_text("\n".join(md) + "\n")
    return report
