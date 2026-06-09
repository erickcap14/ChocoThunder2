"""Dev/build compositor: turn each level's PixelLab 3/4-view *Sally scene* illustration
into a premium transition/intro card — the themed scene scaled to fill the card, with a
vignette and soft dark scrims behind the title block and the bottom prompt so the overlaid
white/green card text stays readable (Sally is white, so the text needs a backing scrim).

    PYTHONPATH=. python scripts/compose_transition.py

Reads  pixellab/_src/transitions/scene_level{1..N}.png  (raw 400x240 *dog-less* scenes)
       pixellab/_src/transitions/sally_dog.png          (one standalone Sally, transparent)
Writes pixellab/transitions/level{1..N}.png             (1200x720 cards)

The SAME Sally sprite is composited into every scene (bottom-centre) so she is identical
across all levels. Headless pygame, no new deps. Selected at runtime by the ART_SET toggle;
absent files make the transition screens fall back to a plain black card (original set).
"""
from __future__ import annotations

import os
from collections import deque

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from game import config
from game.levels import LEVELS

W, H = config.SCREEN_WIDTH, config.SCREEN_HEIGHT
_BG_LIGHT = 235          # min-channel >= this == background (Sally rendered on near-white)


def _drop_white_bg(surf: pygame.Surface) -> pygame.Surface:
    """Make the near-white background transparent via a flood fill from the borders.
    Sally's dark single-colour outline stops the fill, so her (enclosed) body — even
    its white highlights — is preserved while the surrounding white is keyed out."""
    surf = surf.convert_alpha()
    sw, sh = surf.get_size()
    seen = bytearray(sw * sh)

    def light(c) -> bool:
        return min(c[0], c[1], c[2]) >= _BG_LIGHT and c[3] > 0

    dq = deque(
        [(x, 0) for x in range(sw)] + [(x, sh - 1) for x in range(sw)]
        + [(0, y) for y in range(sh)] + [(sw - 1, y) for y in range(sh)]
    )
    while dq:
        x, y = dq.popleft()
        if x < 0 or y < 0 or x >= sw or y >= sh or seen[y * sw + x]:
            continue
        seen[y * sw + x] = 1
        c = surf.get_at((x, y))
        if not light(c):
            continue
        surf.set_at((x, y), (c[0], c[1], c[2], 0))
        dq.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])
    return surf


def _band(y: int, yc: int, half: int, peak: int) -> int:
    """Triangular falloff: `peak` alpha at row yc, 0 at yc±half."""
    return int(peak * max(0.0, 1.0 - abs(y - yc) / half))


def _scrims() -> pygame.Surface:
    """Subtle uniform dim + a soft dark band behind the upper title/subtitle/score block
    (y≈220–385) and behind the bottom prompt (y≈630), so text reads over a busy scene."""
    ov = pygame.Surface((W, H), pygame.SRCALPHA)
    for y in range(H):
        a = max(55, _band(y, 300, 150, 165), _band(y, 660, 95, 150))
        pygame.draw.line(ov, (0, 0, 0, a), (0, y), (W, y))
    return ov


def _vignette() -> pygame.Surface:
    """Radial darkening toward the edges (built small, smoothscaled up)."""
    g = 64
    rad = pygame.Surface((g, g), pygame.SRCALPHA)
    cx = cy = (g - 1) / 2
    maxd = (cx ** 2 + cy ** 2) ** 0.5
    for y in range(g):
        for x in range(g):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 / maxd
            a = int(95 * max(0.0, d - 0.4) / 0.6)
            rad.set_at((x, y), (0, 0, 0, a))
    return pygame.transform.smoothscale(rad, (W, H))


_SALLY_H = 340          # Sally drawn height on the card (px)
_SALLY_FEET_Y = 712     # y of Sally's feet (just above the card bottom)


def _place_sally(card: pygame.Surface, sally: pygame.Surface) -> None:
    """Composite Sally bottom-centre at a fixed size, preserving her aspect."""
    sw, sh = sally.get_size()
    w = max(1, round(sw * _SALLY_H / sh))
    scaled = pygame.transform.scale(sally, (w, _SALLY_H))
    card.blit(scaled, scaled.get_rect(midbottom=(W // 2, _SALLY_FEET_Y)))


def main() -> None:
    pygame.init()
    pygame.display.set_mode((W, H))
    src_dir = config.PIXELLAB / "_src" / "transitions"
    out_dir = config.PIXELLAB / "transitions"
    out_dir.mkdir(parents=True, exist_ok=True)
    scrims, vignette = _scrims(), _vignette()

    sally_path = src_dir / "sally_dog.png"
    sally = _drop_white_bg(pygame.image.load(str(sally_path))) if sally_path.exists() else None
    if sally is None:
        print(f"warning: {sally_path} missing — cards will have no Sally")

    for n in range(1, len(LEVELS) + 1):
        src = src_dir / f"scene_level{n}.png"
        if not src.exists():
            print(f"skip level{n}: {src} missing (no scene art yet)")
            continue
        scene = pygame.image.load(str(src)).convert_alpha()
        card = pygame.Surface((W, H))
        card.fill(config.BLACK)                               # covers any transparent edges
        card.blit(pygame.transform.scale(scene, (W, H)), (0, 0))
        if sally is not None:
            _place_sally(card, sally)
        card.blit(vignette, (0, 0))
        card.blit(scrims, (0, 0))
        dst = out_dir / f"level{n}.png"
        pygame.image.save(card, str(dst))
        print(f"saved {dst}")

    pygame.quit()


if __name__ == "__main__":
    main()
