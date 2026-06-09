"""PreLevelScreen — black intro card shown before each level begins.

Displays the upcoming level name, a punny intro teaser, and a prompt to
continue.  On Enter → GameState.RUNNING (App builds the PlayScreen).
"""

from __future__ import annotations

import pygame

from game import config, fonts
from game.levels import LEVELS
from game.screens.chrome import Chrome
from game.screens.transition import draw_backdrop
from game.state_machine import GameState

_PROMPT = "Press Enter to Begin"


class PreLevelScreen:
    def __init__(
        self,
        screen: pygame.Surface,
        state_machine,
        audio,
        level: int,
        score: int,
    ) -> None:
        self.screen = screen
        self.sm = state_machine
        self.audio = audio
        self.level = level    # the level about to start
        self.score = score    # accumulated score carried in

        self._setup_fonts()

        # This level's music starts here on the transition card and plays through
        # gameplay and the completion card. play_music is idempotent, so when the
        # track is already going (e.g. Thunderstruck from the Start screen for
        # Level 1) it continues seamlessly instead of restarting. An empty track
        # (a level with no song yet) stops music for a silent level.
        idx = max(0, min(self.level - 1, len(LEVELS) - 1))
        self.audio.play_music(LEVELS[idx].music)

        self._chrome = Chrome(self.screen, self.audio, self.sm, show_return=True)

    # ------------------------------------------------------------------
    def _setup_fonts(self) -> None:
        self._font_title  = fonts.load(72)
        self._font_sub    = fonts.load(48)
        self._font_score  = fonts.load(36)
        self._font_prompt = fonts.load(40)

    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        if self._chrome.handle_event(event):
            return
        if self._chrome.is_blocking():
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.sm.force_state(GameState.RUNNING)

    def update(self, dt: float) -> None:  # noqa: ARG002
        pass

    def draw(self) -> None:
        draw_backdrop(self.screen, self.level)

        idx = max(0, min(self.level - 1, len(LEVELS) - 1))
        spec = LEVELS[idx]

        fonts.blit_outlined(
            self.screen, self._font_title, spec.name, y=220
        )
        self._blit_centered(
            self._font_sub,
            spec.intro_subtitle,
            config.WHITE,
            y=310,
        )
        if self.score > 0:
            self._blit_centered(
                self._font_score,
                f"Score so far: {self.score}",
                config.WHITE,
                y=385,
            )
        self._blit_centered(
            self._font_prompt,
            _PROMPT,
            config.GREEN,
            y=630,
        )

        self._chrome.draw()

    # ------------------------------------------------------------------
    def _blit_centered(
        self, font: pygame.font.Font, text: str, color: tuple, y: int
    ) -> None:
        surf = font.render(text, True, color)
        rect = surf.get_rect(centerx=config.SCREEN_WIDTH // 2, top=y)
        self.screen.blit(surf, rect)
