# Video Shorts: one-command AI shorts system

This system is built from the guide *"Build Your Own Shortify"* by Claude Code Club. The full transcription is in [TRANSCRIPT.md](TRANSCRIPT.md).

Give it a long video, a recorded take, or just a topic. **One command** writes the script, cuts and reframes the video, builds the motion graphics and captions, checks every frame, and writes captions for each platform plus a DM script and a cover. Then it stops until you approve. After you say go, it schedules posts to Instagram, Facebook, TikTok, YouTube, X and LinkedIn.

## Install

```bash
./video-shorts/install.sh          # skill in .claude/skills/shorts-system + workspace in video-shorts/workspace
./video-shorts/install.sh --user   # also install for every project (~/.claude/skills)
```

You need Python 3.10+ and ffmpeg. The installer pip-installs Pillow and faster-whisper, plus the optional anthropic package.

## The one command

**In Claude Code** (no API key needed; Claude does the writing, planning and frame checks with subagents):

```
/shorts-system cut ~/Videos/podcast-ep12.mp4 into 3 short ads for my booking page https://mysite.com/book
/shorts-system make a short about "Claude Code builds client websites", lane top
/shorts-system post the approved short to instagram, tiktok and youtube tomorrow morning
```

**From a terminal:**

```bash
S=.claude/skills/shorts-system/scripts/shorts.py
python3 $S make --source long.mp4 --count 3 --lane middle --thing "the full video" --link https://youtu.be/...
python3 $S make --recording take.mp4 --topic "Free 342-hour AI course" --lane top --thing "the free guide" --link https://...
python3 $S make --topic "..." --hook "proven hook, word for word" --hook-views 300000 --hook-median 40000   # writes the script, then stops for "locked"
python3 $S approve video-shorts/workspace/shorts/<folder>     # after YOU watched final.mp4
python3 $S post    video-shorts/workspace/shorts/<folder> --platforms instagram,facebook,tiktok,youtube --provider ayrshare --media-url https://...
python3 $S status
```

If `ANTHROPIC_API_KEY` is set, `make` uses Claude to pick segments, write and cold-read scripts, plan the visual moments, and review contact sheets (vision QA, fix, re-render). Without a key it uses an offline planner.

## What `make` does

| Stage (guide) | Done by |
|---|---|
| 1 Topic card, 2 Keyword | `keywords.py`: checked against reserved, retired, your DM automations, recent captions and common words |
| 3 Hook, 4 Script lock | stolen hook (≥3x median, ≥70% of words kept), 105–125 words, cold read by a fresh-context reviewer, stops for "locked" |
| 5 Voice + face | your take or an AI-twin render; pauses trimmed before the render |
| 6 Dissect | `plan.json`: moments, graphics from `GRAPHICS.md`, verb picks the motion; the rules are enforced automatically |
| 7 Build | `graphics.py` (title, big number that counts up, list, steps, before/after, prompt typing, CTA card, proof image, face), 1–2 word captions on word timestamps, dark/light tone runs, face card, whoosh/tick sound effects, music bed, −14 LUFS |
| 8 QA | length, loudness, black frames, dead air, cut during the hook, beats under 0.5s, safe zones, caption length, tone split, CTA ending. Plus contact sheets at 3 frames per second, reviewed frame by frame, fixed and re-rendered |
| 9 Captions + cover | `captions.md` for each platform, `dm.md` (follow gate, two buttons, public reply), `cover.jpg` + grid-crop preview |
| 10 Schedule (you approve) | `approve` hashes the exact video; `post` refuses otherwise, checks that the link is live, and books one post a day |

## Folders

```
video-shorts/
  TRANSCRIPT.md          the guide, transcribed
  install.sh             installs the skill + workspace
  shorts-system/         the skill (copied to .claude/skills/shorts-system)
    SKILL.md             what Claude follows for /shorts-system
    scripts/             shorts.py (CLI), media, plan, graphics, render, qa, keywords, publish, planner
    templates/           STYLE.md, GRAPHICS.md, style.json, keywords.json, MISTAKES.md
    references/          the 11 prompts, script rules, plan format, posting, checklist
  workspace/             your style, graphics guide, keywords, and one folder per short
```

## Make it yours

- **Look:** edit `workspace/STYLE.md` and `workspace/style.json` together (colors, fonts, caption size), or run Prompt 3 from `references/prompts.md`.
- **Graphics:** add a renderer to `scripts/graphics.py` whenever a script needs something the library can't draw, then add a row to `workspace/GRAPHICS.md`.
- **Posting:** set `AYRSHARE_API_KEY` (one API for every platform) or `SHORTS_WEBHOOK_URL` (a Zapier/Make/n8n hook). See `references/posting.md`.
- **Comment-to-DM:** paste `dm.md` into your DM tool (ManyChat or similar) and test it from a second account.
- **Cost:** about $0 per short with your own camera and no paid tools. The guide's paid setup (AI twin + scheduler) runs about $8 per short.
