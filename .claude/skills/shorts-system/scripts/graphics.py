"""The graphics library (guide section J). Each graphic takes text + timing and renders
transparent 1080x1920 PNG overlays, one per build step, so the graphic builds in time
with the words instead of cutting on every line.

Graphics: title, statement, big_number, list, steps, before_after, prompt, cta, image, face.
Add a new renderer here every time a script needs something the library can't draw,
and add its row to GRAPHICS.md."""
import random
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from common import (W, H, GRAPHIC_BOX, CARD_BOX, CARD_RADIUS, font_path, hex_rgb)

GRAPHICS = ["title", "statement", "big_number", "list", "steps", "before_after",
            "prompt", "cta", "image", "face"]


# ------------------------------------------------------------------------- primitives
def _font(kind, size, style):
    override = (style.get("fonts") or {}).get({"black": "title", "bold": "title",
                                               "regular": "body", "mono": "mono"}[kind])
    p = font_path(kind, override)
    return ImageFont.truetype(p, size) if p else ImageFont.load_default(size)


def _wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = f"{cur} {w}".strip()
        if draw.textlength(t, font=font) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit(text, kind, max_w, max_h, style, max_size=120, min_size=34, max_lines=4, spacing=1.08):
    """Largest font where the wrapped text fits the box. Never lets text get cut off
    (the QA defect 'text cut off' is prevented by construction)."""
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    size = max_size
    while size >= min_size:
        f = _font(kind, size, style)
        lines = _wrap(probe, text, f, max_w)
        too_wide = any(probe.textlength(l, font=f) > max_w for l in lines)
        if len(lines) <= max_lines and len(lines) * size * spacing <= max_h and not too_wide:
            return f, lines, size
        size -= 4
    f = _font(kind, min_size, style)
    return f, _wrap(probe, text, f, max_w), min_size


def _glow(img, layer, color, radius=18, strength=1):
    """Premium comes from light: blur a copy of the shapes in the accent colour underneath."""
    alpha = layer.split()[-1]
    glow = Image.new("RGBA", img.size, color[:3] + (0,))
    glow.putalpha(alpha.filter(ImageFilter.GaussianBlur(radius)).point(lambda a: min(255, int(a * 0.9))))
    for _ in range(strength):
        img.alpha_composite(glow)
    img.alpha_composite(layer)


def text_block(img, text, box, style, tone, kind="black", max_size=120, min_size=34,
               color=None, align="center", glow=True, max_lines=4, accent_words=()):
    pal = style[tone]
    x0, y0, x1, y1 = box
    f, lines, size = fit(text, kind, x1 - x0, y1 - y0, style, max_size, min_size, max_lines)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    lh = int(size * 1.08)
    y = y0 + ((y1 - y0) - lh * len(lines)) // 2
    accents = {a.lower().strip(".,!?") for a in accent_words}
    for line in lines:
        lw = d.textlength(line, font=f)
        x = x0 + ((x1 - x0) - lw) / 2 if align == "center" else x0
        for word in line.split(" "):
            c = hex_rgb(pal["accent"]) if word.lower().strip(".,!?") in accents else (color or hex_rgb(pal["text"]))
            d.text((x, y), word, font=f, fill=c)
            x += d.textlength(word + " ", font=f)
        y += lh
    if glow and tone == "dark":
        _glow(img, layer, hex_rgb(pal["accent"]), radius=22)
    else:
        img.alpha_composite(layer)
    return y


def rounded_panel(img, box, style, tone, outline=True, fill_alpha=225, radius=28, lit=False):
    pal = style[tone]
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(box, radius=radius, fill=hex_rgb(pal["panel"], fill_alpha),
                        outline=hex_rgb(pal["accent"], 255 if lit else 120) if outline else None,
                        width=3 if lit else 2)
    if lit and tone == "dark":
        _glow(img, layer, hex_rgb(pal["accent"]), radius=16)
    else:
        img.alpha_composite(layer)


def blank():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


# ---------------------------------------------------------------------- backgrounds
def background(style, tone, out):
    """Dark ground or light paper: radial light + dot grid + grain."""
    pal = style[tone]
    img = Image.new("RGBA", (W, H), hex_rgb(pal["bg"]))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((W * 0.5 - 700, 120, W * 0.5 + 700, 1300), fill=hex_rgb(pal["bg2"], 255))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(200)))
    d = ImageDraw.Draw(img)
    dot = hex_rgb(pal["muted"], 28)
    for y in range(40, H, 44):
        for x in range(40, W, 44):
            d.point((x, y), fill=dot)
    rng = random.Random(7 if tone == "dark" else 11)
    g = style.get("grain", 10)
    if g:
        noise = Image.new("L", (W // 2, H // 2))
        noise.putdata([rng.randint(128 - g * 4, 128 + g * 4) for _ in range(W * H // 4)])
        noise = noise.resize((W, H))
        overlay = Image.new("RGBA", (W, H), (128, 128, 128, 0))
        overlay.putalpha(noise.point(lambda v: abs(v - 128) // 2))
        img.alpha_composite(overlay)
    img.convert("RGB").save(out)
    return out


def card_assets(style, mask_out, frame_out):
    """Mask that rounds the face card, plus a lit outline drawn over it."""
    x0, y0, x1, y1 = CARD_BOX
    m = Image.new("L", (x1 - x0, y1 - y0), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, x1 - x0 - 1, y1 - y0 - 1), radius=CARD_RADIUS, fill=255)
    m.save(mask_out)
    fr = blank()
    layer = blank()
    ImageDraw.Draw(layer).rounded_rectangle(CARD_BOX, radius=CARD_RADIUS,
                                            outline=hex_rgb(style["dark"]["accent"], 160), width=3)
    _glow(fr, layer, hex_rgb(style["dark"]["accent"]), radius=20)
    fr.save(frame_out)


# --------------------------------------------------------------------------- renderers
def _steps_times(items, start, end):
    n = len(items)
    times = []
    for i, it in enumerate(items):
        at = it.get("at") if isinstance(it, dict) else None
        times.append(float(at) if at is not None else start + (end - start) * i / max(n, 1) * 0.8)
    times[0] = min(times[0], start)
    return times


def r_title(m, style, tone):
    data = m.get("data", {})
    img = blank()
    x0, y0, x1, y1 = GRAPHIC_BOX
    title = data.get("title") or m.get("text", "")
    bottom = text_block(img, title, (x0, y0 + 40, x1, y0 + 520), style, tone, max_size=124,
                        accent_words=data.get("accent", "").split())
    if data.get("sub"):
        f, lines, size = fit(data["sub"], "bold", 600, 90, style, 64, 34, 1)
        tw = ImageDraw.Draw(img).textlength(lines[0], font=f)
        bx = ((W - tw) / 2 - 36, bottom + 60, (W + tw) / 2 + 36, bottom + 60 + size + 50)
        rounded_panel(img, bx, style, tone, lit=True)
        ImageDraw.Draw(img).text((bx[0] + 36, bx[1] + 22), lines[0], font=f, fill=hex_rgb(style[tone]["accent"]))
    return [(img, m["start"])]


def r_statement(m, style, tone):
    img = blank()
    data = m.get("data", {})
    text_block(img, data.get("text") or m.get("text", ""), GRAPHIC_BOX, style, tone, max_size=112,
               accent_words=data.get("accent", "").split())
    return [(img, m["start"])]


def r_big_number(m, style, tone):
    data = m.get("data", {})
    raw = str(data.get("value", m.get("text", "0")))
    match = re.search(r"[\d][\d,]*\.?\d*", raw)
    pre, suf = (raw[:match.start()], raw[match.end():]) if match else ("", "")
    num_s = match.group(0) if match else raw
    target = float(num_s.replace(",", "")) if match else None
    decimals = len(num_s.split(".")[1]) if "." in num_s else 0
    pre = data.get("prefix", pre)
    suf = data.get("suffix", suf)
    steps = 9 if target is not None else 1
    span = min(0.7, (m["end"] - m["start"]) * 0.5)
    frames = []
    x0, y0, x1, y1 = GRAPHIC_BOX
    for i in range(steps):
        p = 1 - (1 - (i + 1) / steps) ** 3        # ease-out: numbers always count up
        v = target * p if target is not None else None
        if v is None:
            s = raw
        elif decimals:
            s = f"{v:,.{decimals}f}" if "," in num_s else f"{v:.{decimals}f}"
        else:
            s = f"{int(round(v)):,}" if "," in num_s or target >= 10000 else str(int(round(v)))
        img = blank()
        text_block(img, f"{pre}{s}{suf}", (x0, y0 + 60, x1, y0 + 520), style, tone,
                   max_size=300, min_size=90, max_lines=1, color=hex_rgb(style[tone]["accent"]))
        if data.get("label"):
            text_block(img, data["label"].upper(), (x0, y0 + 560, x1, y0 + 680), style, tone,
                       kind="black", max_size=76, max_lines=2, glow=False)
        if data.get("sub"):
            text_block(img, data["sub"], (x0, y0 + 690, x1, y0 + 770), style, tone, kind="regular",
                       max_size=46, glow=False, max_lines=1, color=hex_rgb(style[tone]["accent"]))
        frames.append((img, m["start"] + span * i / steps))
    return frames


def _list_like(m, style, tone, numbered):
    data = m.get("data", {})
    items = data.get("items") or [{"text": t} for t in re.split(r",|;", m.get("text", "")) if t.strip()]
    items = [it if isinstance(it, dict) else {"text": str(it)} for it in items][:6]
    times = _steps_times(items, m["start"], m["end"])
    x0, y0, x1, y1 = GRAPHIC_BOX
    head_h = 0
    frames = []
    title = data.get("title")
    row_h = min(240 if len(items) <= 2 else 190, int((y1 - y0 - (170 if title else 0)) / max(len(items), 1)) - 18)
    block_h = (170 if title else 0) + len(items) * (row_h + 18)
    y0 = y0 + max(0, ((y1 - y0) - block_h) // 2)
    for k in range(len(items)):
        img = blank()
        if title:
            text_block(img, title, (x0, y0, x1, y0 + 150), style, tone, max_size=88, max_lines=2)
            head_h = 170
        y = y0 + head_h
        for i, it in enumerate(items[:k + 1]):
            lit = i == k
            box = (x0 + 16, y, x1 - 16, y + row_h)
            rounded_panel(img, box, style, tone, lit=lit)
            pad = 34
            tx = box[0] + pad
            if numbered:
                nf = _font("mono", max(28, row_h // 3), style)
                ImageDraw.Draw(img).text((tx, y + row_h / 2), f"{i + 1:02d}", font=nf,
                                         fill=hex_rgb(style[tone]["accent"]), anchor="lm")
                tx += int(row_h * 0.75)
            text_block(img, it["text"], (tx, y + 10, box[2] - pad, y + row_h - 10), style, tone,
                       max_size=min(76, row_h - 30), min_size=30, max_lines=3, align="left",
                       glow=lit, color=None if lit else hex_rgb(style[tone]["muted"]))
            y += row_h + 18
        frames.append((img, times[k]))
    return frames


def r_list(m, style, tone):
    return _list_like(m, style, tone, numbered=False)


def r_steps(m, style, tone):
    return _list_like(m, style, tone, numbered=True)


def r_before_after(m, style, tone):
    data = m.get("data", {})
    b, a = data.get("before", {}), data.get("after", {})
    at = float(data.get("at", (m["start"] + m["end"]) / 2))
    x0, y0, x1, y1 = GRAPHIC_BOX
    mid = (x0 + x1) // 2
    frames = []
    for show_after in (False, True):
        img = blank()
        if data.get("title"):
            text_block(img, data["title"], (x0, y0, x1, y0 + 140), style, tone, max_size=84, max_lines=2)
        for side, d, lit in ((0, b, not show_after), (1, a, show_after)):
            if side == 1 and not show_after:
                continue
            bx = (x0 + 10 if side == 0 else mid + 15, y0 + 180, mid - 15 if side == 0 else x1 - 10, y1 - 40)
            rounded_panel(img, bx, style, tone, lit=lit)
            text_block(img, (d.get("label") or ("BEFORE" if side == 0 else "AFTER")).upper(),
                       (bx[0] + 20, bx[1] + 30, bx[2] - 20, bx[1] + 110), style, tone, kind="black",
                       max_size=52, max_lines=1, glow=False, color=hex_rgb(style[tone]["accent"]))
            text_block(img, d.get("text", ""), (bx[0] + 30, bx[1] + 140, bx[2] - 30, bx[3] - 40), style,
                       tone, max_size=84, min_size=34, max_lines=5, glow=lit)
        frames.append((img, m["start"] if not show_after else at))
    return frames


def r_prompt(m, style, tone):
    """A prompt typing into the app on the spoken words, then the answer."""
    data = m.get("data", {})
    prompt = data.get("text") or m.get("text", "")
    answer = data.get("answer", "")
    words = prompt.split()
    x0, y0, x1, y1 = GRAPHIC_BOX
    t0, t1 = m["start"], m["end"] - (0.9 if answer else 0.2)
    n = max(1, min(len(words), 14))
    frames = []
    pal = style[tone]
    for k in range(1, n + 1):
        cut = round(len(words) * k / n)
        img = blank()
        panel = (x0 + 20, y0 + 60, x1 - 20, y1 - 60)
        rounded_panel(img, panel, style, tone, lit=False, fill_alpha=235)
        d = ImageDraw.Draw(img)
        for i, c in enumerate(("accent", "muted", "muted")):
            d.ellipse((panel[0] + 36 + i * 38, panel[1] + 34, panel[0] + 60 + i * 38, panel[1] + 58),
                      fill=hex_rgb(pal[c]))
        text_block(img, data.get("app_title", "What should we build?"),
                   (panel[0] + 40, panel[1] + 90, panel[2] - 40, panel[1] + 200), style, tone,
                   kind="bold", max_size=58, max_lines=1, glow=False)
        box = (panel[0] + 40, panel[1] + 230, panel[2] - 40, panel[3] - 200)
        rounded_panel(img, box, style, tone, lit=True, fill_alpha=255)
        text_block(img, " ".join(words[:cut]) + ("|" if k < n else ""),
                   (box[0] + 30, box[1] + 25, box[2] - 30, box[3] - 25), style, tone, kind="bold",
                   max_size=62, min_size=30, max_lines=6, align="left", glow=False)
        frames.append((img, t0 + (t1 - t0) * (k - 1) / n))
    if answer:
        img = frames[-1][0].copy()
        panel_bottom = (x0 + 60, y1 - 250, x1 - 60, y1 - 90)
        rounded_panel(img, panel_bottom, style, tone, lit=True)
        text_block(img, answer, (panel_bottom[0] + 30, panel_bottom[1] + 15, panel_bottom[2] - 30,
                                 panel_bottom[3] - 15), style, tone, kind="bold", max_size=50,
                   max_lines=2, color=hex_rgb(pal["accent"]))
        frames.append((img, t1))
    return frames


def r_cta(m, style, tone):
    data = m.get("data", {})
    img = blank()
    x0, y0, x1, y1 = GRAPHIC_BOX
    kw = (data.get("keyword") or "").upper()
    if kw:
        text_block(img, data.get("verb", "Comment"), (x0, y0 + 120, x1, y0 + 280), style, tone, max_size=120)
        f, lines, size = fit(kw, "black", 620, 150, style, 130, 60, 1)
        tw = ImageDraw.Draw(img).textlength(lines[0], font=f)
        pill = ((W - tw) / 2 - 70, y0 + 320, (W + tw) / 2 + 70, y0 + 320 + size + 70)
        layer = blank()
        ImageDraw.Draw(layer).rounded_rectangle(pill, radius=(pill[3] - pill[1]) // 2,
                                                fill=hex_rgb(style[tone]["accent"]))
        _glow(img, layer, hex_rgb(style[tone]["accent"]), radius=30, strength=2)
        ImageDraw.Draw(img).text(((pill[0] + pill[2]) / 2, (pill[1] + pill[3]) / 2), lines[0], font=f,
                                 fill=hex_rgb(style[tone]["bg"]), anchor="mm")
        if data.get("thing"):
            text_block(img, f"for {data['thing']}", (x0, pill[3] + 30, x1, pill[3] + 140), style, tone,
                       kind="bold", max_size=64, max_lines=2, glow=False)
    else:
        text_block(img, data.get("line") or m.get("text", "Link in bio"), GRAPHIC_BOX, style, tone, max_size=110)
    return [(img, m["start"])]


def r_image(m, style, tone):
    """Real proof (a screenshot / product shot). Must read at phone size in one second."""
    data = m.get("data", {})
    img = blank()
    x0, y0, x1, y1 = GRAPHIC_BOX
    p = data.get("path")
    if p and Path(p).exists():
        shot = Image.open(p).convert("RGBA")
        bw, bh = x1 - x0, (y1 - y0) - (110 if data.get("label") else 0)
        shot.thumbnail((bw, bh))
        mask = Image.new("L", shot.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, *shot.size), radius=24, fill=255)
        px = x0 + (bw - shot.width) // 2
        py = y0 + (bh - shot.height) // 2
        img.paste(shot, (px, py), mask)
    if data.get("label"):
        text_block(img, data["label"], (x0, y1 - 100, x1, y1), style, tone, kind="bold", max_size=56, max_lines=1)
    return [(img, m["start"])]


RENDERERS = {"title": r_title, "statement": r_statement, "big_number": r_big_number, "list": r_list,
             "steps": r_steps, "before_after": r_before_after, "prompt": r_prompt, "cta": r_cta,
             "image": r_image}


def render_moments(moments, style, out_dir):
    """Returns overlays [(png, start, end)] and bboxes [(png, (x0,y0,x1,y1))] for safe-zone QA."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("m*.png"):
        old.unlink()
    overlays, boxes = [], []
    for i, m in enumerate(moments):
        g = m.get("graphic", "statement")
        if g == "face":
            continue
        fn = RENDERERS.get(g, r_statement)
        frames = fn(m, style, m.get("tone", "dark"))
        for k, (img, t) in enumerate(frames):
            end = frames[k + 1][1] if k + 1 < len(frames) else m["end"]
            t = max(m["start"], min(t, m["end"]))
            if end - t <= 0.01:
                continue
            p = out_dir / f"m{i:02d}_{k:02d}.png"
            img.save(p)
            overlays.append((str(p), round(t, 3), round(min(end, m["end"]), 3)))
            solid = img.getchannel("A").point(lambda a: 255 if a > 80 else 0)
            boxes.append((str(p), solid.getbbox()))
    return overlays, boxes
