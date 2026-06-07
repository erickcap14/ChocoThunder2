"""App — initializes pygame and runs the main game loop.

Each frame the loop:
  1. Calls write_state(...)       — publish current state for the MCP server
  2. Calls poll_mcp_command(...)  — apply any command the MCP server queued
  3. Detects state changes        — swaps active screen
  4. Dispatches events, updates, draws

The MCP harness (steps 1–2) is a desktop dev/test sidecar: it needs a second
local process and a shared filesystem, neither of which exist in the browser
WASM sandbox. So those steps are gated behind ``_mcp_enabled`` and skipped under
Emscripten. The desktop path (``run``) and the WASM path (``run_async``) share
the same per-frame body in ``_tick``.
"""

from __future__ import annotations

import sys

import pygame

from game import config
from game.audio import AudioManager
from game.state_machine import GameState, StateMachine


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

        # MCP file-IPC only works on desktop CPython; the browser WASM sandbox
        # has no sidecar process or shared filesystem.
        self._mcp_enabled = sys.platform != "emscripten"

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
    def _tick(self, dt: float) -> bool:
        """Advance one frame. Returns False when the game should stop.

        Shared by the desktop (``run``) and WASM (``run_async``) loops.
        """
        if self._mcp_enabled:
            from main import poll_mcp_command  # desktop-only; pulls in mcp_server
            from mcp_server.state_bridge import write_state

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

        running = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif self._active_screen is not None:
                self._active_screen.handle_event(event)

        if self._active_screen is not None:
            self._active_screen.update(dt)
            self._active_screen.draw()

        pygame.display.flip()
        return running

    # ------------------------------------------------------------------
    def run(self) -> None:
        """Desktop entry: synchronous loop with the MCP harness active."""
        running = True
        while running:
            dt = self.clock.tick(config.FPS) / 1000.0
            running = self._tick(dt)

        from mcp_server.state_bridge import write_state
        write_state(self.sm.state.name, running=False, score=0, level=1,
                    music_on=self.audio.music_on, sfx_on=self.audio.sfx_on)
        pygame.quit()

    # ------------------------------------------------------------------
    async def run_async(self) -> None:
        """WASM/browser entry (pygbag): async loop that yields each frame.

        pygbag runs CPython-on-WASM in the browser's single thread, so the loop
        must hand control back with ``await asyncio.sleep(0)`` every frame. MCP
        is disabled here (see ``_mcp_enabled``).
        """
        import asyncio

        running = True
        while running:
            dt = self.clock.tick(config.FPS) / 1000.0
            running = self._tick(dt)
            await asyncio.sleep(0)

        pygame.quit()
