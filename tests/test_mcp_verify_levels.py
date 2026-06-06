"""Phase 5 MCP-verify tests — levels bridge roundtrip + screenshots.

Validates that:
  1. set_level 1..4 bridge roundtrip correctly dispatches to PlayScreen.
  2. write_state / read_state roundtrip carries the level field correctly.
  3. PlayScreen at level 1 renders a non-black frame (pixel sample).
  4. PlayScreen at level 4 renders without crash and saves a screenshot.
"""

from __future__ import annotations

import pytest
import pygame

import main
from game.screens.play import PlayScreen
from game.state_machine import GameState, StateMachine
from mcp_server import state_bridge as bridge
from game import config


pytestmark = pytest.mark.usefixtures("clean_bridge")


class _FakeAudio:
    def play_music(self, *a, **kw): pass
    def stop_music(self): pass
    def toggle_music(self): pass
    def toggle_sfx(self): pass
    def play_sfx(self, *a, **kw): pass


# ---------------------------------------------------------------------------
# Bridge roundtrip tests — set_level 1..4
# ---------------------------------------------------------------------------

@pytest.mark.log_meta(phase="phase_5", subtask="5.1", action="bridge set_level 1")
def test_set_level_1_command_roundtrip(pygame_env):
    """set_level n=1 survives a write → poll → dispatch cycle; ps.level is 1."""
    sm = StateMachine(GameState.RUNNING)
    audio = _FakeAudio()
    ps = PlayScreen(pygame_env, sm, audio)

    bridge.write_command_with_args("set_level", n=1)
    cmd, args = bridge.read_command_full()
    assert cmd == "set_level"
    assert args == {"n": 1}

    main.poll_mcp_command(sm, ps, audio)
    assert ps.level == 1
    assert bridge.read_command_full() is None  # consumed


@pytest.mark.log_meta(phase="phase_5", subtask="5.2", action="bridge set_level 2")
def test_set_level_2_command_roundtrip(pygame_env):
    """set_level n=2 survives a write → poll → dispatch cycle; ps.level is 2."""
    sm = StateMachine(GameState.RUNNING)
    audio = _FakeAudio()
    ps = PlayScreen(pygame_env, sm, audio)

    bridge.write_command_with_args("set_level", n=2)
    cmd, args = bridge.read_command_full()
    assert cmd == "set_level"
    assert args == {"n": 2}

    main.poll_mcp_command(sm, ps, audio)
    assert ps.level == 2
    assert bridge.read_command_full() is None  # consumed


@pytest.mark.log_meta(phase="phase_5", subtask="5.3", action="bridge set_level 3")
def test_set_level_3_command_roundtrip(pygame_env):
    """set_level n=3 survives a write → poll → dispatch cycle; ps.level is 3."""
    sm = StateMachine(GameState.RUNNING)
    audio = _FakeAudio()
    ps = PlayScreen(pygame_env, sm, audio)

    bridge.write_command_with_args("set_level", n=3)
    cmd, args = bridge.read_command_full()
    assert cmd == "set_level"
    assert args == {"n": 3}

    main.poll_mcp_command(sm, ps, audio)
    assert ps.level == 3
    assert bridge.read_command_full() is None  # consumed


@pytest.mark.log_meta(phase="phase_5", subtask="5.4", action="bridge set_level 4 demo level")
def test_set_level_4_command_roundtrip(pygame_env):
    """set_level n=4 (demo/bonus level) survives the full bridge cycle; ps.level is 4."""
    sm = StateMachine(GameState.RUNNING)
    audio = _FakeAudio()
    ps = PlayScreen(pygame_env, sm, audio)

    bridge.write_command_with_args("set_level", n=4)
    cmd, args = bridge.read_command_full()
    assert cmd == "set_level"
    assert args == {"n": 4}

    main.poll_mcp_command(sm, ps, audio)
    assert ps.level == 4
    assert bridge.read_command_full() is None  # consumed


# ---------------------------------------------------------------------------
# State bridge roundtrip — level field
# ---------------------------------------------------------------------------

def test_state_roundtrip_carries_level_field():
    """write_state with level=3 is readable by the MCP side with the correct value."""
    bridge.write_state("RUNNING", running=True, score=0, level=3,
                       music_on=True, sfx_on=True)
    state = bridge.read_state()
    assert state["state"] == "RUNNING"
    assert state["level"] == 3


# ---------------------------------------------------------------------------
# Render tests + screenshots
# ---------------------------------------------------------------------------

@pytest.mark.log_meta(phase="phase_5", subtask="5.6", action="level 1 renders non-black")
def test_level_1_renders_non_black(pygame_env):
    """PlayScreen at level=1 produces a non-black centre pixel."""
    sm = StateMachine(GameState.RUNNING)
    audio = _FakeAudio()
    ps = PlayScreen(pygame_env, sm, audio)
    ps.update(0.016)
    ps.draw()

    cx, cy = config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2
    pixel = pygame_env.get_at((cx, cy))
    assert pixel[:3] != (0, 0, 0), (
        "centre pixel is pure black at level 1 — play screen may not be rendering"
    )


@pytest.mark.log_meta(phase="phase_5", subtask="5.7", action="level 4 renders and saves screenshot")
def test_level_4_renders_and_saves_screenshot(pygame_env):
    """PlayScreen at level=4 renders without crash and saves level4_verified.png."""
    sm = StateMachine(GameState.RUNNING)
    audio = _FakeAudio()
    ps = PlayScreen(pygame_env, sm, audio)
    ps.set_level(4)
    ps.update(0.016)
    ps.draw()

    out = config.SCREENSHOTS / "level4_verified.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(pygame_env, str(out))
    assert out.exists(), f"Screenshot was not saved to {out}"
