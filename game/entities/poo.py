"""Poo entity — Sally's chocolate surprise.

A simple animated sprite placed at Sally's position when Spacebar is pressed.
The drop cooldown (Bug #3 fix: elapsed-time accumulator, not a repeating timer)
is managed by PlayScreen, which tracks a float and calls Poo(pos, powered) only
when the accumulator has elapsed POO_COOLDOWN_SECONDS.
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

    def update(self, dt: float) -> None:  # type: ignore[override]
        self.animate(dt)
