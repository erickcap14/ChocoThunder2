"""App — initializes pygame and runs the main game loop.

Each frame the loop:
  1. Calls write_state(...)       — publish current state for the MCP server
  2. Calls poll_mcp_command(...)  — apply any command the MCP server queued
  3. Detects state changes        — swaps active screen
  4. Dispatches events, updates, draws
"""

from __future__ import annotations

import pygame

from game import config
from game.audio import AudioManager
from game.state_machine import GameState, StateMachine
from main import poll_mcp_command
from mcp_server.state_bridge import write_state


class App:
    def __init__(self):
        pygame.init()
        if pygame.mixer.get_init() is None:
            try:
                pygame.mixer.init()
            except pygame.error:
                pass

        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption(config.CAPTION)
        self.clock = pygame.time.Clock()
        self.sm = StateMachine(GameState.START)
        self.audio = AudioManager()

        self._active_screen = self._make_screen(self.sm.state)
        self._last_state = self.sm.state

    # ------------------------------------------------------------------
    def _make_screen(self, state: GameState):
        prev = self._active_screen

        if state == GameState.START:
            from game.screens.start import StartScreen
            return StartScreen(self.screen, self.sm, self.audio)

        if state == GameState.RUNNING:
            from game.screens.play import PlayScreen
            ps = PlayScreen(self.screen, self.sm, self.audio)
            try:
                from game.screens.transition import TransitionScreen
                if isinstance(prev, TransitionScreen):
                    ps.resume(prev.level + 1, prev.score)
            except ImportError:
                pass
            return ps

        if state == GameState.TRANSITION:
            from game.screens.transition import TransitionScreen
            return TransitionScreen(
                self.screen, self.sm, self.audio,
                level=getattr(prev, "level", 1),
                score=getattr(prev, "score", 0),
            )

        if state == GameState.END:
            from game.screens.end import EndScreen
            try:
                from game.screens.transition import TransitionScreen
                win = isinstance(prev, TransitionScreen)
            except ImportError:
                win = False
            return EndScreen(
                self.screen, self.sm, self.audio,
                score=getattr(prev, "score", 0),
                win=win,
            )

        if state == GameState.SCOREBOARD:
            from game.screens.scoreboard import ScoreboardScreen
            return ScoreboardScreen(
                self.screen, self.sm, self.audio,
                score=getattr(prev, "score", 0),
            )

        return None

    # ------------------------------------------------------------------
    def run(self) -> None:
        running = True
        while running:
            dt = self.clock.tick(config.FPS) / 1000.0

            write_state(
                self.sm.state.name,
                running=True,
                score=getattr(self._active_screen, "score", 0),
                level=getattr(self._active_screen, "level", 1),
                music_on=self.audio.music_on,
                sfx_on=self.audio.sfx_on,
            )
            poll_mcp_command(self.sm, self._active_screen, self.audio)

            if self.sm.state is not self._last_state:
                self._active_screen = self._make_screen(self.sm.state)
                self._last_state = self.sm.state

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif self._active_screen is not None:
                    self._active_screen.handle_event(event)

            if self._active_screen is not None:
                self._active_screen.update(dt)
                self._active_screen.draw()

            pygame.display.flip()

        write_state(self.sm.state.name, running=False, score=0, level=1,
                    music_on=self.audio.music_on, sfx_on=self.audio.sfx_on)
        pygame.quit()
