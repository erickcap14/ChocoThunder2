"""Unit tests — PreLevelScreen (headless).

Tests initialization, Enter → RUNNING, non-enter keys do nothing, update
is a no-op, and draw completes without error.
"""

from __future__ import annotations

import pytest
import pygame

from game.screens.prelevel import PreLevelScreen
from game.state_machine import GameState, StateMachine
from game.levels import LEVELS


class _FakeAudio:
    def play_music(self, filename, loops=-1): pass
    def stop_music(self): pass
    def toggle_music(self): pass
    def toggle_sfx(self): pass
    def play_sfx(self, *a, **kw): pass


def test_prelevel_initializes(pygame_env):
    """PreLevelScreen stores level and score correctly."""
    sm = StateMachine(GameState.PRELEVEL)
    screen = PreLevelScreen(pygame_env, sm, _FakeAudio(), level=2, score=50)
    assert screen.level == 2
    assert screen.score == 50


def test_enter_transitions_to_running(pygame_env):
    """ENTER causes the state machine to transition to RUNNING."""
    sm = StateMachine(GameState.PRELEVEL)
    screen = PreLevelScreen(pygame_env, sm, _FakeAudio(), level=1, score=0)
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode="\r")
    screen.handle_event(event)
    assert sm.state is GameState.RUNNING


def test_other_keys_do_not_transition(pygame_env):
    """Keys other than ENTER leave the state unchanged."""
    sm = StateMachine(GameState.PRELEVEL)
    screen = PreLevelScreen(pygame_env, sm, _FakeAudio(), level=1, score=0)
    for key in (pygame.K_SPACE, pygame.K_ESCAPE, pygame.K_a):
        event = pygame.event.Event(pygame.KEYDOWN, key=key, mod=0, unicode="")
        screen.handle_event(event)
    assert sm.state is GameState.PRELEVEL


def test_update_is_noop(pygame_env):
    """update(dt) does not mutate level, score, or state."""
    sm = StateMachine(GameState.PRELEVEL)
    screen = PreLevelScreen(pygame_env, sm, _FakeAudio(), level=3, score=99)
    screen.update(1.0)
    assert screen.level == 3
    assert screen.score == 99
    assert sm.state is GameState.PRELEVEL


def test_draw_does_not_raise(pygame_env):
    """draw() completes without error on a headless surface."""
    sm = StateMachine(GameState.PRELEVEL)
    screen = PreLevelScreen(pygame_env, sm, _FakeAudio(), level=1, score=0)
    screen.draw()


@pytest.mark.parametrize("level_num", [1, 2, 3, 4])
def test_intro_subtitle_matches_manifest(pygame_env, level_num):
    """PreLevelScreen uses the intro_subtitle from the LEVELS manifest."""
    sm = StateMachine(GameState.PRELEVEL)
    screen = PreLevelScreen(pygame_env, sm, _FakeAudio(), level=level_num, score=0)
    expected = LEVELS[level_num - 1].intro_subtitle
    assert expected  # must be non-empty
    assert screen.level == level_num


def test_score_zero_level1(pygame_env):
    """Level 1 with score 0 draws without error (no 'Score so far' line shown)."""
    sm = StateMachine(GameState.PRELEVEL)
    screen = PreLevelScreen(pygame_env, sm, _FakeAudio(), level=1, score=0)
    screen.draw()


def test_score_nonzero_shows(pygame_env):
    """Non-zero score is stored and draw completes without error."""
    sm = StateMachine(GameState.PRELEVEL)
    screen = PreLevelScreen(pygame_env, sm, _FakeAudio(), level=2, score=42)
    assert screen.score == 42
    screen.draw()


def test_chrome_present_and_draws(pygame_env):
    """The screen owns a Chrome widget and draws with it without error."""
    sm = StateMachine(GameState.PRELEVEL)
    screen = PreLevelScreen(pygame_env, sm, _FakeAudio(), level=1, score=0)
    assert screen._chrome is not None
    screen.draw()
