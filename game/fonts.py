"""Font loader — single source of truth for the game's typeface."""

from __future__ import annotations

import pygame

from game import assets

_FACE = "AlfaSlabOne-Regular.ttf"


def load(size: int) -> pygame.font.Font:
    return pygame.font.Font(str(assets.font_path(_FACE)), size)
