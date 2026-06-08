"""Fetch a PixelLab character's walk animation into the game's directional layout.

Dev/build-time tool — NOT imported by the game. Downloads the character's bulk ZIP
(rotations + animations) from the PixelLab MCP download endpoint and writes the walk
cycle into <dest>/{down,left,right,up}/{0..N}.png, the layout the game's
assets.load_directional_frames() expects.

PixelLab direction -> game direction:  south->down, north->up, east->right, west->left.

Usage:
    python scripts/fetch_character.py <character_id> <dest_dir> [animation_name]
    # e.g. python scripts/fetch_character.py 11093d1b-... pixellab/characters
    #      python scripts/fetch_character.py <id> pixellab/npc/char1
    # animation_name defaults to the first animation found in the zip (usually "walking").
"""
from __future__ import annotations

import io
import sys
import urllib.request
import zipfile
from pathlib import Path

DIR_MAP = {"south": "down", "north": "up", "east": "right", "west": "left"}
DOWNLOAD_URL = "https://api.pixellab.ai/mcp/characters/{cid}/download"


def fetch(character_id: str, dest: Path, anim: str | None = None) -> None:
    url = DOWNLOAD_URL.format(cid=character_id)
    with urllib.request.urlopen(url) as resp:          # follows redirects
        data = resp.read()
    zf = zipfile.ZipFile(io.BytesIO(data))
    names = zf.namelist()

    # Discover the animation name if not given: animations/<anim>/<dir>/frame_*.png
    anims = sorted({n.split("/animations/")[1].split("/")[0]
                    for n in names if "/animations/" in n})
    if not anims:
        raise SystemExit(f"no animations found in zip for {character_id}; have: {names[:5]}")
    chosen = anim or anims[0]
    if chosen not in anims:
        raise SystemExit(f"animation '{chosen}' not in {anims}")

    written = 0
    for pix_dir, game_dir in DIR_MAP.items():
        frames = sorted(n for n in names
                        if f"/animations/{chosen}/{pix_dir}/" in n and n.endswith(".png"))
        if not frames:
            raise SystemExit(f"missing direction '{pix_dir}' for anim '{chosen}' ({character_id})")
        out_dir = dest / game_dir
        out_dir.mkdir(parents=True, exist_ok=True)
        # Clear any stale frames so frame counts don't mix.
        for old in out_dir.glob("*.png"):
            old.unlink()
        for i, name in enumerate(frames):
            (out_dir / f"{i}.png").write_bytes(zf.read(name))
            written += 1
    print(f"{character_id}: wrote {written} frames ({chosen}) -> {dest}/"
          + "{down,left,right,up}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    cid = sys.argv[1]
    dest = Path(sys.argv[2])
    anim = sys.argv[3] if len(sys.argv) > 3 else None
    fetch(cid, dest, anim)
