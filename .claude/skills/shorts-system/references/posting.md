# Posting to platforms

`shorts.py post DIR` refuses unless `shorts.py approve DIR` was run on the exact `final.mp4` (sha256 match),
checks the guide/link is live, and picks the next free morning slot (one post a day).

| Provider | Set up | Notes |
|---|---|---|
| `dry-run` (default) | nothing | Prints what would be posted. |
| `ayrshare` | `export AYRSHARE_API_KEY=...`; host `final.mp4` somewhere public and pass `--media-url` | One API to Instagram, Facebook, TikTok, YouTube, X, LinkedIn. One request per platform so each gets its own caption. |
| `webhook` | `export SHORTS_WEBHOOK_URL=...` (Zapier / Make / n8n catch hook) | Sends platform, caption, slot, keyword, file paths, DM script. Build the posting Zap/scenario on your side. |

Inside Claude Code you can also post through connected tools after approval (e.g. a Zapier MCP action, or a
TikTok publish connector) — same rule: only after the user says go in that chat.

**Comment-to-DM:** `dm.md` has the trigger word, follow gate, DM text with two buttons, and the public reply.
Paste it into your DM tool (ManyChat or similar). Instagram + Facebook only: other apps can't answer a comment,
which is why their captions carry the link instead.

**Cadence:** one post a day, same morning slot. Don't reuse the music bed from the day before or after.
Two days after a free-guide short goes live, count unique keyword commenters; the best one twice a week becomes
a community post (who it's for, when to skip it). Never post the same resource twice.
