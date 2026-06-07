"""ScoreboardScreen — name-entry then top-10 high-score display.

Two phases:
  ENTRY  (_submitted=False): player types their name and presses ENTER.
  VIEW   (_submitted=True):  shows the top-10 table; ENTER/SPACE → START.
"""

from __future__ import annotations

import pygame
from game import config, fonts, scores
from game.state_machine import GameState


class ScoreboardScreen:
    def __init__(self, screen: pygame.Surface, state_machine, audio, score: int):
        self.screen = screen
        self.sm = state_machine
        self.audio = audio
        self.score = score
        self.level = 1  # state bridge compatibility

        self._name: str = ""
        self._submitted: bool = False
        self._entries: list[tuple[str, int]] = scores.load_scores()
        self._setup_fonts()

    # ------------------------------------------------------------------
    def _setup_fonts(self) -> None:
        self._font_title  = fonts.load(60)
        self._font_name   = fonts.load(48)
        self._font_row    = fonts.load(36)
        self._font_prompt = fonts.load(36)

    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if not self._submitted:
            if event.key == pygame.K_RETURN and self._name.strip():
                self._entries = scores.add_score(self._name.strip(), self.score)
                self._submitted = True
            elif event.key == pygame.K_BACKSPACE:
                self._name = self._name[:-1]
            elif event.unicode and event.unicode.isprintable() and len(self._name) < 20:
                self._name += event.unicode
        else:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.sm.force_state(GameState.START)

    def update(self, dt: float) -> None:  # no-op
        pass

    def draw(self) -> None:
        self.screen.fill(config.DARK_GREY)
        if self._submitted:
            self._draw_view()
        else:
            self._draw_entry()

    # ------------------------------------------------------------------  entry phase
    def _draw_entry(self) -> None:
        cx = config.SCREEN_WIDTH // 2
        cy = config.SCREEN_HEIGHT // 2

        # Title
        fonts.blit_outlined(self.screen, self._font_title, "Enter Your Name:", y=160)

        # Name box
        name_display = self._name if self._name else " "
        name_surf = self._font_name.render(name_display, True, config.WHITE)
        name_rect = name_surf.get_rect(centerx=cx, centery=cy - 20)
        box_padding = 14
        box_rect = pygame.Rect(
            name_rect.left - box_padding,
            name_rect.top - box_padding,
            name_rect.width + box_padding * 2,
            name_rect.height + box_padding * 2,
        )
        pygame.draw.rect(self.screen, config.BLACK, box_rect, border_radius=6)
        pygame.draw.rect(self.screen, config.WHITE, box_rect, width=2, border_radius=6)
        self.screen.blit(name_surf, name_rect)

        # Score readout
        self._blit_centered(
            self._font_row,
            f"Score: {self.score}",
            config.WHITE,
            y=cy + 60,
        )

        # Prompt
        self._blit_centered(
            self._font_prompt,
            "Press Enter to submit",
            config.GREEN,
            y=config.SCREEN_HEIGHT - 70,
        )

    # ------------------------------------------------------------------  view phase
    def _draw_view(self) -> None:
        # Title
        fonts.blit_outlined(self.screen, self._font_title, "HIGH SCORES", y=60)

        # Table header
        col_rank  = config.SCREEN_WIDTH // 2 - 260
        col_name  = config.SCREEN_WIDTH // 2 - 120
        col_score = config.SCREEN_WIDTH // 2 + 200

        row_start = 150
        row_gap   = 44

        for i, (entry_name, entry_score) in enumerate(self._entries):
            y = row_start + i * row_gap
            color = config.WHITE if i % 2 == 0 else (200, 200, 200)

            rank_surf  = self._font_row.render(f"{i + 1}.", True, color)
            name_surf  = self._font_row.render(entry_name, True, color)
            score_surf = self._font_row.render(str(entry_score), True, color)

            self.screen.blit(rank_surf,  rank_surf.get_rect(right=col_rank + 30, top=y))
            self.screen.blit(name_surf,  name_surf.get_rect(left=col_name, top=y))
            self.screen.blit(score_surf, score_surf.get_rect(right=col_score, top=y))

        # Prompt
        self._blit_centered(
            self._font_prompt,
            "Press Enter to Play Again",
            config.GREEN,
            y=config.SCREEN_HEIGHT - 70,
        )

    # ------------------------------------------------------------------
    def _blit_centered(
        self, font: pygame.font.Font, text: str, color: tuple, y: int
    ) -> None:
        surf = font.render(text, True, color)
        rect = surf.get_rect(centerx=config.SCREEN_WIDTH // 2, top=y)
        self.screen.blit(surf, rect)
