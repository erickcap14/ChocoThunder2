"""EndScreen — win or lose image with final score and scoreboard prompt.

Ground-truth spec (PRD):
  - Win image (win.jpg) or lose image (lose.jpg) scaled to full screen
  - Semi-transparent dark overlay panel
  - "You Win!" / "Game Over"  — large font, BROWN
  - "Final Score: {score}"     — medium font, WHITE
  - "Thanks for playing!" / "Better luck next time!" — body font, WHITE
  - "Press Enter to view the Scoreboard" — GREEN, near bottom
  - ENTER or SPACE → transitions to SCOREBOARD
"""

from __future__ import annotations

import pygame

from game import assets, config, fonts
from game.state_machine import GameState


class EndScreen:
    def __init__(
        self,
        screen: pygame.Surface,
        state_machine,
        audio,
        score: int,
        win: bool,
    ):
        self.screen = screen
        self.sm = state_machine
        self.audio = audio
        self.score = score
        self.win = win
        self.level = 1  # state bridge compatibility — App reads this

        self._setup_bg()
        self._setup_fonts()
        self._setup_overlay()

    # ------------------------------------------------------------------
    def _setup_bg(self) -> None:
        image_name = "win.jpg" if self.win else "lose.jpg"
        path = assets.endscreen(image_name)
        self._bg = assets.load_image(
            str(path), (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        )

    def _setup_fonts(self) -> None:
        self._font_large  = fonts.load(80)
        self._font_medium = fonts.load(52)
        self._font_body   = fonts.load(36)
        self._font_prompt = fonts.load(40)

    def _setup_overlay(self) -> None:
        w, h = config.SCREEN_WIDTH, config.SCREEN_HEIGHT
        self._overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        self._overlay.fill((20, 20, 20, 200))

    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in (
            pygame.K_RETURN,
            pygame.K_SPACE,
        ):
            self.sm.force_state(GameState.SCOREBOARD)

    def update(self, dt: float) -> None:  # no-op
        pass

    def draw(self) -> None:
        # Background image (scaled to full screen).
        self.screen.blit(self._bg, (0, 0))

        # Semi-transparent dark overlay.
        self.screen.blit(self._overlay, (0, 0))

        # Headline.
        headline = "You Win!" if self.win else "Game Over"
        self._blit_centered(self._font_large, headline, config.BROWN, y=180)

        # Final score.
        self._blit_centered(
            self._font_medium,
            f"Final Score: {self.score}",
            config.WHITE,
            y=290,
        )

        # Flavour line.
        flavour = "Thanks for playing!" if self.win else "Better luck next time!"
        self._blit_centered(self._font_body, flavour, config.WHITE, y=380)

        # Scoreboard prompt near the bottom.
        self._blit_centered(
            self._font_prompt,
            "Press Enter to view the Scoreboard",
            config.GREEN,
            y=630,
        )

    def _blit_centered(
        self, font: pygame.font.Font, text: str, color: tuple, y: int
    ) -> None:
        surf = font.render(text, True, color)
        rect = surf.get_rect(centerx=config.SCREEN_WIDTH // 2, top=y)
        self.screen.blit(surf, rect)
