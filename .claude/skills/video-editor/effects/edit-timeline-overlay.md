---
name: edit-timeline-overlay
extends: null
type: overlay
seen_in: https://www.tiktok.com/t/ZTfk55pWb/ (@taki.gpt, "20 Video Effects Created by Claude") at 0:20–0:22
---

# B-roll Overlay

**What it looks like:** A screen recording of an editing app fills the top of the frame. Underneath sits a simplified two-track timeline: a blue 'Talking head' bar on V1 and an orange 'B-roll' clip on V2, with a playhead sweeping across.

**When to use it:** Explaining an edit, a process, or 'here's what I added' moments.

**Timing:** Timeline rises in 0.3 s, the B-roll clip drops onto V2 with a small bounce, and the playhead moves in sync with the video time.

**Brand hooks:** V1 bar `primary_color`, V2 clip `accent_color`, labels in `font`.

## How to build it

- Timeline: HTML block with two rows; playhead position tied to composition time so it seeks correctly.
- Top panel: the owner's own screen recording or B-roll clip in a rounded window.
- Keep track labels readable at phone size (min 28 px).

## Check before shipping

- Reads on a phone at full speed; stays inside the 9:16 safe zone.
- Doesn't hide the speaker's face or the captions for longer than the beat needs.
