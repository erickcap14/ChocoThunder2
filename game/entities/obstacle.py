"""Obstacle entity — immovable furniture.

Exposes push_out(rect) to reposition any moving rect out of this obstacle
using minimum-overlap axis separation. This fixes Bug #2: the original game
zeroed the player's position on overlap, causing a permanent soft-lock.

PlayScreen creates one Obstacle per furniture image loaded from
assets.obstacle_dir(room), placing each at a random position from
config.OBSTACLE_X / OBSTACLE_Y.
"""

from __future__ import annotations

import pygame

from game import config
from game.sprites import ImageSprite


class Obstacle(ImageSprite):
    def __init__(self, image: pygame.Surface, pos):
        super().__init__(image, pos, hitbox_size=config.OBSTACLE_SIZE)

    def push_out(self, mover_rect: pygame.Rect) -> None:
        """Push mover_rect out of self.rect on the axis of minimum overlap (in-place)."""
        if not self.rect.colliderect(mover_rect):
            return
        overlap_left = self.rect.right - mover_rect.left
        overlap_right = mover_rect.right - self.rect.left
        overlap_top = self.rect.bottom - mover_rect.top
        overlap_bottom = mover_rect.bottom - self.rect.top
        if min(overlap_left, overlap_right) <= min(overlap_top, overlap_bottom):
            if overlap_left < overlap_right:
                mover_rect.left = self.rect.right
            else:
                mover_rect.right = self.rect.left
        else:
            if overlap_top < overlap_bottom:
                mover_rect.top = self.rect.bottom
            else:
                mover_rect.bottom = self.rect.top
