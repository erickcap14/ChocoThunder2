"""Compose a full level background from a PixelLab top-down Wang floor tileset.

Dev/build-time tool — NOT imported by the game. Tiles a 32px Wang tileset across
a 1184x736 canvas using proper corner autotiling, with a centered "accent" region
of the upper terrain (rug / mat / stone patio). Output is a single PNG suitable
for `pixellab/maps/<level>.png` (selected at runtime via ART_SET=pixellab).

Usage:
    python scripts/compose_backgrounds.py <tileset.png> <metadata.json> <out.png> \
        [accent_cols accent_rows]
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

W, H = 1184, 736
TS = 32
COLS, ROWS = W // TS, H // TS  # 37 x 23


def load_lut(png: Path, meta: Path) -> dict[tuple, pygame.Surface]:
    sheet = pygame.image.load(str(png))
    m = json.loads(Path(meta).read_text())
    lut: dict[tuple, pygame.Surface] = {}
    for t in m["tileset_data"]["tiles"]:
        c = t["corners"]
        bb = t["bounding_box"]
        key = (c["NW"], c["NE"], c["SE"], c["SW"])
        rect = pygame.Rect(bb["x"], bb["y"], bb["width"], bb["height"])
        lut[key] = sheet.subsurface(rect).copy()
    return lut


def compose(png: Path, meta: Path, out: Path, accent_w: int = 14, accent_h: int = 9) -> None:
    pygame.init()
    lut = load_lut(png, meta)
    pure_lower = lut[("lower", "lower", "lower", "lower")]

    # Centered accent rectangle, in vertex coordinates.
    c0 = (COLS - accent_w) // 2
    r0 = (ROWS - accent_h) // 2
    c1, r1 = c0 + accent_w, r0 + accent_h

    def terrain(vx: int, vy: int) -> str:
        return "upper" if (c0 <= vx <= c1 and r0 <= vy <= r1) else "lower"

    surf = pygame.Surface((W, H))
    for cy in range(ROWS):
        for cx in range(COLS):
            key = (
                terrain(cx, cy),       # NW
                terrain(cx + 1, cy),   # NE
                terrain(cx + 1, cy + 1),  # SE
                terrain(cx, cy + 1),   # SW
            )
            surf.blit(lut.get(key, pure_lower), (cx * TS, cy * TS))

    out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surf, str(out))
    print(f"wrote {out} ({W}x{H})")


if __name__ == "__main__":
    png, meta, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    aw = int(sys.argv[4]) if len(sys.argv) > 4 else 14
    ah = int(sys.argv[5]) if len(sys.argv) > 5 else 9
    compose(png, meta, out, aw, ah)
