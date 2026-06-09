"""Central configuration for ChocolateThunder2: ElectricBoogaloo.

Single source of truth for window/timing constants, gameplay tuning, colours,
and on-disk paths. Everything that the original game hard-coded across many
files lives here so the rest of the codebase stays declarative.
"""

import os
from pathlib import Path

# --- Paths -----------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
PIXELLAB = ROOT / "pixellab"               # optional alternate art set
IMPL = ROOT / ".implementations"           # IPC + logs (gitignored)
SCREENSHOTS = ROOT / "testscreenshots"     # committed test screenshots

# --- Art set ---------------------------------------------------------------
# Selects which art tree image accessors resolve against. Originals are the
# default and are never modified; pixellab/ is optional and per-asset
# fallback (see game.assets._art) means a partial set transparently uses
# originals for anything missing.
ART_SET = os.getenv("CT2_ART_SET", "original")  # "original" | "pixellab"


def art_root() -> Path:
    """Active art root, read at call time so tests can monkeypatch ART_SET."""
    return PIXELLAB if ART_SET == "pixellab" else ASSETS

# IPC files used by the Game State MCP bridge
STATE_FILE = IMPL / "game_state.json"
COMMAND_FILE = IMPL / "game_command.json"
TEST_LOG_FILE = IMPL / "test_log.json"

# --- Window / loop ---------------------------------------------------------
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 720
FPS = 60
CAPTION = "ChocolateThunder2: ElectricBoogaloo"

# --- Gameplay tuning (ported from the original, now named) -----------------
LEVEL_SECONDS = 60          # countdown per level
PLAYER_SPEED = 5            # px/frame toward the click target
PLAYER_SIZE = (40, 40)      # Sally's hitbox (collision footprint — kept small/nimble)
PLAYER_RENDER_SIZE = (115, 115)  # Sally drawn size (a dog ~4/5 of an NPC)
NPC_SPEED = 2.2
NPC_SIZE = (60, 60)         # tenant hitbox (catch box) — larger body than Sally
NPC_RENDER_SIZE = (144, 144)    # tenant drawn size (a person, Sally is 4/5 of this)
NPC_CHASE_RADIUS = 300      # start chasing within this distance
NUM_OBSTACLES = 4
OBSTACLE_SIZE = (100, 150)        # obstacle hitbox (collision footprint) — unchanged
OBSTACLE_RENDER_MAX = (160, 160)  # default drawn box; obstacle fits it, aspect preserved (decoupled from hitbox)
# Per-object render box overrides (keyed by PNG filename stem) — bigger hero pieces.
OBSTACLE_RENDER_OVERRIDES = {
    "dining_table": (260, 200),
    "tv_stand": (210, 160),
    "sofa": (220, 220),
    "bbq_grill": (110, 110),
}
POO_SIZE = (50, 60)
POWERUP_SIZE = (50, 60)

POWERUP_SPAWN_SECONDS = 5.0     # cake appears this often
INVINCIBLE_SECONDS = 3.0        # real invincibility window granted by a cake
POO_COOLDOWN_SECONDS = 1.0      # min time between surprises

SCORE_DEFAULT = 1               # points for a normal surprise
SCORE_BONUS = 5                 # points for a surprise while invincible

# Candidate obstacle placement — central band only, away from the perimeter
# walls/decor baked into the room backgrounds (decor hugs the edges; centre stays clear).
OBSTACLE_X = (430, 600, 770)
OBSTACLE_Y = (250, 400, 550)

# --- Colours ---------------------------------------------------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GREY = (77, 77, 77)
GREEN = (0, 200, 0)
BROWN = (139, 69, 19)
BLUE = (40, 90, 200)

# --- Scores ----------------------------------------------------------------
SCORES_FILE = ROOT / "scores.txt"
MAX_HIGH_SCORES = 10
