---
name: background-swap
extends: null
type: background
seen_in: https://www.tiktok.com/t/ZTfk55pWb/ (@taki.gpt, "20 Video Effects Created by Claude") at 0:33–0:34
---

# Green Screen

**What it looks like:** The real background is replaced, first with a flat green screen as a joke reveal, then with an illustrated backdrop (a sunset city skyline with lit windows), while the speaker stays in place.

**When to use it:** Changing location for a story, explaining a 'behind the scenes' trick, or matching a topic's setting.

**Timing:** Hard cut to green on a word, hold about 0.7 s, then a hard cut to the new backdrop on the next beat.

**Brand hooks:** Backdrop colors pulled from `primary_color` and `accent_color` where it fits.

## How to build it

- Speaker matte (see README) over any background plate.
- For real green-screen footage, use FFmpeg directly: `chromakey=0x00FF00:0.12:0.08` then `overlay` onto the new plate.
- Match light: if the new backdrop is warm or cool, tint the speaker 3–5% to match.

## Check before shipping

- Reads on a phone at full speed; stays inside the 9:16 safe zone.
- Doesn't hide the speaker's face or the captions for longer than the beat needs.
