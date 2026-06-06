"""NPC entity — tenant that patrols randomly and chases Sally when close.

Two modes:
- PATROL: walk toward a random target; pick a new one on arrival.
- CHASE:  walk toward the player when within NPC_CHASE_RADIUS.

Catching the player (rect overlap while player is not invincible) is detected
by PlayScreen, which then transitions to the END state.
"""

from __future__ import annotations

import random

import pygame

from game import assets, config
from game.entities import clamp_rect
from game.sprites import DirectionalSprite

_PATROL = "patrol"
_CHASE = "chase"


class NPC(DirectionalSprite):
    def __init__(self, char: str, pos, bounds: pygame.Rect):
        frames = assets.load_directional_frames(assets.npc_dir(char), config.PLAYER_SIZE)
        super().__init__(frames, pos, hitbox_size=config.PLAYER_SIZE)
        self._bounds = bounds
        self._mode = _PATROL
        self._patrol_target: pygame.Vector2 = self._random_target()

    def _random_target(self) -> pygame.Vector2:
        x = random.randint(self._bounds.left, self._bounds.right)
        y = random.randint(self._bounds.top, self._bounds.bottom)
        return pygame.Vector2(x, y)

    @property
    def is_chasing(self) -> bool:
        return self._mode == _CHASE

    def update(self, dt: float, player_rect: pygame.Rect) -> None:  # type: ignore[override]
        my_pos = pygame.Vector2(self.rect.center)
        player_pos = pygame.Vector2(player_rect.center)

        if my_pos.distance_to(player_pos) <= config.NPC_CHASE_RADIUS:
            self._mode = _CHASE
            target = player_pos
        else:
            self._mode = _PATROL
            target = self._patrol_target
            if my_pos.distance_to(target) < config.NPC_SPEED:
                self._patrol_target = self._random_target()

        diff = target - my_pos
        if diff.length() > config.NPC_SPEED:
            step = diff.normalize() * config.NPC_SPEED
            self.rect.center = my_pos + step
            if abs(step.x) >= abs(step.y):
                self.set_status("right" if step.x > 0 else "left")
            else:
                self.set_status("down" if step.y > 0 else "up")
            self.animate(dt)

        clamp_rect(self.rect, self._bounds)
