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
from game.screens.chrome import Chrome
from game.settings import settings
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
    "  Mouse click      —  send Sally to that spot",
    "  Click + drag     —  Sally follows the cursor",
    "  Arrow keys       —  steer Sally directly",
    "  Space Bar        —  leave a chocolate surprise",
    "  Eat a cake       —  become invincible (bonus!)",
)
_DIFFICULTY_CAPTION = "Easy: tenants can't catch you    Hard: caught = game over"
_PROMPT = "Press Space Bar to Play"
_PROMPT_TOUCH = "Tap to Play"

# Chase cast, drawn back-to-front; (folder, visible height px, x, run fps). Heights are
# roughly proportional: a small terrier, adult tenants, a looming cartoon T-rex.
_RUNNERS = (
    ("trex",  180, 215, 9),
    ("char3", 150, 380, 11),
    ("char2", 150, 520, 10),
    ("char1", 150, 660, 11),
    ("sally",  74, 800, 13),
)
_FEET_Y = config.SCREEN_HEIGHT - 22


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

        self._chrome = Chrome(self.screen, self.audio, self.sm, show_return=False)

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
        # Surprise: a googly poop sitting on the grass that scrolls past with the
        # background (so it reads as a real object in the world), then respawns.
        self._sp_active = False
        self._sp_timer = 3.0
        self._sp_x = 0.0

    @staticmethod
    def _crop_scale(surf: pygame.Surface, bbox: pygame.Rect, height: int) -> pygame.Surface:
        cropped = surf.subsurface(bbox).copy()
        w = max(1, round(bbox.width * height / bbox.height))
        return pygame.transform.scale(cropped, (w, height))

    @classmethod
    def _load_runner(cls, folder, height: int) -> list[pygame.Surface] | None:
        try:
            frames = assets.load_frames(folder)
        except FileNotFoundError:
            return None
        # Scale by *visible* height (transparent padding cropped); a shared union bbox keeps
        # the feet planted across the run cycle so the character doesn't bob vertically.
        bbox = None
        for f in frames:
            r = f.get_bounding_rect()
            bbox = r if bbox is None else bbox.union(r)
        if bbox is None or bbox.height == 0:
            bbox = frames[0].get_rect()
        return [cls._crop_scale(f, bbox, height) for f in frames]

    @classmethod
    def _load_sprite(cls, path, height: int) -> pygame.Surface | None:
        if not path.exists():
            return None
        img = assets.load_image(str(path))
        bbox = img.get_bounding_rect() or img.get_rect()
        return cls._crop_scale(img, bbox, height)

    def _setup_fonts(self) -> None:
        self._font_title  = fonts.load(72)
        self._font_sub    = fonts.load(48)
        self._font_body   = fonts.load(26)
        self._font_prompt = fonts.load(40)

    def _setup_overlay(self) -> None:
        w = 960
        self._body_line_h = self._font_body.get_linesize()
        self._caption_font = self._font_body
        pad = 18          # top/bottom inner padding
        gap = 10          # blurb -> controls gap
        btn_gap = 16      # controls -> difficulty buttons gap
        cap_gap = 10      # buttons -> caption gap
        self._btn_h = 44

        text_block = self._body_line_h * (len(_BLURB) + len(_CONTROLS)) + gap
        cap_h = self._caption_font.get_linesize()
        h = pad + text_block + btn_gap + self._btn_h + cap_gap + cap_h + pad

        self._overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        self._overlay.fill((20, 20, 20, 190))
        # Anchor below the titles so the panel never overlaps the subtitle, and so
        # the "Press Space" prompt below it still clears the bottom of the screen.
        self._overlay_rect = self._overlay.get_rect(midtop=(config.SCREEN_WIDTH // 2, 206))

        self._text_top = self._overlay_rect.top + pad
        controls_bottom = (
            self._text_top + self._body_line_h * len(_BLURB) + gap
            + self._body_line_h * len(_CONTROLS)
        )

        # Easy / Hard buttons, centred side by side below the controls text.
        btn_w, btn_y = 200, controls_bottom + btn_gap
        cx = self._overlay_rect.centerx
        self._easy_btn = pygame.Rect(cx - btn_w - 14, btn_y, btn_w, self._btn_h)
        self._hard_btn = pygame.Rect(cx + 14, btn_y, btn_w, self._btn_h)
        self._caption_y = btn_y + self._btn_h + cap_gap

        # Prompt sits just below the overlay panel.
        self._prompt_y = self._overlay_rect.bottom + 26

    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        if self._chrome.handle_event(event):
            return
        if self._chrome.is_blocking():
            return

        start = event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self._easy_btn.collidepoint(event.pos):
                settings.hard_mode = False
                return
            if self._hard_btn.collidepoint(event.pos):
                settings.hard_mode = True
                return
            if config.touch_ui_enabled():
                start = True  # touch layer: a tap off the buttons starts the game

        if start:
            # Leave Thunderstruck playing: it's Level 1's track too, so it carries
            # seamlessly from here through Level 1's transition, play, and complete.
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
        if self._sp_active:
            self._sp_x -= _SCROLL_SPEED * dt  # scroll with the background
            if self._sp_x < -60:
                self._sp_active = False
                self._sp_timer = random.uniform(3.5, 7.0)
        else:
            self._sp_timer -= dt
            if self._sp_timer <= 0:
                self._sp_active = True
                self._sp_x = config.SCREEN_WIDTH + 40

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
        y += 14
        for line in _CONTROLS:
            color = config.WHITE if not line.startswith("  ") else (200, 200, 200)
            self._blit_centered(self._font_body, line, color, y=y)
            y += self._body_line_h

        self._draw_difficulty()

        self._blit_centered(
            self._font_prompt,
            _PROMPT_TOUCH if config.touch_ui_enabled() else _PROMPT,
            config.GREEN,
            y=self._prompt_y,
        )

        self._chrome.draw()

    def _draw_difficulty(self) -> None:
        self._draw_diff_btn(self._easy_btn, "EASY", selected=not settings.hard_mode)
        self._draw_diff_btn(self._hard_btn, "HARD", selected=settings.hard_mode)
        cap = self._caption_font.render(_DIFFICULTY_CAPTION, True, (190, 190, 190))
        self.screen.blit(
            cap, cap.get_rect(centerx=config.SCREEN_WIDTH // 2, top=self._caption_y)
        )

    def _draw_diff_btn(self, rect: pygame.Rect, label: str, *, selected: bool) -> None:
        if selected:
            fill, border, text = (40, 130, 60), config.WHITE, config.WHITE
            border_w = 3
        else:
            fill, border, text = (40, 40, 50), (110, 110, 120), (170, 170, 175)
            border_w = 1
        pygame.draw.rect(self.screen, fill, rect, border_radius=8)
        pygame.draw.rect(self.screen, border, rect, width=border_w, border_radius=8)
        surf = self._font_prompt.render(label, True, text)
        self.screen.blit(surf, surf.get_rect(center=rect.center))

    def _draw_scene(self) -> None:
        if self._surprise is not None and self._sp_active:
            self.screen.blit(
                self._surprise,
                self._surprise.get_rect(midbottom=(int(self._sp_x), _FEET_Y + 4)),
            )
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
