---
name: checklist-pills
extends: success-check + spring-pop-entrance
type: overlay
seen_in: https://www.tiktok.com/t/ZTfk55pWb/ (@taki.gpt, "20 Video Effects Created by Claude") at 0:10–0:12
---

# Checklist Pop

**What it looks like:** Three white pill tags (Edit, Captions, Effects) pop in one at a time to the right of the speaker's face, each with a check icon that draws on.

**When to use it:** Listing 2–4 quick points, benefits, or steps while talking.

**Timing:** Each pill springs in 0.35 s apart (scale 0.6 to 1, back.out). Check draws 0.15 s after its pill lands.

**Brand hooks:** Check circles in `accent_color`; pill text in `font`, dark text on white.

## How to build it

- `spring-pop-entrance` rule for the pills, `success-check` component for the ticks.
- Place them in the empty side of the frame, opposite the speaker's dominant hand.
- Keep pill text to one word each.

## Check before shipping

- Reads on a phone at full speed; stays inside the 9:16 safe zone.
- Doesn't hide the speaker's face or the captions for longer than the beat needs.
