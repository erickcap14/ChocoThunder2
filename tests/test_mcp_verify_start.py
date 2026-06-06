"""Phase 2 MCP-verify tests — StartScreen bridge roundtrip + screenshot.

Validates that:
  1. The IPC bridge correctly writes and reads a jump_to_start command.
  2. poll_mcp_command dispatches jump_to_start to the state machine.
  3. A headless StartScreen renders without producing a solid-black surface.
  4. A screenshot is saved to testscreenshots/ as visual evidence.
"""

from __future__ import annotations

import pytest
import pygame

import main
from game.screens.start import StartScreen
from game.state_machine import GameState, StateMachine
from mcp_server import state_bridge as bridge


pytestmark = pytest.mark.usefixtures("clean_bridge")


class _FakeAudio:
    def play_music(self, *a, **kw): pass
    def stop_music(self): pass
    def toggle_music(self): pass
    def toggle_sfx(self): pass


# --- Bridge roundtrip -------------------------------------------------------

@pytest.mark.log_meta(phase="phase_2", subtask="2.4", action="bridge jump_to_start")
def test_jump_to_start_command_roundtrip():
    """jump_to_start command survives a write → read → dispatch cycle."""
    sm = StateMachine(GameState.RUNNING)
    bridge.write_command("jump_to_start")
    cmd, args = bridge.read_command_full()
    assert cmd == "jump_to_start" and args == {}

    main.poll_mcp_command(sm)
    assert sm.state is GameState.START
    assert bridge.read_command_full() is None  # consumed


def test_start_state_written_to_bridge():
    """write_state with START is readable by the MCP side."""
    bridge.write_state("START", running=True, score=0, level=1,
                       music_on=True, sfx_on=True)
    state = bridge.read_state()
    assert state["state"] == "START"
    assert state["running"] is True


# --- Render + screenshot ----------------------------------------------------

@pytest.mark.log_meta(phase="phase_2", subtask="2.5", action="start screenshot")
def test_start_renders_and_saves_screenshot(pygame_env):
    """StartScreen draws a non-black frame and saves it to testscreenshots/."""
    from game import config

    sm = StateMachine(GameState.START)
    screen = StartScreen(pygame_env, sm, _FakeAudio())
    screen.update(0.016)
    screen.draw()

    # Pixel sample: centre of the screen must not be pure black.
    cx, cy = config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2
    pixel = pygame_env.get_at((cx, cy))
    assert pixel[:3] != (0, 0, 0), "centre pixel is pure black — start screen may not be rendering"

    # Save screenshot as visual evidence.
    out = config.SCREENSHOTS / "start_verified.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(pygame_env, str(out))
    assert out.exists()
