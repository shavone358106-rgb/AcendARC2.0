---
name: headline-storm
extends: overwhelm-surround (blueprint) + news-ticker styling
type: overlay
seen_in: https://www.tiktok.com/t/ZTfk55pWb/ (@taki.gpt, "20 Video Effects Created by Claude") at 0:12–0:14
---

# Headline Storm

**What it looks like:** Breaking-news ribbons ("BREAKING", "JUST IN", "UPDATE" tags, then a white headline bar) slam in one after another at random tilts, piling up around and partly behind the speaker until the frame is crowded.

**When to use it:** Hype or 'everyone is talking about this' moments. Short: 1.5–2 s.

**Timing:** 6–10 ribbons, one every 120–180 ms, each sliding in from off-screen with 4–8° tilt. Some go behind the speaker (matte), some in front.

**Brand hooks:** Tag chips in `accent_color`, headline bars white with `primary_color` text, `font` uppercase.

## How to build it

- Build each ribbon as a block from the `news-ticker` look; arrange them with `overwhelm-surround` close-in staging.
- Use the speaker matte so at least half the ribbons pass behind the head.
- Write the headlines from the transcript; never invent news claims.

## Check before shipping

- Reads on a phone at full speed; stays inside the 9:16 safe zone.
- Doesn't hide the speaker's face or the captions for longer than the beat needs.
