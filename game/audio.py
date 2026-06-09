"""AudioManager — per-level music, SFX, and toggle state.

Safe to construct when the mixer is unavailable (headless/dummy driver):
every public method silently no-ops if ``_mixer_ok`` is False.
"""

from __future__ import annotations

import pygame

from game import assets, config


class AudioManager:
    def __init__(self):
        self.music_on: bool = True
        self.sfx_on: bool = True
        # Volume levels (0.0–1.0), adjustable in-game via the volume panel and
        # shared across every screen (the AudioManager is a single instance).
        self.music_volume: float = config.DEFAULT_MUSIC_VOLUME
        self.sfx_volume: float = config.DEFAULT_SFX_VOLUME
        # Audio assets are OGG (Vorbis), which both desktop pygame-ce and
        # pygbag's SDL_mixer can decode — so audio runs in the browser too.
        # Mixer is only unavailable in the headless/dummy-driver case, where
        # every method below silently no-ops.
        self._mixer_ok: bool = pygame.mixer.get_init() is not None
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        # The track currently loaded/looping. Lets play_music continue a track
        # seamlessly across screen changes instead of restarting it.
        self._current_track: str | None = None
        if self._mixer_ok:
            self._preload_sfx()
            pygame.mixer.music.set_volume(self.music_volume)

    # ------------------------------------------------------------------
    def _preload_sfx(self) -> None:
        for name, filename in [
            ("shotgun",        "12-Gauge-Pump-Action-Shotgun.ogg"),
            ("lose_life",      "MarioLoseLife.ogg"),
            ("powerup_fart",   "powerupFart.ogg"),
            ("unpowered_fart", "unpoweredFart.ogg"),
        ]:
            path = assets.sfx_path(filename)
            if path.exists():
                try:
                    sound = assets.load_sound(path)
                    sound.set_volume(self.sfx_volume)
                    self._sounds[name] = sound
                except pygame.error:
                    pass

    # ------------------------------------------------------------------
    def play_music(self, filename: str, loops: int = -1) -> None:
        """Load and loop a music track, continuing it seamlessly if already playing.

        A track spans multiple screens (e.g. a level's music plays across its
        transition card, gameplay, and completion card). Re-requesting the track
        that's already current is a no-op so it keeps playing uninterrupted rather
        than restarting from the top. An empty filename stops music — used for
        levels that have no track yet. Does nothing if music is off or mixer absent.
        """
        if not self._mixer_ok or not self.music_on:
            return
        if not filename:
            self.stop_music()
            return
        if filename == self._current_track and pygame.mixer.music.get_busy():
            return  # already playing this track — let it continue
        path = assets.music_path(filename)
        if not path.exists():
            self.stop_music()
            return
        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops)
            self._current_track = filename
        except pygame.error:
            pass

    def stop_music(self) -> None:
        self._current_track = None
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

    def set_music_volume(self, volume: float) -> None:
        """Set the music level (clamped to 0.0–1.0) and apply it live."""
        self.music_volume = max(0.0, min(1.0, volume))
        if not self._mixer_ok:
            return
        try:
            pygame.mixer.music.set_volume(self.music_volume)
        except pygame.error:
            pass

    def set_sfx_volume(self, volume: float) -> None:
        """Set the SFX level (clamped to 0.0–1.0) and apply it to every loaded sound."""
        self.sfx_volume = max(0.0, min(1.0, volume))
        if not self._mixer_ok:
            return
        for sound in self._sounds.values():
            try:
                sound.set_volume(self.sfx_volume)
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
