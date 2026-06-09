"""Chrome — the persistent on-screen controls shared by every screen.

Two pieces of always-available UI, composed by each screen:

  * Volume control (all screens): a "VOL" button in the bottom-right corner that
    opens a small panel with draggable Music and SFX sliders. Levels live on the
    shared AudioManager, so a change made on one screen persists to every other.

  * Return-to-Start (gameplay → leaderboard only, via ``show_return``): a button
    in the bottom-left corner that opens a Yes/No confirm; "Yes" abandons the run
    and jumps to the start screen.

Usage from a host screen::

    self._chrome = Chrome(self.screen, self.audio, self.sm, show_return=True)
    # in handle_event:  if self._chrome.handle_event(event): return
    # in update:        if self._chrome.is_blocking(): <freeze game logic>
    # at end of draw:   self._chrome.draw()

``handle_event`` returns True when it consumed the event so the host skips its own
handling (e.g. clicking the VOL button must not also move Sally). ``is_blocking``
is True while a modal — the volume panel or the quit confirm — is open.
"""

from __future__ import annotations

import pygame

from game import config, fonts
from game.state_machine import GameState

_TOP = 5                     # y of the top button row (centered in the 50px HUD bar)
_BTN_H = 40
_GEAR_W = 64                 # "VOL" button
_RETURN_W = 112             # "Return" button (compact to fit left of the timer)
_TIMER_RESERVE = 258         # px kept clear at the right edge for the play-screen timer
_PANEL_W, _PANEL_H = 280, 132
_TRACK_W = 150
_KNOB_R = 9


class Chrome:
    def __init__(self, screen: pygame.Surface, audio, state_machine, *, show_return: bool):
        self.screen = screen
        self.audio = audio
        self.sm = state_machine
        self.show_return = show_return

        self._panel_open = False
        self._confirm_open = False
        self._dragging: str | None = None  # "music" | "sfx" | None

        self._font_btn = fonts.load(18)
        self._font_panel = fonts.load(22)
        self._font_confirm = fonts.load(28)

        W, H = config.SCREEN_WIDTH, config.SCREEN_HEIGHT

        # Top-right, just left of the (play-screen) timer:  [ Return ] [ VOL ]
        gear_right = W - _TIMER_RESERVE
        self._gear = pygame.Rect(gear_right - _GEAR_W, _TOP, _GEAR_W, _BTN_H)
        self._return = pygame.Rect(self._gear.left - 10 - _RETURN_W, _TOP, _RETURN_W, _BTN_H)

        # Volume panel drops down from below the VOL button, right-aligned to it.
        self._panel = pygame.Rect(
            self._gear.right - _PANEL_W, self._gear.bottom + 10, _PANEL_W, _PANEL_H
        )
        track_x = self._panel.left + 92
        self._music_track = pygame.Rect(track_x, self._panel.top + 52, _TRACK_W, 6)
        self._sfx_track = pygame.Rect(track_x, self._panel.top + 96, _TRACK_W, 6)

        # Centered confirm dialog.
        cw, ch = 440, 190
        self._confirm = pygame.Rect((W - cw) // 2, (H - ch) // 2, cw, ch)
        by = self._confirm.bottom - 64
        self._yes = pygame.Rect(self._confirm.centerx - 150, by, 130, 44)
        self._no = pygame.Rect(self._confirm.centerx + 20, by, 130, 44)

    # ------------------------------------------------------------------
    def is_blocking(self) -> bool:
        """True while a modal (volume panel or quit-confirm) is open; the host
        screen should freeze gameplay behind it."""
        return self._panel_open or self._confirm_open

    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Process the chrome's UI. Returns True if the event was consumed."""
        # Confirm dialog is fully modal while open.
        if self._confirm_open:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self._yes.collidepoint(event.pos):
                    self._confirm_open = False
                    self.sm.force_state(GameState.START)
                elif self._no.collidepoint(event.pos):
                    self._confirm_open = False
                return True
            if event.type in (pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                return True
            return False

        if self._panel_open:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self._slider_hit(self._music_track, event.pos):
                    self._dragging = "music"
                    self._set_from_pos(event.pos)
                elif self._slider_hit(self._sfx_track, event.pos):
                    self._dragging = "sfx"
                    self._set_from_pos(event.pos)
                elif not self._panel.collidepoint(event.pos):
                    self._panel_open = False  # click-away closes
                return True
            if event.type == pygame.MOUSEMOTION and self._dragging:
                self._set_from_pos(event.pos)
                return True
            if event.type == pygame.MOUSEBUTTONUP:
                self._dragging = None
                return True
            # Swallow other mouse events over the panel so they don't fall through.
            if event.type in (pygame.MOUSEMOTION,) and self._panel.collidepoint(event.pos):
                return True
            return False

        # Nothing open: the two corner buttons.
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self._gear.collidepoint(event.pos):
                self._panel_open = True
                return True
            if self.show_return and self._return.collidepoint(event.pos):
                self._confirm_open = True
                return True
        return False

    # ------------------------------------------------------------------
    def _slider_hit(self, track: pygame.Rect, pos) -> bool:
        return track.inflate(_KNOB_R * 2, 24).collidepoint(pos)

    def _set_from_pos(self, pos) -> None:
        track = self._music_track if self._dragging == "music" else self._sfx_track
        value = (pos[0] - track.left) / track.width
        value = max(0.0, min(1.0, value))
        if self._dragging == "music":
            self.audio.set_music_volume(value)
        else:
            self.audio.set_sfx_volume(value)

    # ------------------------------------------------------------------
    def draw(self) -> None:
        self._draw_button(self._gear, "VOL")
        if self.show_return:
            self._draw_button(self._return, "Return")
        if self._panel_open:
            self._draw_panel()
        if self._confirm_open:
            self._draw_confirm()

    def _draw_button(self, rect: pygame.Rect, label: str) -> None:
        pygame.draw.rect(self.screen, (50, 50, 120), rect, border_radius=6)
        pygame.draw.rect(self.screen, config.WHITE, rect, width=1, border_radius=6)
        surf = self._font_btn.render(label, True, config.WHITE)
        self.screen.blit(surf, surf.get_rect(center=rect.center))

    def _draw_panel(self) -> None:
        panel = pygame.Surface(self._panel.size, pygame.SRCALPHA)
        panel.fill((15, 15, 35, 235))
        self.screen.blit(panel, self._panel.topleft)
        pygame.draw.rect(self.screen, config.WHITE, self._panel, width=2, border_radius=8)

        title = self._font_panel.render("Volume", True, (255, 220, 60))
        self.screen.blit(title, (self._panel.left + 16, self._panel.top + 12))

        self._draw_slider("Music", self._music_track, self.audio.music_volume)
        self._draw_slider("SFX", self._sfx_track, self.audio.sfx_volume)

    def _draw_slider(self, label: str, track: pygame.Rect, value: float) -> None:
        lbl = self._font_panel.render(label, True, config.WHITE)
        self.screen.blit(lbl, lbl.get_rect(midright=(track.left - 12, track.centery)))
        pygame.draw.rect(self.screen, (90, 90, 110), track, border_radius=3)
        filled = pygame.Rect(track.left, track.top, int(track.width * value), track.height)
        pygame.draw.rect(self.screen, config.GREEN, filled, border_radius=3)
        knob_x = track.left + int(track.width * value)
        pygame.draw.circle(self.screen, config.WHITE, (knob_x, track.centery), _KNOB_R)
        pct = self._font_btn.render(f"{round(value * 100):d}%", True, config.WHITE)
        self.screen.blit(pct, pct.get_rect(midleft=(track.right + 12, track.centery)))

    def _draw_confirm(self) -> None:
        scrim = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        scrim.fill((0, 0, 0, 150))
        self.screen.blit(scrim, (0, 0))

        box = pygame.Surface(self._confirm.size, pygame.SRCALPHA)
        box.fill((20, 20, 40, 245))
        self.screen.blit(box, self._confirm.topleft)
        pygame.draw.rect(self.screen, config.WHITE, self._confirm, width=2, border_radius=10)

        msg = self._font_confirm.render("Return to Start?", True, config.WHITE)
        self.screen.blit(msg, msg.get_rect(centerx=self._confirm.centerx, top=self._confirm.top + 28))
        sub = self._font_btn.render("Your current run will be lost.", True, (210, 210, 210))
        self.screen.blit(sub, sub.get_rect(centerx=self._confirm.centerx, top=self._confirm.top + 70))

        self._draw_dialog_btn(self._yes, "Yes", (150, 40, 40))
        self._draw_dialog_btn(self._no, "No", (50, 50, 120))

    def _draw_dialog_btn(self, rect: pygame.Rect, label: str, color) -> None:
        pygame.draw.rect(self.screen, color, rect, border_radius=6)
        pygame.draw.rect(self.screen, config.WHITE, rect, width=1, border_radius=6)
        surf = self._font_panel.render(label, True, config.WHITE)
        self.screen.blit(surf, surf.get_rect(center=rect.center))
