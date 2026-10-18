---
name: shorts-system
description: One-command AI shorts system (built from the Shortify guide). Turns a topic, a recorded take, or a long video into finished 9:16 short ad videos. It writes and cold-reads the script, cuts and reframes, trims pauses, adds word-synced captions and motion graphics, checks every frame, writes captions for each platform plus the DM script and a cover, then posts to Instagram, Facebook, TikTok, YouTube, X and LinkedIn only after the user approves. Use when the user asks to make a short, reel, TikTok, YouTube Short or short ad video, cut a long video into shorts, run "/shorts-system", or schedule or post shorts.
---

# Shorts System

**One topic → one short → one comment → one DM → one warm lead.**
The user gives one command; you run every stage below without stopping, except at the two gates.

`SKILL_DIR` = the folder that holds this file (`.claude/skills/shorts-system` or `~/.claude/skills/shorts-system`).
CLI: `python3 SKILL_DIR/scripts/shorts.py`. Workspace (style, graphics guide, keywords, the shorts): `$SHORTS_HOME`,
default `./video-shorts/workspace`. Run `shorts.py init` once if it doesn't exist.

## The two gates (never skip)
1. **Script lock**: when a script must be voiced (new topic, no footage yet), stop after the cold read until the user says **"locked"**. Every word changed after the voice costs a new render.
2. **Approval**: nothing posts or gets scheduled until the user has watched `final.mp4` and says **go** in this chat. Then run `shorts.py approve DIR` and `shorts.py post DIR`. `post` refuses if the video or captions changed after approval.

## What the user's one command means
| They give you | You run |
|---|---|
| A long video (+ maybe "make 3") | **Cut mode** with `--source FILE --count N` |
| A recorded take or AI-twin render | **Take mode** with `--recording FILE` |
| A topic only | **Script mode**: card → keyword → hook → script → cold read → STOP for "locked" |
| "post / schedule it" | Gate 2, then `post` |

Ask only for what you can't infer: the lane (top/middle/bottom/ad), what the comment gets (`--thing`), and the link. Defaults: lane `top`; lane `middle` for the user's own long videos; lane `ad` for a product or offer.

## Pipeline (you drive it; the CLI does the heavy lifting)
Read the workspace `STYLE.md`, `GRAPHICS.md` and `MISTAKES.md` first. Point to them; don't copy them into prompts.

1. **Topic card + lane.** Source, real numbers, lane, and 2–3 proven hook options. For trend topics, use outliers (≥3x the creator's median views), from the last 7 days, that fit what the user teaches and haven't been covered by 3 competitors or posted already.
2. **Keyword.** `shorts.py keyword check WORD --topic "..."`. It must pass before any script is written. Bottom lane always uses the fixed community word.
3. **Hook.** Steal a winner word for word and swap only the slots (`references/script-rules.md`). Refuse winners under 3x the median.
4. **Script + cold read.** Write 105–125 words in the shape from `references/script-rules.md`. Then spawn a **cold-reader subagent** that has never seen the project (Prompt 2 in `references/prompts.md`). Show the fixed script and **STOP (gate 1)**.
5. **Voice + face.** The user records it, or renders an AI twin once (e.g. a HeyGen tool if connected). One render per short.
6. **Prepare the footage**:
   `shorts.py make --source|--recording FILE [--count N] --lane L --topic "..." --thing "..." --link URL [--keyword W] [--asset proof.png] [--music bed.mp3] --planner external`
   It cuts, reframes to 9:16, trims pauses, gets word timestamps, then exits with code 3 and `PLAN_NEEDED` for each short folder.
7. **Dissect.** For each folder, spawn a **dissector subagent** (Prompt 7). Give it `plan_request.md`, `words.json`, workspace `GRAPHICS.md` and `references/plan-format.md`. It writes `plan.json`: every sentence split into small visual moments, the verb picks the motion, graphics picked from GRAPHICS.md, a dark/light split of about 40–60%, a title on frame 0, and a dark CTA ending.
8. **Build + QA.** Re-run the same `make` command. It renders graphics, captions, sound effects and music, composites, runs the automatic QA, and writes contact sheets (3 frames per second) to `qa/`.
9. **Check every frame.** Spawn a **QA-reviewer subagent** (Prompt 6). It opens every `qa/sheet_*.jpg`, then `qa/frames/*.jpg` at full size where something looks off. It lists defects with timestamps, worst first: cut-off or tiny text, empty frames, unreadable screenshots, captions on top of graphics, something shown before it's said, beats too short to read, cuts during the hook, text in safe zones. Fix by editing `plan.json`, run `shorts.py build DIR`, and repeat until the list is empty and `qa/report.md` has no high issues.
10. **Captions + cover.** `make`/`build` already wrote `captions.md` (Instagram and Facebook open with the comment line; TikTok, YouTube, X and LinkedIn carry the link; 5 hashtags max), `dm.md` and `cover.jpg` (also check `cover_gridcrop.jpg`). Tighten the wording if needed.
11. **Stop and show everything**: `final.mp4`, the cover, the captions, the DM setup, the QA report, the moments table from `SUMMARY.md`, and the spend. Walk the checklist in `references/checklist.md`. **Wait for "go" (gate 2).**
12. **Post**: `shorts.py approve DIR` → `shorts.py post DIR --platforms instagram,facebook,tiktok,youtube --provider ayrshare|webhook` (see `references/posting.md`). One post a day, same morning slot. The link must be live or the slot is skipped. If a posting connector is available in this session (e.g. Zapier), you may use it instead, after approval only.

Without Claude Code (plain terminal + `ANTHROPIC_API_KEY`), `shorts.py make` does steps 4, 7 and 9 itself through the Claude API. Without either, it falls back to an offline planner.

## Subagents (one helper per job, a brief that stands alone)
Give each subagent the files to read, the goal, the rules, and where to save. Ask for a report of under 150 words: what it made, where it saved it, what it wasn't sure about. Then you review it. The splits that work: topic scout, creator study (Prompt 4, one per creator), cold reader, graphics builder (one per new renderer in `scripts/graphics.py`), dissector, QA reviewer. Several short folders can run side by side.

## Rules that bite
- Real numbers only, each with a source. Write money as words in the spoken script; numerals only in captions and graphics.
- The hook holds with no cut until the first sentence ends. Anything under 0.5s is a build step, never a new shot.
- Claims show proof within 2 s. Every screenshot must read in 1 s at phone size, or build a graphic with the real number instead. If a tool is named, show it.
- One look, locked (`STYLE.md`). Change it on purpose, once, after a side-by-side test.
- When the library can't draw something, add a renderer to `scripts/graphics.py` and a row to `GRAPHICS.md`.
- Every fix you make goes as one line into the workspace `MISTAKES.md`, so it doesn't happen again.
- Spend is logged per short in `spend.json` (`shorts.py status` shows totals). Log AI-twin and other paid renders with their cost.
