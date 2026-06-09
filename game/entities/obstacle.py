"""Obstacle entity — immovable furniture with exact-shape (pixel-mask) collision.

The collision footprint is the *visible shape of the obstacle image*, not a fixed
rectangle: ``self.mask`` is built from the sprite's opaque pixels and aligned to
``self.rect`` (which is the full image rect, so the mask, the rect, and the
centered draw all share one coordinate frame). This lets movers slide around the
real furniture silhouette instead of bumping an invisible box (Bug #2 / "gets
stuck" fix), and keeps collision matched to what the player sees on screen.

Two collision services:
  - ``collides_rect(rect)``  — exact-shape overlap test (broad-phase rect reject,
    then pixel-mask check). Used by PlayScreen's move-and-slide.
  - ``push_out(rect)``       — recovery eject for a mover that ended up *inside*
    the shape (spawn overlap, separation shove): pushes it to the nearest edge of
    the visible bounding box on the min-overlap axis.
"""

from __future__ import annotations

import pygame

from game.sprites import ImageSprite

# Solid (fully-set) masks for mover hitboxes, cached by size so the per-frame
# overlap tests don't rebuild a mask every call.
_SOLID_MASKS: dict[tuple[int, int], pygame.mask.Mask] = {}


def _solid_mask(size: tuple[int, int]) -> pygame.mask.Mask:
    mask = _SOLID_MASKS.get(size)
    if mask is None:
        mask = pygame.mask.Mask(size, fill=True)
        _SOLID_MASKS[size] = mask
    return mask


class Obstacle(ImageSprite):
    def __init__(self, image: pygame.Surface, pos):
        # No decoupled hitbox: rect == image rect, so the pixel mask aligns with
        # rect.topleft and the centered draw lands exactly on the collision shape.
        super().__init__(image, pos)
        self.mask = pygame.mask.from_surface(image)
        # World-space rect of the visible (opaque) pixels — tighter than the padded
        # image rect; used for eject direction and spawn-clearance queries.
        self.bbox = image.get_bounding_rect().move(self.rect.topleft)

    def collides_rect(self, mover_rect: pygame.Rect) -> bool:
        """True if mover_rect overlaps an opaque pixel of this obstacle (exact shape)."""
        if not self.rect.colliderect(mover_rect):
            return False
        offset = (mover_rect.x - self.rect.x, mover_rect.y - self.rect.y)
        return self.mask.overlap(_solid_mask(mover_rect.size), offset) is not None

    def push_out(self, mover_rect: pygame.Rect) -> None:
        """If mover_rect overlaps the shape, eject it to the nearest edge of the
        visible bounding box on the min-overlap axis (in-place). Recovery only —
        normal movement is handled by PlayScreen's slide, which keeps movers from
        entering in the first place."""
        if not self.collides_rect(mover_rect):
            return
        b = self.bbox
        overlap_left = b.right - mover_rect.left
        overlap_right = mover_rect.right - b.left
        overlap_top = b.bottom - mover_rect.top
        overlap_bottom = mover_rect.bottom - b.top
        if min(overlap_left, overlap_right) <= min(overlap_top, overlap_bottom):
            if overlap_left < overlap_right:
                mover_rect.left = b.right
            else:
                mover_rect.right = b.left
        else:
            if overlap_top < overlap_bottom:
                mover_rect.top = b.bottom
            else:
                mover_rect.bottom = b.top
