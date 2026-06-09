"""Dev/build compositor for the win / lose / leaderboard cards (Artwork Upgrade).

Builds 1200x720 cards from the PixelLab 3/4 scenes in pixellab/_src/screens/, dimmed +
vignetted with scrims sized for each screen's text, and (for win/leaderboard) the same
standalone Sally used on the transition cards composited in for a consistent character.

    PYTHONPATH=. python scripts/compose_screens.py

Writes:
  pixellab/endscreens/win.jpg   (EndScreen win  — Sally on the podium)
  pixellab/endscreens/lose.jpg  (EndScreen lose — red barn, no Sally)
  pixellab/ui/scoreboard.jpg    (ScoreboardScreen — trophy hall, small Sally, heavy dim)

Saved as .jpg names (PNG bytes) so the existing assets.endscreen()/ui_image() loaders find
them; pygame loads by content, not extension. Headless pygame, no new deps.
"""
from __future__ import annotations

import os
from collections import deque

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from game import config

W, H = config.SCREEN_WIDTH, config.SCREEN_HEIGHT
_BG_LIGHT = 235

_SRC = config.PIXELLAB / "_src" / "screens"
_SALLY = config.PIXELLAB / "_src" / "transitions" / "sally_dog.png"


def _drop_white_bg(surf: pygame.Surface) -> pygame.Surface:
    """Border flood-fill the near-white background to transparent (outline protects Sally)."""
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


def _vignette(peak: int = 95) -> pygame.Surface:
    g = 64
    rad = pygame.Surface((g, g), pygame.SRCALPHA)
    cx = cy = (g - 1) / 2
    maxd = (cx ** 2 + cy ** 2) ** 0.5
    for y in range(g):
        for x in range(g):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 / maxd
            a = int(peak * max(0.0, d - 0.4) / 0.6)
            rad.set_at((x, y), (0, 0, 0, a))
    return pygame.transform.smoothscale(rad, (W, H))


def _band(y: int, yc: int, half: int, peak: int) -> int:
    return int(peak * max(0.0, 1.0 - abs(y - yc) / half))


def _scrims(base: int, bands: list[tuple[int, int, int]]) -> pygame.Surface:
    """Per-row overlay: a uniform `base` alpha plus triangular dark `bands` (yc, half, peak)."""
    ov = pygame.Surface((W, H), pygame.SRCALPHA)
    for y in range(H):
        a = base
        for yc, half, peak in bands:
            a = max(a, _band(y, yc, half, peak))
        pygame.draw.line(ov, (0, 0, 0, a), (0, y), (W, y))
    return ov


def _place_sally(card, sally, height, midbottom) -> None:
    sw, sh = sally.get_size()
    scaled = pygame.transform.scale(sally, (max(1, round(sw * height / sh)), height))
    card.blit(scaled, scaled.get_rect(midbottom=midbottom))


def _build(scene_name, out_path, *, sally=None, sally_args=None, base, bands):
    src = _SRC / scene_name
    if not src.exists():
        print(f"skip {out_path.name}: {src} missing")
        return
    card = pygame.Surface((W, H))
    card.fill(config.BLACK)
    card.blit(pygame.transform.scale(pygame.image.load(str(src)).convert_alpha(), (W, H)), (0, 0))
    if sally is not None and sally_args is not None:
        _place_sally(card, sally, *sally_args)
    card.blit(_vignette(), (0, 0))
    card.blit(_scrims(base, bands), (0, 0))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(card, str(out_path))
    print(f"saved {out_path}")


def main() -> None:
    pygame.init()
    pygame.display.set_mode((W, H))
    sally = _drop_white_bg(pygame.image.load(str(_SALLY))) if _SALLY.exists() else None

    # EndScreen text: headline y180, score y290, flavour y380, prompt y630.
    end_bands = [(300, 200, 150), (645, 95, 150)]
    _build("scene_win.png", config.PIXELLAB / "endscreens" / "win.jpg",
           sally=sally, sally_args=(300, (W // 2, 705)), base=45, bands=end_bands)
    _build("scene_lose.png", config.PIXELLAB / "endscreens" / "lose.jpg",
           base=55, bands=end_bands)
    # ScoreboardScreen: title y60 + a full top-10 table — needs a heavy, even dim.
    _build("scene_leaderboard.png", config.PIXELLAB / "ui" / "scoreboard.jpg",
           sally=sally, sally_args=(210, (W - 150, 715)), base=140, bands=[(60, 70, 60)])

    pygame.quit()


if __name__ == "__main__":
    main()
