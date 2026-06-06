"""ChocolateThunder2: ElectricBoogaloo — entry point and game loop.

Each frame the loop does two MCP-related things, in order:
    1. write_state(...)        -> publish current state for the MCP server
    2. poll_mcp_command(...)   -> apply any command the MCP server queued

Run the game:            python main.py
Headless MCP smoke test: python main.py --smoke --frames 120
"""

from __future__ import annotations

import argparse
import os

from game.state_machine import GameState, StateMachine
from mcp_server.state_bridge import (
    clear_command,
    read_command_full,
    write_state,
)

# Map jump_* commands to the state they force.
_JUMPS = {
    "jump_to_start": GameState.START,
    "jump_to_transition": GameState.TRANSITION,
    "jump_to_running": GameState.RUNNING,
    "jump_to_end": GameState.END,
    "jump_to_scoreboard": GameState.SCOREBOARD,
}


def poll_mcp_command(state_machine, active_screen=None, audio_manager=None) -> None:
    """Apply at most one queued MCP command. Call once per frame AFTER write_state.

    Screen-specific commands are dispatched only if the active screen implements
    the matching method, so this is safe across every screen.
    """
    data = read_command_full()
    if not data:
        return
    cmd, args = data

    if cmd in _JUMPS:
        state_machine.force_state(_JUMPS[cmd])
    elif cmd == "set_level" and hasattr(active_screen, "set_level"):
        active_screen.set_level(int(args.get("n", 1)))
    elif cmd == "spawn_powerup" and hasattr(active_screen, "spawn_powerup"):
        active_screen.spawn_powerup()
    elif cmd == "spawn_npc" and hasattr(active_screen, "spawn_npc"):
        active_screen.spawn_npc()
    elif cmd == "drop_poo" and hasattr(active_screen, "drop_poo"):
        active_screen.drop_poo()
    elif cmd == "set_invincible" and hasattr(active_screen, "set_invincible"):
        active_screen.set_invincible(bool(args.get("on", True)))
    elif cmd == "toggle_music" and audio_manager is not None:
        audio_manager.toggle_music()
    elif cmd == "toggle_sfx" and audio_manager is not None:
        audio_manager.toggle_sfx()

    clear_command()


def _smoke(frames: int) -> None:
    """Headless harness: prove write_state + poll_mcp_command + IPC work end-to-end.

    Runs without a real game so the MCP harness can be validated (Phase 1) before
    any screens exist. Drives a bare StateMachine for ``frames`` iterations.
    """
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    import time

    sm = StateMachine(GameState.START)
    for _ in range(frames):
        write_state(sm.state.name, running=True, score=0, level=1,
                    music_on=True, sfx_on=True)
        poll_mcp_command(sm)
        time.sleep(0.01)
    # Final publish so an observer can read the last state.
    write_state(sm.state.name, running=False, score=0, level=1)
    print(f"smoke complete: final state = {sm.state.name}")


def run_game() -> None:
    """Launch the real game (screens wired in from Phase 2 onward)."""
    from game.app import App  # imported lazily; built in later phases
    App().run()


def main() -> None:
    parser = argparse.ArgumentParser(description="ChocolateThunder2: ElectricBoogaloo")
    parser.add_argument("--smoke", action="store_true",
                        help="run the headless MCP smoke harness instead of the game")
    parser.add_argument("--frames", type=int, default=120,
                        help="frames to run in --smoke mode")
    args = parser.parse_args()

    if args.smoke:
        _smoke(args.frames)
    else:
        run_game()


if __name__ == "__main__":
    main()
