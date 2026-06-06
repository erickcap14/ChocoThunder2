# Changelog

All notable changes to ChocolateThunder2: ElectricBoogaloo are documented here.

## [0.1.0] — Phase 0 & 1: Scaffold + MCP harness
### Added
- New project `ChocoThunder2` scaffolded as an improved rebuild of the original
  Chocolate Thunder class project (kept as read-only ground truth).
- All ground-truth assets copied + normalized into `assets/` (player, NPC, obstacles,
  cakes, surprises, maps, end screens, music, SFX).
- `game/config.py` — centralized constants, tuning, paths, colours.
- `game/state_machine.py` — `GameState` enum + `StateMachine.force_state`.
- **Game State MCP harness:** `mcp_server/state_bridge.py` (file IPC) and
  `mcp_server/server.py` (FastMCP, 13 tools: state jumps, `get_state`, and screen actions).
- `main.py` with `poll_mcp_command` wired into the loop, plus a headless `--smoke` harness.
- Test harness: `tests/conftest.py` (headless pygame fixture + log_meta hook),
  `tests/logger.py`, and `tests/test_mcp_bridge.py` (12 passing).
- Project docs: `prd.md`, `.claude/CLAUDE.md`, `README.md`; `requirements.txt`, `run.sh`,
  `.gitignore`, `.claude/settings.json` (MCP wiring).

### Verified
- Phase 1 gate green: bridge roundtrip tests pass, FastMCP server boots & registers all
  tools, and a live headless harness responds to MCP-issued state jumps end-to-end.

### Notes
- Requires Python ≥ 3.10 (the `mcp` package); developed on 3.13. Uses `pygame-ce`
  (not upstream `pygame`) to match `pygame_gui`.
