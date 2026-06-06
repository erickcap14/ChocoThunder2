"""AudioManager — per-level music, SFX, and toggle state.

Safe to construct when the mixer is unavailable (headless/dummy driver):
every public method silently no-ops if ``_mixer_ok`` is False.
"""

from __future__ import annotations

import pygame

from game import assets


class AudioManager:
    def __init__(self):
        self.music_on: bool = True
        self.sfx_on: bool = True
        self._mixer_ok: bool = pygame.mixer.get_init() is not None
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        if self._mixer_ok:
            self._preload_sfx()

    # ------------------------------------------------------------------
    def _preload_sfx(self) -> None:
        for name, filename in [
            ("shotgun",        "12-Gauge-Pump-Action-Shotgun.mp3"),
            ("lose_life",      "MarioLoseLife.mp3"),
            ("powerup_fart",   "powerupFart.mp3"),
            ("unpowered_fart", "unpoweredFart.mp3"),
        ]:
            path = assets.sfx_path(filename)
            if path.exists():
                try:
                    self._sounds[name] = assets.load_sound(path)
                except pygame.error:
                    pass

    # ------------------------------------------------------------------
    def play_music(self, filename: str, loops: int = -1) -> None:
        """Load and loop a music track. Does nothing if music is off or mixer absent."""
        if not self._mixer_ok or not self.music_on:
            return
        path = assets.music_path(filename)
        if not path.exists():
            return
        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.play(loops)
        except pygame.error:
            pass

    def stop_music(self) -> None:
        if not self._mixer_ok:
            return
        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass

    def play_sfx(self, name: str) -> None:
        """Play a named SFX. Silently skips if sfx is off or sound not loaded."""
        if not self._mixer_ok or not self.sfx_on:
            return
        sound = self._sounds.get(name)
        if sound is not None:
            try:
                sound.play()
            except pygame.error:
                pass

    def toggle_music(self) -> None:
        self.music_on = not self.music_on
        if not self._mixer_ok:
            return
        try:
            if self.music_on:
                pygame.mixer.music.unpause()
            else:
                pygame.mixer.music.pause()
        except pygame.error:
            pass

    def toggle_sfx(self) -> None:
        self.sfx_on = not self.sfx_on
