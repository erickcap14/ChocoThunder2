# Product Requirements Document

Purpose: This file defines what we are building and for whom, focusing on the project's features, goals, and user experience.

> ChocolateThunder2: ElectricBoogaloo is a ground-up, improved rebuild of the original
> CS3021 class project **Chocolate Thunder**. The original game (in
> `../ChocolateThunder/`) is treated as **ground truth** for art, audio, and game feel —
> every sprite, spritesheet, sound, and music track is reused unchanged. We keep what made
> it fun, fix the bugs, delete the academic scaffolding, make levels easy to add, and wrap
> it in an automated test harness so it can keep growing safely.

---

## 1. The Big Picture (What are we making?)

* **Project Name:** ChocolateThunder2: ElectricBoogaloo
* **One-Sentence Summary:** You play Sally, an adorable white terrier, sneaking around a
  house leaving "chocolate surprises" everywhere for points while dodging the tenants who
  will send her to "the farm" if they catch her.
* **Who is this for?** Fans of light, silly arcade-style score-chasers; the original
  authors and players who want a cleaner, less buggy, extensible version.
* **What this app will NOT do:**
  * No online/multiplayer — single-player, local only.
  * No accounts, ads, microtransactions, or network calls.
  * No new art style *by default* — it deliberately reuses the original's sprites and audio.
    *(Exception: an art-upgrade phase adds an **optional, toggle-selected**
    PixelLab-generated art set in `pixellab/`. The originals are never deleted and stay fully
    available via the toggle; as of Story 16 the `pixellab` set is the runtime default. See
    Stories 13–17.)*
  * No level *editor* in-app (levels are added by developers via a data manifest).

---

## 2. The Features (What can it do?)

Each story names a feature so it can be tracked as a beads issue (`bd create`). In this
repo, **Scribe owns beads writes** — run `/scribe` to create these.

* **Story 1 — `movement`:** As a player, I want to **click anywhere to send Sally walking
  there** so that I can navigate the room smoothly. *(Ground-truth control scheme.)*
* **Story 2 — `pooping`:** As a player, I want to **press Spacebar to leave a chocolate
  surprise** (with a short cooldown) so that I can rack up points.
* **Story 3 — `scoring`:** As a player, I want **+1 per normal surprise and +5 while
  powered up** so that I'm rewarded for risky, well-timed play.
* **Story 4 — `powerup_invincibility`:** As a player, I want **eating a cake to make Sally
  truly invincible for a few seconds** (tenants can't catch me, and my surprises are worth
  bonus points) so that the cake actually matters. *(In the original this was never
  implemented — it is a real feature here.)*
* **Story 5 — `npc_ai`:** As a player, I want **tenants that patrol randomly and chase me
  when I get close** so that avoiding them is tense and fair.
* **Story 6 — `obstacles`:** As a player, I want **furniture I can bump into without getting
  permanently stuck** so that collisions are an obstacle, not a softlock. *(Fixes an
  original bug.)*
* **Story 7 — `level_system`:** As a player, I want **multiple themed levels with a timer**
  so that the game has escalating variety; as a developer, I want **adding a level to be one
  data entry** so that the game is easy to extend.
* **Story 8 — `audio`:** As a player, I want **per-level music and sound effects I can
  toggle** so that the game feels alive and I stay in control.
* **Story 9 — `scoreboard`:** As a player, I want to **enter my name and see the top scores**
  at the end so that I can compete. *(Now in-engine, replacing the original tkinter popup.)*
* **Story 10 — `game_state_mcp`:** As a developer, I want a **Game State MCP server** that can
  jump the game to any screen and trigger actions so that Claude Code can drive and verify it.
* **Story 11 — `headless_tests`:** As a developer, I want **pytest unit tests + MCP-roundtrip
  screenshot tests** for every screen so that changes are verified automatically and saved to
  `testscreenshots/`.
### Artwork Upgrade Phase

> A polished art set generated with the **PixelLab MCP** (https://www.pixellab.ai/mcp), stored
> in a root-level **`pixellab/`** tree mirroring `assets/`, selected at runtime by an `ART_SET`
> toggle in `game/config.py`. PixelLab is a **dev-time generator** — only committed PNGs ship,
> so the offline-runtime and supply-chain rules in `security.md`/`sbom.md` are preserved. The
> ground-truth originals are never deleted and remain fully available via `CT2_ART_SET=original`;
> as of Story 16 the `pixellab` set is the runtime default (fully reversible). Stories are
> listed in implementation order.

* **Story 13 — `art_backgrounds`:** As a developer, I want **top-down tileset backgrounds
  generated via the PixelLab MCP into `pixellab/maps/`, selectable by an `ART_SET` config
  toggle**, so that levels have upgraded backgrounds without deleting the ground-truth originals.
  *(Establishes the `pixellab/` tree + toggle; provenance recorded in `sbom.md`.)*
* **Story 14 — `art_characters`:** As a player, I want **Sally and the tenant NPCs to use new
  PixelLab-generated directional spritesheets** (`pixellab/characters/`, `pixellab/npc/`) so
  that the characters look polished, with the originals still available via the toggle.
* **Story 15 — `art_obstacles`:** As a player, I want **refreshed furniture/obstacle sprites**
  (`pixellab/obstacles/<room>/`) so that each room matches the upgraded look.
* **Story 16 — `art_transitions`:** As a player, I want **upgraded transition-screen artwork**
  so that level intros feel premium instead of plain black cards.
* **Story 17 — `art_startscreen`:** As a player, I want a **polished start/title screen** so
  that the game's first impression feels premium.

---

## 3. The Look and Feel (How should it vibe?)

* **Overall Style:** Cartoonish, irreverent, lightly chaotic. Top-down 2D rooms with
  hand-drawn furniture and an animated terrier. Comedic tone (the whole game is a poop joke).
* **Main Colors:** White room backgrounds, brown UI accents (the title), black transition
  cards, white HUD text over a dark-grey panel. Inherited from the original art.
* **Key Screens:**
    * **Start / Title:** Scrolling title background, game blurb, control list, "Press
      Space Bar to Play."
    * **Level Transition:** Black card with the level name + a punny subtitle ("Working Out
      A Big One", "Sem-Poo-Ku"), "Press Enter to Continue."
    * **Play:** The room map, Sally, patrolling tenants, furniture, spawning cakes, dropped
      surprises, and a HUD showing Score + Timer.
    * **End:** Win or lose image, final score, thank-you text, prompt to view the scoreboard.
    * **Scoreboard:** Name entry + top-10 high scores (in-engine).

---

## Appendix A — Technical Architecture (added section)

> The base PRD template avoids tech detail, but this project's brief is explicitly
> technical, so the constraints are recorded here.

* **Engine:** Python 3.13 + `pygame-ce`. `pygame_gui` only where a widget genuinely helps.
  No tkinter (the original's two-toolkit handoff is removed).
* **Single source of truth:** `game/config.py` holds all tuning, paths, and colours.
* **Data-driven levels:** `game/levels.py` defines a `LevelSpec` per level (map image, NPC
  art, NPC count, obstacle room, music, transition text). **Adding a level = appending one
  entry + dropping assets** — no `if/elif` edits. The original hard-wired all of this.
* **Removed academic scaffolding:** the original's hand-rolled `FIFO` / `LinkedList` /
  `MyDictionary` (~700 lines) are replaced with native `dict` / `list` / `collections.deque`.
* **State machine:** `game/state_machine.py` (`GameState` enum + `force_state`) replaces the
  original string flags.
* **Testing harness (replaces Playwright):** Playwright is browser-only and cannot drive a
  pygame window, so testing is done with:
  * **Game State MCP** (`mcp_server/`): a FastMCP sidecar + file IPC (`.implementations/`).
    Claude Code calls tools (`jump_to_*`, `get_state`, `spawn_powerup`, `set_invincible`,
    `set_level`, `toggle_music/sfx`, …) to control the running game.
  * **pytest** with headless pygame (dummy SDL drivers): two files per screen —
    `test_<screen>.py` (pure logic) and `test_mcp_verify_<screen>.py` (bridge roundtrip +
    pixel sampling + screenshot saved to `testscreenshots/`).
* **Controls (decision):** click-to-move + spacebar-to-poop (the ground-truth scheme).
* **Asset contract:** all original sprites/sounds copied into `assets/` (normalized to a
  lowercase tree); the original folder is never modified.

## Appendix B — Bugs Fixed vs. the Original

1. Cake "invincibility" now actually protects the player (was cosmetic only).
2. Obstacle collision no longer permanently sticks the player.
3. Power-down / poo-cooldown use elapsed-time accumulators, not reused repeating timers.
4. Nonsensical `MOUSEBUTTONDOWN and != UI_BUTTON_PRESSED` event guard removed.
5. High-score parsing tolerates malformed lines instead of crashing.
6. Dead code removed (unused `copy` imports, unused idle moveset, duplicated obstacle block,
   boilerplate dunders).

