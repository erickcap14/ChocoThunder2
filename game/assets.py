"""Asset loading helpers.

Replaces the original `s_sprite.importFolderImageList` /
`d_sprite.importFolderAnimationList` (two near-identical importers) with a single
cached loader. Images are loaded lazily and cached by (path, size).
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import pygame

from game import config

_DIRECTIONS = ("down", "left", "right", "up")
_num_re = re.compile(r"(\d+)")


def _natural_key(p: Path):
    """Sort '0.png','1.png',...,'10.png' and 'Sprite 2.png' numerically."""
    nums = _num_re.findall(p.stem)
    return [int(n) for n in nums] if nums else [0]


def _convert(surf: pygame.Surface) -> pygame.Surface:
    """convert_alpha when a display exists; otherwise return as-is (headless safety)."""
    if pygame.display.get_surface() is not None:
        try:
            return surf.convert_alpha()
        except pygame.error:
            return surf
    return surf


@lru_cache(maxsize=None)
def load_image(path: str, size: tuple[int, int] | None = None) -> pygame.Surface:
    """Load a single image (cached). Optionally scaled to ``size``."""
    surf = _convert(pygame.image.load(path))
    if size is not None:
        surf = pygame.transform.scale(surf, size)
    return surf


def load_frames(folder: str | Path, size: tuple[int, int] | None = None) -> list[pygame.Surface]:
    """Load all PNG frames in a folder, sorted naturally, optionally scaled."""
    folder = Path(folder)
    frames = []
    for png in sorted(folder.glob("*.png"), key=_natural_key):
        if png.name.startswith("."):
            continue
        frames.append(load_image(str(png), size))
    if not frames:
        raise FileNotFoundError(f"No PNG frames found in {folder}")
    return frames


def load_directional_frames(
    folder: str | Path, size: tuple[int, int] | None = None
) -> dict[str, list[pygame.Surface]]:
    """Load down/left/right/up subfolders into a status->frames dict."""
    folder = Path(folder)
    return {d: load_frames(folder / d, size) for d in _DIRECTIONS}


def load_sound(path: str | Path) -> pygame.mixer.Sound:
    """Load a sound effect (caller handles mixer availability)."""
    return pygame.mixer.Sound(str(path))


# Convenience asset-path accessors (single source of truth for the layout).
def player_dir() -> Path:
    return config.ASSETS / "characters"


def npc_dir(char: str) -> Path:
    return config.ASSETS / "npc" / char


def obstacle_dir(room: str) -> Path:
    return config.ASSETS / "obstacles" / room


def powerups_dir() -> Path:
    return config.ASSETS / "powerups"


def surprises_dir(powered: bool) -> Path:
    return config.ASSETS / "surprises" / ("powered" if powered else "unpowered")


def map_image(name: str) -> Path:
    return config.ASSETS / "maps" / name


def endscreen(name: str) -> Path:
    return config.ASSETS / "endscreens" / name


def music_path(name: str) -> Path:
    return config.ASSETS / "sounds" / "music" / name


def sfx_path(name: str) -> Path:
    return config.ASSETS / "sounds" / "sfx" / name


def font_path(name: str) -> Path:
    return config.ASSETS / "fonts" / name
