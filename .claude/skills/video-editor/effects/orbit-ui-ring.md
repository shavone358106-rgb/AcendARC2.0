---
name: orbit-ui-ring
extends: orbit-3d-entry (hyperframes-animation/rules)
type: overlay
seen_in: https://www.tiktok.com/t/ZTfk55pWb/ (@taki.gpt, "20 Video Effects Created by Claude") at 0:03–0:04
---

# Orbit

**What it looks like:** Small app-style icon chips (play, CC, Aa, waveform, scissors, logo) travel on a dashed elliptical path around the speaker's head. Chips pass **behind** the head on the far side of the ring and in front on the near side.

**When to use it:** Hook or intro, while naming the tools or features you'll cover. One beat only (1–1.5 s).

**Timing:** Ring draws on over 0.3 s, chips flip in staggered 60 ms apart, then orbit one-third to half a turn and fade. Ease: power2.inOut.

**Brand hooks:** Chip fills white with an icon in `primary_color`; one chip in `accent_color` as the hero. Dashed ring at 60% white.

## How to build it

- Matte the speaker (see *Shared building blocks* in README) and sit the ring between the background plate and the matte layer.
- Use `orbit-3d-entry` for the motion; add a z-index flip at the ring's back half so chips slide behind the head.
- Chips: 64–72 px rounded squares, soft drop shadow.

## Check before shipping

- Reads on a phone at full speed; stays inside the 9:16 safe zone.
- Doesn't hide the speaker's face or the captions for longer than the beat needs.
