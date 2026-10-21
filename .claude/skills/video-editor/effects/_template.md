---
name: effect-id-in-kebab-case
extends: null          # existing effect ID if this is a variation, else null
type: caption | transition | text-animation | overlay | color-grade | camera-move | audio
seen_in: https://...   # reference video URL + timestamp (e.g. 0:03–0:05)
---

# Effect name

**What it looks like:** one or two sentences a non-editor would recognize.

**When to use it:** platform, moment in the video (hook, beat drop, CTA), mood.

**Timing:** duration, easing, how it lines up with speech or the beat.

**Brand hooks:** which parts take the brand colors / font from `../brand.json`.

## How to build it

- **FFmpeg** (if it's a straight cut, color, or zoom effect): the filter chain.
- **HyperFrames** (if it's motion graphics or captions): the rules/blueprint it builds on and
  the composition snippet.

## Check before shipping

- Reads on a phone at full speed; stays inside the 9:16 safe zone.
- Doesn't hide the speaker's face or the captions.
