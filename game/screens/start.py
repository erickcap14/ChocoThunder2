"""StartScreen — scrolling title background, game blurb, and controls.

Ground-truth spec (PRD §3):
  - Scrolling title background (introscreen.png)
  - Game blurb + control list
  - "Press Space Bar to Play"
  - SPACE → transitions to RUNNING
"""

from __future__ import annotations

import pygame

from game import assets, config, fonts
from game.state_machine import GameState

_SCROLL_SPEED = 80  # px/sec; background scrolls left

_TITLE_1 = "CHOCOLATE THUNDER 2"
_TITLE_2 = "Electric Boogaloo"
_BLURB = (
    "You are Sally, an adorable white terrier.  Sneak around the house,",
    "leave chocolate surprises for points, and dodge the tenants!",
)
_CONTROLS = (
    "Controls:",
    "  Click anywhere  —  move Sally",
    "  Space Bar        —  leave a chocolate surprise",
    "  Eat a cake       —  become invincible (bonus points!)",
)
_PROMPT = "Press Space Bar to Play"


class StartScreen:
    def __init__(self, screen: pygame.Surface, state_machine, audio):
        self.screen = screen
        self.sm = state_machine
        self.audio = audio
        self.score = 0
        self.level = 1

        self._setup_bg()
        self._setup_fonts()
        self._setup_overlay()

        self.audio.play_music("A1-Thunderstruck_01.ogg")

    # ------------------------------------------------------------------
    def _setup_bg(self) -> None:
        raw = pygame.image.load(str(assets.map_image("introscreen.png")))
        # Scale to screen height; preserve aspect ratio for width.
        scale = config.SCREEN_HEIGHT / raw.get_height()
        self._bg_w = max(int(raw.get_width() * scale), config.SCREEN_WIDTH + 1)
        self._bg = pygame.transform.scale(raw, (self._bg_w, config.SCREEN_HEIGHT))
        self._bg_x: float = 0.0

    def _setup_fonts(self) -> None:
        self._font_title  = fonts.load(72)
        self._font_sub    = fonts.load(48)
        self._font_body   = fonts.load(26)
        self._font_prompt = fonts.load(40)

    def _setup_overlay(self) -> None:
        w, h = 960, 310
        self._overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        self._overlay.fill((20, 20, 20, 190))
        self._overlay_rect = self._overlay.get_rect(
            center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 30)
        )
        # Center the blurb + controls block vertically inside the panel.
        self._body_line_h = self._font_body.get_linesize()
        block_h = self._body_line_h * (len(_BLURB) + len(_CONTROLS)) + 10
        self._text_top = self._overlay_rect.top + (h - block_h) // 2

    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.audio.stop_music()
            self.sm.force_state(GameState.PRELEVEL)

    def update(self, dt: float) -> None:
        self._bg_x -= _SCROLL_SPEED * dt
        if self._bg_x <= -self._bg_w:
            self._bg_x = 0.0

    def draw(self) -> None:
        # Scrolling background (tiled with two blits for seamless wrap).
        x = int(self._bg_x)
        self.screen.blit(self._bg, (x, 0))
        self.screen.blit(self._bg, (x + self._bg_w, 0))

        # Dark overlay panel.
        self.screen.blit(self._overlay, self._overlay_rect)

        # Title — yellow fill with red outline.
        fonts.blit_outlined(self.screen, self._font_title, _TITLE_1, y=80)
        fonts.blit_outlined(self.screen, self._font_sub,   _TITLE_2, y=148)

        # Blurb + controls — vertically centered inside the overlay panel.
        y = self._text_top
        for line in _BLURB:
            self._blit_centered(self._font_body, line, config.WHITE, y=y)
            y += self._body_line_h

        y += 10  # gap between blurb and controls
        for line in _CONTROLS:
            color = config.WHITE if not line.startswith("  ") else (200, 200, 200)
            self._blit_centered(self._font_body, line, color, y=y)
            y += self._body_line_h

        # Prompt.
        self._blit_centered(self._font_prompt, _PROMPT, config.GREEN, y=630)

    # ------------------------------------------------------------------
    def _blit_centered(
        self, font: pygame.font.Font, text: str, color: tuple, y: int
    ) -> None:
        surf = font.render(text, True, color)
        rect = surf.get_rect(centerx=config.SCREEN_WIDTH // 2, top=y)
        self.screen.blit(surf, rect)

