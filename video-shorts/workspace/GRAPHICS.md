# GRAPHICS.md — which graphic when

The library lives in `scripts/graphics.py`. This page is where the taste lives: it maps the kind of line to the graphic.
Every moment in `plan.json` names one `graphic` and passes its `data`.

| Line is doing… | Graphic | `data` fields | Notes |
|---|---|---|---|
| Hook (frame 0) | `title` | `title` (3–8 words), `accent` (word(s) to colour), `sub` (one object under it, optional) | Holds with no cut until the first sentence ends. Dark. |
| A claim ("56,000 people starred it") | `image` if you have the real screenshot, else `big_number` | `image`: `path`, `label` · `big_number`: `value`, `label`, `sub` | Proof within 2 seconds. Crop to the word. |
| A number | `big_number` | `value` ("342", "$5.70", "0.1s"), `label`, `sub` | Huge, counts up. Never just appears. |
| A list of 3 | `list` | `title`, `items: [{text, at}]` (`at` = second the item is spoken) | One row lands per spoken item. "But here's the best part" goes before the best one. |
| Steps ("First… Then…") | `steps` | `title`, `items: [{text, at}]` | Numbered ladder that builds. |
| Before / after, old way / new way | `before_after` | `title`, `before {label,text}`, `after {label,text}`, `at` | Both sides labeled and visible. |
| A prompt / what Claude does | `prompt` | `text` (the prompt), `answer`, `app_title` | Types in on your voice, then the answer. App, not a terminal. |
| An idea in plain words | `statement` | `text`, `accent` | Fallback when nothing better fits. |
| The problem line, "here's the trick", an opinion, a payoff, "You don't." | `face` | — | Full-frame face, 1–2 seconds. |
| The ending | `cta` | `keyword`, `thing`, `verb` ("Comment") — or `line` for link-only | Always dark. Matches the lane's CTA line word for word. |

## When to cut vs keep building
- Cut when the idea changes. Hang while it builds: add a row, a step, a highlight on the graphic already up.
- Anything spoken in under half a second is a step on the current graphic, never a new moment.
- One line often holds two pictures ("start at lesson one… grind through all 523" = close-up, then zoom out). Split it.
- The verb picks the motion: *turns into* = morph, *pick one* = pick, *one to all* = zoom out, *send it to* = show it sent, *you don't* = cut to face.
- Real footage / screenshots are about a quarter of the beats. Graphics carry the rest.

## Never do
- Six fast cuts in a row. One graphic that builds in time with the words is smoother.
- A caption on top of a graphic.
- Something shown before it's said.

## No graphic yet for… (add a renderer to graphics.py, then a row above)
- Hub / loop diagrams (Read → Think → Act → Check)
- Zoom from one tile to a full grid
- Logo strip for tool / repo / launch shorts
