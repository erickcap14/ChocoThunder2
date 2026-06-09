"""Phase 4 unit tests — EndScreen (headless).

Tests pure logic: initialization with win/lose state, ENTER/SPACE → SCOREBOARD
transition, no-op update, and draw smoke tests.  No display or audio hardware required.
"""

from __future__ import annotations

import pytest
import pygame

from game.screens.end import EndScreen
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

@pytest.mark.log_meta(phase="phase_4", subtask="4.2", action="end init win")
def test_end_initializes_win(pygame_env):
    """EndScreen stores win=True, the given score, and level == 1."""
    sm = StateMachine(GameState.END)
    screen = EndScreen(pygame_env, sm, _FakeAudio(), score=42, win=True)
    assert screen.win is True
    assert screen.score == 42
    assert screen.level == 1


def test_end_initializes_lose(pygame_env):
    """EndScreen stores win=False when the player lost."""
    sm = StateMachine(GameState.END)
    screen = EndScreen(pygame_env, sm, _FakeAudio(), score=0, win=False)
    assert screen.win is False


@pytest.mark.log_meta(phase="phase_4", subtask="4.2", action="enter goes to scoreboard")
def test_enter_goes_to_scoreboard(pygame_env):
    """ENTER key event causes the state machine to transition to SCOREBOARD."""
    sm = StateMachine(GameState.END)
    screen = EndScreen(pygame_env, sm, _FakeAudio(), score=10, win=True)

    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode="\r")
    screen.handle_event(event)

    assert sm.state is GameState.SCOREBOARD


@pytest.mark.log_meta(phase="phase_4", subtask="4.2", action="space goes to scoreboard")
def test_space_goes_to_scoreboard(pygame_env):
    """K_SPACE key event causes the state machine to transition to SCOREBOARD."""
    sm = StateMachine(GameState.END)
    screen = EndScreen(pygame_env, sm, _FakeAudio(), score=10, win=False)

    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE, mod=0, unicode=" ")
    screen.handle_event(event)

    assert sm.state is GameState.SCOREBOARD


def test_other_keys_do_not_transition(pygame_env):
    """Keys other than ENTER and SPACE leave the state unchanged."""
    sm = StateMachine(GameState.END)
    screen = EndScreen(pygame_env, sm, _FakeAudio(), score=10, win=True)

    for key in (pygame.K_a, pygame.K_ESCAPE):
        event = pygame.event.Event(pygame.KEYDOWN, key=key, mod=0, unicode="")
        screen.handle_event(event)

    assert sm.state is GameState.END


@pytest.mark.log_meta(phase="phase_4", subtask="4.2", action="update no-op")
def test_update_is_noop(pygame_env):
    """update(dt) does not alter score, win flag, or state."""
    sm = StateMachine(GameState.END)
    screen = EndScreen(pygame_env, sm, _FakeAudio(), score=99, win=True)
    screen.update(1.0)
    assert screen.score == 99
    assert screen.win is True
    assert sm.state is GameState.END


def test_draw_win_does_not_raise(pygame_env):
    """draw() completes without error when win=True."""
    sm = StateMachine(GameState.END)
    screen = EndScreen(pygame_env, sm, _FakeAudio(), score=100, win=True)
    screen.draw()


def test_draw_lose_does_not_raise(pygame_env):
    """draw() completes without error when win=False."""
    sm = StateMachine(GameState.END)
    screen = EndScreen(pygame_env, sm, _FakeAudio(), score=3, win=False)
    screen.draw()


def test_chrome_present_and_draws(pygame_env):
    """EndScreen owns a Chrome widget and draw() (incl. chrome) runs cleanly."""
    sm = StateMachine(GameState.END)
    screen = EndScreen(pygame_env, sm, _FakeAudio(), score=7, win=True)
    assert screen._chrome is not None
    screen.draw()  # exercises chrome.draw() without error
