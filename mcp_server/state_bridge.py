"""File-based IPC primitives shared by the game and the Game State MCP server.

The game is the *producer* of state and the *consumer* of commands:
  - every frame it calls ``write_state(...)`` then ``read_command_full()``.
The MCP server is the *consumer* of state and the *producer* of commands:
  - tools call ``read_state()`` / ``write_command(...)``.

No shared memory, sockets, or threads -- just two tiny JSON files. This keeps
the game loop and the MCP server fully decoupled and trivially testable.
"""

from __future__ import annotations

import json
from pathlib import Path

# Resolved relative to this file so cwd never matters (game vs. MCP vs. pytest).
_IMPL = Path(__file__).resolve().parent.parent / ".implementations"
STATE_FILE = _IMPL / "game_state.json"
COMMAND_FILE = _IMPL / "game_command.json"


def _ensure_dir() -> None:
    _IMPL.mkdir(parents=True, exist_ok=True)


# --- State: game writes, MCP reads ----------------------------------------
def write_state(state_name: str, **extra) -> None:
    """Game calls this every frame. Merges ``extra`` kwargs into the JSON."""
    _ensure_dir()
    payload = {"state": state_name, "running": True, **extra}
    STATE_FILE.write_text(json.dumps(payload))


def read_state() -> dict:
    """MCP calls this. Returns a sentinel dict if the game isn't running."""
    if not STATE_FILE.exists():
        return {"state": "UNKNOWN", "running": False}
    try:
        return json.loads(STATE_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {"state": "UNKNOWN", "running": False}


# --- Commands: MCP writes, game reads -------------------------------------
def write_command(command: str) -> None:
    """MCP calls this to send a no-argument command to the game."""
    write_command_with_args(command)


def write_command_with_args(command: str, **args) -> None:
    """MCP calls this for commands that take arguments."""
    _ensure_dir()
    COMMAND_FILE.write_text(json.dumps({"command": command, "args": args}))


def read_command() -> str | None:
    """Game calls this. Returns the command name, or None if nothing pending."""
    full = read_command_full()
    return full[0] if full else None


def read_command_full() -> tuple[str, dict] | None:
    """Game calls this. Returns ``(command, args)`` or None if nothing pending."""
    if not COMMAND_FILE.exists():
        return None
    try:
        data = json.loads(COMMAND_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return None
    return data.get("command", ""), data.get("args", {})


def clear_command() -> None:
    """Game calls this after executing a command (deletes COMMAND_FILE)."""
    COMMAND_FILE.unlink(missing_ok=True)
