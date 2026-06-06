"""Phase 4 MCP-verify tests — ScoreboardScreen bridge roundtrip + screenshot.

Validates that:
  1. The IPC bridge correctly writes and reads a jump_to_scoreboard command.
  2. poll_mcp_command dispatches jump_to_scoreboard to the state machine.
  3. A headless ScoreboardScreen renders without producing a solid-black surface.
  4. A screenshot is saved to testscreenshots/ as visual evidence.
"""

from __future__ import annotations

import pytest
import pygame

import main
from game import config
from game.screens.scoreboard import ScoreboardScreen
from game.state_machine import GameState, StateMachine
from mcp_server import state_bridge as bridge


pytestmark = pytest.mark.usefixtures("clean_bridge")


class _FakeAudio:
    def play_music(self, *a, **kw): pass
    def stop_music(self): pass
    def toggle_music(self): pass
    def toggle_sfx(self): pass
    def play_sfx(self, *a, **kw): pass


# --- Bridge roundtrip --------------------------------------------------------

@pytest.mark.log_meta(phase="phase_4", subtask="4.3", action="bridge jump_to_scoreboard")
def test_jump_to_scoreboard_command_roundtrip():
    """jump_to_scoreboard survives a write → read → dispatch cycle and is consumed."""
    sm = StateMachine(GameState.START)
    bridge.write_command("jump_to_scoreboard")
    cmd, args = bridge.read_command_full()
    assert cmd == "jump_to_scoreboard" and args == {}

    main.poll_mcp_command(sm)
    assert sm.state is GameState.SCOREBOARD
    assert bridge.read_command_full() is None  # consumed


def test_scoreboard_state_written_to_bridge():
    """write_state with SCOREBOARD is readable by the MCP side."""
    bridge.write_state("SCOREBOARD", running=True, score=42, level=1,
                       music_on=True, sfx_on=True)
    state = bridge.read_state()
    assert state["state"] == "SCOREBOARD"
    assert state["running"] is True


# --- Render + screenshot -----------------------------------------------------

@pytest.mark.log_meta(phase="phase_4", subtask="4.3", action="scoreboard screenshot")
def test_scoreboard_renders_and_saves_screenshot(pygame_env):
    """ScoreboardScreen draws a non-black frame and saves it to testscreenshots/."""
    sm = StateMachine(GameState.SCOREBOARD)
    screen = ScoreboardScreen(pygame_env, sm, _FakeAudio(), score=42)
    screen.update(0.016)
    screen.draw()

    # Pixel sample: top strip of the screen is filled with DARK_GREY by draw()
    # and is never overwritten by the name-entry box (which lives at mid-screen).
    # DARK_GREY = (77, 77, 77) — clearly non-black — confirms the fill ran.
    cx = config.SCREEN_WIDTH // 2
    pixel = pygame_env.get_at((cx, 10))
    assert pixel[:3] != (0, 0, 0), (
        "top-strip pixel is pure black — scoreboard draw() may not have run"
    )

    # Save screenshot as visual evidence.
    out = config.SCREENSHOTS / "scoreboard_verified.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(pygame_env, str(out))
    assert out.exists()
