"""Dev tool: headless-render every level through the real PlayScreen and save a
screenshot per level, for the active art set (CT2_ART_SET).

    CT2_ART_SET=pixellab PYTHONPATH=. python scripts/render_levels.py [out_prefix]

Saves testscreenshots/<prefix>_level{1..N}.png (default prefix: <art_set>_levels).
Used to eyeball backgrounds + obstacles + characters composited in-engine without
needing a real window. Player spawns dead-centre; obstacles sit at config.OBSTACLE_X/Y.
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game import config
from game.levels import LEVELS
from game.screens.play import PlayScreen
from game.state_machine import GameState, StateMachine


class _FakeAudio:
    def play_music(self, *a, **kw): pass
    def stop_music(self): pass
    def toggle_music(self): pass
    def toggle_sfx(self): pass
    def play_sfx(self, *a, **kw): pass


def main() -> None:
    prefix = sys.argv[1] if len(sys.argv) > 1 else f"{config.ART_SET}_levels"
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

    sm = StateMachine(GameState.RUNNING)
    ps = PlayScreen(screen, sm, _FakeAudio())

    config.SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    for n in range(1, len(LEVELS) + 1):
        ps.level = n
        ps._build_level(n)
        ps.update(0.016)
        ps.draw()
        out = config.SCREENSHOTS / f"{prefix}_level{n}.png"
        pygame.image.save(screen, str(out))
        print(f"saved {out}  (art_set={config.ART_SET}, room={LEVELS[n-1].obstacle_room})")

    pygame.quit()


if __name__ == "__main__":
    main()
