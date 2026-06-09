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


def load_image_fit(path: str, max_box: tuple[int, int]) -> pygame.Surface:
    """Load an image scaled to fit within ``max_box``, preserving aspect ratio.

    Unlike ``load_image(path, size)`` (which stretches to an exact size), this keeps
    the source proportions — a long table stays long, a tall vase stays tall — so the
    drawn obstacle can be decoupled from its (fixed) collision hitbox.
    """
    native = load_image(path)
    nw, nh = native.get_size()
    scale = min(max_box[0] / nw, max_box[1] / nh)
    fit = (max(1, round(nw * scale)), max(1, round(nh * scale)))
    return load_image(path, fit)


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


# --- Art-set resolver ------------------------------------------------------
def _has_pngs(d: Path) -> bool:
    return any(d.rglob("*.png"))


def _art(*parts: str) -> Path:
    """Resolve an art path against the active ART_SET, with per-asset fallback to assets/.

    File paths fall back when the file is missing; directory paths fall back when the dir
    is missing OR contains no PNGs (so an empty/ungenerated pixellab/ dir uses originals).
    """
    candidate = config.art_root().joinpath(*parts)
    if candidate.suffix:                      # a file (e.g. "level1.png")
        return candidate if candidate.exists() else config.ASSETS.joinpath(*parts)
    if candidate.is_dir() and _has_pngs(candidate):   # a non-empty dir
        return candidate
    return config.ASSETS.joinpath(*parts)


# Convenience asset-path accessors (single source of truth for the layout).
# Image accessors route through _art() (ART_SET-aware, per-asset fallback);
# font/music/sfx stay on assets/ since PixelLab is art only.
def player_dir() -> Path:
    return _art("characters")


def npc_dir(char: str) -> Path:
    return _art("npc", char)


def npc_available(char: str) -> bool:
    """True if the active art set has loadable frames for every direction of an NPC.

    Lets level data list a tenant (e.g. char4, which exists only in the pixellab set)
    without crashing the original set, where PlayScreen skips unavailable tenants.
    """
    base = npc_dir(char)
    return all(any((base / d).glob("*.png")) for d in _DIRECTIONS)


def obstacle_dir(room: str) -> Path:
    return _art("obstacles", room)


def powerups_dir() -> Path:
    return _art("powerups")


def surprises_dir(powered: bool) -> Path:
    return _art("surprises", "powered" if powered else "unpowered")


def map_image(name: str) -> Path:
    return _art("maps", name)


def endscreen(name: str) -> Path:
    return _art("endscreens", name)


def transition_image(name: str) -> Path:
    return _art("transitions", name)


def music_path(name: str) -> Path:
    return config.ASSETS / "sounds" / "music" / name


def sfx_path(name: str) -> Path:
    return config.ASSETS / "sounds" / "sfx" / name


def font_path(name: str) -> Path:
    return config.ASSETS / "fonts" / name
