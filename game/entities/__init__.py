"""Entity package for ChocolateThunder2.

Shared constants and helpers used across entities. Individual entity classes
are re-exported here as each is implemented (T031–T035) so callers can always
do ``from game.entities import Player, NPC, ...``.
"""

from __future__ import annotations

import pygame

# Canonical direction strings for DirectionalSprite-based entities (Player, NPC).
DIRECTIONS = ("down", "left", "right", "up")


def clamp_rect(rect: pygame.Rect, bounds: pygame.Rect) -> None:
    """Clamp rect in-place so it stays fully within bounds."""
    rect.left = max(bounds.left, min(rect.left, bounds.right - rect.width))
    rect.top = max(bounds.top, min(rect.top, bounds.bottom - rect.height))


from game.entities.player import Player
from game.entities.poo import Poo
from game.entities.obstacle import Obstacle
from game.entities.npc import NPC
from game.entities.powerup import PowerUp

__all__ = ["DIRECTIONS", "clamp_rect", "Player", "Poo", "Obstacle", "NPC", "PowerUp"]
