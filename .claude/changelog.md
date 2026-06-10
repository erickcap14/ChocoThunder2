# Changelog

All notable changes to ChocolateThunder2: ElectricBoogaloo are documented here.

## [Unreleased] — T111 revision: tap Sally to drop a surprise (replaces button)

### Changed
- **Touch surprise mechanic** (user-requested): instead of an on-screen poop
  button, you now **tap Sally herself** — she puffs up a tiny bit
  (`SALLY_TAP_PULSE_SCALE` = 12%, decaying over `SALLY_TAP_PULSE_SECONDS` =
  0.25s via `Player.tap_pulse`) and leaves a surprise. The tappable area is
  her drawn 115px sprite (`Player.render_rect`), not the 40px hitbox, so
  fingers have something to hit. Tap-on-Sally never retargets her; the 1s
  poo cooldown still applies. The on-screen button and its drawing code are
  removed.
- **Touch-worded control text**: start-screen controls panel and the play
  screen's help overlay now show touch instructions under the touch layer
  ("Tap Sally — leave a chocolate surprise", "Touch + drag — Sally follows
  your finger"); desktop wording unchanged.

### Verified
- 174 tests pass (17 touch tests, incl. render-edge tap, pulse decay,
  cooldown, desktop-off guards).
- Live browser session: the WASM build was played hands-on through Level 3
  (score 96) using the tap-Sally mechanic. (Investigation note: a suspected
  "phantom input" bug turned out to be real user input — the Playwright
  browser is headed and shares the user's desktop, so verify with the user
  hands-off or rely on headless tests.)

---

## [Unreleased] — T111: touch-control layer for iPad

### Added
- **`config.touch_ui_enabled()`** — touch layer toggle: auto-on under the
  WASM/browser build (`sys.platform == "emscripten"`), `CT2_TOUCH_UI=1/0`
  forces it for desktop testing. Desktop behavior is unchanged when off.
- **On-screen poop button** (PlayScreen, bottom-right): brown disc with the
  poo sprite, tap = Space (places a surprise, respects the 1s cooldown,
  dims while cooling down). Taps on the button never retarget Sally;
  taps anywhere else still move her (tap-to-move came free via SDL's
  touch→mouse translation).
- **Tap-to-advance** on every key-gated screen: start (tap off the EASY/HARD
  buttons starts the game), prelevel, transition, end. Scoreboard: a tap
  submits the typed name or "SALLY" as the no-keyboard default, then a tap
  returns to start. All prompts switch wording under touch
  ("Tap to Play", "Tap to Begin", "Tap to submit as SALLY", …).
- **16 new tests** (`tests/test_touch_ui.py`) covering button placement/
  cooldown/no-retarget, every tap-to-advance flow, and desktop-off guards.

### Verified
- 173 tests pass (157 + 16).
- Full clicks-only browser run of the WASM build: "Tap to Play" → "Tap to
  Begin" → tap-to-move (no accidental poo) → poop-button tap (score 0→1,
  button dims for cooldown). Screenshots `testscreenshots/wasm_t111_*.png`.
- Hands-off observation window showed no phantom input events; an earlier
  anomaly traced to pygbag queueing pre-boot clicks and replaying them once
  Python is ready — drive browser verification with single clicks after the
  page title flips to the game caption.

---

## [Unreleased] — T136 complete: Phase 8 art verification sign-off

### Verified
- **Tests:** 157/157 green, including all 6 `ART_SET` fallback tests
  (pixellab→assets per-asset fallback for fonts/sounds/powerups/surprises,
  empty-dir fallback, `npc_available` direction checks).
- **In-engine renders:** all 4 levels rendered headlessly through the real
  `PlayScreen` with `CT2_ART_SET=pixellab`
  (`testscreenshots/t136_pixellab_level{1-4}.png`) — maps, obstacles, Sally,
  and tenants composited correctly; user reviewed and signed off.
- **Offline preserved:** zero network/PixelLab API code in `game/`,
  `main.py`, `web_main.py` (grep for urllib/requests/httpx/socket/API hosts —
  only a docstring hit). All PixelLab art is committed files.

### Notes
- T136's "both art sets" wording predates commit `6811bb9`, which retired the
  original art set (assets/ keeps only fonts/sounds/powerups/surprises);
  `CT2_ART_SET=original` therefore has no maps by design, and the fallback
  machinery is what the tests verify. Phase 8 (Artwork Upgrade) is fully
  closed: T130–T136 all done.

---

## [Unreleased] — T113 complete: WASM gameplay verified in-browser

### Fixed
- **WASM entry point never started (the real T113 blocker).** The gray
  "stuck" screen was never the UME gate: pygbag's loader always sources
  `assets/main.py` from the archive, so building from the repo root packed the
  *desktop* `main.py` as the web entry — its `if __name__ == "__main__"` guard
  never fires under `shell.source`, so the bundle loaded and silently did
  nothing. (Chrome's autoplay policy usually auto-unlocked UME without any
  click at all.)
- **`web_main.py` now imports pygame at top level.** pygbag's in-browser
  dependency scanner only reads the entry file's top-level imports to decide
  which WASM wheels to fetch; without it, `pygame` resolved to an empty stub
  and `App()` died at `pygame.init()`.
- **macOS AppleDouble files crashed level build.** `._*.png` metadata files
  smuggled into the tar by macOS `tar` are extracted as real files by Python's
  `tarfile` in the browser FS, win the alphabetical obstacle glob, and crash
  `pygame.image.load` ("Unsupported image format"). Fixed with
  `COPYFILE_DISABLE=1` during packing.

### Added
- **`scripts/build_web.sh`** — reproducible web build: stages `web_main.py`
  *as* `main.py` with `game/`, `assets/`, `pixellab/`; tars without
  AppleDouble files; pairs with the committed pygbag 0.9.3 loader; mirrors the
  pygame-ce wheel into `build/web/cdn/` (on localhost the loader rewrites the
  CDN to `http://localhost:8000/cdn/`, so serve `build/web` on port 8000).
  Bypasses `pygbag --build` entirely — its template fetch hangs forever on
  macOS (urllib SSL `CERTIFICATE_VERIFY_FAILED`).
- **`web/index.html` + `web/favicon.png`** — committed pygbag 0.9.3 loader
  template (previously only lived in gitignored `build/`).
- **Verification screenshots** `testscreenshots/wasm_t113_{startscreen,play,move}.png`
  — animated start screen, live Level 1 gameplay (HUD, NPC, cake, ticking
  timer), and arrow-key movement, all driven via Playwright in a real browser.

### Verified
- Full in-browser flow: boot → UME click → animated start screen → Space →
  Level 1 card → Enter → live gameplay with keyboard input. T113 closed.
- 157 tests still pass.

---

## [Unreleased] — pygbag.ini exclusions, T113 UME-gate investigation

### Added
- **`pygbag.ini`** — proper build exclusions (`/.venv`, `/.git`, `/build`, `/testscreenshots`,
  `/tests`, `/.claude`, `/pixellab`, etc.) so the WASM archive only packs runtime game files.
  Uses `/`-prefixed paths matching pygbag 0.9.3's internal relative-path scheme.
- **WASM browser screenshots** (`testscreenshots/wasm_browser_initial.png`,
  `wasm_browser_loading.png`, `wasm_after_click.png`, `wasm_after_resume.png`) — artefacts
  from T113 Playwright verification run.

### Discovered / In Progress
- **T113 UME gate** — Playwright MCP browser successfully reaches the gray "Ready to start"
  overlay (CPython WASM boots, game archive loads, `ume_block=1` state confirmed). A plain
  `body` click satisfies the gate; however, a subsequent JS `Module.resumeMainLoop()` call
  triggered a Python crash → `beforeunload` → page auto-restart. Fix: click only (no JS
  resumeMainLoop call) and wait for the start-screen canvas render before screenshotting.
- **T114 & T115** — confirmed already done as part of T110: all music assets are OGG
  (no MP3s remain); `scores.py` already has the full `localStorage` backend for
  `sys.platform == "emscripten"`. Both tasks closed.

### Verified
- 157 tests still pass.

---

## [Unreleased] — Level 3 music, test-mode audio, top-bar chrome buttons

### Added
- **Level 3 music — "Wheel in the Sky"** (`09 Wheel in the Sky.ogg`, converted from
  the supplied MP3 via ffmpeg to match the OGG/WASM convention). Wired into
  `levels.py`; the existing per-level system plays it from the Level 3 transition
  card through gameplay to the complete card.
- **Music in the `--test` walkthrough.** The UI walkthrough now drives a per-screen
  track (parallel to the screen/label lists) so scrolling is never silent: it
  continues within a level and switches at level boundaries (Thunderstruck → I
  Wanna Rock → Wheel in the Sky → Angel), with Angel carrying onto the
  win/lose/leaderboard screens.

### Changed
- **Return + VOL buttons moved to the top-right**, in the gap just left of the
  play-screen timer (was bottom corners). "Return to Start" label shortened to
  "Return" to fit; the volume panel now drops down below the VOL button. Other
  screens' titles sit below the y5–45 button row, so no overlaps.

### Verified
- 157 tests pass. Confirmed the Level 3 OGG resolves + loads in the mixer, the
  walkthrough maps all 16 screens to the right track, and the repositioned buttons
  render cleanly on play/start/end via headless renders.

---

## [Unreleased] — Persistent chrome: volume, return-to-start, difficulty

### Added
- **Shared `Chrome` widget** (`game/screens/chrome.py`) composed by every screen —
  one reusable control bar with consistent behavior and an event-consumption
  contract (`handle_event -> bool`, `is_blocking()`, `draw()`).
- **Volume control on all screens** — a **VOL** button (bottom-right) opens a panel
  with draggable **Music** and **SFX** sliders (+% readouts). Levels live on the
  shared `AudioManager` (`set_music_volume`/`set_sfx_volume`, applied live to
  `pygame.mixer.music` and every loaded SFX), so a change persists across screens.
  Defaults `DEFAULT_MUSIC_VOLUME`/`DEFAULT_SFX_VOLUME` (0.7) in config.
- **Return to Start** button (bottom-left) on Play → PreLevel → Transition → End →
  Scoreboard (everything from gameplay up to the leaderboard, not the Start
  screen). Opens a **"Return to Start? Yes/No"** confirm; Yes abandons the run and
  jumps to Start.
- **Easy/Hard difficulty** — EASY/HARD buttons on the start screen (default
  **Easy**, highlighted) backed by a `settings` singleton (`game/settings.py`).
  Easy: tenants can't end the game; Hard: caught = game over. Wired into
  PlayScreen's catch logic (`if settings.hard_mode and not invincible`).

### Changed
- **Start-screen control instructions** rewritten to list all three movement
  methods (mouse click, click+drag, arrow keys) plus space/cake, with the overlay
  panel sized dynamically to fit the text + difficulty buttons + caption.
- Each screen freezes/ignores its own input while a chrome modal (volume panel or
  quit confirm) is open (`is_blocking()` guard); PlayScreen also pauses the game.

### Verified
- 157 tests pass (new `test_chrome.py`, `test_audio_volume.py`, plus per-screen
  chrome tests; play catch tests updated to set `settings.hard_mode` via
  monkeypatch so the global singleton never leaks across tests). Visually
  confirmed start (difficulty + instructions + VOL), play (both buttons + open
  volume panel over the HUD), and end screens via headless renders.

---

## [Unreleased] — Sally controls + asset cleanup

### Added
- **Two new movement modes for Sally** (alongside click-to-move):
  - **Arrow keys** steer her directly; held keys become a per-frame direction
    vector that overrides the click target. Releasing pins the seek target to her
    current spot so she stops instead of darting back to a stale click point.
  - **Click-drag** retargets her to the latest cursor position every frame while
    the button is held (`PlayScreen._mouse_held`, `_held_dirs`;
    `Player.set_move_dir`). Both modes still flow through obstacle move-and-slide
    (verified they can't tunnel into furniture). Help/start controls text updated.

### Changed
- **Retired the original art set.** PixelLab is now the sole art set, so the
  redundant originals were deleted: `assets/{characters,npc,obstacles,maps,
  endscreens}` (124 files; `maps` included the now-unused `introscreen.png`, since
  the start screen uses `pixellab/startscreen/backyard.png`). Removed the empty
  `pixellab/{powerups,surprises/*}` `.gitkeep` stub dirs.
- `assets/` now keeps only what PixelLab doesn't provide — **fonts, sounds,
  powerups, surprises** — which the per-asset fallback in `game.assets._art` still
  sources when pixellab/ has no PNGs. The resolver and `CT2_ART_SET` stay in place
  (the fallback is load-bearing for powerups/surprises); `config.py` comment
  updated to note "original" is no longer a full art set.

### Verified
- 138 tests pass (added drag-follow, arrow-move, arrow-release-stop control
  cases). Headless smoke built all 4 levels + every screen and loaded
  powerups/surprises/splat from `assets/` — no missing-asset crashes.

---

## [Unreleased] — Gameplay polish: collision, music, splat surprise, HUD

### Fixed
- **Obstacle collision now matches the art exactly.** Obstacles previously used a
  fixed `100×150` rectangular hitbox while their sprite was drawn (via
  `Group.draw`) at `rect.topleft` — so furniture (and tenants) were drawn ~40–60px
  down-right of where they actually collided. Obstacles now collide on their
  **exact image silhouette** (`pygame.mask.from_surface`) and every entity is
  drawn **centered on its hitbox**, so art and collision finally line up. Verified
  with mask/bbox overlays on all four levels (incl. the japanese room).
- **Characters no longer get stuck on furniture.** Collision resolution moved from
  per-frame push-out to **move-and-slide** (`PlayScreen._slide_out`): a mover that
  hits an obstacle keeps the free axis and slides around the silhouette; a
  mask-gated eject recovers anything that starts inside a shape.
- **Slowed tenants no longer freeze.** NPC movement now integrates in a **float
  position accumulator** (rounded into `rect` only for draw/collision), so
  sub-pixel steps (a slowed tenant moves ~0.9px/frame) accumulate instead of
  truncating to zero. External rect moves (slide/separation/clamp) fold back in.

### Added
- **Splat surprise mechanic.** When a tenant steps over a *powered* ("whippy
  steaming") surprise, it visually transforms into a **splat** (the previously
  unused 18-frame `splat_idle` animation) and **slows the tenant to 40% speed for
  ~3s**, then it fades from the floor (~3s). One-shot trap; unpowered surprises are
  inert. New `Poo.splat()`, `NPC.apply_slow()`, `assets.splat_dir()`, and
  `NPC_SLOW_SECONDS` / `NPC_SLOW_MULTIPLIER` / `SPLAT_FADE_SECONDS` config.
- **Per-level continuous music.** A level's track now starts on its transition card
  and plays uninterrupted through gameplay and the complete card (`play_music` is
  idempotent — re-requesting the current track is a no-op). Thunderstruck carries
  the Start screen through Level 1's complete card; *I Wanna Rock* covers Level 2;
  Level 3 is silent (no track yet); *Angel* covers Level 4 and carries through the
  win screen onto the leaderboard. Losing still cuts the music (unchanged).

### Changed
- **Transition card copy rewritten** per level: intro ("transition") and complete
  subtitles now themed to each room (e.g. gym → "Gains Made, Mess Made" /
  "Number Two: Mission Accomplished"; garden → "The Final Defecation" /
  "Fertile Ground, Fertile Hound").
- **Help button repositioned** from screen-center (where it overlapped the
  INVINCIBLE! text) into the gap between the score and the centered INVINCIBLE!
  text (left edge x=260, measured to clear both).

### Verified
- 135 tests pass (added `tests/test_poo_splat.py`, `tests/test_npc_slow.py`, plus
  splat-integration cases in `tests/test_play.py`). Visually confirmed via headless
  renders: level-3 collision alignment, HUD with `Score: 300` + INVINCIBLE!, and a
  powered surprise → splat + tenant slow.

---

## [Unreleased] — Animated side-scroller start screen (art_startscreen)

### Added
- **Animated title scene** (`art_startscreen`): `StartScreen` now plays a side-scroller
  backyard where **Sally runs in place fleeing right while all four tenants (char1/2/3 + the
  T-rex) chase her**, a butterfly flits past every few seconds, and a googly-eyed "surprise"
  pops up in the background. The title + blurb + controls panel and "Press Space" prompt sit
  on top. Activates when `pixellab/startscreen/backyard.png` exists; otherwise falls back to
  the original scrolling introscreen (original art set unaffected).
- Art at `pixellab/startscreen/` — `backyard.png`, `butterfly.png`, `surprise.png`, and
  per-runner right-facing run cycles `{sally,char1,char2,char3,trex}/{0..3}.png` (PixelLab
  side-view characters + `running-4-frames` east). Provenance in
  `pixellab/_src/startscreen/manifest.json`.

- Runners are scaled by their *visible* height (transparent padding cropped, shared union
  bbox for planted feet) at sensible proportions — a small terrier, adult tenants, a looming
  T-rex. The grass surprise scrolls left with the background so it reads as a world object.

### Verified
- 129 tests pass; rendered + approved in-engine (`testscreenshots/pixellab_startscreen.png`).

### Beads
- `art_startscreen` (`ChocoThunder2-ash`) **closed** — this **completes the Artwork Upgrade
  epic `ChocoThunder2-41u`** (backgrounds, characters, obstacles, transitions, win/lose,
  leaderboard, powered Sally, start screen all shipped).

---

## [Unreleased] — Win/Lose/Leaderboard art + powered Sally

### Added
- **Illustrated win & lose screens** (`art_winscreen`, `art_losescreen`): `EndScreen` now shows
  themed PixelLab cards at `pixellab/endscreens/{win,lose}.jpg` — win = Sally celebrating on a
  trophy podium; lose = a red barn farm (matching the original "sent to the farm" gag). The
  overlay auto-lightens for the pre-dimmed pixellab cards (heavy overlay kept for the original
  photos). ART_SET-aware with fallback to the originals.
- **Leaderboard backdrop** (`art_leaderboard`): `ScoreboardScreen` now paints a dimmed
  trophy hall-of-fame behind the top-10 table (`pixellab/ui/scoreboard.jpg`, via
  `assets.ui_image()`), with Sally peeking in the corner; falls back to the solid `DARK_GREY`.
- **Powered-up Sally spritesheet** (`art_powered_sally`): a distinct caped, gold-glowing
  "Super Sally" 4-direction walk at `pixellab/characters_powered/`. `Player` loads it alongside
  the normal sheet and swaps to it while `is_invincible` (the cake window), falling back to the
  normal sprite when the active art set has no powered art (original set unaffected).
- `scripts/compose_screens.py` — compositor for the three cards (scene + shared Sally + vignette
  + per-screen text scrims). Provenance + object/character IDs in
  `pixellab/_src/screens/manifest.json`.

### Verified
- 129 tests pass. Rendered in-engine under `CT2_ART_SET=pixellab`: win/lose/leaderboard cards
  (`testscreenshots/pixellab_{win,lose,scoreboard}.png`) and the powered-Sally swap during
  invincibility (`testscreenshots/pixellab_player_powered.png`).

### Beads
- `art_winscreen` (`-h1x`), `art_losescreen` (`-suw`), `art_leaderboard` (`-6no`),
  `art_powered_sally` (`-q1u`) **closed**.

---

## [Unreleased] — Transition art (Story 16) + pixellab default + spawn fixes

### Added
- **Premium per-level transition/intro cards** (`art_transitions`, Story 16): each level's
  `PreLevelScreen` (intro) and `TransitionScreen` (complete) now show a themed **3/4-view
  illustrated scene with Sally** (living room / gym / Japanese room / backyard) instead of a
  plain black card. One standalone Sally sprite is composited into every dog-less scene so she
  is **identical across all levels**, then dimmed + vignetted with a text scrim so the (unchanged)
  card font/colours stay readable. Wired via the `ART_SET` toggle — `original` keeps the plain
  black cards. Art at `pixellab/transitions/level{1..4}.png`; `assets.transition_image()` +
  `screens.transition.draw_backdrop()` load it with a black fallback.
- `scripts/compose_transition.py` — compositor: scene + Sally (border flood-fill keys out
  PixelLab's near-white bg) + vignette + scrims → 1200×720 card. Raw inputs + IDs under
  `pixellab/_src/transitions/` (`manifest.json`).

### Changed
- **`CT2_ART_SET` now defaults to `pixellab`** (the iOS-bound look). The ground-truth `original`
  set is untouched and still selectable via `CT2_ART_SET=original`. (Refines PRD Stories 13–17,
  which described `original` as the default; see prd.md note.)

### Fixed
- **Obstacles no longer spawn on the player** and are **spaced apart** for manoeuvre room:
  `PlayScreen._pick_obstacle_positions` chooses points ≥`OBSTACLE_PLAYER_CLEARANCE` from the
  centre spawn and ≥`OBSTACLE_MIN_SPACING` apart (retries shuffles for a fully-spaced set).
- **NPCs no longer spawn inside an obstacle / on the player / on each other**:
  `PlayScreen._npc_spawn_pos` retries until the spawn is clear by `NPC_SPAWN_CLEARANCE`.
  Verified: 400 builds (both art sets × 4 levels × 50 seeds) → 0 violations, min obstacle
  spacing 260px.

### Beads
- `art_transitions` (`ChocoThunder2-2rm`) **closed**.

---

## [Unreleased] — Artwork Upgrade (PixelLab): obstacles shipped (T133) + WASM follow-ups

### Added
- **16 upgraded obstacle/furniture sprites** (PixelLab `create_map_object`, bold/saturated,
  low top-down, transparent) at `pixellab/obstacles/<room>/`, selected under `CT2_ART_SET=pixellab`:
  - `genericroom` (L1): sofa, tv_stand, **bookshelf**, dining_table
  - `gym` (L2): stationary_bike, weight_bench, single_dumbbells, squat_rack
  - `japaneseroom` (L3): chabudai, byobu, tansu, vase
  - `garden` (L4, **new room**): bench, bbq_grill, fountain, shrub
- **New `garden` obstacle room for Level 4** — `game/levels.py` repoints L4 `obstacle_room`
  `genericroom`→`garden` (its background is a backyard). `assets/obstacles/garden/` mirrors
  `genericroom` so the **original art set's L4 is unchanged**.
- **Proportional obstacle rendering** — drawn size decoupled from the collision hitbox:
  `assets.load_image_fit()` scales each sprite to fit `config.OBSTACLE_RENDER_MAX` (160²)
  preserving aspect (so a dining table reads long, a vase tall), while the hitbox stays
  `OBSTACLE_SIZE` (100×150). Per-object overrides (`OBSTACLE_RENDER_OVERRIDES`) make hero
  pieces bigger/smaller: dining_table, tv_stand, sofa up; bbq_grill down. Affects both art
  sets' *rendering* (originals were previously squished to a fixed box); collisions unchanged.
- **Central obstacle placement** — `OBSTACLE_X/Y` pulled into a central band (430–770 × 250–550)
  so furniture no longer clashes with the perimeter wall/decor baked into the room backgrounds.
- **NPC separation rule** — overlapping tenant hitboxes now push apart (`PlayScreen._separate_npcs`,
  min-overlap axis, 4 relaxation passes) so tenants don't stack, then clamp inside the play bounds.
- **4th tenant on Level 4** — added `char1` to L4 `npcs` → 4 tenants under the pixellab set
  (char1–4, incl. the T-rex); the original set shows 3 (char4 has no original art and is skipped).
- **WASM follow-ups merged**: **T114** converted all audio MP3→OGG (Vorbis) and re-enabled
  `AudioManager` under Emscripten (single OGG path desktop+web; MP3s removed); **T115** persists
  high scores via browser `localStorage` under WASM (`platform.window.localStorage`), desktop
  file path unchanged.
- `scripts/render_levels.py` — dev tool: headless-renders every level through the real
  `PlayScreen` to `testscreenshots/<prefix>_level{1..N}.png` for the active art set.
- Provenance (16 object IDs + bookshelf v1→v3 history) in `pixellab/_src/obstacles/manifest.json`
  and `sbom.md §4c`.

### Verified
- 129 tests pass. In-engine render of all 4 levels under `CT2_ART_SET=pixellab`
  (`testscreenshots/pixellab_obstacles_level{1..4}.png`): centered proportional furniture,
  L4 garden + 4 tenants. NPC separation stress test: 6 overlapping pairs → 0 after updates.

### Beads
- `art_obstacles` (`ChocoThunder2-cgo` / T133) **closed**; `T114` (`-ewp`) and `T115` (`-ag6`) **closed**.

---

## [Unreleased] — Artwork Upgrade (PixelLab): characters shipped (T131)

### Added
- **Upgraded character spritesheets** (4-direction, 4-frame walk cycles, low top-down /
  selective outline / detailed shading): **Sally** the player at `pixellab/characters/`
  (now a cute white **terrier** via PixelLab's quadruped dog template), and tenant NPCs at
  `pixellab/npc/char{1..4}/` — char1 casual man, char2 businessman, char3 older man, and
  **char4 a green T-rex** (a bonus tenant on Level 4). Selected under `CT2_ART_SET=pixellab`,
  per-character fallback to `assets/` otherwise.
- `scripts/fetch_character.py` — dev tool: downloads a PixelLab character's bulk zip and writes
  the walk frames into the game's `down/left/right/up` layout (maps south/north/east/west).
- **char4 (T-rex) wiring** — added to Level 4's `npcs` in `game/levels.py`; `game/assets.py`
  gains `npc_available()` and `PlayScreen` skips tenants with no art in the active set, so the
  **original art set is unchanged** (Level 4 still shows char2+char3, no crash) while the
  pixellab set adds the T-rex.
- Provenance (character IDs) recorded in `sbom.md §4c`.
- **Realistic character proportions**: decoupled drawn size from the collision hitbox —
  `PLAYER_RENDER_SIZE` (115) and `NPC_RENDER_SIZE` (144) drive the sprite while
  `PLAYER_SIZE`/`NPC_SIZE` remain the hitboxes (gameplay feel unchanged). Sally (dog) is
  4/5 the NPC size; tenants now read human-height against the furniture. Affects both art sets.

### Verified
- 125 tests pass (original mode); in-engine render of all 4 levels under `CT2_ART_SET=pixellab`
  shows Sally + tenants walking, Level 4 includes the T-rex
  (`testscreenshots/pixellab_chars_level{1..4}.png`).

### Beads
- `art_characters` (`ChocoThunder2-hy3` / T131) **closed**.

---

## [Unreleased] — Artwork Upgrade (PixelLab): backgrounds shipped (T131)

### Added
- **4 upgraded level backgrounds** at `pixellab/maps/level{1..4}.png` (1184×736): themed
  top-down rooms — L1 house (oak + persian rug), L2 gym (rubber + blue mat), L3 japanese
  (wood + tatami), L4 backyard (grass + flagstone). Each = a 32px PixelLab Wang floor tileset
  + a procedural themed wall band + ~7 perimeter decor objects (wall-art on the back wall,
  floor furniture along the edges), all baked-in and non-collidable. Selected at runtime via
  `CT2_ART_SET=pixellab`; absent files fall back to `assets/maps/`. Collidable furniture stays
  T133.
- `scripts/compose_level.py` — dev/build compositor: floor (corner autotiling) + color-driven
  wall band (top back wall, side/bottom baseboards, doorway gap) + decor blitted from a per-level
  `manifest.json`. Headless pygame, no new deps. (Supersedes the floor-only
  `scripts/compose_backgrounds.py`.)
- `pixellab/_src/level{1..4}/` — committed raw floor tilesets + metadata + `decor/*.png` +
  `manifest.json` (placement/scale) for provenance and resumability.
- Provenance recorded in `sbom.md §4c` (v3 floor tileset IDs + decor approach).

### Verified
- In-engine render of all 4 levels through the real `PlayScreen` code path with
  `CT2_ART_SET=pixellab` (screenshots in `testscreenshots/pixellab_level{1..4}_verified.png`).
  `ART_SET` default stays `original`, so normal play is unchanged.

### Beads
- `art_backgrounds` (`ChocoThunder2-bez` / T131) **closed**; unblocks the remaining four art
  stories (characters, obstacles, transitions, start screen).

---

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
