"""Compose the final 9:16 short: background tone runs, face card, graphic overlays,
full-frame face beats, captions, quiet SFX on every visual change, music bed, loudness."""
from pathlib import Path

from common import (W, H, CARD_BOX, ffmpeg, duration, has_audio)
from graphics import background, card_assets


def _sfx(dir_):
    """Generate a soft whoosh (cut) and tick (build step) once."""
    whoosh, tick = dir_ / "whoosh.wav", dir_ / "tick.wav"
    if not whoosh.exists():
        ffmpeg(["-f", "lavfi", "-i", "anoisesrc=d=0.35:c=pink:a=0.5", "-af",
                "highpass=f=400,lowpass=f=5000,afade=t=in:d=0.15,afade=t=out:st=0.15:d=0.2,volume=0.6",
                "-ar", "48000", "-ac", "2", whoosh])
    if not tick.exists():
        ffmpeg(["-f", "lavfi", "-i", "sine=f=1800:d=0.05", "-af", "afade=t=out:st=0.01:d=0.04,volume=0.5",
                "-ar", "48000", "-ac", "2", tick])
    return whoosh, tick


def compose(short_dir, clip, plan, overlays, ass, style, music=None, out="final.mp4"):
    d = Path(short_dir)
    d = d.resolve()
    assets = d / "build"
    assets.mkdir(exist_ok=True)
    total = duration(clip)
    bg_dark = background(style, "dark", assets / "bg_dark.png")
    bg_light = background(style, "light", assets / "bg_light.png")
    card_assets(style, assets / "card_mask.png", assets / "card_frame.png")
    whoosh, tick = _sfx(assets)

    moments = plan["moments"]
    light = [(m["start"], m["end"]) for m in moments if m.get("tone") == "light" and m.get("graphic") != "face"]
    face = [(m["start"], m["end"]) for m in moments if m.get("graphic") == "face"]

    def between(rs):
        return "+".join(f"between(t,{a:.3f},{b:.3f})" for a, b in rs) or "0"

    cx0, cy0, cx1, cy1 = CARD_BOX
    cw, ch = cx1 - cx0, cy1 - cy0
    inputs = ["-i", Path(clip).resolve(), "-loop", "1", "-i", bg_dark, "-loop", "1", "-i", bg_light,
              "-loop", "1", "-i", assets / "card_mask.png", "-loop", "1", "-i", assets / "card_frame.png"]
    n = 5
    f = [
        f"[1:v]scale={W}:{H},setsar=1,format=yuv420p,trim=duration={total:.3f}[bgd]",
        f"[2:v]scale={W}:{H},setsar=1,format=yuv420p,trim=duration={total:.3f}[bgl]",
        f"[bgd][bgl]overlay=enable='{between(light)}'[bg]",
        "[0:v]split=2[vc][vf]",
        f"[vc]scale={cw}:{ch}:force_original_aspect_ratio=increase,crop={cw}:{ch},format=yuva420p[card0]",
        "[3:v]format=gray[cmask]",
        "[card0][cmask]alphamerge[card]",
        f"[bg][card]overlay={cx0}:{cy0}:shortest=1[s0]",
        "[s0][4:v]overlay=0:0[s1]",
        f"[vf]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1[full]",
    ]
    last = "s1"
    for i, (png, a, b) in enumerate(overlays):
        inputs += ["-loop", "1", "-i", Path(png).resolve()]
        f.append(f"[{last}][{n}:v]overlay=0:0:enable='between(t,{a:.3f},{b - 0.001:.3f})'[o{i}]")
        last = f"o{i}"
        n += 1
    f.append(f"[{last}][full]overlay=0:0:enable='{between(face)}'[s2]")
    ass_rel = Path(ass).name
    f.append(f"[s2]ass={ass_rel},format=yuv420p[v]")

    # Audio: voice + SFX on every visual change + optional bed well below the voice.
    vol = style.get("sfx_volume", 0.35)
    events = [(m["start"], "w") for m in moments[1:]]
    seen = {round(m["start"], 2) for m in moments}
    events += [(a, "t") for _, a, _ in overlays if round(a, 2) not in seen]
    inputs += ["-i", whoosh, "-i", tick]
    wi, ti = n, n + 1
    n += 2
    a_parts = []
    voice = "[0:a]" if has_audio(clip) else None
    if not voice:
        f.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={total:.3f}[sil]")
        voice = "[sil]"
    ws = [e for e in events if e[1] == "w"]
    ts = [e for e in events if e[1] == "t"]
    if ws:
        f.append(f"[{wi}:a]asplit={len(ws)}" + "".join(f"[w{i}]" for i in range(len(ws))))
        for i, (t, _) in enumerate(ws):
            ms = max(0, int(t * 1000) - 120)
            f.append(f"[w{i}]adelay={ms}|{ms},volume={vol}[wd{i}]")
            a_parts.append(f"[wd{i}]")
    if ts:
        f.append(f"[{ti}:a]asplit={len(ts)}" + "".join(f"[t{i}]" for i in range(len(ts))))
        for i, (t, _) in enumerate(ts):
            ms = int(t * 1000)
            f.append(f"[t{i}]adelay={ms}|{ms},volume={vol}[td{i}]")
            a_parts.append(f"[td{i}]")
    if music:
        inputs += ["-stream_loop", "-1", "-i", Path(music).resolve()]
        f.append(f"[{n}:a]atrim=duration={total:.3f},volume={style.get('music_volume', 0.12)},"
                 f"afade=t=out:st={max(0, total - 1.2):.3f}:d=1.2[bed]")
        a_parts.append("[bed]")
        n += 1
    mix_in = voice + "".join(a_parts)
    f.append(f"{mix_in}amix=inputs={1 + len(a_parts)}:normalize=0:duration=first,"
             f"loudnorm=I={style.get('loudness_lufs', -14)}:TP=-1.5:LRA=11,aresample=48000[a]")

    script = assets / "filter.txt"
    script.write_text(";\n".join(f))
    ffmpeg([*inputs, "-filter_complex_script", str(script.resolve()),
            "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}", "-r", "30",
            "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], cwd=d)
    return d / out
