"""Phase 4 MCP-verify tests — EndScreen bridge roundtrip + screenshot.

Validates that:
  1. The IPC bridge correctly writes and reads a jump_to_end command.
  2. poll_mcp_command dispatches jump_to_end to the state machine.
  3. A headless EndScreen (win) renders without producing a solid-black surface.
  4. A headless EndScreen (lose) renders and saves its screenshot.
"""

from __future__ import annotations

import pytest
import pygame

import main
from game.screens.end import EndScreen
from game.state_machine import GameState, StateMachine
from mcp_server import state_bridge as bridge


pytestmark = pytest.mark.usefixtures("clean_bridge")


class _FakeAudio:
    def play_music(self, *a, **kw): pass
    def stop_music(self): pass
    def toggle_music(self): pass
    def toggle_sfx(self): pass
    def play_sfx(self, *a, **kw): pass


# --- Bridge roundtrip -------------------------------------------------------

@pytest.mark.log_meta(phase="phase_4", subtask="4.2", action="bridge jump_to_end")
def test_jump_to_end_command_roundtrip():
    """jump_to_end command survives a write → read → dispatch cycle."""
    sm = StateMachine(GameState.RUNNING)
    bridge.write_command("jump_to_end")
    cmd, args = bridge.read_command_full()
    assert cmd == "jump_to_end" and args == {}

    main.poll_mcp_command(sm)
    assert sm.state is GameState.END
    assert bridge.read_command_full() is None  # consumed


def test_end_state_written_to_bridge():
    """write_state with END is readable by the MCP side and preserves score."""
    bridge.write_state("END", running=True, score=50, level=1,
                       music_on=True, sfx_on=True)
    state = bridge.read_state()
    assert state["state"] == "END"
    assert state["score"] == 50


# --- Render + screenshot ----------------------------------------------------

@pytest.mark.log_meta(phase="phase_4", subtask="4.2", action="end win screenshot")
def test_end_win_renders_and_saves_screenshot(pygame_env):
    """EndScreen(win=True) draws a non-black frame and saves end_win_verified.png."""
    from game import config

    sm = StateMachine(GameState.END)
    screen = EndScreen(pygame_env, sm, _FakeAudio(), score=50, win=True)
    screen.draw()

    cx, cy = config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2
    pixel = pygame_env.get_at((cx, cy))
    assert pixel[:3] != (0, 0, 0), "centre pixel is pure black — end win screen may not be rendering"

    out = config.SCREENSHOTS / "end_win_verified.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(pygame_env, str(out))
    assert out.exists()


def test_end_lose_renders_and_saves_screenshot(pygame_env):
    """EndScreen(win=False) draws a non-black frame and saves end_lose_verified.png."""
    from game import config

    sm = StateMachine(GameState.END)
    screen = EndScreen(pygame_env, sm, _FakeAudio(), score=5, win=False)
    screen.draw()

    cx, cy = config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2
    pixel = pygame_env.get_at((cx, cy))
    assert pixel[:3] != (0, 0, 0), "centre pixel is pure black — end lose screen may not be rendering"

    out = config.SCREENSHOTS / "end_lose_verified.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(pygame_env, str(out))
    assert out.exists()
