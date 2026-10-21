---
name: zoom-portal
extends: zoom-through-transition (hyperframes-registry component)
type: transition
seen_in: https://www.tiktok.com/t/ZTfk55pWb/ (@taki.gpt, "20 Video Effects Created by Claude") at 0:14–0:16
---

# Zoom Portal

**What it looks like:** A small circular 'portal' with an orange ring opens in the corner showing a second shot (or the same speaker). The camera then pushes into the portal while the main shot blurs, and the portal shot becomes full-frame.

**When to use it:** Jumping to a second angle, a flashback, or a related clip.

**Timing:** Portal scales in over 0.3 s, holds about 0.8 s, then a 0.5 s zoom into it with a background blur ramp (0 to 12 px).

**Brand hooks:** Portal ring in `accent_color`, 6 px.

## How to build it

- Use `zoom-through-transition`, with a circular mask (border-radius 50%) on the focal card.
- Main shot blur: `depth-of-field-blur` rule.
- The portal clip should already be playing before the push so motion carries through.

## Check before shipping

- Reads on a phone at full speed; stays inside the 9:16 safe zone.
- Doesn't hide the speaker's face or the captions for longer than the beat needs.
