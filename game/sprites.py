"""Sprite base classes.

Three small bases cover every entity, replacing the original d_sprite/s_sprite
pair (which leaned on a custom hash-map for animations):

- ``DirectionalSprite`` — status (down/left/right/up) -> frame list. Player, NPC.
- ``FrameSprite``       — a single animated frame list. Poo.
- ``ImageSprite``       — one static image. Obstacle, cake power-up.

All three decouple the *hitbox* (``self.rect``, used for collisions) from the
*drawn image* (centered on the hitbox), so visuals and collision can differ.
"""

from __future__ import annotations

import pygame


class _Base(pygame.sprite.Sprite):
    def __init__(self, image: pygame.Surface, pos, hitbox_size=None):
        super().__init__()
        self.image = image
        size = hitbox_size or image.get_size()
        self.rect = pygame.Rect(0, 0, *size)
        self.rect.center = pos

    # Center-based position helpers (kept compatible with the original API).
    @property
    def posX(self) -> int:
        return self.rect.centerx

    @posX.setter
    def posX(self, v):
        self.rect.centerx = int(v)

    @property
    def posY(self) -> int:
        return self.rect.centery

    @posY.setter
    def posY(self, v):
        self.rect.centery = int(v)

    def draw(self, surface: pygame.Surface) -> None:
        """Blit the current image centered on the hitbox."""
        surface.blit(self.image, self.image.get_rect(center=self.rect.center))


class DirectionalSprite(_Base):
    def __init__(self, frames_by_status: dict, pos, hitbox_size=None, anim_fps=8):
        self.frames = frames_by_status
        self.status = "down" if "down" in frames_by_status else next(iter(frames_by_status))
        self.frame_index = 0.0
        self.anim_fps = anim_fps
        super().__init__(self.frames[self.status][0], pos, hitbox_size)

    def set_status(self, status: str) -> None:
        if status in self.frames:
            self.status = status

    def animate(self, dt: float) -> None:
        frames = self.frames[self.status]
        self.frame_index += self.anim_fps * dt
        if self.frame_index >= len(frames):
            self.frame_index = 0.0
        self.image = frames[int(self.frame_index)]


class FrameSprite(_Base):
    def __init__(self, frames: list, pos, hitbox_size=None, anim_fps=10):
        self.frames = frames
        self.frame_index = 0.0
        self.anim_fps = anim_fps
        super().__init__(frames[0], pos, hitbox_size)

    def animate(self, dt: float) -> None:
        self.frame_index += self.anim_fps * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0.0
        self.image = self.frames[int(self.frame_index)]


class ImageSprite(_Base):
    def __init__(self, image: pygame.Surface, pos, hitbox_size=None):
        super().__init__(image, pos, hitbox_size)
