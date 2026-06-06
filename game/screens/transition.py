"""TransitionScreen — black card shown between levels.

Displays the just-completed level name, a punny subtitle, the accumulated
score, and a prompt to continue.  On Enter:
  - level < _MAX_LEVELS  → GameState.RUNNING  (App builds next PlayScreen)
  - level >= _MAX_LEVELS → GameState.END       (App builds EndScreen with win=True)
"""

from __future__ import annotations

import pygame

from game import config
from game.levels import LEVELS
from game.state_machine import GameState

_PROMPT = "Press Enter to Continue"


class TransitionScreen:
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
        self.level = level    # the just-completed level number
        self.score = score    # accumulated score so far

        self._setup_fonts()

    # ------------------------------------------------------------------
    def _setup_fonts(self) -> None:
        self._font_title  = pygame.font.Font(None, 72)
        self._font_sub    = pygame.font.Font(None, 48)
        self._font_score  = pygame.font.Font(None, 36)
        self._font_prompt = pygame.font.Font(None, 40)

    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            if self.level >= len(LEVELS):
                self.sm.force_state(GameState.END)
            else:
                self.sm.force_state(GameState.RUNNING)

    def update(self, dt: float) -> None:  # noqa: ARG002
        pass

    def draw(self) -> None:
        self.screen.fill(config.BLACK)

        subtitle = LEVELS[self.level - 1].transition_subtitle if 1 <= self.level <= len(LEVELS) else ""

        self._blit_centered(
            self._font_title,
            f"Level {self.level} Complete!",
            config.BROWN,
            y=220,
        )
        self._blit_centered(
            self._font_sub,
            subtitle,
            config.WHITE,
            y=310,
        )
        self._blit_centered(
            self._font_score,
            f"Score: {self.score}",
            config.WHITE,
            y=385,
        )
        self._blit_centered(
            self._font_prompt,
            _PROMPT,
            config.GREEN,
            y=630,
        )

    # ------------------------------------------------------------------
    def _blit_centered(
        self, font: pygame.font.Font, text: str, color: tuple, y: int
    ) -> None:
        surf = font.render(text, True, color)
        rect = surf.get_rect(centerx=config.SCREEN_WIDTH // 2, top=y)
        self.screen.blit(surf, rect)
