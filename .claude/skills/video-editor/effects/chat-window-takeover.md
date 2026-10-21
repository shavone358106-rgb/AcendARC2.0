---
name: chat-window-takeover
extends: claude-exchange (hyperframes-registry block)
type: overlay / transition
seen_in: https://www.tiktok.com/t/ZTfk55pWb/ (@taki.gpt, "20 Video Effects Created by Claude") at 0:04–0:06
---

# Chat Takeover

**What it looks like:** The live footage shrinks into a chat window as an attached video. Above it, the prompt ("Edit this video, caption every word, then add these effects") appears as a message. Below, a reply streams in as a checklist that ticks off: cut the pauses, caption every word, add the effects.

**When to use it:** Behind-the-scenes or 'how I made this' moments; showing the request behind the edit.

**Timing:** Footage scales 100% to ~40% into the attachment slot over 0.5 s (expo.out). Window rises from below. Checklist rows tick every 0.4–0.5 s.

**Brand hooks:** Window chrome stays neutral white; check ticks and the send button take `accent_color`. Use the owner's own app or logo, never another company's branding unless it's genuinely their tool.

## How to build it

- Start from `claude-exchange` (or `ai-chat-reveal`) and replace the static attachment with the live video element.
- Animate the video wrapper's transform from full-frame to the attachment rect (FLIP), so it keeps playing during the move.
- Checklist ticks: `success-check` component.

## Check before shipping

- Reads on a phone at full speed; stays inside the 9:16 safe zone.
- Doesn't hide the speaker's face or the captions for longer than the beat needs.
