"""Font loader and shared text helpers."""

from __future__ import annotations

import pygame

from game import assets

_FACE = "AlfaSlabOne-Regular.ttf"

TITLE_FILL    = (255, 215,   0)   # gold yellow
TITLE_OUTLINE = (200,   0,   0)   # deep red
_OUTLINE_PX   = 2


def load(size: int) -> pygame.font.Font:
    return pygame.font.Font(str(assets.font_path(_FACE)), size)


def blit_outlined(
    screen: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    y: int,
    cx: int | None = None,
) -> None:
    """Blit text with a TITLE_OUTLINE border and TITLE_FILL centre, centred at cx."""
    if cx is None:
        from game import config
        cx = config.SCREEN_WIDTH // 2
    outline = font.render(text, True, TITLE_OUTLINE)
    fill    = font.render(text, True, TITLE_FILL)
    for dx in range(-_OUTLINE_PX, _OUTLINE_PX + 1):
        for dy in range(-_OUTLINE_PX, _OUTLINE_PX + 1):
            if dx == 0 and dy == 0:
                continue
            screen.blit(outline, outline.get_rect(centerx=cx + dx, top=y + dy))
    screen.blit(fill, fill.get_rect(centerx=cx, top=y))
