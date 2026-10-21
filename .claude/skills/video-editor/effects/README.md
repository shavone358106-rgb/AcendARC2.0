# Effects library — extension

New effects copied from reference videos (TikTok, Reels, YouTube) live here, one file per
effect, using `_template.md`. This folder **extends** the effects the HyperFrames skills
already ship; it never repeats them.

## Rule: no duplicates

Before adding an effect, check it against **both** lists below.

- If it already exists (same look, even under another name), **don't add a file**. Add the
  reference video to that effect's "Seen in" line in the *Added effects* table, or note the
  existing effect ID next to the reference in your report.
- If it's a **variation** of an existing effect (e.g. an existing glitch caption, but in brand
  colors with a faster cut), write it as a preset of that effect: name the base effect in
  `extends:` and list only what changes.
- Only a genuinely new look gets a new file.

## Effects that already exist (do not re-add)

**Caption styles** — `embedded-captions/CATALOG.md` (35):
cream, ink, editorial, keynote, documentary, loud, neon, glitch, chrome, velocity, anchor,
ordnance, terminal, neonsign, stardust, stomp, lastpage, scoreboard, transit, vhs, arcade,
dossier, laser, thunder, hologram, biolume, aurora, spectrum, papercut, popup, chalkboard,
graffiti, brush, inkwater, ransom

**Motion rules** — `hyperframes-animation/rules/`:
3d-camera-flight, 3d-page-scroll, 3d-text-depth-layers, ai-tracking-box, ambient-glow-bloom,
anchored-layout-expand, asr-keyword-glow, avatar-cloud-network, camera-cursor-tracking,
card-morph-anchor, center-outward-expansion, chart-scrub-readout, chromatic-glitch,
context-sensitive-cursor, control-target-sync, coordinate-target-zoom, counting-dynamic-scale,
css-marker-patterns, cursor-click-ripple, cursor-drag, depth-of-field-blur,
depth-scatter-assemble, discrete-text-sequence, dynamic-content-sequencing,
gradient-text-sweep, gsap-effects, hacker-flip-3d, kinetic-beat-slam, motion-blur-streak,
multi-cursor-choreography, multi-phase-camera, nudge-curve, orbit-3d-entry, particle-burst,
physics-press-reaction, press-release-spring, reactive-displacement, scale-swap-transition,
sine-wave-loop, split-tilt-cards, spring-pop-entrance, stat-bars-and-fills,
svg-icon-enrichment, svg-path-draw, theme-crossfade-morph, vertical-spring-ticker,
viewport-change, waterfall-entry

**Scene blueprints** — `hyperframes-animation/blueprints/`:
agent-progress-theater, camera-journey, comparison-split, constellation-hub, cta-morph-press,
cursor-ui-demo, dataviz-countup, device-surface-showcase, fixed-anchor-cycle,
grid-card-assemble, kinetic-type-beats, logo-assemble-lockup, overwhelm-surround,
panel-edit-live-sync, prompt-type-submit-generate, spatial-pan-stations, ticker-takeover,
titlecard-reveal, transcript-scroll-artifact-reveal, typewriter-reveal, video-text-pivot,
zoom-out-workspace-reveal

**Transitions** — `hyperframes-animation/transitions/` (see `TRANSITION-REGISTRY.md` for every
ID): 3d, blur, cover, destruction, dissolve, distortion, grid, light, mechanical, push, radial,
scale, other

**Text animations** — `hyperframes-animation/adapters/animate-text.md` (24 named effects,
e.g. typewriter, soft-blur-in, mask-reveal-up, kinetic-center-build, short-slide-*)

**Hosted registry** — `hyperframes-registry` (~400 blocks: glitch, CRT, film grain, shimmer,
confetti, charts, maps…). Search it with `npx hyperframes catalog` before writing anything new.

## Added effects

| Effect | File | Extends | Seen in | Added |
|---|---|---|---|---|
| Orbit | `orbit-ui-ring.md` | orbit-3d-entry | @taki.gpt 0:03–0:04 | 2026-10-21 |
| Chat Takeover | `chat-window-takeover.md` | claude-exchange | @taki.gpt 0:04–0:06 | 2026-10-21 |
| Frame Escape | `frame-escape.md` | — | @taki.gpt 0:06–0:08 | 2026-10-21 |
| Checklist Pop | `checklist-pills.md` | success-check + spring-pop-entrance | @taki.gpt 0:10–0:12 | 2026-10-21 |
| Headline Storm | `headline-storm.md` | overwhelm-surround | @taki.gpt 0:12–0:14 | 2026-10-21 |
| Zoom Portal | `zoom-portal.md` | zoom-through-transition | @taki.gpt 0:14–0:16 | 2026-10-21 |
| Growth Curve | `growth-curve-backdrop.md` | chart-story | @taki.gpt 0:16–0:18 | 2026-10-21 |
| Studio Reveal | `studio-reveal.md` | — | @taki.gpt 0:18–0:20 | 2026-10-21 |
| B-roll Overlay | `edit-timeline-overlay.md` | — | @taki.gpt 0:20–0:22 | 2026-10-21 |
| Paper Cutout | `sticker-cutout.md` | freeze-frame-dressing | @taki.gpt 0:22–0:24 | 2026-10-21 |
| Magazine Cover | `magazine-cover.md` | — | @taki.gpt 0:27–0:29 | 2026-10-21 |
| Liquid Glass | `liquid-glass-lens.md` | gravitational-lens | @taki.gpt 0:29–0:31 | 2026-10-21 |
| Green Screen | `background-swap.md` | — | @taki.gpt 0:33–0:34 | 2026-10-21 |
| Digital Zoom | `viewfinder-digital-zoom.md` | camcorder-hud | @taki.gpt 0:35–0:37 | 2026-10-21 |
| Phone Mockup | `reels-phone-mockup.md` | device-frame-stage | @taki.gpt 0:37–0:39 | 2026-10-21 |
| Checklist (recap) | `recap-checklist-counter.md` | count-up + success-check | @taki.gpt 0:39–0:40 | 2026-10-21 |

### Seen in reference videos but already in the library (no file added)

| Effect (as named in the reference) | Use this instead | Seen in |
|---|---|---|
| Snap Zoom | `punch-in` in `hyperframes-keyframes`, or `yt-camera-move` (registry) | @taki.gpt 0:08 |
| Dolly Zoom | `camera-dolly-zoom` (registry) | @taki.gpt 0:24 |
| Zoom Through Cut | `zoom-through` transition (`TRANSITION-REGISTRY.md`) / `zoom-through-transition` (registry) | @taki.gpt 0:31 |
| Frame Break | `vfx-shatter` / `transitions-destruction` (registry) | @taki.gpt 0:34 |

Reference: @taki.gpt, "20 Video Effects Created by Claude":
https://www.tiktok.com/t/ZTfk55pWb/. We copy the *technique*, never their footage, branding
or wording.

## Shared building blocks

Most of these effects put graphics **between** the background and the speaker. They all
start from a speaker matte (the person cut out with transparency):

```bash
npx hyperframes remove-background source.mp4 -o speaker-matte.webm   # see hyperframes-cli
```

Then stack the layers: background plate, effect graphics, speaker matte, captions.

Tested 2026-10-21 (sticker-cutout and magazine-cover composited with FFmpeg over the matte):
- Speed: about 0.45 s per frame on CPU, so roughly 15 minutes per minute of footage. Cut the
  edit first, then matte only the seconds that need an effect.
- Objects touching the speaker (a high-back chair, a mic arm) come through as a faint ghost at
  the edges. Tell the owner, and suggest filming effect-heavy videos against a plain wall.
- FFmpeg needs `-c:v libvpx-vp9` **before** `-i matte.webm` to keep the transparency.
Pure green-screen footage can skip the matte and use FFmpeg `chromakey` instead.
