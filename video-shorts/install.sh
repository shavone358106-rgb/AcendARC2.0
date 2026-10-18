#!/usr/bin/env bash
# Install the Shorts System skill.
#   ./video-shorts/install.sh            -> project skill (.claude/skills/shorts-system) + workspace
#   ./video-shorts/install.sh --user     -> also ~/.claude/skills/shorts-system (all your projects)
#   ./video-shorts/install.sh --no-deps  -> skip pip installs
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
USER_INSTALL=0; DEPS=1
for a in "$@"; do
  case "$a" in
    --user) USER_INSTALL=1 ;;
    --no-deps) DEPS=0 ;;
    *) echo "unknown option $a"; exit 1 ;;
  esac
done

command -v python3 >/dev/null || { echo "python3 is required"; exit 1; }
if ! command -v ffmpeg >/dev/null; then
  echo "ffmpeg is required (with libass + libfreetype):"
  echo "  macOS: brew install ffmpeg    Ubuntu/Debian: sudo apt install ffmpeg    Windows: winget install ffmpeg"
  exit 1
fi

if [ "$DEPS" = 1 ]; then
  echo "installing python packages..."
  python3 -m pip install -q -r "$HERE/requirements.txt" 2>/dev/null \
    || python3 -m pip install -q --user -r "$HERE/requirements.txt" 2>/dev/null \
    || python3 -m pip install -q --break-system-packages -r "$HERE/requirements.txt"
fi

install_to() {
  local dest="$1"
  mkdir -p "$(dirname "$dest")"
  rm -rf "$dest"
  cp -R "$HERE/shorts-system" "$dest"
  find "$dest" -name "__pycache__" -type d -prune -exec rm -rf {} +
  chmod +x "$dest/scripts/shorts.py"
  echo "skill installed: $dest"
}

install_to "$ROOT/.claude/skills/shorts-system"
[ "$USER_INSTALL" = 1 ] && install_to "$HOME/.claude/skills/shorts-system"

cd "$ROOT" && python3 "$HERE/shorts-system/scripts/shorts.py" init

echo
echo "Done. In Claude Code:   /shorts-system cut my-long-video.mp4 into 3 shorts"
echo "From a terminal:        python3 .claude/skills/shorts-system/scripts/shorts.py make --source my-video.mp4 --count 3"
