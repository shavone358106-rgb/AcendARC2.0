---
name: viewfinder-digital-zoom
extends: camcorder-hud (registry block) + punch-in (hyperframes-keyframes)
type: camera move / overlay
seen_in: https://www.tiktok.com/t/ZTfk55pWb/ (@taki.gpt, "20 Video Effects Created by Claude") at 0:35–0:37
---

# Digital Zoom

**What it looks like:** Camera viewfinder chrome appears (REC dot, timecode, corner brackets, a zoom pill reading 1.0× → 1.6× → 2.6×). The shot pixelates as it digitally zooms in, refocuses on the face with a small square focus box, then zooms back out to 1.0×.

**When to use it:** Emphasis on a reaction or a key line; 'zoom and enhance' jokes.

**Timing:** Zoom steps 0.25 s each; pixelation spikes for 2–3 frames at each step, then clears. Return to 1.0× in 0.3 s.

**Brand hooks:** Zoom pill and REC dot can take `accent_color`; the rest of the HUD stays white.

## How to build it

- HUD: `camcorder-hud` block plus a zoom readout pill and a focus square.
- Zoom: `punch-in` keyframes on the video wrapper.
- Pixelation, FFmpeg route: `scale=iw/12:-1,scale=iw*12:-1:flags=neighbor` for 2–3 frames at each step.

## Check before shipping

- Reads on a phone at full speed; stays inside the 9:16 safe zone.
- Doesn't hide the speaker's face or the captions for longer than the beat needs.
