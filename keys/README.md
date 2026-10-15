# API Keys

Central place for the API keys your automations pull from.

- `keys/.env` — your real keys (gitignored, never pushed to GitHub)
- `keys/.env.example` — template showing which keys are expected
- `keys/load_keys.py` — helper: `get_secret("ANTHROPIC_API_KEY")`

Setup on a new machine:

```bash
cp keys/.env.example keys/.env
# then edit keys/.env and paste your key
```

Lookup order: environment variable first, then `keys/.env`.
For Claude Code cloud sessions, add the key as an environment variable in the
environment settings instead, since cloud containers are wiped after each session.
