---
name: frame-escape
extends: null
type: overlay
seen_in: https://www.tiktok.com/t/ZTfk55pWb/ (@taki.gpt, "20 Video Effects Created by Claude") at 0:06–0:08
---

# Frame Escape

**What it looks like:** The shot shrinks into a tilted white-bordered photo card on a dark background. The speaker's head and shoulders then break out over the top edge of the card while the rest of the body stays inside it, like they're stepping out of the photo.

**When to use it:** Pattern break around 0:05–0:10, or to punctuate a 'step outside the box' line.

**Timing:** Card shrink and tilt (−3° to 3°) over 0.4 s. Head pops out 0.2 s later with a small overshoot (back.out(1.6)). Hold 1–1.5 s, then reverse or cut.

**Brand hooks:** Background `primary_color` (dark). Optional thin `accent_color` card border instead of white.

## How to build it

- Layers, bottom to top: dark background, card (white border plus the full shot), matte of the speaker **clipped to the area above the card's top edge**.
- The matted head sits exactly on top of the same pixels in the card, so the escape reads as one person.
- Card shadow: 0 30px 60px rgba(0,0,0,.5).

## Check before shipping

- Reads on a phone at full speed; stays inside the 9:16 safe zone.
- Doesn't hide the speaker's face or the captions for longer than the beat needs.
