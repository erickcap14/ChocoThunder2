"""PowerUp entity — animated cake that triggers real invincibility when collected.

When PlayScreen detects collision between Player and this sprite, it calls
player.set_invincible(True) and kills this sprite. The three-frame cake
animation runs until collected.
"""

from __future__ import annotations

import pygame

from game import assets, config
from game.sprites import FrameSprite


class PowerUp(FrameSprite):
    def __init__(self, pos):
        frames = assets.load_frames(assets.powerups_dir(), config.POWERUP_SIZE)
        super().__init__(frames, pos, hitbox_size=config.POWERUP_SIZE)

    def update(self, dt: float) -> None:  # type: ignore[override]
        self.animate(dt)
