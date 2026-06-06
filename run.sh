#!/usr/bin/env bash
# Launch ChocolateThunder2: ElectricBoogaloo.
# Activates a local .venv if present, then runs the game.
set -e
cd "$(dirname "$0")"

if [ -d ".venv" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

exec python main.py "$@"
