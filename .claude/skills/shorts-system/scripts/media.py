"""Cutting, silence trimming and word-level transcription."""
import re
from pathlib import Path

from common import ffmpeg, duration, has_audio, run, save_json, load_json


# ----------------------------------------------------------------------------- cutting
def extract(src, start, end, out):
    """Frame-accurate cut, normalised to 30fps / 48k so later concat + filters behave."""
    args = ["-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", src,
            "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p"]
    args += ["-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k"] if has_audio(src) else ["-an"]
    ffmpeg([*args, out])
    return out


def silences(path, noise_db=-35, min_len=0.35):
    out = ffmpeg(["-i", path, "-af", f"silencedetect=noise={noise_db}dB:d={min_len}", "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    if len(ends) < len(starts):
        ends.append(duration(path))
    return list(zip(starts, ends))


def trim_silence(src, out, noise_db=-35, min_len=0.35, pad=0.08):
    """Cut dead air (the guide: trim pauses before the render; you pay for raw seconds).
    Returns the kept intervals so callers can map old times to new ones."""
    total = duration(src)
    if not has_audio(src):
        extract(src, 0, total, out)
        return [(0.0, total)]
    keep, cursor = [], 0.0
    for s, e in silences(src, noise_db, min_len):
        a, b = cursor, min(total, s + pad)
        if b - a > 0.05:
            keep.append((a, b))
        cursor = max(cursor, e - pad)
    if total - cursor > 0.05:
        keep.append((cursor, total))
    if not keep:
        keep = [(0.0, total)]
    sel = "+".join(f"between(t,{a:.3f},{b:.3f})" for a, b in keep)
    ffmpeg(["-i", src,
            "-vf", f"select='{sel}',setpts=N/FRAME_RATE/TB",
            "-af", f"aselect='{sel}',asetpts=N/SR/TB",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-ar", "48000", "-b:a", "192k", out])
    return keep


# ----------------------------------------------------------------------- transcription
def transcribe(media, out_json, model="base", language=None):
    """Word-level timestamps. The guide: snap every caption to them; a quarter second off feels broken.
    Tries faster-whisper, then openai-whisper. Output: [{"word","start","end"}]."""
    words = None
    try:
        from faster_whisper import WhisperModel
        m = WhisperModel(model, device="auto", compute_type="int8")
        segs, _ = m.transcribe(str(media), word_timestamps=True, language=language, vad_filter=True)
        words = [{"word": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)}
                 for s in segs for w in (s.words or []) if w.word.strip()]
    except ImportError:
        try:
            import whisper
            m = whisper.load_model(model)
            r = m.transcribe(str(media), word_timestamps=True, language=language)
            words = [{"word": w["word"].strip(), "start": round(w["start"], 3), "end": round(w["end"], 3)}
                     for s in r["segments"] for w in s.get("words", []) if w["word"].strip()]
        except ImportError:
            raise RuntimeError(
                "No transcriber installed. Run: pip install faster-whisper   "
                "(or pass --words FILE.json with [{word,start,end}] from your avatar/TTS tool).")
    save_json(out_json, words)
    return words


def shift_words(words, start, end):
    """Words inside [start,end) re-based to 0 (for cutting a segment out of a long transcript)."""
    return [{"word": w["word"], "start": round(w["start"] - start, 3), "end": round(w["end"] - start, 3)}
            for w in words if w["start"] >= start - 0.05 and w["end"] <= end + 0.05]


def remap_words(words, kept):
    """Map word times through the kept intervals of trim_silence (pauses removed)."""
    out, offset, spans = [], 0.0, []
    for a, b in kept:
        spans.append((a, b, offset))
        offset += b - a
    for w in words:
        for a, b, off in spans:
            if a - 0.05 <= w["start"] <= b + 0.05:
                s = off + max(0.0, w["start"] - a)
                e = off + min(b - a, max(w["end"] - a, w["start"] - a + 0.05))
                out.append({"word": w["word"], "start": round(s, 3), "end": round(max(e, s + 0.05), 3)})
                break
    return out


def sentences(words):
    """Group words into sentences: [(start, end, text, [word idx])]."""
    out, cur = [], []
    for i, w in enumerate(words):
        cur.append(i)
        if re.search(r"[.!?]$", w["word"]) or i == len(words) - 1:
            out.append((words[cur[0]]["start"], words[cur[-1]]["end"],
                        " ".join(words[j]["word"] for j in cur), list(cur)))
            cur = []
    return out


def pick_segments(words, target=32.0, count=1, min_len=20.0, max_len=45.0):
    """Offline segment picker: sentence-aligned windows near the target length, densest speech first,
    never overlapping. (With an API key the planner picks by meaning instead.)"""
    sents = sentences(words)
    cands = []
    for i in range(len(sents)):
        for j in range(i, len(sents)):
            s, e = sents[i][0], sents[j][1]
            L = e - s
            if L > max_len:
                break
            if L >= min_len:
                n = sum(len(x[3]) for x in sents[i:j + 1])
                score = n / L - abs(L - target) * 0.05
                cands.append((score, s, e))
    cands.sort(reverse=True)
    chosen = []
    for _, s, e in cands:
        if all(e <= a or s >= b for a, b in chosen):
            chosen.append((s, e))
        if len(chosen) == count:
            break
    return sorted(chosen)


def load_words(path):
    return load_json(path, []) or []
