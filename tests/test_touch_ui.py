"""Unit tests — touch-control layer (T111, headless).

The layer activates via ``config.touch_ui_enabled()``: "auto" means
emscripten-only, "1"/"0" force it on/off. Tests monkeypatch ``config.TOUCH_UI``
directly. Touch mode adds:
  - an on-screen poop button on the play screen (tap = Space),
  - tap-to-advance on start/prelevel/transition/end/scoreboard.
Desktop mode ("0") must behave exactly as before — no button, taps ignored.
"""

from __future__ import annotations

import pygame
import pytest

from game import config
from game.screens.end import EndScreen
from game.screens.play import PlayScreen
from game.screens.prelevel import PreLevelScreen
from game.screens.scoreboard import ScoreboardScreen
from game.screens.start import StartScreen
from game.screens.transition import TransitionScreen
from game.levels import LEVELS
from game.state_machine import GameState, StateMachine


class _FakeAudio:
    def play_music(self, filename, loops=-1): pass
    def stop_music(self): pass
    def toggle_music(self): pass
    def toggle_sfx(self): pass
    def play_sfx(self, *a, **kw): pass


@pytest.fixture
def touch_on(monkeypatch):
    monkeypatch.setattr(config, "TOUCH_UI", "1")


@pytest.fixture
def touch_off(monkeypatch):
    monkeypatch.setattr(config, "TOUCH_UI", "0")


@pytest.fixture
def tmp_scores(tmp_path):
    """Redirect SCORES_FILE to a temporary path for the duration of the test."""
    orig = config.SCORES_FILE
    config.SCORES_FILE = tmp_path / "scores.txt"
    yield config.SCORES_FILE
    config.SCORES_FILE = orig


def _tap(pos) -> pygame.event.Event:
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos)


# A tap position in open floor: clear of the HUD bar, chrome buttons (top
# right), and the bottom-right poop button.
_FLOOR = (400, 400)


# ---------------------------------------------------------------------------
# Play screen: poop button
# ---------------------------------------------------------------------------

def test_desktop_play_has_no_poo_button(pygame_env, touch_off):
    ps = PlayScreen(pygame_env, StateMachine(GameState.RUNNING), _FakeAudio())
    assert ps._poo_btn is None


def test_touch_play_has_poo_button_and_draws(pygame_env, touch_on):
    ps = PlayScreen(pygame_env, StateMachine(GameState.RUNNING), _FakeAudio())
    assert ps._poo_btn is not None
    ps.draw()  # must not raise with the button visible


def test_poo_button_tap_places_poo_without_moving_sally(pygame_env, touch_on):
    ps = PlayScreen(pygame_env, StateMachine(GameState.RUNNING), _FakeAudio())
    target_before = pygame.Vector2(ps._player._target)
    ps.handle_event(_tap(ps._poo_btn.center))
    assert len(ps._poos) == 1
    assert ps._player._target == target_before
    assert not ps._mouse_held


def test_poo_button_respects_cooldown(pygame_env, touch_on):
    ps = PlayScreen(pygame_env, StateMachine(GameState.RUNNING), _FakeAudio())
    ps.handle_event(_tap(ps._poo_btn.center))
    ps.handle_event(_tap(ps._poo_btn.center))  # still on cooldown
    assert len(ps._poos) == 1


def test_touch_tap_on_floor_still_moves_sally(pygame_env, touch_on):
    ps = PlayScreen(pygame_env, StateMachine(GameState.RUNNING), _FakeAudio())
    ps.handle_event(_tap(_FLOOR))
    assert ps._player._target == pygame.Vector2(_FLOOR)
    assert len(ps._poos) == 0


# ---------------------------------------------------------------------------
# Tap-to-advance screens
# ---------------------------------------------------------------------------

def test_touch_tap_starts_game_from_start_screen(pygame_env, touch_on):
    sm = StateMachine(GameState.START)
    screen = StartScreen(pygame_env, sm, _FakeAudio())
    screen.handle_event(_tap(_FLOOR))
    assert sm.state is GameState.PRELEVEL


def test_touch_difficulty_buttons_do_not_start_game(pygame_env, touch_on):
    sm = StateMachine(GameState.START)
    screen = StartScreen(pygame_env, sm, _FakeAudio())
    screen.handle_event(_tap(screen._hard_btn.center))
    assert sm.state is GameState.START


def test_desktop_click_does_not_start_game(pygame_env, touch_off):
    sm = StateMachine(GameState.START)
    screen = StartScreen(pygame_env, sm, _FakeAudio())
    screen.handle_event(_tap(_FLOOR))
    assert sm.state is GameState.START


def test_touch_tap_advances_prelevel(pygame_env, touch_on):
    sm = StateMachine(GameState.PRELEVEL)
    screen = PreLevelScreen(pygame_env, sm, _FakeAudio(), level=1, score=0)
    screen.handle_event(_tap(_FLOOR))
    assert sm.state is GameState.RUNNING


def test_desktop_click_does_not_advance_prelevel(pygame_env, touch_off):
    sm = StateMachine(GameState.PRELEVEL)
    screen = PreLevelScreen(pygame_env, sm, _FakeAudio(), level=1, score=0)
    screen.handle_event(_tap(_FLOOR))
    assert sm.state is GameState.PRELEVEL


def test_touch_tap_advances_transition_mid_game(pygame_env, touch_on):
    sm = StateMachine(GameState.TRANSITION)
    screen = TransitionScreen(pygame_env, sm, _FakeAudio(), level=1, score=10)
    screen.handle_event(_tap(_FLOOR))
    assert sm.state is GameState.PRELEVEL


def test_touch_tap_advances_final_transition_to_end(pygame_env, touch_on):
    sm = StateMachine(GameState.TRANSITION)
    screen = TransitionScreen(
        pygame_env, sm, _FakeAudio(), level=len(LEVELS), score=10
    )
    screen.handle_event(_tap(_FLOOR))
    assert sm.state is GameState.END


def test_touch_tap_advances_end_to_scoreboard(pygame_env, touch_on):
    sm = StateMachine(GameState.END)
    screen = EndScreen(pygame_env, sm, _FakeAudio(), score=42, win=True)
    screen.handle_event(_tap(_FLOOR))
    assert sm.state is GameState.SCOREBOARD


def test_touch_tap_submits_default_name_then_restarts(
    pygame_env, touch_on, tmp_scores
):
    sm = StateMachine(GameState.SCOREBOARD)
    screen = ScoreboardScreen(pygame_env, sm, _FakeAudio(), score=7)
    screen.handle_event(_tap(_FLOOR))  # entry phase: submit as default name
    assert screen._submitted
    assert ("SALLY", 7) in screen._entries
    screen.handle_event(_tap(_FLOOR))  # view phase: back to start
    assert sm.state is GameState.START


def test_touch_tap_submits_typed_name_when_present(
    pygame_env, touch_on, tmp_scores
):
    sm = StateMachine(GameState.SCOREBOARD)
    screen = ScoreboardScreen(pygame_env, sm, _FakeAudio(), score=3)
    screen._name = "REX"
    screen.handle_event(_tap(_FLOOR))
    assert ("REX", 3) in screen._entries


def test_desktop_click_does_not_submit_scoreboard(
    pygame_env, touch_off, tmp_scores
):
    sm = StateMachine(GameState.SCOREBOARD)
    screen = ScoreboardScreen(pygame_env, sm, _FakeAudio(), score=7)
    screen.handle_event(_tap(_FLOOR))
    assert not screen._submitted
