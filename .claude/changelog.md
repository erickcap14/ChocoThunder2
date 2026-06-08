# Changelog

All notable changes to ChocolateThunder2: ElectricBoogaloo are documented here.

## [Unreleased] — Artwork Upgrade (PixelLab): resolver foundation + MCP wiring (T130)

### Added
- **`ART_SET` resolver foundation** (`game/config.py`): `PIXELLAB` path, `ART_SET`
  (env `CT2_ART_SET`, default `"original"`), and `art_root()`.
- **Per-asset fallback resolver** (`game/assets.py` `_art()`): routes the 7 image accessors
  (`player_dir`, `npc_dir`, `obstacle_dir`, `powerups_dir`, `surprises_dir`, `map_image`,
  `endscreen`) through `art_root()`, falling back to `assets/` when a file is missing or a
  pixellab dir is empty of PNGs. Fonts/music/sfx stay pinned to `assets/`. `levels.py` data
  unchanged (comment-only).
- **`pixellab/` tree** scaffolded (mirrors `assets/` image subdirs, `.gitkeep`) + README
  (tool→asset map, connect command, confirm-before-generate reminder).
- **PixelLab MCP wiring**: committed `.mcp.json` connects the hosted HTTP MCP
  (`https://api.pixellab.ai/mcp`) via `${PIXELLAB_API_KEY}` env expansion; `.env.example` added;
  `.env` git-ignored (token never committed).
- **`tests/test_assets_artset.py`**: 6 hermetic tests (original parity, empty/missing fallback,
  planted-asset resolution, fonts/audio pinned). Suite now **125 passing**.

### Beads
- `art_pipeline_foundation` (`ChocoThunder2-hvu` / T130) **closed**; unblocks `art_backgrounds`
  (`ChocoThunder2-bez` / T131).

---

## [Unreleased] — Artwork Upgrade (PixelLab) phase planned

### Added (docs + backlog only — no code yet)
- **PRD Stories 13–17** (`.claude/prd.md` §2): a pre-iOS-ship Artwork Upgrade phase generating an
  optional, toggle-selected art set with the PixelLab MCP, stored in a root-level `pixellab/` tree
  mirroring `assets/`. `art_backgrounds`, `art_characters`, `art_obstacles`, `art_transitions`,
  `art_startscreen`. Originals stay the default and are never deleted.
- **Beads epic `ChocoThunder2-41u`** + 5 feature issues; `art_backgrounds` (`ChocoThunder2-bez`)
  establishes the `pixellab/` tree + `ART_SET` toggle and blocks the other four. Resolver-seam
  design + `lru_cache` startup-only caveat recorded on `bez`.
- **Resolver foundation split out** as `art_pipeline_foundation` (`ChocoThunder2-hvu`, ready):
  `config.ART_SET`/`art_root()` + `assets.py` `_art()` per-asset fallback + `test_assets_artset.py`,
  no image generation; blocks `art_backgrounds`.
- **Confirm-before-generate gate** added to all five art-gen issues' acceptance criteria and
  persisted via `bd remember` (`artwork-upgrade-confirm-visual-direction-before-generating`):
  agree the visual direction with the user (style, palette, top-down perspective, reference, size)
  and get sign-off before any PixelLab MCP call.
- **`tasks.md` Phase 8** added (`T130`–`T136`) mapped to the beads IDs, with dependency graph +
  summary updated (Total 77, Remaining 13, Blocked 6).

### Changed
- `.claude/prd.md` §1 non-goal "No new art style" amended to allow the optional toggle-selected set.
- `.claude/sbom.md`: new §4c PixelLab-generated-asset provenance (dev-time only; confirm license
  before public distribution; not a runtime dependency).
- `.claude/security.md`: note PixelLab MCP is dev-time only — no outbound calls in the shipped game.
- `.claude/infra.md`: `pixellab/` added to the directory structure.

---

## [Unreleased] — UI test mode + help text fixes

### Added
- `--test` CLI flag (`python main.py --test`): 16-screen UI walkthrough mode.
  - Cycles: Start → (PreLevel → Play → Transition) × 4 levels → End Win → End Lose → Scoreboard.
  - `←`/`→` arrow keys navigate backward/forward; state-machine transitions from screens are blocked.
  - Play screens: sprites animate in place (no movement), timer replaced with "NO TIMER" in amber.
  - Bottom bar shows `TEST MODE | X / 16: Screen Label`; arrow indicators at mid-left/mid-right.
- `run_test.sh` launcher (mirrors `run.sh`): activates `.venv` then runs `main.py --test`.
  Pairs with the local `ct2_test` zsh alias.
- `GameState.PRELEVEL` + `PreLevelScreen` (`game/screens/prelevel.py`): black intro card shown
  **before** each level starts (level name + punny intro teaser + "Press Enter to Begin").
  - Level 1 intro fires from the Start screen (SPACE → PRELEVEL, not RUNNING).
  - Subsequent level intros fire from the post-level TransitionScreen (Enter → PRELEVEL → RUNNING).
  - `LevelSpec` gains `intro_subtitle` field with a teaser for each of the 4 levels.
- `Hover-For-Help` overlay in PlayScreen HUD: centred button; hovering freezes game timer and entity
  movement while sprites continue animating; overlay lists all controls.

### Fixed
- Help button text overflow: font 28→18pt, button 160→176px ("? Hover for Help" = 155px).
- Help overlay text overflow: font 28→22pt, panel 680→640px, line text tightened — max line 562px
  now fits in 640px panel with margin.

### Tests
- `tests/test_prelevel.py` added (11 tests).
- `tests/test_start.py` + `tests/test_transition.py` updated for PRELEVEL routing.
- `tests/test_levels.py` updated to cover `intro_subtitle` field.
- All 81 unit tests pass.

---

## [Unreleased] — Title style applied globally

### Changed
- `fonts.blit_outlined` promoted to `game/fonts.py` as shared helper (was
  private to `StartScreen`). All screens that previously used `config.BROWN`
  for headlines now use gold-yellow fill + deep-red 2px outline:
  EndScreen ("You Win!" / "Game Over"), TransitionScreen ("Level X Complete!"),
  ScoreboardScreen ("Enter Your Name:" + "HIGH SCORES").

---

## [Unreleased] — Title screen polish

### Changed
- Overlay box widened 820→960px; body font reduced 32→26pt so all instruction
  lines fit horizontally inside the panel (longest line was 1115px vs 820px box).
- Title "CHOCOLATE THUNDER 2" and subtitle now render with gold-yellow fill +
  deep-red 2px outline (`_blit_outlined`) — AC/DC thunderbolt aesthetic.

---

## [Unreleased] — Desktop launcher + startup fix

### Added
- `run.sh` made executable (`chmod +x`)
- `ct2_desktop` alias added to `~/.zshrc` pointing to `run.sh`

### Fixed
- `App.__init__` crash (`AttributeError: 'App' object has no attribute '_active_screen'`):
  `_active_screen` is now set to `None` before the first `_make_screen()` call so `prev`
  is always defined on the initial construction pass.

---

## [Unreleased] — Phase 7 (T110): pygbag → WASM spike

Exploratory spike to de-risk the iPad path. Scope was **T110 only** (compile to
WebAssembly + load in a browser); touch (T111) and Capacitor (T112) remain deferred.

### Added
- `web_main.py` — async pygbag entry point (`asyncio.run(main())` → `App.run_async()`),
  free of desktop-only imports (no argparse / `mcp_server` / `main`).
- `App.run_async()` + shared `App._tick()` — the per-frame loop is now shared by the
  desktop (sync) and WASM (async, yields with `await asyncio.sleep(0)`) drivers.
- `requirements-build.txt` — build-only `pygbag>=0.9,<1` (MIT), kept out of runtime deps.

### Changed
- `App` gates the MCP harness behind `_mcp_enabled` (`sys.platform != "emscripten"`):
  the desktop build is unchanged; the browser build skips file-IPC (no sidecar/filesystem
  in the sandbox). MCP imports are now lazy so the WASM bundle never pulls them in.
- `AudioManager` treats Emscripten as mixer-unavailable — pygbag's SDL_mixer lacks MP3
  support and decoding the (MP3) assets aborted the WASM runtime at startup. With audio
  off under WASM, the runtime advanced from a hang to "Ready to start".
- `.claude/infra.md`, `.claude/sbom.md` — recorded the WASM/browser build target (P2
  exception to "no browser") and the pygbag build dependency + pygame-ce LGPL-2.1 obligation
  for distributed builds (P1).

### Fixed
- Flaky `test_obstacle_pushes_player_out`: PlayScreen places obstacles with the global
  `random`, so the test was order-dependent. Added an autouse `_seed_rng` fixture
  (`random.seed(0)` per test) — suite is now deterministic and order-independent.

### Verified / Known gaps
- ✅ Desktop unchanged: 109/109 pytest green (deterministic) + smoke harness passes.
- ✅ WASM build compiles (`pygbag --build`) → valid `index.html` + 30 MB bundle.
- ✅ Browser load: cpython312 boots, game archive downloads byte-exact, 0 fatal Python
  errors, reaches pygbag's "Ready to start" (evidence: `testscreenshots/wasm_ready_to_start.png`).
- ⚠️ In-browser gameplay render **not confirmed in headless Playwright** — pygbag's UME
  "click/touch to start" gate isn't satisfied by synthetic input. Needs a real/headed
  browser. (Follow-up issue.)
- ⚠️ Follow-ups: convert MP3 → OGG for WASM audio; persist `scores.txt` via IndexedDB/
  localStorage; touch-control layer (T111).

## [1.0.0] — Phase 6 complete: Full QA / Release Gate ✓
### Verified (T100–T104)

**T100 — Full pytest suite green**
109/109 tests pass across all phases (unit + MCP-verify):
- Phase 1: 12 bridge tests
- Phase 2: 9 start-screen tests
- Phase 3: 25 play-screen tests (entities, AI, scoring, collisions)
- Phase 4: 39 transition/end/scoreboard tests
- Phase 5: 24 levels-manifest tests

**T101 — All 7 screenshots reviewed**
| Screenshot | Result |
|---|---|
| `start_verified.png` | ✅ Title, blurb, controls, "Press Space Bar to Play" |
| `play_verified.png` | ✅ Room map, Sally, NPC, furniture, HUD (Score/Timer) |
| `transition_verified.png` | ✅ Black card, level name, punny subtitle, score, Enter prompt |
| `end_win_verified.png` | ✅ Win image (white dog), "You Win!", final score, scoreboard prompt |
| `end_lose_verified.png` | ✅ Lose image (farm), "Game Over", final score, scoreboard prompt |
| `scoreboard_verified.png` | ✅ Name entry cursor, score display, Enter prompt |
| `level4_verified.png` | ✅ Level 4 room, char2+char3 NPCs, obstacles, HUD — demo level confirmed |

**T102 — All 13 MCP tools exercised via bridge**
| Tool | Covered by |
|---|---|
| `get_state` | `test_mcp_bridge.py::test_state_roundtrip` |
| `jump_to_start/transition/running/end/scoreboard` | `test_mcp_bridge.py::test_poll_jumps` (parametrized) |
| `set_level` | `test_mcp_verify_levels.py` (n=1..4) + `test_mcp_verify_play.py` |
| `spawn_powerup` | `test_mcp_verify_play.py` + `test_mcp_bridge.py::test_poll_screen_actions` |
| `spawn_npc` | `test_mcp_verify_play.py` + `test_mcp_bridge.py::test_poll_screen_actions` |
| `drop_poo` | `test_mcp_verify_play.py` + `test_mcp_bridge.py::test_poll_screen_actions` |
| `set_invincible` | `test_mcp_verify_play.py` + `test_mcp_bridge.py::test_poll_screen_actions` |
| `toggle_music` | `test_mcp_bridge.py::test_poll_audio_toggles` |
| `toggle_sfx` | `test_mcp_bridge.py::test_poll_audio_toggles` |

**T103 — All 6 fixed bugs + 4th level confirmed**
| Bug | Fix | Test |
|---|---|---|
| #1 Invincibility was cosmetic | Real timer-based (`INVINCIBLE_SECONDS`) | `test_play.py` invincibility tests |
| #2 Obstacle permanently sticks | AABB SAT `push_out()` | `test_play.py::test_obstacle_collision` |
| #3 Reused repeating timer | Elapsed-time accumulator | `test_play.py::test_poo_cooldown_blocks_drop` |
| #4 Nonsensical event guard | Removed from PlayScreen | Code audit + docstring |
| #5 Malformed score crash | Tolerant `rindex(",")` parsing | `test_scoreboard.py` malformed-line tests |
| #6 Dead code present | Native dict/list/deque, no FIFO/LinkedList | Code audit (700 lines removed) |
| 4th level extensibility | `LevelSpec` append proves design | `test_mcp_verify_levels.py::test_set_level_4_*` |

### Phase 6 Release Sign-Off
> **Status: GATE PASSED** — ChocolateThunder2: ElectricBoogaloo is feature-complete
> for the desktop target. All Phases 1–6 done. Phase 7 (iPad/iOS packaging) is
> next, gated behind this sign-off.

---

## [0.7.0] — Phase 5 complete: Data-driven levels
### Added
- `game/levels.py` — `LevelSpec` frozen dataclass (map_image, npcs, obstacle_room, music,
  transition_subtitle) + `LEVELS` list of 4 entries. Single source of truth: adding a level
  is one `LevelSpec` append + dropping assets — zero if/elif edits anywhere.
- `assets/maps/level4.png` — demo 4th level asset (proves extensibility). Level 4 uses
  char2+char3 NPCs, genericroom obstacles, Thunderstruck music, "Double Down Dirty Dog"
  subtitle.
- `tests/test_levels.py` — 17 unit tests: manifest structure (4 levels, unique names/maps,
  frozen dataclass), PlayScreen initializes/set_level for all 4 levels, TransitionScreen
  subtitle sourced from manifest.
- `tests/test_mcp_verify_levels.py` — 7 bridge tests: `set_level` roundtrip for n=1..4,
  state write/read carries level field, level-1 render is non-black, level-4 renders and
  saves `testscreenshots/level4_verified.png`.

### Changed
- `game/screens/play.py` — Removed hardcoded `_LEVELS` dict; now reads from `LEVELS`
  manifest. `set_level`, `resume`, `spawn_npc` all use `len(LEVELS)` for range clamping.
- `game/screens/transition.py` — Removed `_MAX_LEVELS = 3` and `_SUBTITLES` dict;
  uses `len(LEVELS)` for final-level check and `LEVELS[n-1].transition_subtitle` for text.
- `tests/test_transition.py` — Final-level test now uses `len(LEVELS)` instead of
  hardcoded `3`, staying correct as more levels are added.

### Verified
- Full pytest suite green: 109/109 passing (24 new Phase 5 tests).
- Closes T058–T063 (ChocoThunder2-dzt).

---

## [0.6.0] — Phase 4 complete: Transition, End & Scoreboard screens
### Added
- `game/scores.py` — `load_scores()` / `save_scores()` / `add_score()`: tolerant
  `scores.txt` parsing using `rindex(",")` so names may contain commas; malformed
  lines are silently skipped. Fixes Bug #5. `config.MAX_HIGH_SCORES = 10`.
- `game/screens/transition.py` — `TransitionScreen(screen, sm, audio, level, score)`:
  solid black card with the just-completed level number, a punny subtitle per level
  ("Working Out A Big One", "Sem-Poo-Ku", "The Final Defecation"), accumulated score,
  and "Press Enter to Continue". ENTER on level < 3 → RUNNING; on level 3 → END.
- `game/screens/end.py` — `EndScreen(screen, sm, audio, score, win)`: full-screen
  win/lose image (`assets/endscreens/win.jpg` / `lose.jpg`) with a semi-transparent
  overlay, headline, final score, flavour text, and ENTER/SPACE → SCOREBOARD.
- `game/screens/scoreboard.py` — `ScoreboardScreen(screen, sm, audio, score)`: two
  phases — ENTRY (type name, ENTER submits via `scores.add_score`) and VIEW (top-10
  table with rank/name/score columns, ENTER/SPACE → START). Replaces the original
  tkinter popup. Story 9 complete.
- `game/screens/play.py` — `resume(level, score)` method for cross-level progression
  without resetting accumulated score (distinct from `set_level` which resets for MCP
  testing).
- `game/app.py` — `_make_screen` now handles all 5 `GameState` values; score and level
  are carried across transitions (TRANSITION → RUNNING via `PlayScreen.resume`,
  PlayScreen/TransitionScreen → END with win-flag detection).

### Tests
- `tests/test_transition.py` (7) + `tests/test_mcp_verify_transition.py` (3)
- `tests/test_end.py` (8) + `tests/test_mcp_verify_end.py` (4)
- `tests/test_scoreboard.py` (14) + `tests/test_mcp_verify_scoreboard.py` (3)
- Screenshots: `transition_verified.png`, `end_win_verified.png`,
  `end_lose_verified.png`, `scoreboard_verified.png`.
- **Phase 4 gate: 85/85 tests passing.**
- Closes T044–T057 (ChocoThunder2-rqq epic).

---

## [0.5.0] — Phase 3 complete: PlayScreen + MCP handlers + test suite
### Added
- `game/screens/play.py` — `PlayScreen(screen, sm, audio)`: core gameplay screen.
  Draws the level room map (3 levels, distinct assets/music), renders all entity groups,
  shows HUD (score top-left, timer top-right, INVINCIBLE indicator centre), wires all
  collisions, and manages per-level countdown. Scoring: +1 normal, +5 powered.
  Automatic cake spawn every `POWERUP_SPAWN_SECONDS` when none on screen.
  Fixes Bug #4 (MOUSEBUTTONDOWN handled directly, no UI_BUTTON_PRESSED guard).
- `game/app.py` — `_make_screen` extended with `GameState.RUNNING` → `PlayScreen`.
- `PlayScreen` MCP poll handler methods: `set_level(n)`, `spawn_powerup()`,
  `spawn_npc()`, `drop_poo()`, `set_invincible(on)` — all dispatched by
  `main.poll_mcp_command`. Closes T038 (MCP wiring).
- `tests/test_play.py` (18) — covers click-to-move, poo cooldown (Bug #3), obstacle
  push-out (Bug #2), NPC catch → END, invincibility (Bug #1), scoring +1/+5, timer
  expiry → TRANSITION, cake auto-spawn, and all 5 MCP handlers.
- `tests/test_mcp_verify_play.py` (7) — full MCP bridge roundtrips for all 5 screen
  actions + RUNNING state write + `play_verified.png` screenshot.
- **Phase 3 gate: 46/46 tests passing.**
- Closes T036–T043 (ChocoThunder2-vnd epic).

---

## [0.4.0] — Phase 3 (partial): Entity layer complete
### Added
- `game/entities/__init__.py` — package entry point; exports `DIRECTIONS`, `clamp_rect`,
  and all five entity classes. `clamp_rect(rect, bounds)` is the shared boundary helper
  used by `Player` and `NPC`.
- `game/entities/player.py` — `Player(DirectionalSprite)`: click-to-move toward a
  `set_target(pos)` at `PLAYER_SPEED` px/frame, directional animation, and real
  timer-based invincibility (`set_invincible(bool)` / `_invincible_remaining` accumulator).
  Fixes Bug #1 (invincibility was cosmetic) and Bug #3 (no repeating timer).
- `game/entities/poo.py` — `Poo(FrameSprite)`: animated surprise sprite placed at Sally's
  position; `powered` flag selects the correct frame set. Drop cooldown is managed by
  PlayScreen (dt accumulator), fixing Bug #3 for the cooldown path too.
- `game/entities/obstacle.py` — `Obstacle(ImageSprite)`: immovable furniture sprite with
  `push_out(rect)` using minimum-overlap axis separation (AABB SAT). Fixes Bug #2
  (original zeroed position on overlap → soft-lock).
- `game/entities/npc.py` — `NPC(DirectionalSprite)`: two-mode AI — random `PATROL` with
  retargeting on arrival, `CHASE` when `distance(npc, player) ≤ NPC_CHASE_RADIUS`.
  `is_chasing` property exposed for PlayScreen catch detection.
- `game/entities/powerup.py` — `PowerUp(FrameSprite)`: three-frame animated cake sprite.
  PlayScreen detects collection and calls `player.set_invincible(True)`.

### Verified
- All 5 entities import cleanly from `game.entities`; smoke-tested under headless SDL.
- Full pytest suite still green: 21/21 passing.
- Closes T030–T035 (ChocoThunder2-14f, -y3g, -daq, -owa, -znj, -dlm).

---

## [0.3.0] — Phase X: Context templates filled
### Added
- `.claude/infra.md` populated with Python/pygame-ce stack, directory conventions,
  install/run commands, and data storage (`scores.txt`).
- `.claude/sbom.md` populated with real dependency table (pygame-ce ≥2.5, pygame_gui ≥0.6,
  mcp ≥1.2, pytest ≥8.0), licenses, and LGPL note for future iPad milestone.
- `.claude/tests.md` populated with two-files-per-screen testing strategy, SDL dummy driver
  setup, phase gate table, and scenario coverage per PRD story.
- `.claude/security.md` expanded with project-specific baseline: no secrets, local-only,
  stdio-only MCP, `.implementations/` gitignored, pre-PR security checklist.
- Closes `ChocoThunder2-5jr` (T120–T123).

---

## [0.2.0] — Phase 2: Engine + Start Screen
### Added
- `game/audio.py` — `AudioManager`: mixer-safe per-level music (`play_music`), 4 SFX
  preloaded (`shotgun`, `lose_life`, `powerup_fart`, `unpowered_fart`), `toggle_music` /
  `toggle_sfx` methods wired to MCP poll handlers.
- `game/app.py` — `App` class: 60 fps game loop, `write_state` + `poll_mcp_command` each
  frame, screen switching on `StateMachine` state transitions, graceful shutdown.
- `game/screens/start.py` — `StartScreen`: scrolling `introscreen.png` background, dark
  overlay panel, brown title, blurb, controls list, "Press Space Bar to Play" in green,
  SPACE → `RUNNING` transition, plays Thunderstruck music.
- `tests/test_start.py` — 6 headless unit tests covering init, SPACE transition, non-SPACE
  key no-op, scroll advance, wrap, and draw-without-error.
- `tests/test_mcp_verify_start.py` — bridge roundtrip tests + headless render + pixel
  assertion + screenshot saved to `testscreenshots/start_verified.png`.

### Verified
- Phase 2 gate green: 21/21 pytest tests pass; `start_verified.png` reviewed.
- Closes `ChocoThunder2-12l` (T015–T022).

---

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
