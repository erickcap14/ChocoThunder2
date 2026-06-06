"""Game State MCP server.

A FastMCP sidecar that lets Claude Code drive the running game for automated
verification. Tools translate to commands written into the IPC command file; the
game polls that file once per frame (see ``poll_mcp_command`` in main.py).

Run standalone:   python -m mcp_server.server
Wired into Claude Code via .claude/settings.json -> mcpServers.game-state
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from mcp_server.state_bridge import (
    read_state,
    write_command,
    write_command_with_args,
)

mcp = FastMCP("Game State MCP")


# --- Query -----------------------------------------------------------------
@mcp.tool()
def get_state() -> dict:
    """Return the current game state as JSON (state name, running flag, score, level, audio)."""
    return read_state()


# --- State jumps -----------------------------------------------------------
@mcp.tool()
def jump_to_start() -> str:
    """Force the running game to the START (title) screen."""
    write_command("jump_to_start")
    return "Command sent: jump_to_start"


@mcp.tool()
def jump_to_transition() -> str:
    """Force the running game to the level TRANSITION screen."""
    write_command("jump_to_transition")
    return "Command sent: jump_to_transition"


@mcp.tool()
def jump_to_running() -> str:
    """Force the running game into active gameplay (RUNNING)."""
    write_command("jump_to_running")
    return "Command sent: jump_to_running"


@mcp.tool()
def jump_to_end() -> str:
    """Force the running game to the END screen."""
    write_command("jump_to_end")
    return "Command sent: jump_to_end"


@mcp.tool()
def jump_to_scoreboard() -> str:
    """Force the running game to the SCOREBOARD screen."""
    write_command("jump_to_scoreboard")
    return "Command sent: jump_to_scoreboard"


# --- Screen-specific actions ----------------------------------------------
@mcp.tool()
def set_level(n: int) -> str:
    """Load level ``n`` (1-based) immediately."""
    write_command_with_args("set_level", n=n)
    return f"Command sent: set_level n={n}"


@mcp.tool()
def spawn_powerup() -> str:
    """Spawn a cake power-up on the play screen."""
    write_command("spawn_powerup")
    return "Command sent: spawn_powerup"


@mcp.tool()
def spawn_npc() -> str:
    """Spawn an additional tenant (NPC) on the play screen."""
    write_command("spawn_npc")
    return "Command sent: spawn_npc"


@mcp.tool()
def drop_poo() -> str:
    """Drop a chocolate surprise at the player's current position."""
    write_command("drop_poo")
    return "Command sent: drop_poo"


@mcp.tool()
def set_invincible(on: bool = True) -> str:
    """Toggle the player's invincibility window on or off."""
    write_command_with_args("set_invincible", on=on)
    return f"Command sent: set_invincible on={on}"


@mcp.tool()
def toggle_music() -> str:
    """Toggle background music on/off."""
    write_command("toggle_music")
    return "Command sent: toggle_music"


@mcp.tool()
def toggle_sfx() -> str:
    """Toggle sound effects on/off."""
    write_command("toggle_sfx")
    return "Command sent: toggle_sfx"


if __name__ == "__main__":
    mcp.run()
