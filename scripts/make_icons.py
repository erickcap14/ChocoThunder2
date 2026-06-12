"""Compose the app / PWA icon set from the shared standalone Sally sprite.

Sally (pixellab/_src/transitions/sally_dog.png, the one reused across every
transition card so she looks identical everywhere) is keyed off her near-white
background and centered on a grass-green rounded card — matching the backyard
start screen. Outputs to web/icons/:

    icon-1024.png        master / iOS app icon source
    icon-512.png         PWA manifest
    icon-192.png         PWA manifest
    apple-touch-icon.png 180x180, Safari add-to-home-screen

Run: PYTHONPATH=. .venv/bin/python scripts/make_icons.py
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compose_transition import _drop_white_bg

ROOT = Path(__file__).resolve().parent.parent
SALLY = ROOT / "pixellab" / "_src" / "transitions" / "sally_dog.png"
OUT = ROOT / "web" / "icons"

GRASS_TOP = (96, 169, 64)
GRASS_BOTTOM = (58, 122, 41)
SIZES = {"icon-1024.png": 1024, "icon-512.png": 512, "icon-192.png": 192,
         "apple-touch-icon.png": 180}


def make_master(size: int = 1024) -> pygame.Surface:
    icon = pygame.Surface((size, size), pygame.SRCALPHA)
    # vertical grass gradient backdrop
    for y in range(size):
        t = y / (size - 1)
        col = [round(a + (b - a) * t) for a, b in zip(GRASS_TOP, GRASS_BOTTOM)]
        pygame.draw.line(icon, col, (0, y), (size, y))
    # Sally centered, filling ~78% of the height
    sally = _drop_white_bg(pygame.image.load(str(SALLY)))
    target_h = round(size * 0.78)
    target_w = round(sally.get_width() * target_h / sally.get_height())
    sally = pygame.transform.smoothscale(sally, (target_w, target_h))
    icon.blit(sally, sally.get_rect(center=(size // 2, round(size * 0.54))))
    return icon


def main() -> None:
    pygame.init()
    pygame.display.set_mode((64, 64))
    OUT.mkdir(parents=True, exist_ok=True)
    master = make_master()
    for name, size in SIZES.items():
        surf = master if size == 1024 else pygame.transform.smoothscale(master, (size, size))
        pygame.image.save(surf, str(OUT / name))
        print(f"wrote {OUT / name} ({size}x{size})")


if __name__ == "__main__":
    main()
