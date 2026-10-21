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
| _(none yet: waiting on the first reference video)_ | | | | |
