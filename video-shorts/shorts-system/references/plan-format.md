# plan.json format (what Claude writes in the "dissect" stage)

Times are seconds on the final timeline (`clip.mp4`, after pause trimming). Word timestamps are in `words.json`.

```json
{
  "title": "Turn Claude Code into a client machine",
  "hook_end": 2.6,
  "keyword": "MACHINE",
  "moments": [
    {"start": 0.0, "end": 2.6, "job": "hook", "graphic": "title", "tone": "dark",
     "text": "This free tool builds websites for local businesses.",
     "data": {"title": "Turn Claude Code into a client machine", "accent": "machine", "sub": "a website"}},
    {"start": 2.6, "end": 4.4, "job": "problem", "graphic": "face", "tone": "dark", "text": "..."},
    {"start": 4.4, "end": 9.8, "job": "steps", "graphic": "steps", "tone": "light", "text": "...",
     "data": {"title": "How it works", "items": [{"text": "Find a bakery", "at": 4.5}, {"text": "Rebuild the site", "at": 6.9}]}},
    {"start": 9.8, "end": 12.0, "job": "number", "graphic": "big_number", "tone": "light",
     "data": {"value": "342", "label": "hours of lessons", "sub": "free on GitHub"}},
    {"start": 27.5, "end": 31.2, "job": "cta", "graphic": "cta", "tone": "dark",
     "data": {"keyword": "MACHINE", "thing": "the free setup guide"}}
  ],
  "captions": {"thing": "the free setup guide", "result": "your first client site this week",
               "link": "https://example.com/guide", "hashtags": ["claudecode", "ai", "webdesign"]},
  "cover": {"line1": "Turn Claude Code into a", "line2": "client machine"}
}
```

Rules the builder enforces automatically (you'll see "rule fix" lines): frame 0 is `title`, nothing cuts before
`hook_end`, moments under 0.5s fold into the previous one, the timeline is contiguous, the last moment is a dark
`cta` card. Graphics and their `data` fields: workspace `GRAPHICS.md`.
