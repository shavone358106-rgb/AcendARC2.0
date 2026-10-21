---
name: recap-checklist-counter
extends: count-up + success-check (hyperframes-registry components)
type: overlay / end card
seen_in: https://www.tiktok.com/t/ZTfk55pWb/ (@taki.gpt, "20 Video Effects Created by Claude") at 0:39–0:40
---

# Checklist (recap)

**What it looks like:** A full-screen recap card: a big number counts 0 → 20 next to '/20 effects', while a two-column checklist of everything in the video ticks off item by item.

**When to use it:** End of a list or tutorial video, just before the call to action.

**Timing:** Counter and ticks run together over about 1–1.5 s (roughly 50–70 ms per item), then hold 0.5 s.

**Brand hooks:** Counter and checks in `accent_color`; card `primary_color`; labels in `font`.

## How to build it

- `count-up` component for the number, `success-check` for each tick, laid out in a two-column grid.
- Pull the list from the video's own chapters so it's always accurate.

## Check before shipping

- Reads on a phone at full speed; stays inside the 9:16 safe zone.
- Doesn't hide the speaker's face or the captions for longer than the beat needs.
