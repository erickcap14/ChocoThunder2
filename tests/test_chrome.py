"""Chrome widget — volume panel + return-to-start confirm (headless)."""

from __future__ import annotations

import pygame

from game.screens.chrome import Chrome
from game.state_machine import GameState


class _FakeAudio:
    def __init__(self):
        self.music_volume = 0.7
        self.sfx_volume = 0.7

    def set_music_volume(self, v):
        self.music_volume = max(0.0, min(1.0, v))

    def set_sfx_volume(self, v):
        self.sfx_volume = max(0.0, min(1.0, v))


class _FakeSM:
    def __init__(self):
        self.state = GameState.RUNNING

    def force_state(self, s):
        self.state = s


def _down(pos):
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=1)


def _make(pygame_env, show_return=True):
    return Chrome(pygame_env, _FakeAudio(), _FakeSM(), show_return=show_return)


def test_gear_click_opens_volume_panel(pygame_env):
    c = _make(pygame_env)
    assert not c.is_blocking()
    consumed = c.handle_event(_down(c._gear.center))
    assert consumed is True
    assert c._panel_open is True
    assert c.is_blocking() is True


def test_dragging_music_slider_sets_volume(pygame_env):
    c = _make(pygame_env)
    c.handle_event(_down(c._gear.center))
    # Click the far-left of the music track -> volume 0.0
    c.handle_event(_down((c._music_track.left, c._music_track.centery)))
    assert c.audio.music_volume == 0.0
    # Drag to the far-right -> volume 1.0
    c.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=(c._music_track.right, c._music_track.centery), rel=(0, 0), buttons=(1, 0, 0)))
    assert c.audio.music_volume == 1.0


def test_dragging_sfx_slider_sets_volume(pygame_env):
    c = _make(pygame_env)
    c.handle_event(_down(c._gear.center))
    c.handle_event(_down((c._sfx_track.centerx, c._sfx_track.centery)))
    assert abs(c.audio.sfx_volume - 0.5) < 0.05


def test_click_away_closes_panel(pygame_env):
    c = _make(pygame_env)
    c.handle_event(_down(c._gear.center))
    c.handle_event(_down((5, 5)))  # far from the panel
    assert c._panel_open is False


def test_return_button_opens_confirm_then_yes_goes_to_start(pygame_env):
    c = _make(pygame_env, show_return=True)
    assert c.handle_event(_down(c._return.center)) is True
    assert c._confirm_open is True
    assert c.is_blocking() is True
    c.handle_event(_down(c._yes.center))
    assert c.sm.state is GameState.START
    assert c._confirm_open is False


def test_confirm_no_keeps_state(pygame_env):
    c = _make(pygame_env, show_return=True)
    c.handle_event(_down(c._return.center))
    c.handle_event(_down(c._no.center))
    assert c.sm.state is GameState.RUNNING
    assert c._confirm_open is False


def test_no_return_button_when_hidden(pygame_env):
    c = _make(pygame_env, show_return=False)
    # Clicking where the return button would be is not consumed and opens nothing.
    assert c.handle_event(_down(c._return.center)) is False
    assert c._confirm_open is False
