"""Phase 4 MCP-verify tests — TransitionScreen bridge roundtrip + screenshot.

Validates that:
  1. The IPC bridge correctly writes and reads a jump_to_transition command.
  2. poll_mcp_command dispatches jump_to_transition to the state machine.
  3. A headless TransitionScreen renders without producing a solid-black surface.
  4. A screenshot is saved to testscreenshots/ as visual evidence.
"""

from __future__ import annotations

import pytest
import pygame

import main
from game.screens.transition import TransitionScreen
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

@pytest.mark.log_meta(phase="phase_4", subtask="4.1", action="bridge jump_to_transition")
def test_jump_to_transition_command_roundtrip():
    """jump_to_transition command survives a write → read → dispatch cycle."""
    sm = StateMachine(GameState.RUNNING)
    bridge.write_command("jump_to_transition")
    cmd, args = bridge.read_command_full()
    assert cmd == "jump_to_transition" and args == {}

    main.poll_mcp_command(sm)
    assert sm.state is GameState.TRANSITION
    assert bridge.read_command_full() is None  # consumed


def test_transition_state_written_to_bridge():
    """write_state with TRANSITION is readable by the MCP side."""
    bridge.write_state("TRANSITION", running=True, score=42, level=1,
                       music_on=True, sfx_on=True)
    state = bridge.read_state()
    assert state["state"] == "TRANSITION"
    assert state["score"] == 42


# --- Render + screenshot ----------------------------------------------------

@pytest.mark.log_meta(phase="phase_4", subtask="4.1", action="transition screenshot")
def test_transition_renders_and_saves_screenshot(pygame_env):
    """TransitionScreen draws a non-black frame and saves it to testscreenshots/."""
    from game import config

    sm = StateMachine(GameState.TRANSITION)
    screen = TransitionScreen(pygame_env, sm, _FakeAudio(), level=2, score=10)
    screen.draw()

    # Pixel sample: scan a horizontal strip across the "Level 2 Complete!" title
    # (rendered at y=220 in BROWN).  At least one pixel in that row must be
    # non-black, confirming the screen drew something.
    cx = config.SCREEN_WIDTH // 2
    strip_pixels = [pygame_env.get_at((cx + dx, 235))[:3] for dx in range(-150, 151)]
    assert any(p != (0, 0, 0) for p in strip_pixels), (
        "no non-black pixel found in title row — transition screen may not be rendering"
    )

    # Save screenshot as visual evidence.
    out = config.SCREENSHOTS / "transition_verified.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(pygame_env, str(out))
    assert out.exists()
