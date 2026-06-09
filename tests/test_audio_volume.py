"""AudioManager volume control — value storage and clamping (headless-safe)."""

from __future__ import annotations

from game import config
from game.audio import AudioManager


def test_defaults_match_config(pygame_env):
    a = AudioManager()
    assert a.music_volume == config.DEFAULT_MUSIC_VOLUME
    assert a.sfx_volume == config.DEFAULT_SFX_VOLUME


def test_set_music_volume_stores_value(pygame_env):
    a = AudioManager()
    a.set_music_volume(0.42)
    assert a.music_volume == 0.42


def test_set_sfx_volume_stores_value(pygame_env):
    a = AudioManager()
    a.set_sfx_volume(0.13)
    assert a.sfx_volume == 0.13


def test_volume_clamps_to_unit_range(pygame_env):
    a = AudioManager()
    a.set_music_volume(5.0)
    assert a.music_volume == 1.0
    a.set_music_volume(-2.0)
    assert a.music_volume == 0.0
    a.set_sfx_volume(9.9)
    assert a.sfx_volume == 1.0
    a.set_sfx_volume(-0.5)
    assert a.sfx_volume == 0.0
