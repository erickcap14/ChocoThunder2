"""Player entity — Sally, the chocolate-depositing terrier.

Movement has two modes, both at PLAYER_SPEED px/frame:
  - Click / click-drag: PlayScreen sets a target (the latest cursor position
    while the button is held) via ``set_target``; Sally seeks it.
  - Arrow keys: PlayScreen sets a direction via ``set_move_dir``; a non-zero
    direction steers Sally directly and overrides the seek target.

Invincibility (from cakes) is tracked here so both PlayScreen collision checks
and the MCP set_invincible tool share one source.
"""

from __future__ import annotations

import pygame

from game import assets, config
from game.entities import clamp_rect
from game.sprites import DirectionalSprite


class Player(DirectionalSprite):
    def __init__(self, pos):
        self._frames_normal = assets.load_directional_frames(
            assets.player_dir(), config.PLAYER_RENDER_SIZE
        )
        # Optional distinct "powered" spritesheet shown during invincibility; falls back
        # to the normal frames when the active art set has no powered art (e.g. original).
        self._frames_powered = self._load_powered_frames()
        super().__init__(self._frames_normal, pos, hitbox_size=config.PLAYER_SIZE)
        self._target: pygame.Vector2 = pygame.Vector2(pos)
        self._move_dir: pygame.Vector2 = pygame.Vector2(0, 0)  # arrow-key steer
        self.is_invincible: bool = False
        self._invincible_remaining: float = 0.0

    @staticmethod
    def _load_powered_frames():
        try:
            return assets.load_directional_frames(
                assets.player_powered_dir(), config.PLAYER_RENDER_SIZE
            )
        except FileNotFoundError:
            return None

    def _apply_powered_skin(self) -> None:
        """Swap the active spritesheet to match invincibility state (no-op without art)."""
        if self._frames_powered is None:
            return
        want = self._frames_powered if self.is_invincible else self._frames_normal
        if want is not self.frames:
            self.frames = want
            frames = want[self.status]
            self.image = frames[int(self.frame_index) % len(frames)]

    def set_target(self, pos) -> None:
        self._target = pygame.Vector2(pos)

    def set_move_dir(self, dx: float, dy: float) -> None:
        """Set the arrow-key movement direction (0,0 = none). A non-zero direction
        steers Sally directly, overriding the click/drag seek target."""
        self._move_dir = pygame.Vector2(dx, dy)

    def set_invincible(self, state: bool) -> None:
        """Activate or deactivate invincibility. MCP set_invincible calls this."""
        self.is_invincible = state
        self._invincible_remaining = config.INVINCIBLE_SECONDS if state else 0.0

    def update(self, dt: float, bounds: pygame.Rect) -> None:
        self._apply_powered_skin()
        current = pygame.Vector2(self.rect.center)

        # Arrow keys steer directly and win over the click/drag target; otherwise
        # Sally seeks the latest click/drag position.
        arrow_driving = self._move_dir.length_squared() > 0
        if arrow_driving:
            step = self._move_dir.normalize() * config.PLAYER_SPEED
        else:
            diff = self._target - current
            step = (
                diff.normalize() * config.PLAYER_SPEED
                if diff.length() > config.PLAYER_SPEED
                else pygame.Vector2()
            )

        if step.length_squared() > 0:
            self.rect.center = current + step
            if abs(step.x) >= abs(step.y):
                self.set_status("right" if step.x > 0 else "left")
            else:
                self.set_status("down" if step.y > 0 else "up")
            self.animate(dt)

        clamp_rect(self.rect, bounds)
        # While arrow-driving, pin the seek target to where Sally ended up so that
        # releasing the keys stops her here instead of darting back to a stale click.
        if arrow_driving:
            self._target = pygame.Vector2(self.rect.center)

        if self.is_invincible:
            self._invincible_remaining -= dt
            if self._invincible_remaining <= 0.0:
                self.is_invincible = False
                self._invincible_remaining = 0.0
