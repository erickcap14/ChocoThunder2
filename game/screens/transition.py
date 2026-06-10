"""TransitionScreen — black card shown between levels.

Displays the just-completed level name, a punny subtitle, the accumulated
score, and a prompt to continue.  On Enter:
  - level < _MAX_LEVELS  → GameState.RUNNING  (App builds next PlayScreen)
  - level >= _MAX_LEVELS → GameState.END       (App builds EndScreen with win=True)
"""

from __future__ import annotations

import pygame

from game import assets, config, fonts
from game.levels import LEVELS
from game.screens.chrome import Chrome
from game.state_machine import GameState

_PROMPT = "Press Enter to Continue"
_PROMPT_TOUCH = "Tap to Continue"


def draw_backdrop(screen: pygame.Surface, level: int) -> None:
    """Paint the per-level themed transition backdrop (ART_SET=pixellab) behind the
    card text, falling back to a plain black card when no backdrop art exists."""
    lvl = max(1, min(level, len(LEVELS)))
    path = assets.transition_image(f"level{lvl}.png")
    if path.exists():
        screen.blit(
            assets.load_image(str(path), (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)),
            (0, 0),
        )
    else:
        screen.fill(config.BLACK)


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

        # Keep the just-completed level's music going on the complete card.
        # Idempotent, so it continues seamlessly from gameplay. For the final
        # level this is the track (Angel) that carries on into the win screen and
        # the leaderboard, since neither of those touches the music.
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
        advance = event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN
        if config.touch_ui_enabled() and event.type == pygame.MOUSEBUTTONDOWN:
            advance = True  # touch layer: a tap is the Enter gesture
        if advance:
            if self.level >= len(LEVELS):
                self.sm.force_state(GameState.END)
            else:
                self.sm.force_state(GameState.PRELEVEL)

    def update(self, dt: float) -> None:  # noqa: ARG002
        pass

    def draw(self) -> None:
        draw_backdrop(self.screen, self.level)

        subtitle = LEVELS[self.level - 1].transition_subtitle if 1 <= self.level <= len(LEVELS) else ""

        fonts.blit_outlined(
            self.screen, self._font_title, f"Level {self.level} Complete!", y=220
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
            _PROMPT_TOUCH if config.touch_ui_enabled() else _PROMPT,
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
