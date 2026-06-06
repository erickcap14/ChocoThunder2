# Project Tasks

> Last updated: 2026-06-06 | Generated from: .claude/ context files

## Legend

- **Status:** `[ ]` = TODO, `[~]` = IN PROGRESS, `[x]` = DONE
- **ID:** Sequential `T###`, stable for the life of the project. Never renumber or reuse.
- **Blocks:** IDs of tasks that cannot start until this one is `[x]`.
- **Blocked By:** IDs that must be `[x]` before this task may be claimed.
- `—` in Blocks/Blocked By means none.
- **Build order per screen (from CLAUDE.md):** build screen → register in app/state machine → ensure `jump_to_*` MCP tool exists → wire poll handler → write `test_<screen>.py` + `test_mcp_verify_<screen>.py` → run pytest → review screenshot in `testscreenshots/`.
- **Conflict precedence:** security.md/sbom.md > infra.md > CLAUDE.md > prd.md > workflow.md.
- **Note:** `infra.md`, `sbom.md`, and `tests.md` are still unfilled blueprint templates; their concrete content for this Python/pygame-ce project is captured as tasks below.

---

## Phase 0: Scaffold & Project Setup

> Objective: Stand up the repo, ground-truth assets, core config, state machine, and tooling so feature work can begin. (COMPLETE — per changelog 0.1.0.)

| ID | Task | Status | Blocks | Blocked By | Notes |
|----|------|--------|--------|------------|-------|
| T001 | Scaffold project tree (`game/`, `mcp_server/`, `tests/`, `assets/`, `testscreenshots/`, `.implementations/`) | [x] | T002,T003,T004,T005 | — | entities/ & screens/ packages exist but empty |
| T002 | Copy + normalize all ground-truth assets into `assets/` (player, npc, obstacles, powerups, surprises, maps, endscreens, music, sfx) | [x] | T010,T030 | T001 | Original `../ChocolateThunder/` never modified |
| T003 | `game/config.py` — centralized window/timing/tuning constants, colours, paths | [x] | T010,T015,T030 | T001 | Single source of truth |
| T004 | `game/state_machine.py` — `GameState` enum (START/TRANSITION/RUNNING/END/SCOREBOARD) + `force_state` | [x] | T015 | T001 | Replaces original string flags |
| T005 | Project tooling: `requirements.txt`, `run.sh`, `.gitignore`, `.claude/settings.json` (MCP wiring) | [x] | — | T001 | pygame-ce (not upstream pygame), Python ≥3.10 |
| T006 | Project docs: `prd.md`, `.claude/CLAUDE.md`, `README.md` | [x] | — | T001 | Design, fixed-bugs appendix, iPad roadmap |

---

## Phase 1: Game State MCP Harness

> Objective: A FastMCP sidecar + file IPC so Claude Code can drive and verify the running game; headless pytest fixtures in place. (COMPLETE — per changelog 0.1.0, Phase 1 gate green.)

| ID | Task | Status | Blocks | Blocked By | Notes |
|----|------|--------|--------|------------|-------|
| T007 | `mcp_server/state_bridge.py` — file IPC (`write_state`, `read_command_full`, `clear_command`) | [x] | T008,T009 | T003 | Uses `.implementations/` |
| T008 | `mcp_server/server.py` — FastMCP server, 13 tools (5 state jumps, `get_state`, `set_level`, `spawn_powerup`, `spawn_npc`, `drop_poo`, `set_invincible`, `toggle_music`, `toggle_sfx`) | [x] | T009 | T007 | Screen-action tools queue commands; handlers wired per phase |
| T009 | `main.py` — `poll_mcp_command` wired into loop + `--smoke` headless harness | [x] | T012,T015 | T004,T007,T008 | Dispatches screen cmds only if active screen implements method |
| T010 | Test harness: `tests/conftest.py` (headless pygame fixture, dummy SDL drivers, log_meta hook) + `tests/logger.py` | [x] | T020,T035 | T002,T003 | |
| T011 | `tests/test_mcp_bridge.py` — bridge roundtrip tests (passing) | [x] | T012 | T010 | 12 passing |
| T012 | Phase 1 gate: bridge roundtrip green, FastMCP boots & registers all tools, live headless state jumps verified end-to-end | [x] | — | T009,T011 | Phase 1 sign-off |

---

## Phase 2: Engine + Start Screen

> Objective: Asset loader, sprite bases, AudioManager, the App/game-loop, and the Start screen, each verified by unit + MCP-roundtrip screenshot tests.

| ID | Task | Status | Blocks | Blocked By | Notes |
|----|------|--------|--------|------------|-------|
| T013 | `game/assets.py` — cached image/frame/directional/sound loaders + asset-path accessors | [x] | T016,T017,T030 | T002,T003 | Replaces dual importers; headless-safe convert |
| T014 | `game/sprites.py` — `DirectionalSprite` / `FrameSprite` / `ImageSprite` bases (hitbox decoupled from image) | [x] | T031,T032,T033,T034,T035,T036 | — | Replaces original d_sprite/s_sprite |
| T015 | `game/app.py` — App + main game loop wiring `write_state` → `poll_mcp_command` each frame, owns StateMachine + active screen + AudioManager | [x] | T017,T019,T037,T045,T047,T060 | T003,T004,T009,T013,T016 | `run_game()` imports this lazily |
| T016 | `game/audio.py` — AudioManager (per-level music, SFX, `toggle_music`/`toggle_sfx`); mixer-availability safe | [x] | T015,T018,T035 | T013 | Wired to `toggle_music`/`toggle_sfx` MCP handlers |
| T017 | `game/screens/start.py` — StartScreen (scrolling title bg, blurb, control list, "Press Space Bar to Play") | [x] | T019,T020,T021 | T013,T014,T015 | Story-driven UI |
| T018 | Wire AudioManager into App + connect `toggle_music`/`toggle_sfx` poll handlers to AudioManager | [x] | T035 | T015,T016 | poll_mcp_command already routes to audio_manager |
| T019 | Register StartScreen in App/state machine + confirm `jump_to_start` reaches it | [x] | T020,T021 | T015,T017 | START is default state |
| T020 | `tests/test_start.py` — pure logic unit tests for StartScreen | [x] | T022 | T010,T017,T019 | |
| T021 | `tests/test_mcp_verify_start.py` — bridge roundtrip + pixel sample + screenshot to `testscreenshots/` | [x] | T022 | T017,T019 | |
| T022 | Run pytest (start suite green) + review Start screenshot vs checklist | [x] | T100,T101 | T020,T021 | Phase 2 verification |

---

## Phase 3: Play Screen (entities, AI, scoring, collisions, power-up)

> Objective: The core gameplay — Player click-to-move, Poo on spacebar with cooldown, fixed obstacle collision, patrol+chase NPC AI, real timer-based invincibility cake, scoring, per-level timer, and the screen-action MCP handlers.

| ID | Task | Status | Blocks | Blocked By | Notes |
|----|------|--------|--------|------------|-------|
| T030 | `game/entities/__init__.py` exports + shared entity helpers | [x] | T031,T032,T033,T034,T035 | T002,T003,T013 | entities/ currently empty |
| T031 | `Player` entity — click-to-move navigation toward target, directional animation | [x] | T036 | T014,T030 | Story 1 `movement` |
| T032 | `Poo` entity — spacebar drop with elapsed-time cooldown accumulator | [x] | T036,T103 | T014,T030 | Story 2 `pooping`; Fixed Bug #3 (no reused repeating timer) |
| T033 | `Obstacle` entity — FIXED collision: blocks/pushes out, never permanently sticks | [x] | T036,T103 | T014,T030 | Story 6 `obstacles`; Fixed Bug #2 |
| T034 | `NPC` entity — random patrol + chase within `NPC_CHASE_RADIUS`; catch sends to "the farm" | [x] | T036 | T014,T030 | Story 5 `npc_ai` |
| T035 | `PowerUp` cake + REAL timer-based invincibility (`INVINCIBLE_SECONDS`); tenants can't catch, surprises worth bonus | [x] | T036,T103 | T014,T016,T030 | Story 4 `powerup_invincibility`; Fixed Bug #1 (was cosmetic), Bug #3 |
| T036 | `game/screens/play.py` — PlayScreen: room map, HUD (score + timer), per-level countdown, scoring (+1 / +5), collision wiring, cake spawn cadence | [x] | T037,T038,T041,T042,T058,T103 | T031,T032,T033,T034,T035 | Stories 3 `scoring`, 7 timer; removes Fixed Bug #4 event guard |
| T037 | Register PlayScreen in App/state machine + confirm `jump_to_running` reaches it | [x] | T038,T041,T042 | T015,T036 | |
| T038 | Wire PlayScreen screen-action poll handlers: `set_level`, `spawn_powerup`, `spawn_npc`, `drop_poo`, `set_invincible` | [x] | T039,T042 | T036,T037 | MCP tools already exist (T008); methods must implement matching names |
| T039 | Confirm/verify the 5 screen-action MCP tools drive PlayScreen live (no new tools needed) | [x] | T102 | T038 | server.py tools already registered |
| T041 | `tests/test_play.py` — unit tests: move, cooldown, no-stick collision, chase AI, invincibility timer, scoring +1/+5, timer | [x] | T043 | T010,T036,T037 | Cover every fixed bug |
| T042 | `tests/test_mcp_verify_play.py` — roundtrip (`set_level`/`spawn_*`/`drop_poo`/`set_invincible`) + pixel sample + screenshot | [x] | T043 | T036,T037,T038 | |
| T043 | Run pytest (play suite green) + review Play screenshot vs checklist | [x] | T100,T101 | T041,T042 | Phase 3 verification |

---

## Phase 4: Transition, End & In-Engine Scoreboard Screens

> Objective: Replace the original tkinter popups with in-engine screens — Level Transition card, End (win/lose) screen, and a Scoreboard with name entry and robust `scores.txt` parsing.

| ID | Task | Status | Blocks | Blocked By | Notes |
|----|------|--------|--------|------------|-------|
| T044 | `game/scores.py` — read/write top-10 high scores; tolerant parsing of malformed lines | [ ] | T048,T055,T058,T103 | T003 | Story 9; Fixed Bug #5 (no crash on bad lines) |
| T045 | `game/screens/transition.py` — black card with level name + punny subtitle, "Press Enter to Continue" | [ ] | T046,T051,T052 | T015,T014 | PRD Key Screens |
| T046 | Register TransitionScreen in App/state machine + confirm `jump_to_transition` reaches it | [ ] | T051,T052,T060 | T015,T045 | |
| T047 | `game/screens/end.py` — End screen: win/lose image, final score, thank-you, prompt to view scoreboard | [ ] | T049,T053,T054 | T015,T014 | PRD Key Screens |
| T048 | `game/screens/scoreboard.py` — in-engine name entry + top-10 list (replaces tkinter) | [ ] | T049,T055,T056 | T044,T015,T014 | Story 9 `scoreboard` |
| T049 | Register End + Scoreboard in App/state machine + confirm `jump_to_end` / `jump_to_scoreboard` reach them | [ ] | T053,T054,T055,T056 | T015,T047,T048 | |
| T051 | `tests/test_transition.py` — transition logic unit tests | [ ] | T057 | T010,T045,T046 | |
| T052 | `tests/test_mcp_verify_transition.py` — roundtrip + screenshot | [ ] | T057 | T045,T046 | |
| T053 | `tests/test_end.py` — end screen logic (win vs lose) unit tests | [ ] | T057 | T010,T047,T049 | |
| T054 | `tests/test_mcp_verify_end.py` — roundtrip + screenshot | [ ] | T057 | T047,T049 | |
| T055 | `tests/test_scoreboard.py` — name entry + tolerant score parsing (incl. malformed lines) | [ ] | T057 | T010,T044,T048,T049 | Fixed Bug #5 |
| T056 | `tests/test_mcp_verify_scoreboard.py` — roundtrip + screenshot | [ ] | T057 | T048,T049 | |
| T057 | Run pytest (transition/end/scoreboard suites green) + review screenshots vs checklists | [ ] | T100,T101 | T051,T052,T053,T054,T055,T056 | Phase 4 verification |

---

## Phase 5: Data-Driven Levels

> Objective: A `LevelSpec` manifest so adding a level is one data entry; port the 3 original levels and add a demo 4th level to prove extensibility.

| ID | Task | Status | Blocks | Blocked By | Notes |
|----|------|--------|--------|------------|-------|
| T058 | `game/levels.py` — `LevelSpec` dataclass (map image, NPC art, NPC count, obstacle room, music, transition text) + ordered manifest | [ ] | T059,T060,T061 | T036,T044 | No if/elif; appending = new level |
| T059 | Port the 3 original levels into the manifest (map, NPC, obstacles, music, punny subtitles) | [ ] | T061,T062 | T058 | Story 7 `level_system` |
| T060 | Wire LevelSpec into App + PlayScreen + TransitionScreen (level advance, `set_level` MCP) | [ ] | T061,T062,T102 | T015,T036,T046,T058 | Drives per-level music via AudioManager |
| T061 | Add a demo 4th level (new entry + assets) to prove extensibility | [ ] | T062,T103 | T058,T059,T060 | PRD extensibility requirement |
| T062 | `tests/test_levels.py` + `tests/test_mcp_verify_levels.py` — manifest loads, 4 levels selectable via `set_level`, screenshots per level | [ ] | T063 | T059,T060,T061 | |
| T063 | Run pytest (levels suite green) + review per-level screenshots vs checklists | [ ] | T100,T101 | T062 | Phase 5 verification |

---

## Phase 6: Full QA / Release Gate

> Objective: Whole-suite green, all screenshots reviewed, every MCP tool exercised live, every fixed bug and the 4th level confirmed. Prerequisite to iOS.

| ID | Task | Status | Blocks | Blocked By | Notes |
|----|------|--------|--------|------------|-------|
| T100 | Run full pytest suite green (all unit + MCP-verify) | [ ] | T104 | T022,T043,T057,T063 | Release gate |
| T101 | Review every screenshot in `testscreenshots/` against per-screen checklists | [ ] | T104 | T022,T043,T057,T063 | |
| T102 | Exercise all 13 MCP tools live against the running game (state jumps + every screen action) | [ ] | T104 | T039,T060 | get_state, jumps, set_level, spawn_*, drop_poo, set_invincible, toggle_music/sfx |
| T103 | Confirm all 6 fixed bugs (Appendix B) + the demo 4th level behave as specified | [ ] | T104 | T032,T033,T035,T036,T044,T061 | Bugs #1-#6 |
| T104 | Update `changelog.md` (Phases 2-6) + Phase 6 release sign-off | [ ] | T110 | T100,T101,T102,T103 | Gate to iOS |

---

## Phase 7: iPad / iOS Packaging (DEFERRED, exploratory)

> Objective: Ship the web build to iPad via pygbag → WASM → touch layer → PWA/Capacitor. Highest risk; gated behind the Phase 6 sign-off. Tasks intentionally deferred/exploratory.

| ID | Task | Status | Blocks | Blocked By | Notes |
|----|------|--------|--------|------------|-------|
| T110 | Compile game to WebAssembly with pygbag (keep Python/pygame code) | [ ] | T111 | T104 | DEFERRED/exploratory |
| T111 | Add touch-control layer (tap→move, on-screen button→poop) | [ ] | T112 | T110 | DEFERRED/exploratory |
| T112 | Wrap web build as iPad app via PWA / Capacitor | [ ] | — | T111 | DEFERRED/exploratory |

---

## Phase X: Cross-Cutting / Documentation

> Objective: Fill the unfilled blueprint templates and capture supply-chain/security facts so context files match reality. (security.md/sbom.md are Priority-1 per the conflict matrix.)

| ID | Task | Status | Blocks | Blocked By | Notes |
|----|------|--------|--------|------------|-------|
| T120 | Populate `.claude/sbom.md` with real stack (Python 3.13, pygame-ce, pygame_gui, mcp/FastMCP, pytest) + versions/licenses | [x] | — | — | Template still has Next.js examples; Priority 1 |
| T121 | Populate `.claude/infra.md` for the Python/pygame-ce project (run/install commands, directory conventions, data storage = `scores.txt`) | [x] | — | — | Template still has Next.js example |
| T122 | Populate `.claude/tests.md` with the real two-files-per-screen strategy (headless pytest + MCP-verify screenshots) | [x] | — | — | Template still placeholder |
| T123 | Confirm security baseline: no secrets, single-player/local-only, no network calls; `.implementations/` gitignored | [x] | — | — | Priority 1; matches security.md baseline |

---

## Dependency Graph

```
Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6 → Phase 7

T001 → T002
T001 → T003
T001 → T004
T001 → T005
T002 → T010
T002 → T030
T003 → T007
T003 → T010
T003 → T015
T003 → T030
T003 → T044
T004 → T015
T007 → T008
T008 → T009
T009 → T012
T009 → T015
T011 → T012
T010 → T020
T010 → T035
T013 → T016
T013 → T017
T013 → T030
T014 → T031
T014 → T032
T014 → T033
T014 → T034
T014 → T035
T014 → T036
T015 → T016
T015 → T017
T015 → T019
T015 → T037
T016 → T018
T016 → T035
T017 → T019
T018 → T035
T019 → T020
T019 → T021
T020 → T022
T021 → T022
T022 → T100
T030 → T031
T030 → T032
T030 → T033
T030 → T034
T030 → T035
T031 → T036
T032 → T036
T033 → T036
T034 → T036
T035 → T036
T036 → T037
T037 → T038
T038 → T039
T038 → T042
T039 → T102
T041 → T043
T042 → T043
T043 → T100
T044 → T048
T044 → T058
T045 → T046
T046 → T051
T046 → T060
T047 → T049
T048 → T049
T049 → T053
T049 → T055
T051 → T057
T057 → T100
T058 → T059
T058 → T060
T059 → T061
T060 → T061
T060 → T102
T061 → T062
T062 → T063
T063 → T100
T100 → T104
T101 → T104
T102 → T104
T103 → T104
T104 → T110
T110 → T111
T111 → T112
```

---

## Summary

| Metric | Count |
|--------|-------|
| Total | 56 |
| Done | 14 |
| In Progress | 0 |
| Remaining | 42 |
| Blocked | 38 |
