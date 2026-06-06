"""Phase 3 unit tests — PlayScreen and entity interactions (headless).

Covers initialization, input handling, collision wiring, scoring rules,
cooldown logic, timer-driven transitions, and all MCP handler methods.
"""

from __future__ import annotations

import pytest
import pygame

from game.screens.play import PlayScreen
from game.state_machine import GameState, StateMachine
from game.entities import PowerUp
from game import config


# ---------------------------------------------------------------------------
# Shared fake objects
# ---------------------------------------------------------------------------

class _FakeAudio:
    def __init__(self):
        self.music_playing: str | None = None
        self.music_stopped = False
        self.sfx_calls: list[str] = []

    def play_music(self, filename, loops=-1):
        self.music_playing = filename

    def stop_music(self):
        self.music_stopped = True

    def toggle_music(self): pass
    def toggle_sfx(self): pass

    def play_sfx(self, name: str) -> None:
        self.sfx_calls.append(name)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ps(pygame_env):
    """Return a fresh (PlayScreen, StateMachine, _FakeAudio) triple."""
    sm = StateMachine(GameState.RUNNING)
    audio = _FakeAudio()
    ps = PlayScreen(pygame_env, sm, audio)
    return ps, sm, audio


def _space_event() -> pygame.event.Event:
    return pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE, mod=0, unicode=" ")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.log_meta(phase="phase_3", subtask="3.1", action="play init")
def test_play_initializes(pygame_env):
    """PlayScreen starts with score=0, level=1, at least one NPC and obstacle, timer=60."""
    ps, sm, _ = _make_ps(pygame_env)
    assert ps.score == 0
    assert ps.level == 1
    assert ps._player is not None
    assert len(ps._npcs) >= 1
    assert len(ps._obstacles) >= 1
    assert ps._level_time_remaining == pytest.approx(config.LEVEL_SECONDS)


@pytest.mark.log_meta(phase="phase_3", subtask="3.2", action="mouse click sets target")
def test_mouse_click_sets_player_target(pygame_env):
    """MOUSEBUTTONDOWN event updates the player's movement target."""
    ps, _, _ = _make_ps(pygame_env)
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(100, 200), button=1)
    ps.handle_event(event)
    assert ps._player._target == pygame.Vector2(100, 200)


@pytest.mark.log_meta(phase="phase_3", subtask="3.3", action="space drops poo scores 1")
def test_space_drops_poo_and_scores(pygame_env):
    """KEYDOWN K_SPACE spawns one poo and awards SCORE_DEFAULT points."""
    ps, _, _ = _make_ps(pygame_env)
    ps.handle_event(_space_event())
    assert len(ps._poos) == 1
    assert ps.score == config.SCORE_DEFAULT


def test_poo_cooldown_prevents_rapid_drop(pygame_env):
    """Pressing SPACE twice in quick succession only drops one poo."""
    ps, _, _ = _make_ps(pygame_env)
    ps.handle_event(_space_event())
    ps.handle_event(_space_event())
    assert len(ps._poos) == 1
    assert ps.score == config.SCORE_DEFAULT


@pytest.mark.log_meta(phase="phase_3", subtask="3.4", action="cooldown resets after wait")
def test_poo_cooldown_resets_after_wait(pygame_env):
    """After advancing time past POO_COOLDOWN_SECONDS a second poo can be dropped."""
    ps, _, _ = _make_ps(pygame_env)
    ps.handle_event(_space_event())
    assert len(ps._poos) == 1
    # Advance time past the cooldown
    ps.update(config.POO_COOLDOWN_SECONDS + 0.01)
    ps.handle_event(_space_event())
    assert len(ps._poos) == 2


@pytest.mark.log_meta(phase="phase_3", subtask="3.5", action="powered poo scores bonus")
def test_powered_poo_scores_bonus(pygame_env):
    """While invincible, dropping a poo awards SCORE_BONUS points."""
    ps, _, _ = _make_ps(pygame_env)
    ps._player.set_invincible(True)
    ps.handle_event(_space_event())
    assert ps.score == config.SCORE_BONUS


@pytest.mark.log_meta(phase="phase_3", subtask="3.6", action="drop_poo mcp bypasses cooldown")
def test_drop_poo_mcp_bypasses_cooldown(pygame_env):
    """MCP drop_poo() adds a poo even while the cooldown timer is still active."""
    ps, _, _ = _make_ps(pygame_env)
    ps.handle_event(_space_event())
    assert ps._poo_cooldown_remaining > 0.0
    ps.drop_poo()
    assert len(ps._poos) == 2


@pytest.mark.log_meta(phase="phase_3", subtask="3.7", action="obstacle pushes player out")
def test_obstacle_pushes_player_out(pygame_env):
    """After update(), the player rect no longer overlaps an obstacle it was placed inside."""
    ps, _, _ = _make_ps(pygame_env)
    obs = next(iter(ps._obstacles))
    # Place player fully inside the obstacle rect
    ps._player.rect.center = obs.rect.center
    # Pin target so player doesn't walk away (movement is deterministic over 1 frame)
    ps._player.set_target(ps._player.rect.center)
    ps.update(0.016)
    assert not obs.rect.colliderect(ps._player.rect)


@pytest.mark.log_meta(phase="phase_3", subtask="3.8", action="npc catches player ends game")
def test_npc_catches_player_ends_game(pygame_env):
    """When player and NPC rects overlap and player is not invincible, state → END."""
    ps, sm, _ = _make_ps(pygame_env)
    ps._player.is_invincible = False
    npc = next(iter(ps._npcs))
    ps._player.rect.center = npc.rect.center
    ps._player.set_target(ps._player.rect.center)
    ps.update(0.016)
    assert sm.state is GameState.END


def test_invincible_player_not_caught(pygame_env):
    """When the player is invincible, NPC collision does NOT end the game."""
    ps, sm, _ = _make_ps(pygame_env)
    ps._player.set_invincible(True)
    npc = next(iter(ps._npcs))
    ps._player.rect.center = npc.rect.center
    ps._player.set_target(ps._player.rect.center)
    ps.update(0.016)
    assert sm.state is GameState.RUNNING


@pytest.mark.log_meta(phase="phase_3", subtask="3.9", action="powerup collection sets invincible")
def test_powerup_collection_sets_invincible(pygame_env):
    """Overlapping a PowerUp sprite makes the player invincible and removes the sprite."""
    ps, _, _ = _make_ps(pygame_env)
    pu = PowerUp(ps._player.rect.center)
    pu.rect.center = ps._player.rect.center
    ps._powerups.add(pu)
    ps._player.set_target(ps._player.rect.center)
    ps.update(0.016)
    assert ps._player.is_invincible is True
    assert pu not in ps._powerups


@pytest.mark.log_meta(phase="phase_3", subtask="3.10", action="level timer expiry transitions")
def test_level_timer_expiry_transitions(pygame_env):
    """When the level countdown hits zero, state machine moves to TRANSITION (Story 7)."""
    ps, sm, _ = _make_ps(pygame_env)
    ps._level_time_remaining = 0.001
    ps._player.set_target(ps._player.rect.center)
    ps.update(0.016)
    assert sm.state is GameState.TRANSITION


@pytest.mark.log_meta(phase="phase_3", subtask="3.11", action="cake autospawns on timer")
def test_cake_autospawns_when_timer_elapses(pygame_env):
    """When _powerup_spawn_timer elapses and no powerups exist, one is auto-spawned."""
    ps, _, _ = _make_ps(pygame_env)
    ps._powerups.empty()
    ps._powerup_spawn_timer = 0.001
    ps._player.set_target(ps._player.rect.center)
    ps.update(0.016)
    assert len(ps._powerups) >= 1


@pytest.mark.log_meta(phase="phase_3", subtask="3.12", action="set_level resets state")
def test_set_level_resets_to_new_level(pygame_env):
    """set_level(2) resets score to 0 and updates level attribute."""
    ps, _, _ = _make_ps(pygame_env)
    ps.score = 42
    ps.set_level(2)
    assert ps.score == 0
    assert ps.level == 2


def test_set_invincible_mcp(pygame_env):
    """set_invincible MCP handler toggles player invincibility on and off."""
    ps, _, _ = _make_ps(pygame_env)
    ps.set_invincible(True)
    assert ps._player.is_invincible is True
    ps.set_invincible(False)
    assert ps._player.is_invincible is False


def test_spawn_npc_adds_one_npc(pygame_env):
    """spawn_npc() adds exactly one NPC to the active group."""
    ps, _, _ = _make_ps(pygame_env)
    before = len(ps._npcs)
    ps.spawn_npc()
    assert len(ps._npcs) == before + 1


def test_spawn_powerup_adds_one_powerup(pygame_env):
    """spawn_powerup() places one PowerUp into the _powerups group."""
    ps, _, _ = _make_ps(pygame_env)
    ps._powerups.empty()
    ps.spawn_powerup()
    assert len(ps._powerups) == 1


def test_draw_does_not_raise(pygame_env):
    """draw() completes without raising on a headless surface."""
    ps, _, _ = _make_ps(pygame_env)
    ps.update(0.016)
    ps.draw()
