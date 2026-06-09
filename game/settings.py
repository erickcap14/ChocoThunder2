"""Runtime game settings shared across screens.

A single process-wide ``settings`` instance holds choices that must outlive
individual screens (which are rebuilt on every state transition) without
threading a new argument through every constructor. Audio volume lives on the
AudioManager (it owns the mixer); gameplay difficulty lives here.

``hard_mode`` is chosen on the start screen (Easy is the default):
  - Easy (False): tenants never end the game — Sally can't be caught out.
  - Hard (True):  being caught by a tenant is game over (the classic behaviour).
"""

from __future__ import annotations


class Settings:
    def __init__(self) -> None:
        self.hard_mode: bool = False  # default Easy


# Process-wide singleton; import and read/write `settings.hard_mode` anywhere.
settings = Settings()
