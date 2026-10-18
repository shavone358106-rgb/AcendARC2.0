"""After the render: captions per platform, the DM script, the cover, your approval, posting.

The rule tattooed on this system: nothing posts without you watching it first.
`post` refuses unless `approve` was run on the exact final.mp4 (sha256 match)."""
import hashlib
import json
import os
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

from PIL import Image, ImageDraw

from common import W, H, CARD_BOX, ffmpeg, load_json, save_json, load_style, hex_rgb, today
from graphics import background, text_block, fit, _glow, blank

COMMENT_PLATFORMS = ["instagram", "facebook"]          # apps where a comment can fire a DM
LINK_PLATFORMS = ["tiktok", "youtube", "x", "linkedin"]
ALL_PLATFORMS = COMMENT_PLATFORMS + LINK_PLATFORMS


# ------------------------------------------------------------------- captions (Prompt 9)
def script_text(plan):
    return [m.get("text", "").strip() for m in plan["moments"] if m.get("text") and m.get("graphic") != "cta"]


def platform_captions(plan):
    c = plan.get("captions", {})
    kw, thing, result, link = plan.get("keyword", ""), c.get("thing", "the guide"), c.get("result", ""), c.get("link", "")
    tags = [t.lstrip("#") for t in c.get("hashtags", [])][:5]          # five at most
    body = "\n".join(script_text(plan))
    hashtags = " ".join(f"#{t}" for t in tags)
    out = {}
    offer = f'Comment "{kw}" to get {thing}' + (f" + {result}" if result else "") + "."
    for p in COMMENT_PLATFORMS:
        out[p] = f"{offer}\n\n{body}\n\n{hashtags}".strip()
    for p in LINK_PLATFORMS:
        # No comment promise: nothing answers comments there.
        tail = f"\n\n{link}" if link else ""
        out[p] = f"{body}{tail}\n\n{hashtags}".strip()
    out["youtube_title"] = (plan.get("title") or plan.get("topic", ""))[:95] + " #shorts"
    return out


def dm_script(plan, community_url=""):
    c = plan.get("captions", {})
    kw = plan.get("keyword", "")
    return f"""# Comment-to-DM setup for {kw}

Trigger: comment contains **{kw}** (exact word, case-insensitive) on this post only.

1. **Follow gate (Instagram):** "Hey! Follow me first and I'll send {c.get('thing', 'it')} right over." (skip if they already follow)
2. **DM:** "Here's {c.get('thing', 'the link')}: {c.get('link', '[LINK]')}"
   - Button 1: {c.get('thing', 'Get it')} -> {c.get('link', '[LINK]')}
   - Button 2: what people get inside the community -> {community_url or '[COMMUNITY LINK]'}
3. **Public reply under every keyword comment:** "Sent, check your DMs"

Test it from a second account (follow gate included) before the post goes live.
"""


def write_captions(short_dir, plan):
    caps = platform_captions(plan)
    md = [f"# Captions — {plan.get('title', '')}", ""]
    for p in ALL_PLATFORMS:
        md += [f"## {p}", "", "```", caps[p], "```", ""]
    md += ["## youtube title", "", caps["youtube_title"], ""]
    Path(short_dir, "captions.md").write_text("\n".join(md))
    save_json(Path(short_dir, "captions.json"), caps)
    Path(short_dir, "dm.md").write_text(dm_script(plan))
    return caps


# ----------------------------------------------------------------------- cover (Prompt 10)
def make_cover(short_dir, final, plan, ws, out="cover.jpg"):
    """One cover per short: Instagram cover + YouTube thumbnail. Never a raw frame grab:
    title big and bold, face bright in the middle, everything inside the middle 3:4."""
    d = Path(short_dir)
    style = load_style(ws)
    tone = "dark"
    bg = d / "build" / "cover_bg.png"
    background(style, tone, bg)
    img = Image.open(bg).convert("RGBA")
    face_m = next((m for m in plan["moments"] if m.get("graphic") == "face"), None)
    t = (face_m["start"] + face_m["end"]) / 2 if face_m else 0.5
    grab = d / "build" / "cover_face.png"
    clip = d / "clip.mp4"
    src = clip if clip.exists() else final
    ffmpeg(["-ss", f"{t:.2f}", "-i", src, "-frames:v", "1", grab])
    face = Image.open(grab).convert("RGBA")
    top, bottom = int(H * 0.13), int(H * 0.87)            # leave top and bottom 13% empty
    fw = 760
    face = face.resize((fw, int(face.height * fw / face.width)))
    fh = min(face.height, 760)
    face = face.crop(((face.width - fw) // 2, 0, (face.width + fw) // 2, fh))
    try:                                                   # clean cutout if rembg is installed
        from rembg import remove
        face = remove(face)
        mask = face.split()[-1]
    except Exception:
        mask = Image.new("L", face.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, *face.size), radius=48, fill=255)
    fx, fy = (W - fw) // 2, top + 330
    layer = blank()
    layer.paste(face, (fx, fy), mask)
    _glow(img, layer, hex_rgb(style[tone]["accent"]), radius=40)
    c = plan.get("cover") or {}
    line1 = c.get("line1") or plan.get("title", "")
    line2 = c.get("line2", "")
    text_block(img, line1, (90, top + 20, W - 90, top + 310), style, tone, max_size=120, max_lines=3)
    if line2:
        f, lines, size = fit(line2, "black", 860, 140, style, 110, 50, 1)
        tw = ImageDraw.Draw(img).textlength(lines[0], font=f)
        bar = ((W - tw) / 2 - 40, fy + fh - 40, (W + tw) / 2 + 40, fy + fh - 40 + size + 50)
        bar = (bar[0], min(bar[1], bottom - (bar[3] - bar[1])), bar[2], min(bar[3], bottom))
        ImageDraw.Draw(img).rounded_rectangle(bar, radius=18, fill=hex_rgb(style[tone]["accent"]))
        ImageDraw.Draw(img).text(((bar[0] + bar[2]) / 2, (bar[1] + bar[3]) / 2), lines[0], font=f,
                                 fill=hex_rgb(style[tone]["bg"]), anchor="mm")
    img.convert("RGB").save(d / out, quality=92)
    # grid-crop preview (profile grid shows the middle 3:4)
    crop_h = int(W * 4 / 3)
    img.convert("RGB").crop((0, (H - crop_h) // 2, W, (H + crop_h) // 2)).save(d / "cover_gridcrop.jpg", quality=85)
    return d / out


# ------------------------------------------------------------------------------ approval
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def approve(short_dir, note=""):
    d = Path(short_dir)
    final = d / "final.mp4"
    if not final.exists():
        raise SystemExit("no final.mp4 to approve")
    rec = {"approved_at": datetime.now().isoformat(timespec="seconds"), "note": note,
           "final_sha256": sha256(final),
           "captions_sha256": sha256(d / "captions.json") if (d / "captions.json").exists() else None}
    save_json(d / "approval.json", rec)
    return rec


def check_approval(short_dir):
    d = Path(short_dir)
    rec = load_json(d / "approval.json")
    if not rec:
        return False, "not approved — watch final.mp4, then run: shorts.py approve " + str(d)
    if rec["final_sha256"] != sha256(d / "final.mp4"):
        return False, "final.mp4 changed after approval — watch it again and re-approve"
    if rec.get("captions_sha256") and rec["captions_sha256"] != sha256(d / "captions.json"):
        return False, "captions changed after approval — re-approve"
    return True, "approved " + rec["approved_at"]


# ------------------------------------------------------------------------------- posting
def link_live(url, timeout=10):
    if not url:
        return True
    try:
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "shorts-system/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status < 400
    except Exception:
        return False


def next_slot(ws, hour="09:00"):
    """One post a day, same morning slot: the first day without a scheduled post."""
    log = load_json(Path(ws) / "posts.json", [])
    taken = {p["slot"][:10] for p in log if p.get("status") in ("scheduled", "posted", "sent")}
    day = datetime.now().date() + timedelta(days=1)
    while day.isoformat() in taken:
        day += timedelta(days=1)
    h, m = map(int, hour.split(":"))
    return datetime(day.year, day.month, day.day, h, m).astimezone().isoformat(timespec="minutes")


def _http_json(url, payload, headers):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST",
                                 headers={"Content-Type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=60) as r:
        body = r.read().decode() or "{}"
        try:
            return r.status, json.loads(body)
        except json.JSONDecodeError:
            return r.status, {"raw": body}


AYRSHARE_NAMES = {"x": "twitter", "instagram": "instagram", "facebook": "facebook", "tiktok": "tiktok",
                  "youtube": "youtube", "linkedin": "linkedin"}


def post(short_dir, ws, platforms, provider="dry-run", slot=None, media_url=None):
    d = Path(short_dir)
    ok, why = check_approval(d)
    if not ok:
        raise SystemExit(f"refusing to post: {why}")
    plan = load_json(d / "plan.json")
    caps = load_json(d / "captions.json")
    link = (plan.get("captions") or {}).get("link")
    if link and not link_live(link):
        raise SystemExit(f"refusing to post: link is not live ({link}). Skip this slot or fix the link.")
    slot = slot or next_slot(ws)
    results = []
    for p in platforms:
        text = caps[p]
        if provider == "dry-run":
            res = {"status": "dry-run", "would_post": text[:80] + "..."}
        elif provider == "ayrshare":
            key = os.environ.get("AYRSHARE_API_KEY") or exit_msg("set AYRSHARE_API_KEY")
            if not media_url:
                raise SystemExit("ayrshare needs --media-url (a public URL of final.mp4)")
            payload = {"post": text, "platforms": [AYRSHARE_NAMES[p]], "mediaUrls": [media_url],
                       "isVideo": True, "scheduleDate": slot}
            if p == "youtube":
                payload["youTubeOptions"] = {"title": caps["youtube_title"], "shorts": True}
            if p == "instagram":
                payload["instagramOptions"] = {"reels": True, "shareReelsFeed": True}
            code, body = _http_json("https://api.ayrshare.com/api/post", payload, {"Authorization": f"Bearer {key}"})
            res = {"status": "scheduled" if code < 300 else "error", "http": code, "response": body}
        elif provider == "webhook":
            url = os.environ.get("SHORTS_WEBHOOK_URL") or exit_msg("set SHORTS_WEBHOOK_URL (Zapier/Make/n8n catch hook)")
            payload = {"platform": p, "caption": text, "slot": slot, "keyword": plan.get("keyword"),
                       "title": caps["youtube_title"], "video_path": str((d / "final.mp4").resolve()),
                       "media_url": media_url, "cover_path": str((d / "cover.jpg").resolve()),
                       "dm": (d / "dm.md").read_text() if (d / "dm.md").exists() else ""}
            code, body = _http_json(url, payload, {})
            res = {"status": "sent" if code < 300 else "error", "http": code, "response": body}
        else:
            raise SystemExit(f"unknown provider {provider}")
        results.append({"platform": p, **res})
    log_path = Path(ws) / "posts.json"
    log = load_json(log_path, [])
    for r in results:
        log.append({"short": d.name, "platform": r["platform"], "slot": slot, "provider": provider,
                    "status": r["status"], "logged": today()})
    save_json(log_path, log)
    return slot, results


def exit_msg(m):
    raise SystemExit(m)
