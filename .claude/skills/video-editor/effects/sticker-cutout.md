---
name: sticker-cutout
extends: freeze-frame-dressing (hyperframes-registry block)
type: background / overlay
seen_in: https://www.tiktok.com/t/ZTfk55pWb/ (@taki.gpt, "20 Video Effects Created by Claude") at 0:22–0:24
---

# Paper Cutout

**What it looks like:** The speaker is cut out with a thick white sticker border and placed on a flat bright background scattered with bold shapes (a star, circles, thick bars). Unlike freeze-frame-dressing, the cut-out stays live and talking.

**When to use it:** Playful or energetic segments, list intros, thumbnails-in-motion.

**Timing:** Background snaps in on a cut. Shapes drift slowly (2–4% movement) so it never feels frozen.

**Brand hooks:** Background `accent_color`; shapes in `primary_color`, white and black.

## How to build it

- Speaker matte, then a white outline: dilate the matte 10–14 px, fill white, place behind the speaker.
- FFmpeg-only route: `alphaextract` the matte, `dilation` repeated, and `overlay` it in white before the speaker.
- Shapes: simple SVG on the background plate.

## Check before shipping

- Reads on a phone at full speed; stays inside the 9:16 safe zone.
- Doesn't hide the speaker's face or the captions for longer than the beat needs.
