"""Phase 2 unit tests — StartScreen (headless).

Tests pure logic: initialization, SPACE event → state transition,
background scroll advancement.  No display or audio hardware required.
"""

from __future__ import annotations

import pytest
import pygame

from game.screens.start import StartScreen
from game.state_machine import GameState, StateMachine  # noqa: F401 (PRELEVEL used in test)


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


# Tests -----------------------------------------------------------------------

@pytest.mark.log_meta(phase="phase_2", subtask="2.1", action="start init")
def test_start_initializes(pygame_env):
    """StartScreen constructs without error on a headless surface."""
    sm = StateMachine(GameState.START)
    audio = _FakeAudio()
    screen = StartScreen(pygame_env, sm, audio)
    assert screen.sm.state is GameState.START
    assert screen.score == 0
    assert screen.level == 1


@pytest.mark.log_meta(phase="phase_2", subtask="2.2", action="space transitions")
def test_space_transitions_to_prelevel(pygame_env):
    """SPACE key event causes the state machine to transition to PRELEVEL."""
    sm = StateMachine(GameState.START)
    audio = _FakeAudio()
    screen = StartScreen(pygame_env, sm, audio)

    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE, mod=0, unicode=" ")
    screen.handle_event(event)

    assert sm.state is GameState.PRELEVEL
    # Thunderstruck must keep playing into Level 1 (it is Level 1's track), so the
    # Start screen no longer stops music on the way out.
    assert audio.music_stopped is False


def test_other_keys_do_not_transition(pygame_env):
    """Keys other than SPACE leave the state unchanged."""
    sm = StateMachine(GameState.START)
    screen = StartScreen(pygame_env, sm, _FakeAudio())

    for key in (pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_a):
        event = pygame.event.Event(pygame.KEYDOWN, key=key, mod=0, unicode="")
        screen.handle_event(event)

    assert sm.state is GameState.START


@pytest.mark.log_meta(phase="phase_2", subtask="2.3", action="bg scroll")
def test_background_scrolls_on_update(pygame_env):
    """Calling update() with positive dt advances the scroll offset leftward."""
    sm = StateMachine(GameState.START)
    screen = StartScreen(pygame_env, sm, _FakeAudio())
    initial_x = screen._bg_x
    screen.update(0.1)
    assert screen._bg_x < initial_x


def test_background_wraps(pygame_env):
    """Scroll offset wraps when it passes -bg_w."""
    sm = StateMachine(GameState.START)
    screen = StartScreen(pygame_env, sm, _FakeAudio())
    screen._bg_x = -screen._bg_w - 1.0
    screen.update(0.0)
    assert screen._bg_x == 0.0


def test_draw_does_not_raise(pygame_env):
    """draw() completes without error on a headless surface."""
    sm = StateMachine(GameState.START)
    screen = StartScreen(pygame_env, sm, _FakeAudio())
    screen.update(0.016)
    screen.draw()
