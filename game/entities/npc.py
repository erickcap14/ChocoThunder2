"""NPC entity — tenant that patrols randomly and chases Sally when close.

Two modes:
- PATROL: walk toward a random target; pick a new one on arrival.
- CHASE:  walk toward the player when within NPC_CHASE_RADIUS.

Catching the player (rect overlap while player is not invincible) is detected
by PlayScreen, which then transitions to the END state.

Stepping on a splat slows the tenant (apply_slow): for NPC_SLOW_SECONDS it walks
at NPC_SLOW_MULTIPLIER of its normal speed, then recovers.

Position is integrated in a float vector (``_pos``) and only rounded into the
integer ``rect`` for drawing/collision. Without this, a sub-pixel step (a slowed
tenant moves ~0.9 px/frame) would truncate to zero every frame and the tenant
would freeze instead of crawling. External rect moves (obstacle slide, NPC
separation, bounds clamp in PlayScreen) are detected and folded back into ``_pos``.
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
        frames = assets.load_directional_frames(assets.npc_dir(char), config.NPC_RENDER_SIZE)
        super().__init__(frames, pos, hitbox_size=config.NPC_SIZE)
        self._bounds = bounds
        self._mode = _PATROL
        self._patrol_target: pygame.Vector2 = self._random_target()
        self._slow_remaining: float = 0.0
        # Float position accumulator; rect is the rounded view of this.
        self._pos = pygame.Vector2(self.rect.center)
        self._last_center = self.rect.center

    def apply_slow(self) -> None:
        """Slow this tenant for NPC_SLOW_SECONDS (e.g. after stepping on a splat)."""
        self._slow_remaining = config.NPC_SLOW_SECONDS

    def _random_target(self) -> pygame.Vector2:
        x = random.randint(self._bounds.left, self._bounds.right)
        y = random.randint(self._bounds.top, self._bounds.bottom)
        return pygame.Vector2(x, y)

    @property
    def is_chasing(self) -> bool:
        return self._mode == _CHASE

    def update(self, dt: float, player_rect: pygame.Rect) -> None:  # type: ignore[override]
        # Adopt any external rect move (obstacle slide / NPC separation last frame)
        # so the float accumulator tracks where the tenant actually ended up.
        if self.rect.center != self._last_center:
            self._pos.update(self.rect.center)

        my_pos = pygame.Vector2(self._pos)
        player_pos = pygame.Vector2(player_rect.center)
        speed = config.NPC_SPEED * (config.NPC_SLOW_MULTIPLIER if self._slow_remaining > 0 else 1.0)

        if my_pos.distance_to(player_pos) <= config.NPC_CHASE_RADIUS:
            self._mode = _CHASE
            target = player_pos
        else:
            self._mode = _PATROL
            target = self._patrol_target
            if my_pos.distance_to(target) < speed:
                self._patrol_target = self._random_target()

        diff = target - my_pos
        if diff.length() > speed:
            step = diff.normalize() * speed
            self._pos += step
            self.rect.center = (round(self._pos.x), round(self._pos.y))
            if abs(step.x) >= abs(step.y):
                self.set_status("right" if step.x > 0 else "left")
            else:
                self.set_status("down" if step.y > 0 else "up")
            self.animate(dt)

        clamp_rect(self.rect, self._bounds)
        # If clamping nudged us back inside, fold that into the accumulator so it
        # can't drift outside the play area.
        if self.rect.center != (round(self._pos.x), round(self._pos.y)):
            self._pos.update(self.rect.center)
        self._last_center = self.rect.center

        if self._slow_remaining > 0:
            self._slow_remaining = max(0.0, self._slow_remaining - dt)
