"""Poo entity — Sally's chocolate surprise.

A simple animated sprite placed at Sally's position when Spacebar is pressed.
The drop cooldown (Bug #3 fix: elapsed-time accumulator, not a repeating timer)
is managed by PlayScreen, which tracks a float and calls Poo(pos, powered) only
when the accumulator has elapsed POO_COOLDOWN_SECONDS.

When a tenant steps on a powered surprise, PlayScreen calls splat(): the sprite
swaps to the splat animation and fades itself off the floor after a few seconds.
"""

from __future__ import annotations

import pygame

from game import assets, config
from game.sprites import FrameSprite


class Poo(FrameSprite):
    def __init__(self, pos, powered: bool = False):
        frames = assets.load_frames(assets.surprises_dir(powered), config.POO_SIZE)
        super().__init__(frames, pos, hitbox_size=config.POO_SIZE)
        self.powered = powered
        self.is_splat = False
        self._splat_remaining = 0.0

    def splat(self) -> None:
        """Transform a (powered) surprise into a splat: swap to the splat animation
        and start a fade timer after which the sprite removes itself."""
        self.frames = assets.load_frames(assets.splat_dir(), config.POO_SIZE)
        self.frame_index = 0.0
        self.is_splat = True
        self._splat_remaining = config.SPLAT_FADE_SECONDS

    def update(self, dt: float) -> None:  # type: ignore[override]
        self.animate(dt)
        if self.is_splat:
            self._splat_remaining -= dt
            if self._splat_remaining <= 0.0:
                self.kill()
