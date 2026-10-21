---
name: video-editor
description: Edit the owner's own recordings into finished, on-brand videos — cut retakes and pauses, split multi-video recordings, add captions/graphics, fix exposure and audio, and export for Reels/TikTok (9:16) or YouTube (16:9). Trigger on "edit this video", "cut this down", "make this a Reel/TikTok/Short", "clean up my recording", "add captions to my video". For designed graphic overlays on a talking head use /talking-head-recut; for captions-only styling use /embedded-captions; for anything from scratch use /hyperframes.
---

# Video Editor

Tools: **FFmpeg** (cutting, color, audio, export), **Whisper** (word-level transcripts),
**Node.js / HyperFrames** skills in `.claude/skills/` (motion graphics, captions, overlays).

The owner is the director. You do the work; they make the calls.

## 1. Before every edit, ask three questions

Ask these together, in one message, before touching anything:

1. **Where is this video going?** (Reels, TikTok, YouTube, website, ad, etc.)
2. **What should the viewer do at the end?** (follow, book a call, visit a link, buy, etc.)
3. **Captions and graphics, or a clean cut?**

Do not start until all three are answered. The answers decide format (rule 6), the
closing call to action, and which HyperFrames skill (if any) to bring in.

## 2. Never touch the original

- Copy the original into a work folder **outside iCloud, Google Drive, and Dropbox**
  (synced folders corrupt or evict large files mid-edit). Default:
  `~/VideoWork/<original-name>/`. All intermediate files live there.
- Never write to, re-encode over, rename, or delete the original.
- Save every **finished** video **next to the original** with a new name:
  `<original-name>__<platform>__edit-v1.mp4` (bump `v2`, `v3` — never overwrite an earlier version).

```bash
mkdir -p ~/VideoWork/"$NAME" && cp -p "$ORIGINAL" ~/VideoWork/"$NAME"/source.${ORIGINAL##*.}
```

## 3. Transcribe every word, keep the best take, cut dead air

```bash
whisper source.mp4 --model medium --word_timestamps True --output_format json --output_dir .
```

- Read the word-level timestamps for the whole recording before deciding any cut.
- **Retakes:** when a sentence or phrase is repeated (restarts, "let me say that again",
  flubs), keep only the best take — usually the last complete, fluent one — and cut the rest.
  List the retakes you removed so the owner can overrule you.
- **Pauses:** cut any silence between words **longer than 0.5 s**. Leave a short breath
  (~0.1–0.15 s) at each cut so speech doesn't sound clipped.
- Build the edit as a list of keep-segments and render it in one pass with FFmpeg
  (`trim`/`atrim` + `concat`), never by repeatedly re-encoding.

## 4. One recording, several videos → separate files

If the transcript shows more than one distinct video in a single recording (new intro,
new topic, "okay, next one"), split it into separate files and edit each one separately.
Name them `<original-name>__part1__<platform>__edit-v1.mp4`, `part2`, … and tell the owner
where each split falls before you finish.

## 5. Make it look like them

- If brand files exist (logo, brand guide, colors, fonts), use them. Check
  `brand.json` in this skill folder first, then ask the owner where their brand files are.
- If there are none, **ask once** for **two brand colors** (hex) and **one font**, then save
  them to `brand.json` in this skill folder so you never ask again.
- Captions, lower-thirds, title cards, and end cards all use the brand colors and font.
  Put the logo on the end card, and on screen throughout only if the owner wants it.

### Graphics, images and video sources

When the edit needs graphics, B-roll, or images beyond the owner's footage, pull from these
before making anything generic:

| Source | How | Good for |
|---|---|---|
| Owner's brand files | local folder they point to | logo, product shots, approved graphics |
| **Canva** | Canva connector / `canva:*` skills | branded templates, title cards, thumbnails |
| **Higgsfield** | Higgsfield connector (`generate_image`, `generate_video`, `upscale_video`, `reframe`) | AI B-roll, stylized images, upscaling, reframing to 9:16 |
| **HeyGen** | HeyGen connector | AI avatar / AI voice segments |
| **Pinterest** | owner shares pins or boards | **mood and style reference only**; never put someone else's pin in a video |
| Figma / other design apps | `figma` skill or exported files | designed frames, icons |

For effects (caption styles, transitions, zooms, overlays), check `effects/README.md` first:
it lists every effect already available and the ones added from reference videos. New effects
copied from a reference video go in `effects/`, one file each, with no duplicates.

Anything pulled from Pinterest or the web is someone else's work. Use it as a reference
unless the owner confirms they have the rights to it. Generated assets (Higgsfield, HeyGen)
spend the owner's credits, so say what you'll generate and roughly what it costs before you run it.

## 6. Format and quality

- **Reels / TikTok / Shorts:** vertical **9:16**, 1080×1920.
- **YouTube:** wide **16:9**, 1920×1080, or 3840×2160 when the source is 4K.
- Never upscale past what the source can honestly hold; never downscale below the target.
- **Always export at the highest quality:**
  `-c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -c:a aac -b:a 320k -movflags +faststart`
  (keep the source frame rate; use `-c:v libx265 -crf 18 -tag:v hvc1` only if the owner asks for smaller files).
- Keep captions and key graphics inside each platform's safe zone (vertical: avoid the
  bottom ~20% and the right edge, where the app buttons sit).

## 7. AI voice + real voice: level them separately

When a video mixes an AI voice (HeyGen, TTS, voiceover) and the owner's real voice, put
them on separate tracks and loudness-normalize each one on its own
(`loudnorm=I=-14:TP=-1.5:LRA=11` for social, `I=-16` for YouTube) before mixing.
The real voice must **never** sound quieter than the AI voice. If in doubt, set the real
voice 0.5–1 LU louder.

## 8. Dark or grainy footage: fix it, then be honest

- Fix what you can: exposure/gamma and contrast (`eq`, `curves`), white balance
  (`colorbalance`), denoise (`hqdn3d` light, or `nlmeans` for heavy grain), light sharpening after denoise.
- Then tell the owner straight whether a **reshoot would look noticeably better**
  (for example: "this is watchable now, but a reshoot facing a window would look much better").
  Don't oversell the fix.

## 9. When you finish

- Say exactly **where the finished file is saved** (full path, next to the original).
- List what you changed: retakes removed, total time cut, splits, color/audio fixes.
- Remind them: **watch it once all the way through before posting. You're the director.**
