"""StartScreen — animated side-scroller title scene + game blurb and controls.

When the pixellab start-screen art is present (pixellab/startscreen/), the background is
a scrolling backyard with Sally running in place and the tenants (incl. the T-rex) chasing
her, a butterfly that flits past now and then, and a googly-eyed "surprise" that pops up in
the background. Otherwise it falls back to the original scrolling introscreen.

  - Title + blurb + controls panel + "Press Space Bar to Play"
  - SPACE → transitions to PRELEVEL
"""

from __future__ import annotations

import math
import random

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

# Chase cast, drawn back-to-front; (folder, drawn height px, x, run fps). Sally is front-right.
_RUNNERS = (
    ("trex",  150, 210, 9),
    ("char3", 145, 360, 11),
    ("char2", 145, 505, 10),
    ("char1", 145, 650, 11),
    ("sally", 120, 800, 13),
)
_FEET_Y = config.SCREEN_HEIGHT - 24


class _Runner:
    """A run cycle animated in place on the ground line."""

    def __init__(self, frames: list[pygame.Surface], x: int, fps: float):
        self.frames = frames
        self.x = x
        self.fps = fps
        self._t = random.random() * len(frames)

    def update(self, dt: float) -> None:
        self._t = (self._t + self.fps * dt) % len(self.frames)

    def draw(self, surface: pygame.Surface) -> None:
        img = self.frames[int(self._t)]
        surface.blit(img, img.get_rect(midbottom=(self.x, _FEET_Y)))


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
        start_dir = config.PIXELLAB / "startscreen"
        backyard = start_dir / "backyard.png"
        self._animated = backyard.exists()
        bg_path = backyard if self._animated else assets.map_image("introscreen.png")

        raw = pygame.image.load(str(bg_path))
        scale = config.SCREEN_HEIGHT / raw.get_height()
        self._bg_w = max(int(raw.get_width() * scale), config.SCREEN_WIDTH + 1)
        self._bg = pygame.transform.scale(raw, (self._bg_w, config.SCREEN_HEIGHT))
        self._bg_x: float = 0.0

        if self._animated:
            self._setup_scene(start_dir)

    def _setup_scene(self, start_dir) -> None:
        self._runners: list[_Runner] = []
        for folder, height, x, fps in _RUNNERS:
            frames = self._load_runner(start_dir / folder, height)
            if frames:
                self._runners.append(_Runner(frames, x, fps))

        self._butterfly = self._load_sprite(start_dir / "butterfly.png", 56)
        self._surprise = self._load_sprite(start_dir / "surprise.png", 80)

        # Butterfly: drifts in from the right every few seconds along a gentle wave.
        self._bf_active = False
        self._bf_timer = 2.0
        self._bf_x = 0.0
        self._bf_y = 0.0
        self._bf_phase = 0.0
        # Surprise: pops up in the sky/background for a beat, then hides.
        self._sp_timer = 3.5
        self._sp_show = 0.0
        self._sp_pos = (0, 0)

    @staticmethod
    def _load_runner(folder, height: int) -> list[pygame.Surface] | None:
        try:
            frames = assets.load_frames(folder)
        except FileNotFoundError:
            return None
        out = []
        for f in frames:
            w, h = f.get_size()
            out.append(pygame.transform.scale(f, (max(1, round(w * height / h)), height)))
        return out

    @staticmethod
    def _load_sprite(path, height: int) -> pygame.Surface | None:
        if not path.exists():
            return None
        img = assets.load_image(str(path))
        w, h = img.get_size()
        return pygame.transform.scale(img, (max(1, round(w * height / h)), height))

    def _setup_fonts(self) -> None:
        self._font_title  = fonts.load(72)
        self._font_sub    = fonts.load(48)
        self._font_body   = fonts.load(26)
        self._font_prompt = fonts.load(40)

    def _setup_overlay(self) -> None:
        w, h = 960, 300
        self._overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        self._overlay.fill((20, 20, 20, 190))
        self._overlay_rect = self._overlay.get_rect(
            center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
        )
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
        if not self._animated:
            return

        for runner in self._runners:
            runner.update(dt)
        self._update_butterfly(dt)
        self._update_surprise(dt)

    def _update_butterfly(self, dt: float) -> None:
        if self._butterfly is None:
            return
        if self._bf_active:
            self._bf_x -= 130 * dt
            self._bf_phase += 3.0 * dt
            if self._bf_x < -60:
                self._bf_active = False
                self._bf_timer = random.uniform(4.0, 8.0)
        else:
            self._bf_timer -= dt
            if self._bf_timer <= 0:
                self._bf_active = True
                self._bf_x = config.SCREEN_WIDTH + 40
                self._bf_y = random.uniform(70, 230)
                self._bf_phase = 0.0

    def _update_surprise(self, dt: float) -> None:
        if self._surprise is None:
            return
        if self._sp_show > 0:
            self._sp_show -= dt
        else:
            self._sp_timer -= dt
            if self._sp_timer <= 0:
                self._sp_show = random.uniform(1.6, 2.4)
                self._sp_timer = random.uniform(4.0, 7.0)
                self._sp_pos = (random.randint(120, config.SCREEN_WIDTH - 120),
                                random.randint(95, 210))

    def draw(self) -> None:
        x = int(self._bg_x)
        self.screen.blit(self._bg, (x, 0))
        self.screen.blit(self._bg, (x + self._bg_w, 0))

        if self._animated:
            self._draw_scene()

        self.screen.blit(self._overlay, self._overlay_rect)

        fonts.blit_outlined(self.screen, self._font_title, _TITLE_1, y=80)
        fonts.blit_outlined(self.screen, self._font_sub,   _TITLE_2, y=148)

        y = self._text_top
        for line in _BLURB:
            self._blit_centered(self._font_body, line, config.WHITE, y=y)
            y += self._body_line_h
        y += 10
        for line in _CONTROLS:
            color = config.WHITE if not line.startswith("  ") else (200, 200, 200)
            self._blit_centered(self._font_body, line, color, y=y)
            y += self._body_line_h

        self._blit_centered(self._font_prompt, _PROMPT, config.GREEN, y=630)

    def _draw_scene(self) -> None:
        if self._surprise is not None and self._sp_show > 0:
            self.screen.blit(self._surprise, self._surprise.get_rect(center=self._sp_pos))
        for runner in self._runners:
            runner.draw(self.screen)
        if self._butterfly is not None and self._bf_active:
            y = self._bf_y + math.sin(self._bf_phase) * 22
            self.screen.blit(self._butterfly, self._butterfly.get_rect(center=(int(self._bf_x), int(y))))

    # ------------------------------------------------------------------
    def _blit_centered(
        self, font: pygame.font.Font, text: str, color: tuple, y: int
    ) -> None:
        surf = font.render(text, True, color)
        rect = surf.get_rect(centerx=config.SCREEN_WIDTH // 2, top=y)
        self.screen.blit(surf, rect)
