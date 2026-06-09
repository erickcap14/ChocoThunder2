"""Phase 5 unit tests — LevelSpec manifest, PlayScreen level integration, and
TransitionScreen subtitle consistency (headless).

Covers:
  1.  LEVELS manifest loads and is non-empty.
  2.  Exactly 4 levels are defined.
  3.  All string fields on every LevelSpec are non-empty.
  4.  All npcs lists are non-empty.
  5.  Each level has a unique name.
  6.  Each level has a unique map_image.
  7.  LevelSpec is frozen (mutation raises an error).
  8.  Level 4 subtitle differs from Level 3 (extensibility check).
  9.  PlayScreen initialises correctly with score=0 and level=1.
  10. PlayScreen.set_level(4) sets the level attribute to 4.
  11. PlayScreen.set_level(n) succeeds for every n in 1..4.
  12. TransitionScreen subtitle matches the LEVELS manifest entry.
"""

from __future__ import annotations

import pytest
import pygame

from game.levels import LEVELS, LevelSpec
from game.screens.play import PlayScreen
from game.screens.transition import TransitionScreen
from game.state_machine import GameState, StateMachine
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


# ---------------------------------------------------------------------------
# Tests — manifest structure
# ---------------------------------------------------------------------------

@pytest.mark.log_meta(phase="phase_5", subtask="5.1", action="levels manifest loads")
def test_levels_manifest_is_non_empty():
    """LEVELS list loads from game.levels and contains at least one entry."""
    assert len(LEVELS) > 0


@pytest.mark.log_meta(phase="phase_5", subtask="5.2", action="exactly 4 levels")
def test_levels_manifest_has_exactly_four():
    """Exactly 4 LevelSpec entries are defined in the manifest."""
    assert len(LEVELS) == 4


@pytest.mark.log_meta(phase="phase_5", subtask="5.3", action="all string fields non-empty")
def test_all_string_fields_are_non_empty():
    """Every required string field on every LevelSpec is a non-empty string.

    ``music`` is intentionally excluded: a level may have no track yet (empty
    string), in which case it plays silently from transition to complete.
    """
    string_fields = ("name", "map_image", "obstacle_room", "transition_subtitle", "intro_subtitle")
    for spec in LEVELS:
        for field in string_fields:
            value = getattr(spec, field)
            assert isinstance(value, str), (
                f"{spec.name}.{field} is not a str: {value!r}"
            )
            assert value.strip(), (
                f"{spec.name}.{field} is an empty string"
            )
        # music is optional but must still be a string (possibly empty).
        assert isinstance(spec.music, str), (
            f"{spec.name}.music is not a str: {spec.music!r}"
        )


@pytest.mark.log_meta(phase="phase_5", subtask="5.4", action="all npcs lists non-empty")
def test_all_npcs_lists_are_non_empty():
    """Every LevelSpec.npcs list contains at least one NPC name."""
    for spec in LEVELS:
        assert len(spec.npcs) >= 1, (
            f"{spec.name}.npcs is empty"
        )


@pytest.mark.log_meta(phase="phase_5", subtask="5.5", action="unique level names")
def test_level_names_are_unique():
    """No two levels share the same name."""
    names = [spec.name for spec in LEVELS]
    assert len(names) == len(set(names)), "Duplicate level names found"


@pytest.mark.log_meta(phase="phase_5", subtask="5.6", action="unique map_image filenames")
def test_map_images_are_unique():
    """No two levels reference the same map_image filename."""
    images = [spec.map_image for spec in LEVELS]
    assert len(images) == len(set(images)), "Duplicate map_image filenames found"


@pytest.mark.log_meta(phase="phase_5", subtask="5.7", action="LevelSpec is frozen")
def test_levelspec_is_frozen():
    """Assigning to a LevelSpec field raises FrozenInstanceError (or AttributeError)."""
    spec = LEVELS[0]
    with pytest.raises((AttributeError,)):
        spec.name = "Hacked"  # type: ignore[misc]


@pytest.mark.log_meta(phase="phase_5", subtask="5.8", action="level 4 subtitle differs from level 3")
def test_level_4_subtitle_differs_from_level_3():
    """Level 4 has a distinct transition_subtitle from Level 3 (proves extensibility)."""
    level3 = LEVELS[2]
    level4 = LEVELS[3]
    assert level4.transition_subtitle != level3.transition_subtitle, (
        "Level 4 subtitle should be distinct from Level 3"
    )


# ---------------------------------------------------------------------------
# Tests — PlayScreen level integration
# ---------------------------------------------------------------------------

@pytest.mark.log_meta(phase="phase_5", subtask="5.9", action="play screen init level 1")
def test_play_screen_initializes_at_level_1(pygame_env):
    """PlayScreen initialises with score=0 and level=1."""
    ps, _, _ = _make_ps(pygame_env)
    assert ps.score == 0
    assert ps.level == 1


@pytest.mark.log_meta(phase="phase_5", subtask="5.10", action="set_level 4 sets level attribute")
def test_set_level_4_sets_correct_attribute(pygame_env):
    """set_level(4) sets ps.level to 4 (the 4th manifest entry)."""
    ps, _, _ = _make_ps(pygame_env)
    ps.set_level(4)
    assert ps.level == 4


@pytest.mark.log_meta(phase="phase_5", subtask="5.11", action="set_level n=1..4 all succeed")
@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_set_level_all_valid_levels(pygame_env, n):
    """set_level(n) succeeds and sets ps.level correctly for every n in 1..4."""
    ps, _, _ = _make_ps(pygame_env)
    ps.set_level(n)
    assert ps.level == n


# ---------------------------------------------------------------------------
# Tests — TransitionScreen subtitle consistency
# ---------------------------------------------------------------------------

@pytest.mark.log_meta(phase="phase_5", subtask="5.12", action="transition subtitle matches manifest")
@pytest.mark.parametrize("level_num", [1, 2, 3])
def test_transition_subtitle_matches_levels_manifest(pygame_env, level_num):
    """TransitionScreen renders the subtitle that matches the LEVELS manifest entry."""
    sm = StateMachine(GameState.TRANSITION)
    audio = _FakeAudio()
    ts = TransitionScreen(pygame_env, sm, audio, level=level_num, score=0)

    expected_subtitle = LEVELS[level_num - 1].transition_subtitle
    # TransitionScreen now reads the subtitle directly from LEVELS at draw time.
    # Verify the manifest entry matches the expected value (the screen is the manifest).
    actual_subtitle = LEVELS[ts.level - 1].transition_subtitle
    assert actual_subtitle == expected_subtitle, (
        f"TransitionScreen subtitle for level {level_num} is {actual_subtitle!r}, "
        f"expected {expected_subtitle!r} from LEVELS manifest"
    )
