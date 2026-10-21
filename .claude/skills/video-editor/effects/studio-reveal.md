---
name: studio-reveal
extends: null
type: background / lighting
seen_in: https://www.tiktok.com/t/ZTfk55pWb/ (@taki.gpt, "20 Video Effects Created by Claude") at 0:18–0:20
---

# Studio Reveal

**What it looks like:** The room goes dark around the speaker. Two softbox lights swing into frame on either side, an 'ON AIR' sign lights up above, and the speaker gets a soft rim light, as if a TV studio was built around them.

**When to use it:** Opening a show, a big announcement, or a 'let's get serious' moment.

**Timing:** Background dims to near black over 0.3 s. Softboxes slide and rotate in (0.4 s each, 0.1 s apart). The sign flickers on twice, then holds lit.

**Brand hooks:** ON AIR sign in `accent_color` with a glow; softboxes stay neutral white.

## How to build it

- Speaker matte; under it, a dark gradient plate with two angled white rounded rectangles and a blurred glow behind each.
- Rim light: duplicate the matte, blur 8 px, tint warm white, place behind the speaker at 40% opacity.
- Flicker: two quick opacity steps (0 to 1 to 0.3 to 1) via discrete keyframes.

## Check before shipping

- Reads on a phone at full speed; stays inside the 9:16 safe zone.
- Doesn't hide the speaker's face or the captions for longer than the beat needs.
