"""Font loader and shared text helpers."""

from __future__ import annotations

import pygame

from game import assets

_FACE = "AlfaSlabOne-Regular.ttf"

TITLE_FILL    = (255, 215,   0)   # gold yellow
TITLE_OUTLINE = (200,   0,   0)   # deep red
_OUTLINE_PX   = 2

# Touch-UI prompt button (matches the start screen's selected-difficulty style)
PROMPT_FILL       = (40, 130, 60)
_PROMPT_PAD_X     = 30
_PROMPT_PAD_Y     = 12
_PROMPT_BORDER_PX = 3
_PROMPT_RADIUS    = 16


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


def blit_prompt(
    screen: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    y: int,
    cx: int | None = None,
) -> pygame.Rect:
    """Blit an advance prompt with its text top edge at y, centred at cx.

    Desktop: plain green text (key instructions aren't clickable). Touch UI:
    white text on an obvious green pill button — purely a visual affordance,
    since tapping anywhere on these screens already advances.
    """
    from game import config

    if cx is None:
        cx = config.SCREEN_WIDTH // 2
    touch = config.touch_ui_enabled()
    label = font.render(text, True, config.WHITE if touch else config.GREEN)
    rect = label.get_rect(centerx=cx, top=y)
    if touch:
        button = rect.inflate(_PROMPT_PAD_X * 2, _PROMPT_PAD_Y * 2)
        pygame.draw.rect(screen, PROMPT_FILL, button, border_radius=_PROMPT_RADIUS)
        pygame.draw.rect(
            screen, config.WHITE, button,
            width=_PROMPT_BORDER_PX, border_radius=_PROMPT_RADIUS,
        )
    screen.blit(label, rect)
    return rect
