"""Compose a full level background: floor + themed wall band + perimeter decor.

Dev/build-time tool — NOT imported by the game. Reads a level source dir holding a
PixelLab Wang floor tileset, its metadata, and a `manifest.json`, then renders a
single 1184x736 PNG suitable for `pixellab/maps/levelN.png` (selected at runtime
via ART_SET=pixellab).

The wall band is procedural (color-driven) so it never shows tile seams; the per-
level theme reads through the wall colour plus wall-mounted decor objects (shoji
panels, mirror, fence run, framed pictures, ...). Decor is purely decorative and
baked in; collidable furniture is handled separately (T133).

Layout of <level_dir> (e.g. pixellab/_src/level1/):
    floor_tileset.png   32px Wang tileset (16 tiles, 128x128)
    floor_meta.json     tileset metadata (corner LUT)
    manifest.json       see schema below
    decor/*.png         decor object sprites referenced by the manifest

manifest.json schema:
    {
      "accent": {"w": 14, "h": 9},          # centered floor accent (rug/mat) in tiles
      "wall": {
        "color":      [120, 120, 130],       # wall/baseboard base colour
        "highlight":  [160, 160, 170],       # inner-edge highlight line (optional)
        "top_height": 56,                     # top wall band thickness px
        "side_thickness": 16,                 # left/right/bottom baseboard px
        "door_gap":   {"x": 544, "w": 96}     # optional doorway gap in bottom band
      },
      "decor": [
        {"image": "decor/sconce.png", "x": 90, "y": 40, "scale": 1.0}
      ]
    }

Any section may be omitted (floor-only still renders). Decor blits in list order
(later items draw on top), anchored top-left, with optional integer-friendly scale.

Usage:
    python scripts/compose_level.py pixellab/_src/level1 [out.png]
    # default out: <level_dir>/full_preview.png
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


def draw_floor(surf: pygame.Surface, lut: dict[tuple, pygame.Surface],
               accent_w: int, accent_h: int) -> None:
    pure_lower = lut[("lower", "lower", "lower", "lower")]
    c0 = (COLS - accent_w) // 2
    r0 = (ROWS - accent_h) // 2
    c1, r1 = c0 + accent_w, r0 + accent_h

    def terrain(vx: int, vy: int) -> str:
        return "upper" if (c0 <= vx <= c1 and r0 <= vy <= r1) else "lower"

    for cy in range(ROWS):
        for cx in range(COLS):
            key = (
                terrain(cx, cy), terrain(cx + 1, cy),
                terrain(cx + 1, cy + 1), terrain(cx, cy + 1),
            )
            surf.blit(lut.get(key, pure_lower), (cx * TS, cy * TS))


def draw_walls(surf: pygame.Surface, wall: dict) -> None:
    color = tuple(wall.get("color", [120, 120, 130]))
    top_h = int(wall.get("top_height", 56))
    side = int(wall.get("side_thickness", 16))
    hl = wall.get("highlight")
    gap = wall.get("door_gap")

    # Top band (full width).
    pygame.draw.rect(surf, color, (0, 0, W, top_h))
    # Left / right baseboards.
    pygame.draw.rect(surf, color, (0, 0, side, H))
    pygame.draw.rect(surf, color, (W - side, 0, side, H))
    # Bottom baseboard, optionally split by a doorway gap.
    if gap:
        gx, gw = int(gap["x"]), int(gap["w"])
        pygame.draw.rect(surf, color, (0, H - side, gx, side))
        pygame.draw.rect(surf, color, (gx + gw, H - side, W - (gx + gw), side))
    else:
        pygame.draw.rect(surf, color, (0, H - side, W, side))

    if hl:
        hl = tuple(hl)
        # Inner-edge highlight lines (2px) where wall meets floor.
        pygame.draw.rect(surf, hl, (0, top_h - 2, W, 2))
        pygame.draw.rect(surf, hl, (side - 2, 0, 2, H))
        pygame.draw.rect(surf, hl, (W - side, 0, 2, H))
        pygame.draw.rect(surf, hl, (0, H - side, W, 2))


def draw_decor(surf: pygame.Surface, level_dir: Path, decor: list[dict]) -> None:
    for d in decor:
        img_path = level_dir / d["image"]
        if not img_path.exists():
            print(f"  ! missing decor image: {img_path}", file=sys.stderr)
            continue
        img = pygame.image.load(str(img_path)).convert_alpha()
        scale = float(d.get("scale", 1.0))
        if scale != 1.0:
            sz = (max(1, round(img.get_width() * scale)),
                  max(1, round(img.get_height() * scale)))
            img = pygame.transform.scale(img, sz)
        surf.blit(img, (int(d["x"]), int(d["y"])))


def compose(level_dir: Path, out: Path) -> None:
    pygame.init()
    pygame.display.set_mode((1, 1))  # enables convert_alpha
    manifest = json.loads((level_dir / "manifest.json").read_text())

    lut = load_lut(level_dir / "floor_tileset.png", level_dir / "floor_meta.json")
    surf = pygame.Surface((W, H))

    accent = manifest.get("accent", {"w": 14, "h": 9})
    draw_floor(surf, lut, int(accent.get("w", 14)), int(accent.get("h", 9)))

    if "wall" in manifest:
        draw_walls(surf, manifest["wall"])
    if manifest.get("decor"):
        draw_decor(surf, level_dir, manifest["decor"])

    out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surf, str(out))
    print(f"wrote {out} ({W}x{H})")


if __name__ == "__main__":
    ld = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else ld / "full_preview.png"
    compose(ld, out)
