"""Shared helpers: paths, ffmpeg wrappers, fonts, layout geometry, JSON IO."""
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES = SKILL_DIR / "templates"

# --- 9:16 canvas and the safe zones from the guide (section E) ----------------
W, H = 1080, 1920
SAFE_TOP = 200                 # top strip: app UI, no text
SAFE_BOTTOM = int(H * 0.8)     # bottom fifth: caption + username, no text
SAFE_RIGHT = W - 120           # right edge, lower half: like/comment/share buttons
GRAPHIC_BOX = (120, 240, 960, 1150)   # symmetric, clear of the right-edge buttons   # graphic owns the top two thirds
CAPTION_Y = 1215                      # one caption line between graphic and face
CARD_BOX = (140, 1290, 940, 1740)     # face as a cutout in a small card at the bottom
CARD_RADIUS = 36


def home(arg=None) -> Path:
    """Workspace that holds STYLE.md, GRAPHICS.md, keywords and the shorts."""
    p = Path(arg or os.environ.get("SHORTS_HOME") or "video-shorts/workspace")
    return p.resolve()


def slugify(text: str, n: int = 40) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return s[:n].strip("-") or "short"


def today() -> str:
    return date.today().isoformat()


def load_json(path, default=None):
    path = Path(path)
    if not path.exists():
        return default
    return json.loads(path.read_text())


def save_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def die(msg, code=1):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def need(binary):
    if not shutil.which(binary):
        die(f"'{binary}' not found. Install it (see video-shorts/README.md).")


def run(cmd, cwd=None, quiet=True):
    """Run a command; return stderr+stdout text. Raise with the tail of stderr on failure."""
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0:
        tail = "\n".join(res.stderr.strip().splitlines()[-25:])
        raise RuntimeError(f"command failed: {' '.join(map(str, cmd[:6]))} ...\n{tail}")
    if not quiet:
        print(res.stdout)
    return res.stdout + res.stderr


def ffmpeg(args, cwd=None):
    need("ffmpeg")
    return run(["ffmpeg", "-hide_banner", "-y", *map(str, args)], cwd=cwd)


def probe(path) -> dict:
    need("ffprobe")
    out = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format",
               "-show_streams", str(path)])
    return json.loads(out[out.index("{"):])


def duration(path) -> float:
    return float(probe(path)["format"]["duration"])


def video_size(path):
    for s in probe(path)["streams"]:
        if s["codec_type"] == "video":
            return int(s["width"]), int(s["height"])
    raise RuntimeError(f"no video stream in {path}")


def has_audio(path) -> bool:
    return any(s["codec_type"] == "audio" for s in probe(path)["streams"])


_FONT_CANDIDATES = {
    "bold": ["Inter-Bold.otf", "InterDisplay-Bold.otf", "Inter-Bold.ttf", "DejaVuSans-Bold.ttf",
             "Arial Bold.ttf", "arialbd.ttf", "LiberationSans-Bold.ttf", "FreeSansBold.ttf"],
    "black": ["Inter-Black.otf", "InterDisplay-Black.otf", "Inter-ExtraBold.otf",
              "Inter-Bold.otf", "DejaVuSans-Bold.ttf", "arialbd.ttf"],
    "regular": ["Inter-Medium.otf", "Inter-Regular.otf", "DejaVuSans.ttf", "arial.ttf",
                "LiberationSans-Regular.ttf", "FreeSans.ttf"],
    "mono": ["DejaVuSansMono-Bold.ttf", "DejaVuSansMono.ttf", "cour.ttf"],
}
_FONT_DIRS = ["/usr/share/fonts", "/usr/local/share/fonts", str(Path.home() / ".fonts"),
              "/Library/Fonts", "/System/Library/Fonts", str(Path.home() / "Library/Fonts"),
              "C:/Windows/Fonts"]
_font_cache = {}


def font_path(kind="bold", override=None) -> str | None:
    if override and Path(override).exists():
        return override
    if kind in _font_cache:
        return _font_cache[kind]
    found = None
    for name in _FONT_CANDIDATES.get(kind, _FONT_CANDIDATES["bold"]):
        for d in _FONT_DIRS:
            if not Path(d).exists():
                continue
            hits = list(Path(d).rglob(name))
            if hits:
                found = str(hits[0])
                break
        if found:
            break
    _font_cache[kind] = found
    return found


def load_style(ws: Path) -> dict:
    style = load_json(TEMPLATES / "style.json", {})
    user = load_json(ws / "style.json", {}) if ws else {}
    for k, v in (user or {}).items():
        if isinstance(v, dict) and isinstance(style.get(k), dict):
            style[k].update(v)
        else:
            style[k] = v
    return style


def hex_rgb(h: str, a: int = 255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def log_spend(short_dir: Path, item: str, usd: float, note: str = ""):
    """The guide: log what each short spent."""
    path = Path(short_dir) / "spend.json"
    rows = load_json(path, [])
    rows.append({"date": today(), "item": item, "usd": round(float(usd), 4), "note": note})
    save_json(path, rows)
