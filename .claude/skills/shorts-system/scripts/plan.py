"""The plan: one JSON per short that says what is on screen and when.

plan.json
{
  "topic": "...", "lane": "top|middle|bottom|ad", "keyword": "WORD",
  "title": "3-8 word frame-0 title (also the cover)",
  "cta_line": "If you want [the thing], comment [WORD].",
  "hook_end": 2.4,                         # seconds; no cuts before this
  "moments": [ {"start":0,"end":2.4,"job":"hook","graphic":"title","tone":"dark",
                "text":"spoken words","data":{...}} , ... ],
  "captions": {"thing":"...","result":"...","link":"https://...","hashtags":["a","b"]},
  "cover": {"line1":"...","line2":"..."}
}

This module enforces the guide's pacing rules on any plan (written by Claude Code,
the Claude API planner, or the offline heuristic) and writes the ASS caption file."""
import re

from common import CAPTION_Y, W

JOB_TO_GRAPHIC = {"hook": "title", "claim": "image", "number": "big_number", "list": "list",
                  "steps": "steps", "prompt": "prompt", "opinion": "face", "payoff": "face",
                  "problem": "face", "twist": "face", "ending": "cta", "cta": "cta"}
LANE_CTA = {
    "top": "If you want {thing}, comment {word}.",
    "middle": "If you want the full video, comment {word}.",
    "bottom": "The full lesson is inside {community}. Comment {word}.",
    "ad": "If you want {thing}, comment {word}.",
}


def norm(w):
    return re.sub(r"[^a-z0-9$%]", "", w.lower())


def hook_end_from_words(words):
    for w in words:
        if re.search(r"[.!?]$", w["word"]):
            return w["end"]
    return words[min(len(words) - 1, 7)]["end"] if words else 2.0


def enforce(plan, words, total):
    """Apply the rules from the guide; return a list of human-readable fixes made."""
    fixes = []
    ms = sorted(plan.get("moments", []), key=lambda m: m["start"])
    if not ms:
        return ["plan had no moments"]
    hook_end = float(plan.get("hook_end") or hook_end_from_words(words))
    plan["hook_end"] = round(hook_end, 3)

    # The hook holds: no cuts until the first sentence ends.
    first = ms[0]
    first["start"] = 0.0
    if first.get("graphic") in (None, "face"):
        first["graphic"] = "title"
        fixes.append("frame 0 must be the title graphic")
    first["tone"] = "dark"
    merged = [m for m in ms[1:] if m["start"] < hook_end - 0.05]
    if merged:
        first["end"] = max(first["end"], max(m["end"] for m in merged), hook_end)
        ms = [first] + [m for m in ms[1:] if m not in merged]
        fixes.append(f"merged {len(merged)} moment(s) into the hook (no cut before {hook_end:.2f}s)")
    first["end"] = max(first["end"], hook_end)

    # Anything under half a second is a step on the current graphic, never a new shot.
    out = [ms[0]]
    for m in ms[1:]:
        if m["end"] - m["start"] < 0.5:
            out[-1]["end"] = max(out[-1]["end"], m["end"])
            fixes.append(f"folded {m['end'] - m['start']:.2f}s moment at {m['start']:.2f}s into the previous one")
        else:
            out.append(m)
    ms = out

    # Contiguous timeline, last moment ends at the end of the audio.
    for a, b in zip(ms, ms[1:]):
        if b["start"] > a["end"] + 0.01 or b["start"] < a["end"] - 0.01:
            a["end"] = b["start"]
    ms[-1]["end"] = round(total, 3)

    # The ending is the CTA card and always dark ("feels like home").
    last = ms[-1]
    if last.get("graphic") != "cta":
        cta_start = max(last["start"], total - 3.0)
        if cta_start - last["start"] >= 0.5:
            last["end"] = cta_start
            ms.append({"start": cta_start, "end": total, "job": "cta", "graphic": "cta", "tone": "dark",
                       "text": plan.get("cta_line", ""), "data": {}})
        else:
            last["graphic"] = "cta"
        fixes.append("added the CTA ending card")
    ms[-1]["tone"] = "dark"
    cta = ms[-1].setdefault("data", {})
    cta.setdefault("keyword", plan.get("keyword", ""))
    cta.setdefault("thing", (plan.get("captions") or {}).get("thing", ""))

    for m in ms:
        m.setdefault("tone", "dark")
        m.setdefault("data", {})
        m["start"], m["end"] = round(m["start"], 3), round(m["end"], 3)
        if m.get("graphic") not in (None,) and m["graphic"] == "face":
            m["tone"] = "dark"
    plan["moments"] = ms
    return fixes


def tone_split(plan):
    designed = [m for m in plan["moments"] if m.get("graphic") not in ("face", "image")]
    t = sum(m["end"] - m["start"] for m in designed) or 1
    light = sum(m["end"] - m["start"] for m in designed if m.get("tone") == "light")
    return light / t


def heuristic_plan(words, topic, lane, keyword, thing="", link="", title=None):
    """Offline planner (no AI): title on the hook, one graphic per sentence chosen by what
    the sentence is doing, dark/light runs in the middle, CTA ending."""
    from media import sentences
    sents = sentences(words)
    total = words[-1]["end"] if words else 30
    step_re = re.compile(r"^(first|then|next|finally|second|third|step)\b", re.I)
    moments = []
    for i, (s, e, text, _) in enumerate(sents):
        nums = re.findall(r"\$?\d[\d,]*\.?\d*%?[kKmM]?", text)
        low = text.lower()
        if i == 0:
            g, data = "title", {"title": title or topic, "sub": ""}
        elif re.search(r"\bcomment\b", low) and i >= len(sents) - 2:
            g, data = "cta", {}
        elif step_re.search(text):
            prev = moments[-1] if moments else None
            if prev and prev["graphic"] == "steps":        # one ladder that builds, not a new cut
                prev["end"] = e
                prev["text"] += " " + text
                prev["data"]["items"].append({"text": text.rstrip("."), "at": s})
                continue
            g, data = "steps", {"items": [{"text": text.rstrip("."), "at": s}]}
        elif ":" in text and text.count(",") >= 1:
            head, tail = text.split(":", 1)
            parts = [p.strip(" .") for p in re.split(r",|\band\b", tail) if p.strip(" .")]
            n = len(parts)
            g, data = "list", {"title": head.strip(),
                               "items": [{"text": p, "at": s + (e - s) * (0.35 + 0.6 * k / max(n, 1))}
                                         for k, p in enumerate(parts)]}
        elif nums:
            g, data = "big_number", {"value": nums[0], "label": " ".join(text.split()[:6])}
        elif re.search(r"\b(but|here's the trick|don't|you don't)\b", low):
            g, data = "face", {}
        else:
            g, data = "statement", {"text": text}
        moments.append({"start": s, "end": e, "job": "line", "graphic": g, "text": text, "data": data})
    # Dark/light runs: hook and ending dark, the middle run of designed graphics light (~40-60%).
    designed = [m for m in moments[1:] if m["graphic"] not in ("face", "cta", "image")]
    n = len(designed)
    for m in moments:
        m["tone"] = "dark"
    if n >= 2:
        a, b = n // 4, n // 4 + max(1, round(n * 0.5))
        for m in designed[a:b]:
            m["tone"] = "light"
    cta = LANE_CTA.get(lane, LANE_CTA["top"]).format(thing=thing or "the guide", word=keyword or "WORD",
                                                     community="the community")
    return {"topic": topic, "lane": lane, "keyword": keyword, "title": title or topic, "cta_line": cta,
            "moments": moments, "captions": {"thing": thing or "the guide", "result": "", "link": link,
                                             "hashtags": []},
            "cover": {"line1": title or topic, "line2": ""}, "planner": "heuristic", "_total": total}


# --------------------------------------------------------------------------- captions
def _ass_time(t):
    t = max(0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def caption_chunks(words, max_words=2):
    """One or two words at a time, cut exactly on the spoken word."""
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        dur = cur[-1]["end"] - cur[0]["start"]
        if len(cur) >= max_words or re.search(r"[.,!?;:]$", w["word"]) or (len(cur) == 1 and dur > 0.45):
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    return chunks


def write_ass(words, plan, style, out):
    cap = style.get("caption", {})
    size, outline = cap.get("size", 88), cap.get("outline", 7)
    dark, light = style["dark"], style["light"]

    def ass_col(h):
        h = h.lstrip("#")
        return f"&H00{h[4:6]}{h[2:4]}{h[0:2]}"

    font = cap.get("font", "Inter")
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Dark,{font} Black,{size},{ass_col(dark['text'])},&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,{outline},2,5,60,60,0,1
Style: Light,{font} Black,{size},{ass_col(light['text'])},&H000000FF,{ass_col(light['panel'])},&H00FFFFFF,-1,0,0,0,100,100,0,0,1,{outline},0,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    hidden = 0
    for ch in caption_chunks(words, cap.get("max_words", 2)):
        s, e = ch[0]["start"], ch[-1]["end"]
        mid = (s + e) / 2
        m = next((m for m in plan["moments"] if m["start"] <= mid < m["end"]), None)
        text = " ".join(w["word"] for w in ch)
        # Hide captions when the graphic already shows the same words (and on the CTA card).
        if m and m.get("graphic") != "face":
            shown = norm(" ".join(str(v) for v in _flatten(m.get("data", {}))))
            if m.get("graphic") == "cta" or (shown and all(norm(w["word"]) in shown for w in ch if norm(w["word"]))):
                hidden += 1
                continue
        if cap.get("uppercase"):
            text = text.upper()
        sty = "Light" if m and m.get("tone") == "light" and m.get("graphic") != "face" else "Dark"
        pop = r"{\fscx92\fscy92\t(0,80,\fscx100\fscy100)}"
        lines.append(f"Dialogue: 0,{_ass_time(s)},{_ass_time(e)},{sty},,0,0,0,,{{\\pos({W // 2},{CAPTION_Y})}}{pop}{text}")
    with open(out, "w") as f:
        f.write(head + "\n".join(lines) + "\n")
    return {"captions": len(lines), "hidden_duplicate": hidden}


def _flatten(x):
    if isinstance(x, dict):
        for v in x.values():
            yield from _flatten(v)
    elif isinstance(x, list):
        for v in x:
            yield from _flatten(v)
    else:
        yield x
