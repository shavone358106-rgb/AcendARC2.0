---
name: reels-phone-mockup
extends: device-frame-stage (hyperframes-registry component)
type: overlay / framing
seen_in: https://www.tiktok.com/t/ZTfk55pWb/ (@taki.gpt, "20 Video Effects Created by Claude") at 0:37–0:39
---

# Phone Mockup

**What it looks like:** The video shrinks into a phone on a dark background and shows inside a Reels/TikTok-style UI (top label, username and caption bottom-left, action icons on the right), so it looks like the finished post on a phone.

**When to use it:** Previewing how the post will look, 'link in bio' or 'post this' segments, end cards.

**Timing:** Phone rises and settles over 0.5 s (`device-frame-stage`), then an idle float of ±4 px.

**Brand hooks:** Background `primary_color` with a subtle glow; the username is the owner's handle.

## How to build it

- `device-frame-stage` with the live video in the screen slot.
- Add platform chrome as a simple overlay (no real logos; generic icons only).
- Use the owner's real handle and caption.

## Check before shipping

- Reads on a phone at full speed; stays inside the 9:16 safe zone.
- Doesn't hide the speaker's face or the captions for longer than the beat needs.
