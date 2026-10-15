"""Load API keys for AcendARC automations.

Reads from real environment variables first, then falls back to keys/.env.

    from keys.load_keys import get_secret
    api_key = get_secret("ANTHROPIC_API_KEY")
"""
import os
from pathlib import Path

_ENV_FILE = Path(__file__).resolve().parent / ".env"


def _read_env_file():
    values = {}
    if _ENV_FILE.exists():
        for line in _ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def get_secret(name):
    value = os.environ.get(name) or _read_env_file().get(name)
    if not value:
        raise KeyError(f"{name} is not set. Add it to keys/.env or your environment.")
    return value
