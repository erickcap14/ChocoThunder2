# ChocolateThunder2: ElectricBoogaloo

An improved rebuild of the original *Chocolate Thunder* class project. Play **Sally**, a
white terrier, leaving "chocolate surprises" for points while dodging the tenants. Click to
move, **Spacebar** to poop, eat cakes for a real invincibility boost.

The original game in `../ChocolateThunder/` is **ground truth** (art, audio, feel) and is
never modified — all its sprites, spritesheets, sounds, and music are reused here.

## Requirements
- **Python ≥ 3.10** (the `mcp` package needs it; developed on 3.13).
- Uses `pygame-ce` (community edition) — do not also install upstream `pygame`.

## Setup
```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
./run.sh              # launches the game
python main.py        # equivalent
```

## Test
```bash
pytest -q             # headless pygame unit + MCP-verify tests
```
Screenshots from MCP-verify tests are written to `testscreenshots/` (committed to git).

## Game State MCP (automated control & verification)
A FastMCP sidecar lets Claude Code drive the running game via file-based IPC.
```bash
python -m mcp_server.server     # start the MCP server (also wired via .claude/settings.json)
python main.py --smoke          # headless harness to validate the bridge without a window
```
Tools include `get_state`, `jump_to_{start,transition,running,end,scoreboard}`, `set_level`,
`spawn_powerup`, `spawn_npc`, `drop_poo`, `set_invincible`, `toggle_music`, `toggle_sfx`.

## Project layout
| Path | Purpose |
|------|---------|
| `main.py` | Entry point + game loop (`write_state` → `poll_mcp_command` each frame) |
| `game/` | Engine: config, state machine, entities, screens, levels, audio, scores |
| `mcp_server/` | `state_bridge.py` (IPC) + `server.py` (FastMCP tools) |
| `assets/` | Ground-truth art/audio (copied + normalized) |
| `tests/` | Pure unit tests + MCP-verify (screenshot) tests |
| `testscreenshots/` | Committed verification screenshots |
| `.implementations/` | Runtime IPC + logs (gitignored) |

See `prd.md` for the full design, fixed bugs, and the iPad roadmap.
