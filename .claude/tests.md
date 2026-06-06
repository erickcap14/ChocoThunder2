# Testing Strategy

Purpose: This file outlines the strategy for testing ChocolateThunder2: ElectricBoogaloo — a Python/pygame-ce game with a FastMCP sidecar used as the automation harness.

---

## 1. Testing Philosophy

**Overall Goal: Every screen must be verifiable end-to-end without a display or audio device.**

Because pygame cannot be driven by Playwright (browser-only), testing uses two complementary layers:

1. **Headless unit tests** — pure logic, no display required, run fast everywhere.
2. **MCP-roundtrip tests** — Claude Code (or CI) drives the running game via the Game State MCP server, confirms state transitions, and saves screenshots to `testscreenshots/` as visual evidence.

The goal is not 100% line coverage; it is confidence that every screen can be reached, rendered, and exercised through the MCP bridge so that regressions are caught automatically.

---

## 2. Types of Tests

| Type | Tool | Description |
|:---|:---|:---|
| **Unit (headless)** | `pytest` + dummy SDL | Pure logic tests for each screen and entity. No display or audio hardware needed. SDL is driven headlessly via `SDL_VIDEODRIVER=dummy` + `SDL_AUDIODRIVER=dummy`. |
| **MCP-roundtrip** | `pytest` + live game + MCP sidecar | Bridge roundtrip tests. Jump to a screen via MCP, poll `get_state`, pixel-sample the surface, and save a screenshot. |
| **Bridge / IPC** | `pytest` | Tests for `mcp_server/state_bridge.py` file IPC primitives in isolation. |

**No E2E browser tests.** Playwright is not used — it cannot drive a pygame window.

---

## 3. Frameworks & Tools

- **Test runner:** `pytest` (≥8.0)
- **Headless fixtures:** `tests/conftest.py` sets `SDL_VIDEODRIVER=dummy` and `SDL_AUDIODRIVER=dummy` before importing pygame. Provides:
  - `pygame_env` (module-scoped) — initializes a headless `pygame.Surface` for the test module.
  - `clean_bridge` — wipes `.implementations/game_state.json` and `.implementations/game_command.json` before/after each MCP test.
- **Structured logging:** `tests/logger.py` + the `@pytest.mark.log_meta(phase, subtask, action)` marker write pass/fail records to `.implementations/test_log.json`.
- **Screenshots:** MCP-verify tests write PNG files to `testscreenshots/` (committed to git as visual evidence).

**How to run all tests:**
```bash
pytest
```

**How to run a single screen suite:**
```bash
pytest tests/test_start.py tests/test_mcp_verify_start.py -v
```

**How to run bridge-only tests (no display, fastest):**
```bash
pytest tests/test_mcp_bridge.py -v
```

---

## 4. Two-Files-Per-Screen Convention

Each game screen has exactly two test files:

| File | Purpose |
|:---|:---|
| `tests/test_<screen>.py` | Pure logic unit tests. Instantiate the screen class with the `pygame_env` fixture, assert state machine transitions, input handling, and scoring math. |
| `tests/test_mcp_verify_<screen>.py` | MCP-roundtrip tests. Requires the game to be running. Use `clean_bridge` fixture. Call `jump_to_<screen>` via MCP, assert `get_state` returns the correct state, pixel-sample the surface for expected colours, and save `testscreenshots/<screen>_verified.png`. |

**Screen → MCP tool mapping:**

| Screen | `jump_to_*` tool | `GameState` value |
|:---|:---|:---|
| Start | `jump_to_start` | `START` |
| Transition | `jump_to_transition` | `TRANSITION` |
| Play | `jump_to_running` | `RUNNING` |
| End | `jump_to_end` | `END` |
| Scoreboard | `jump_to_scoreboard` | `SCOREBOARD` |

---

## 5. Key Test Scenarios (by PRD story)

| Story | Scenario | Test file |
|:---|:---|:---|
| `movement` | Player navigates toward a click target | `test_play.py` |
| `pooping` | Spacebar drops a Poo; cooldown prevents double-drop | `test_play.py` |
| `scoring` | +1 for normal Poo, +5 while invincible | `test_play.py` |
| `powerup_invincibility` | Cake grants timed invincibility; tenants can't catch | `test_play.py` |
| `npc_ai` | NPC patrols randomly, switches to chase within radius | `test_play.py` |
| `obstacles` | Player is pushed out of obstacle, never permanently stuck | `test_play.py` |
| `level_system` | Adding a `LevelSpec` exposes a new level; timer counts down | `test_play.py` |
| `audio` | `toggle_music` / `toggle_sfx` flip state without crashing headless | `test_play.py` |
| `scoreboard` | High-score parsing tolerates malformed lines | `test_scoreboard.py` |
| `game_state_mcp` | All 13 MCP tools registered; state jumps round-trip correctly | `test_mcp_bridge.py` |
| `headless_tests` | Screenshots saved to `testscreenshots/` for every screen | `test_mcp_verify_*.py` |

---

## 6. Phase Gates

Each phase of development has an explicit test gate that must be green before the next phase begins:

| Phase | Gate |
|:---|:---|
| Phase 1 | `test_mcp_bridge.py` — 12 tests green; FastMCP boots + registers all tools |
| Phase 2 | `test_start.py` + `test_mcp_verify_start.py` green; Start screenshot reviewed |
| Phase 3 | `test_play.py` + `test_mcp_verify_play.py` green; Play screenshot reviewed |
| Phase 4 | Transition + End + Scoreboard suites green; screenshots reviewed |
| Phase 5 | Level 2 `LevelSpec` added; level-switch test green |
| Phase 6 | Full suite green (all screens); no regressions |

---

## 7. What We Do Not Test

- **Visual correctness** beyond pixel sampling — subjective art is verified by human review of `testscreenshots/`.
- **Audio output** — mixer is present but output cannot be verified headlessly; toggle state is tested, audio fidelity is not.
- **iPad / WebAssembly (Phase 7)** — deferred; out of scope until Phase 6 gate is green.
