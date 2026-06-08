"""Tests for the ART_SET art-resolver foundation (game.assets._art).

Hermetic: never depends on a real pixellab/ tree existing. The pixellab root is
monkeypatched to a temp dir so we can plant (or omit) assets and assert the
per-asset fallback to assets/ behaves.
"""

from __future__ import annotations

from game import assets
from game import config


# Every image accessor, paired with the relative path it should resolve to.
def _accessors():
    return [
        (assets.player_dir(), ("characters",)),
        (assets.npc_dir("gym"), ("npc", "gym")),
        (assets.obstacle_dir("gym"), ("obstacles", "gym")),
        (assets.powerups_dir(), ("powerups",)),
        (assets.surprises_dir(True), ("surprises", "powered")),
        (assets.surprises_dir(False), ("surprises", "unpowered")),
        (assets.map_image("level1.png"), ("maps", "level1.png")),
        (assets.endscreen("win.png"), ("endscreens", "win.png")),
    ]


def test_original_artset_resolves_under_assets(monkeypatch):
    """ART_SET='original': every image accessor matches today's assets/ paths."""
    monkeypatch.setattr(config, "ART_SET", "original")
    for got, parts in _accessors():
        assert got == config.ASSETS.joinpath(*parts)


def test_pixellab_empty_falls_back_to_assets(monkeypatch, tmp_path):
    """ART_SET='pixellab' with an empty/missing pixellab tree falls back to assets/.

    This is the key safety property: an ungenerated set never breaks loading.
    """
    monkeypatch.setattr(config, "ART_SET", "pixellab")
    monkeypatch.setattr(config, "PIXELLAB", tmp_path)  # empty dir
    for got, parts in _accessors():
        assert got == config.ASSETS.joinpath(*parts)

    # A missing pixellab dir altogether behaves the same.
    monkeypatch.setattr(config, "PIXELLAB", tmp_path / "does_not_exist")
    for got, parts in _accessors():
        assert got == config.ASSETS.joinpath(*parts)


def test_pixellab_planted_assets_resolve_into_pixellab(monkeypatch, tmp_path):
    """Planted pixellab assets resolve into pixellab; un-planted ones fall back."""
    monkeypatch.setattr(config, "ART_SET", "pixellab")
    monkeypatch.setattr(config, "PIXELLAB", tmp_path)

    # Plant a map file and a characters/ dir containing a PNG.
    (tmp_path / "maps").mkdir(parents=True)
    (tmp_path / "maps" / "level1.png").write_bytes(b"")
    (tmp_path / "characters" / "down").mkdir(parents=True)
    (tmp_path / "characters" / "down" / "0.png").write_bytes(b"")

    # Planted file resolves into pixellab.
    assert assets.map_image("level1.png") == tmp_path / "maps" / "level1.png"
    # Planted (non-empty) dir resolves into pixellab.
    assert assets.player_dir() == tmp_path / "characters"

    # Un-planted accessors still fall back to assets/.
    assert assets.obstacle_dir("gym") == config.ASSETS / "obstacles" / "gym"
    assert assets.map_image("level2.png") == config.ASSETS / "maps" / "level2.png"


def test_pixellab_empty_dir_falls_back(monkeypatch, tmp_path):
    """A pixellab dir that exists but has no PNGs falls back to assets/."""
    monkeypatch.setattr(config, "ART_SET", "pixellab")
    monkeypatch.setattr(config, "PIXELLAB", tmp_path)

    (tmp_path / "characters").mkdir(parents=True)  # exists but empty -> no PNGs
    assert assets.player_dir() == config.ASSETS / "characters"


def test_fonts_music_sfx_never_move(monkeypatch, tmp_path):
    """Fonts/music/sfx stay on assets/ regardless of ART_SET (PixelLab is art only)."""
    monkeypatch.setattr(config, "ART_SET", "pixellab")
    monkeypatch.setattr(config, "PIXELLAB", tmp_path)
    assert assets.font_path("x.ttf") == config.ASSETS / "fonts" / "x.ttf"
    assert assets.music_path("x.ogg") == config.ASSETS / "sounds" / "music" / "x.ogg"
    assert assets.sfx_path("x.wav") == config.ASSETS / "sounds" / "sfx" / "x.wav"
