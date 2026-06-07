"""Phase 4 unit tests — TransitionScreen (headless).

Tests pure logic: initialization, ENTER event → state transition (RUNNING or END),
no-op update, and draw completion.  No display or audio hardware required.
"""

from __future__ import annotations

import pytest
import pygame

from game.screens.transition import TransitionScreen
from game.state_machine import GameState, StateMachine


# Shared fake objects --------------------------------------------------------

class _FakeAudio:
    def __init__(self):
        self.music_playing: str | None = None
        self.music_stopped = False

    def play_music(self, filename, loops=-1):
        self.music_playing = filename

    def stop_music(self):
        self.music_stopped = True

    def toggle_music(self): pass
    def toggle_sfx(self): pass
    def play_sfx(self, *a, **kw): pass


# Tests -----------------------------------------------------------------------

@pytest.mark.log_meta(phase="phase_4", subtask="4.1", action="transition init")
def test_transition_initializes(pygame_env):
    """TransitionScreen stores level and score correctly."""
    sm = StateMachine(GameState.TRANSITION)
    screen = TransitionScreen(pygame_env, sm, _FakeAudio(), level=2, score=150)
    assert screen.level == 2
    assert screen.score == 150


@pytest.mark.log_meta(phase="phase_4", subtask="4.1", action="enter advances level 1")
def test_enter_advances_to_prelevel_on_level1(pygame_env):
    """ENTER on level 1 transitions to PRELEVEL (more levels remain)."""
    sm = StateMachine(GameState.TRANSITION)
    screen = TransitionScreen(pygame_env, sm, _FakeAudio(), level=1, score=50)

    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode="\r")
    screen.handle_event(event)

    assert sm.state is GameState.PRELEVEL


@pytest.mark.log_meta(phase="phase_4", subtask="4.1", action="enter advances level 2")
def test_enter_advances_to_prelevel_on_level2(pygame_env):
    """ENTER on level 2 transitions to PRELEVEL (one level still remains)."""
    sm = StateMachine(GameState.TRANSITION)
    screen = TransitionScreen(pygame_env, sm, _FakeAudio(), level=2, score=200)

    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode="\r")
    screen.handle_event(event)

    assert sm.state is GameState.PRELEVEL


@pytest.mark.log_meta(phase="phase_4", subtask="4.1", action="enter goes to end on final level")
def test_enter_goes_to_end_on_final_level(pygame_env):
    """ENTER on the final level (len(LEVELS)) transitions to END."""
    from game.levels import LEVELS
    sm = StateMachine(GameState.TRANSITION)
    screen = TransitionScreen(pygame_env, sm, _FakeAudio(), level=len(LEVELS), score=999)

    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode="\r")
    screen.handle_event(event)

    assert sm.state is GameState.END


def test_other_keys_do_not_transition(pygame_env):
    """Keys other than ENTER leave the state unchanged."""
    sm = StateMachine(GameState.TRANSITION)
    screen = TransitionScreen(pygame_env, sm, _FakeAudio(), level=1, score=0)

    for key in (pygame.K_SPACE, pygame.K_ESCAPE, pygame.K_a):
        event = pygame.event.Event(pygame.KEYDOWN, key=key, mod=0, unicode="")
        screen.handle_event(event)

    assert sm.state is GameState.TRANSITION


def test_update_is_noop(pygame_env):
    """update(dt) does not mutate level, score, or state."""
    sm = StateMachine(GameState.TRANSITION)
    screen = TransitionScreen(pygame_env, sm, _FakeAudio(), level=2, score=77)

    screen.update(1.0)

    assert screen.level == 2
    assert screen.score == 77
    assert sm.state is GameState.TRANSITION


def test_draw_does_not_raise(pygame_env):
    """draw() completes without error on a headless surface."""
    sm = StateMachine(GameState.TRANSITION)
    screen = TransitionScreen(pygame_env, sm, _FakeAudio(), level=1, score=10)
    screen.draw()
