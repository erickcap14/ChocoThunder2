# Changelog

All notable changes to ChocolateThunder2: ElectricBoogaloo are documented here.

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
