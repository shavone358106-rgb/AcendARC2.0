---
name: growth-curve-backdrop
extends: chart-story (hyperframes-registry component)
type: overlay / background
seen_in: https://www.tiktok.com/t/ZTfk55pWb/ (@taki.gpt, "20 Video Effects Created by Claude") at 0:16–0:18
---

# Growth Curve

**What it looks like:** The speaker's background is replaced with a dark grid chart. An orange line climbs behind them from bottom-left to top-right, and a badge in the corner counts 1× → 4× → 10× GROWTH. The speaker stays in front.

**When to use it:** Any results, numbers, or 'this grew my business' line.

**Timing:** Line draws over 1.5–2 s (power2.in so it accelerates). Badge counts on each step. Hold 0.5 s on the final value.

**Brand hooks:** Line and badge `accent_color`; grid and background `primary_color` with a 10% white grid.

## How to build it

- Speaker matte over a `chart-story` line chart.
- **Use the owner's real numbers.** If the reference shows 'sample data', label it that way too; never show a fake growth claim as real.

## Check before shipping

- Reads on a phone at full speed; stays inside the 9:16 safe zone.
- Doesn't hide the speaker's face or the captions for longer than the beat needs.
