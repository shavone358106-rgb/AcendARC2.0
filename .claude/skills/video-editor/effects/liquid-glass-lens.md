---
name: liquid-glass-lens
extends: gravitational-lens (hyperframes-registry shader transition)
type: overlay / distortion
seen_in: https://www.tiktok.com/t/ZTfk55pWb/ (@taki.gpt, "20 Video Effects Created by Claude") at 0:29–0:31
---

# Liquid Glass

**What it looks like:** A clear glass blob glides across the frame over the speaker's face, bending and magnifying what's behind it with a bright rim highlight, like a drop of liquid glass sliding past.

**When to use it:** A soft pattern break or reveal on a key word.

**Timing:** The lens travels across in 0.8–1.2 s on a gentle S-curve, 15–25% of frame width, with slight wobble in its shape.

**Brand hooks:** Mostly neutral; an optional faint `accent_color` tint on the rim.

## How to build it

- Reuse the `gravitational-lens` shader distortion, but as a moving lens over playing footage, not as a scene transition.
- Distortion: radial magnification about 1.15 inside the blob, falling off at the edge, plus a 1–2 px specular rim.
- Keep it off the eyes at the end of the move so the speaker reconnects with camera.

## Check before shipping

- Reads on a phone at full speed; stays inside the 9:16 safe zone.
- Doesn't hide the speaker's face or the captions for longer than the beat needs.
