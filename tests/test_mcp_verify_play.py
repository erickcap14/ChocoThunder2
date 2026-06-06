"""Phase 3 MCP-verify tests — PlayScreen bridge roundtrip + screenshot.

Validates that:
  1. The IPC bridge correctly dispatches all PlayScreen-specific commands.
  2. poll_mcp_command routes set_level, spawn_powerup, spawn_npc, drop_poo,
     and set_invincible to the active PlayScreen.
  3. write_state / read_state roundtrip works for RUNNING state.
  4. A headless PlayScreen renders without producing a solid-black surface.
  5. A screenshot is saved to testscreenshots/ as visual evidence.
"""

from __future__ import annotations

import pytest
import pygame

import main
from game.screens.play import PlayScreen
from game.state_machine import GameState, StateMachine
from mcp_server import state_bridge as bridge


pytestmark = pytest.mark.usefixtures("clean_bridge")


class _FakeAudio:
    def play_music(self, *a, **kw): pass
    def stop_music(self): pass
    def toggle_music(self): pass
    def toggle_sfx(self): pass
    def play_sfx(self, *a, **kw): pass


# --- Bridge roundtrip tests -------------------------------------------------

@pytest.mark.log_meta(phase="phase_3", subtask="3.1", action="bridge set_level")
def test_set_level_command_roundtrip(pygame_env):
    """set_level n=2 survives a write → poll → dispatch cycle."""
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


@pytest.mark.log_meta(phase="phase_3", subtask="3.2", action="bridge spawn_powerup")
def test_spawn_powerup_command_roundtrip(pygame_env):
    """spawn_powerup command causes ≥1 powerup to exist on the play screen."""
    sm = StateMachine(GameState.RUNNING)
    audio = _FakeAudio()
    ps = PlayScreen(pygame_env, sm, audio)

    # Drain any auto-spawned powerups to get a clean baseline.
    initial_count = len(ps._powerups)

    bridge.write_command("spawn_powerup")
    main.poll_mcp_command(sm, ps, audio)

    assert len(ps._powerups) >= 1
    assert len(ps._powerups) > initial_count
    assert bridge.read_command_full() is None  # consumed


@pytest.mark.log_meta(phase="phase_3", subtask="3.3", action="bridge spawn_npc")
def test_spawn_npc_command_roundtrip(pygame_env):
    """spawn_npc command increases the NPC count by exactly one."""
    sm = StateMachine(GameState.RUNNING)
    audio = _FakeAudio()
    ps = PlayScreen(pygame_env, sm, audio)

    npc_before = len(ps._npcs)

    bridge.write_command("spawn_npc")
    main.poll_mcp_command(sm, ps, audio)

    assert len(ps._npcs) == npc_before + 1
    assert bridge.read_command_full() is None  # consumed


@pytest.mark.log_meta(phase="phase_3", subtask="3.4", action="bridge drop_poo")
def test_drop_poo_command_roundtrip(pygame_env):
    """drop_poo command places a poo on the screen and increments the score."""
    sm = StateMachine(GameState.RUNNING)
    audio = _FakeAudio()
    ps = PlayScreen(pygame_env, sm, audio)

    score_before = ps.score

    bridge.write_command("drop_poo")
    main.poll_mcp_command(sm, ps, audio)

    assert len(ps._poos) >= 1
    assert ps.score > score_before
    assert bridge.read_command_full() is None  # consumed


@pytest.mark.log_meta(phase="phase_3", subtask="3.5", action="bridge set_invincible")
def test_set_invincible_command_roundtrip(pygame_env):
    """set_invincible on=True marks the player as invincible."""
    sm = StateMachine(GameState.RUNNING)
    audio = _FakeAudio()
    ps = PlayScreen(pygame_env, sm, audio)

    bridge.write_command_with_args("set_invincible", on=True)
    main.poll_mcp_command(sm, ps, audio)

    assert ps._player.is_invincible is True
    assert bridge.read_command_full() is None  # consumed


# --- State bridge roundtrip -------------------------------------------------

def test_running_state_written_to_bridge():
    """write_state with RUNNING is readable by the MCP side with correct fields."""
    bridge.write_state("RUNNING", running=True, score=5, level=1,
                       music_on=True, sfx_on=True)
    state = bridge.read_state()
    assert state["state"] == "RUNNING"
    assert state["running"] is True
    assert state["score"] == 5


# --- Render + screenshot ----------------------------------------------------

@pytest.mark.log_meta(phase="phase_3", subtask="3.6", action="play screenshot")
def test_play_renders_and_saves_screenshot(pygame_env):
    """PlayScreen draws a non-black frame and saves it to testscreenshots/."""
    from game import config

    sm = StateMachine(GameState.RUNNING)
    audio = _FakeAudio()
    ps = PlayScreen(pygame_env, sm, audio)
    ps.update(0.016)
    ps.draw()

    # Pixel sample: centre of the screen must not be pure black.
    cx, cy = config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2
    pixel = pygame_env.get_at((cx, cy))
    assert pixel[:3] != (0, 0, 0), (
        "centre pixel is pure black — play screen may not be rendering"
    )

    # Save screenshot as visual evidence.
    out = config.SCREENSHOTS / "play_verified.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(pygame_env, str(out))
    assert out.exists()
