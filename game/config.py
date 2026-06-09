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
# Selects which art tree image accessors resolve against. The upgraded pixellab/
# set is the default (iOS-bound look); the ground-truth originals are never
# modified and stay fully available via CT2_ART_SET=original. Per-asset fallback
# (see game.assets._art) means anything missing from pixellab/ transparently uses
# the original.
ART_SET = os.getenv("CT2_ART_SET", "pixellab")  # "pixellab" | "original"


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
# OBSTACLE_SIZE retired: obstacles now collide on their exact image silhouette
# (pixel mask), so there is no fixed rectangular hitbox to tune.
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
NPC_SLOW_SECONDS    = 3.0   # how long a tenant stays slowed after stepping on a splat
NPC_SLOW_MULTIPLIER = 0.4   # slowed tenants move at 40% of NPC_SPEED
SPLAT_FADE_SECONDS  = 3.0   # a splat lingers on the floor this long, then disappears

SCORE_DEFAULT = 1               # points for a normal surprise
SCORE_BONUS = 5                 # points for a surprise while invincible

# Candidate obstacle placement — a grid in the play area, inside the perimeter
# walls/decor baked into the room backgrounds (decor hugs the edges). Obstacles are
# chosen from these so they (a) clear the player's centre spawn and (b) stay spaced.
OBSTACLE_X = (340, 470, 600, 730, 860)
OBSTACLE_Y = (200, 330, 460, 560)
OBSTACLE_PLAYER_CLEARANCE = 175   # min px from an obstacle centre to the player spawn
OBSTACLE_MIN_SPACING = 240        # min px between two obstacle centres (manoeuvre room)
NPC_SPAWN_CLEARANCE = 70          # min px gap from an NPC spawn to obstacles/player/other NPCs

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
