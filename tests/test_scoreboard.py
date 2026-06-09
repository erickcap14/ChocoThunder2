"""Phase 4 unit tests — ScoreboardScreen + scores.py (headless).

Tests pure logic: score persistence, name entry, phase transitions,
and draw safety.  No display or audio hardware required.
"""

from __future__ import annotations

import tempfile
import pathlib

import pytest
import pygame

from game import config, scores
from game.screens.scoreboard import ScoreboardScreen
from game.state_machine import GameState, StateMachine


# --- Fixtures ----------------------------------------------------------------

@pytest.fixture
def tmp_scores(tmp_path):
    """Redirect SCORES_FILE to a temporary path for the duration of the test."""
    orig = config.SCORES_FILE
    config.SCORES_FILE = tmp_path / "scores.txt"
    yield config.SCORES_FILE
    config.SCORES_FILE = orig


class _FakeAudio:
    def play_music(self, *a, **kw): pass
    def stop_music(self): pass
    def toggle_music(self): pass
    def toggle_sfx(self): pass
    def play_sfx(self, *a, **kw): pass


def _make_screen(pygame_env, score: int = 0) -> ScoreboardScreen:
    sm = StateMachine(GameState.SCOREBOARD)
    return ScoreboardScreen(pygame_env, sm, _FakeAudio(), score)


# --- scores.py tests ---------------------------------------------------------

def test_load_scores_empty_when_no_file(tmp_scores):
    """Non-existent scores file returns an empty list, no exception."""
    assert tmp_scores.exists() is False
    assert scores.load_scores() == []


@pytest.mark.log_meta(phase="phase_4", subtask="4.1", action="scores roundtrip")
def test_add_and_load_roundtrip(tmp_scores):
    """add_score then load_scores returns the same entry."""
    scores.add_score("Alice", 10)
    result = scores.load_scores()
    assert result == [("Alice", 10)]


def test_top_10_only(tmp_scores):
    """Adding 12 entries keeps only the top 10 after loading."""
    for i in range(12):
        scores.add_score(f"Player{i}", i)
    result = scores.load_scores()
    assert len(result) == 10


@pytest.mark.log_meta(phase="phase_4", subtask="4.1", action="scores sort order")
def test_sorted_high_first(tmp_scores):
    """Scores are sorted highest-first regardless of insertion order."""
    scores.add_score("Alice", 5)
    scores.add_score("Bob", 10)
    result = scores.load_scores()
    assert result[0] == ("Bob", 10)
    assert result[1] == ("Alice", 5)


@pytest.mark.log_meta(phase="phase_4", subtask="4.1", action="bug5 malformed lines")
def test_tolerates_malformed_lines(tmp_scores):
    """Bug #5: malformed lines are silently skipped; valid entries are kept."""
    tmp_scores.write_text(
        "Alice,50\nNOT_A_SCORE\n,\nBob,abc\nCarol,30\n",
        encoding="utf-8",
    )
    result = scores.load_scores()
    names = [name for name, _ in result]
    assert "Alice" in names
    assert "Carol" in names
    assert "Bob" not in names         # score field is non-integer → skipped
    assert len(result) == 2


# --- WASM localStorage backend (T115) ----------------------------------------

class _FakeLocalStorage:
    """Minimal stand-in for the browser ``window.localStorage`` object."""

    def __init__(self):
        self._store: dict[str, str] = {}

    def getItem(self, key):
        return self._store.get(key)  # returns None when unset, like JS null

    def setItem(self, key, value):
        self._store[key] = value


@pytest.fixture
def fake_localstorage(monkeypatch):
    """Pretend we're running under pygbag/Emscripten with a fake localStorage.

    Patches ``sys.platform`` and injects a fake ``platform`` module exposing
    ``platform.window.localStorage`` so scores.py exercises the browser path.
    """
    import sys
    import types

    storage = _FakeLocalStorage()
    fake_platform = types.ModuleType("platform")
    fake_platform.window = types.SimpleNamespace(localStorage=storage)
    monkeypatch.setitem(sys.modules, "platform", fake_platform)
    monkeypatch.setattr(scores.sys, "platform", "emscripten")
    return storage


@pytest.mark.log_meta(phase="phase_4", subtask="4.1", action="wasm localStorage roundtrip")
def test_wasm_add_and_load_roundtrip(fake_localstorage):
    """Under Emscripten, scores persist through fake localStorage."""
    scores.add_score("Wasm", 42)
    assert scores.load_scores() == [("Wasm", 42)]
    # Verify the blob actually lives in localStorage, not on disk.
    assert fake_localstorage.getItem(scores.SCORES_KEY) == "Wasm,42"


def test_wasm_load_empty_when_unset(fake_localstorage):
    """Missing localStorage key (getItem → None) yields an empty list."""
    assert scores.load_scores() == []


def test_wasm_degrades_when_localstorage_raises(monkeypatch):
    """If localStorage access raises, scores degrade to empty without crashing."""
    import sys
    import types

    class _Boom:
        def getItem(self, key):
            raise RuntimeError("blocked")

        def setItem(self, key, value):
            raise RuntimeError("blocked")

    fake_platform = types.ModuleType("platform")
    fake_platform.window = types.SimpleNamespace(localStorage=_Boom())
    monkeypatch.setitem(sys.modules, "platform", fake_platform)
    monkeypatch.setattr(scores.sys, "platform", "emscripten")

    # Neither call raises despite the backend throwing.
    scores.save_scores([("X", 1)])
    assert scores.load_scores() == []


# --- ScoreboardScreen tests --------------------------------------------------

@pytest.mark.log_meta(phase="phase_4", subtask="4.2", action="scoreboard init")
def test_scoreboard_initializes(pygame_env, tmp_scores):
    """ScoreboardScreen stores score, sets level=1, starts in entry phase."""
    screen = _make_screen(pygame_env, score=99)
    assert screen.score == 99
    assert screen.level == 1
    assert screen._submitted is False
    assert screen._name == ""


def test_typing_builds_name(pygame_env, tmp_scores):
    """Printable key events accumulate in _name."""
    screen = _make_screen(pygame_env)
    for ch in ("A", "l", "i", "c", "e"):
        event = pygame.event.Event(pygame.KEYDOWN, key=ord(ch), mod=0, unicode=ch)
        screen.handle_event(event)
    assert screen._name == "Alice"


@pytest.mark.log_meta(phase="phase_4", subtask="4.2", action="backspace removes char")
def test_backspace_removes_char(pygame_env, tmp_scores):
    """BACKSPACE deletes the last character from _name."""
    screen = _make_screen(pygame_env)
    for ch in ("A", "B"):
        screen.handle_event(
            pygame.event.Event(pygame.KEYDOWN, key=ord(ch), mod=0, unicode=ch)
        )
    screen.handle_event(
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE, mod=0, unicode="")
    )
    assert screen._name == "A"


@pytest.mark.log_meta(phase="phase_4", subtask="4.2", action="enter submits name")
def test_enter_submits_name(pygame_env, tmp_scores):
    """Typing a name then pressing ENTER transitions to VIEW phase."""
    screen = _make_screen(pygame_env)
    for ch in ("Z", "o", "e"):
        screen.handle_event(
            pygame.event.Event(pygame.KEYDOWN, key=ord(ch), mod=0, unicode=ch)
        )
    screen.handle_event(
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode="\r")
    )
    assert screen._submitted is True


def test_empty_name_not_submitted(pygame_env, tmp_scores):
    """Pressing ENTER with an empty _name does not submit."""
    screen = _make_screen(pygame_env)
    screen.handle_event(
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode="\r")
    )
    assert screen._submitted is False


@pytest.mark.log_meta(phase="phase_4", subtask="4.3", action="view phase enter → start")
def test_view_phase_enter_goes_to_start(pygame_env, tmp_scores):
    """In VIEW phase ENTER forces state to START."""
    screen = _make_screen(pygame_env)
    screen._submitted = True
    screen.handle_event(
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode="\r")
    )
    assert screen.sm.state is GameState.START


@pytest.mark.log_meta(phase="phase_4", subtask="4.3", action="view phase space → start")
def test_view_phase_space_goes_to_start(pygame_env, tmp_scores):
    """In VIEW phase SPACE forces state to START."""
    screen = _make_screen(pygame_env)
    screen._submitted = True
    screen.handle_event(
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE, mod=0, unicode=" ")
    )
    assert screen.sm.state is GameState.START


def test_draw_entry_phase_does_not_raise(pygame_env, tmp_scores):
    """draw() in ENTRY phase completes without exception."""
    screen = _make_screen(pygame_env, score=5)
    screen.update(0.016)
    screen.draw()  # must not raise


def test_draw_view_phase_does_not_raise(pygame_env, tmp_scores):
    """draw() in VIEW phase (after submission) completes without exception."""
    screen = _make_screen(pygame_env, score=5)
    screen._submitted = True
    screen.update(0.016)
    screen.draw()  # must not raise


def test_chrome_present_and_draws(pygame_env, tmp_scores):
    """ScoreboardScreen owns a Chrome widget and draw() (incl. chrome) runs cleanly."""
    screen = _make_screen(pygame_env, score=5)
    assert screen._chrome is not None
    screen.draw()  # exercises chrome.draw() without error
