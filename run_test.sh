#!/usr/bin/env bash
# Launch ChocolateThunder2 in UI walkthrough (test) mode.
# Arrow keys cycle through every screen. Activates .venv if present.
set -e
cd "$(dirname "$0")"

if [ -d ".venv" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

exec python main.py --test "$@"
