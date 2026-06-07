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

        self._active_screen = None
        self._active_screen = self._make_screen(self.sm.state)
        self._last_state = self.sm.state

        # UI test mode (activated by App.enable_test_mode() or --test flag).
        self._test_mode: bool = False
        self._test_index: int = 0
        self._test_sequence: list = []
        self._test_labels: list[str] = []
        self._font_test: pygame.font.Font | None = None

    # ------------------------------------------------------------------
    def _make_screen(self, state: GameState):
        prev = self._active_screen

        if state == GameState.START:
            from game.screens.start import StartScreen
            return StartScreen(self.screen, self.sm, self.audio)

        if state == GameState.PRELEVEL:
            from game.screens.prelevel import PreLevelScreen
            from game.screens.transition import TransitionScreen
            if isinstance(prev, TransitionScreen):
                level, score = prev.level + 1, prev.score
            else:
                level = getattr(prev, "level", 1)
                score = getattr(prev, "score", 0)
            return PreLevelScreen(self.screen, self.sm, self.audio, level=level, score=score)

        if state == GameState.RUNNING:
            from game.screens.play import PlayScreen
            from game.screens.prelevel import PreLevelScreen
            ps = PlayScreen(self.screen, self.sm, self.audio)
            try:
                from game.screens.transition import TransitionScreen
                if isinstance(prev, PreLevelScreen):
                    ps.resume(prev.level, prev.score)
                elif isinstance(prev, TransitionScreen):
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
    # UI test mode
    # ------------------------------------------------------------------

    def enable_test_mode(self) -> None:
        """Switch into UI-walkthrough mode. Arrow keys cycle every screen."""
        from game import fonts as _fonts
        self._test_mode = True
        self._mcp_enabled = False  # disable IPC sidecar during walkthrough
        self._test_sequence, self._test_labels = self._build_test_sequence()
        self._test_index = 0
        self._font_test = _fonts.load(22)
        self._active_screen = self._test_sequence[0]()

    def _build_test_sequence(self) -> tuple:
        from game.screens.start import StartScreen
        from game.screens.prelevel import PreLevelScreen
        from game.screens.play import PlayScreen
        from game.screens.transition import TransitionScreen
        from game.screens.end import EndScreen
        from game.screens.scoreboard import ScoreboardScreen
        from game.levels import LEVELS

        S, sm, au = self.screen, self.sm, self.audio
        seq: list = []
        labels: list[str] = []

        seq.append(lambda: StartScreen(S, sm, au))
        labels.append("Start Screen")

        score = 0
        for i, spec in enumerate(LEVELS):
            lvl = i + 1
            lvl_score = score

            seq.append(lambda l=lvl, s=lvl_score: PreLevelScreen(S, sm, au, level=l, score=s))
            labels.append(f"Level {lvl} — Pre-Level")

            def _play(l=lvl, s=lvl_score):
                ps = PlayScreen(S, sm, au, test_mode=True)
                ps.resume(l, s)
                return ps
            seq.append(_play)
            labels.append(f"Level {lvl} — Play")

            score += lvl * 3
            end_score = score
            seq.append(lambda l=lvl, s=end_score: TransitionScreen(S, sm, au, level=l, score=s))
            labels.append(f"Level {lvl} — Transition")

        win_score = score
        seq.append(lambda s=win_score: EndScreen(S, sm, au, score=s, win=True))
        labels.append("End Screen — Win")
        seq.append(lambda: EndScreen(S, sm, au, score=5, win=False))
        labels.append("End Screen — Lose")
        seq.append(lambda s=win_score: ScoreboardScreen(S, sm, au, score=s))
        labels.append("Scoreboard")

        return seq, labels

    def _test_navigate(self, delta: int) -> None:
        new_idx = self._test_index + delta
        if 0 <= new_idx < len(self._test_sequence):
            self.audio.stop_music()
            self._test_index = new_idx
            self._active_screen = self._test_sequence[new_idx]()

    def _draw_test_overlay(self) -> None:
        """Draw navigation arrows and label bar at the bottom of the screen."""
        assert self._font_test is not None
        W, H = config.SCREEN_WIDTH, config.SCREEN_HEIGHT
        bar_h = 46
        bar_y = H - bar_h

        # Darkened bottom bar
        bar = pygame.Surface((W, bar_h), pygame.SRCALPHA)
        bar.fill((10, 10, 10, 210))
        self.screen.blit(bar, (0, bar_y))

        # Label: "TEST MODE  |  3 / 16 — Level 1: Play"
        n = len(self._test_sequence)
        label = self._test_labels[self._test_index]
        text = f"TEST MODE  |  {self._test_index + 1} / {n}:  {label}"
        surf = self._font_test.render(text, True, (255, 220, 60))
        self.screen.blit(surf, surf.get_rect(center=(W // 2, bar_y + bar_h // 2)))

        # Arrow indicators (mid-screen vertically, inset 12px from edges)
        mid_y = (bar_y) // 2
        arrow_font = self._font_test

        if self._test_index > 0:
            arrow_bg = pygame.Surface((54, 54), pygame.SRCALPHA)
            arrow_bg.fill((20, 20, 20, 180))
            self.screen.blit(arrow_bg, (8, mid_y - 27))
            a = arrow_font.render("◀", True, config.WHITE)
            self.screen.blit(a, a.get_rect(center=(35, mid_y)))

        if self._test_index < len(self._test_sequence) - 1:
            arrow_bg = pygame.Surface((54, 54), pygame.SRCALPHA)
            arrow_bg.fill((20, 20, 20, 180))
            self.screen.blit(arrow_bg, (W - 62, mid_y - 27))
            a = arrow_font.render("▶", True, config.WHITE)
            self.screen.blit(a, a.get_rect(center=(W - 35, mid_y)))

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

        # In test mode: block screen transitions, handle arrow navigation instead.
        if not self._test_mode and self.sm.state is not self._last_state:
            self._active_screen = self._make_screen(self.sm.state)
            self._last_state = self.sm.state

        running = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif self._test_mode and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    self._test_navigate(1)
                elif event.key == pygame.K_LEFT:
                    self._test_navigate(-1)
                elif self._active_screen is not None:
                    self._active_screen.handle_event(event)
            elif self._active_screen is not None:
                self._active_screen.handle_event(event)

        if self._active_screen is not None:
            self._active_screen.update(dt)
            self._active_screen.draw()

        if self._test_mode:
            self._draw_test_overlay()

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
