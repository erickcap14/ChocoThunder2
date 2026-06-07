# Infrastructure Blueprint

Purpose: This file describes the project's technical foundation, including the method of hosting, the programming languages, the coding standards, and how to run the code.

---

## What We're Building

- **Programming Language:** Python 3.13
- **Main Framework/Tool:** `pygame-ce` (community edition) for the game engine; `pygame_gui` for any managed UI widgets; `mcp` / `FastMCP` for the Game State MCP harness sidecar.
- **A Quick Summary:** A single-player, top-down 2D arcade game (ChocolateThunder2: ElectricBoogaloo) that runs entirely on a local machine — no network, no server, no browser.

---

## How to Run it on Your Computer

- **Installation Command:** `pip install -r requirements.txt`
- **Startup Command:** `./run.sh` (or `python main.py` directly)
- **Local Address:** Not applicable — this is a native pygame window, not a web app.

> **Note:** `pygame-ce` and upstream `pygame` collide; never install both. Always use `pygame-ce` as specified in `requirements.txt`.

> **Phase 7 exception (WASM/browser target):** The desktop-only "no browser" statement
> above describes the v1.0.0 shipped product. Phase 7 (iPad packaging) introduces a
> **secondary build target**: the game is compiled to WebAssembly with `pygbag` (build-only
> tool, see `sbom.md`) and runs in a browser via `web_main.py` (`App.run_async`). The MCP
> harness is **disabled** under WASM (no sidecar process / shared filesystem in the browser
> sandbox); the desktop build and its MCP path are unchanged. Browser-build verification uses
> Playwright, not pytest/MCP. This is a sanctioned exception, not a change to the desktop runtime.

---

## Project Architecture & Conventions

- **Framework:** Python / pygame-ce (no web framework)
- **Directory Structure:**
  - **`game/`** — All runtime game code.
    - `config.py` — Single source of truth for all constants, tuning values, colours, and on-disk paths.
    - `state_machine.py` — `GameState` enum + `StateMachine.force_state`.
    - `app.py` — `App` class + main game loop (wires `write_state` → `poll_mcp_command` each frame).
    - `assets.py` — Cached image/sound loaders; headless-safe `convert`.
    - `sprites.py` — `DirectionalSprite`, `FrameSprite`, `ImageSprite` base classes.
    - `audio.py` — `AudioManager` (per-level music, SFX, `toggle_music`/`toggle_sfx`).
    - `entities/` — `Player`, `Poo`, `Obstacle`, `NPC`, `PowerUp` entities.
    - `screens/` — One file per screen: `start.py`, `play.py`, `transition.py`, `end.py`, `scoreboard.py`.
    - `levels.py` — `LevelSpec` data classes; adding a level = appending one entry here + dropping assets.
  - **`assets/`** — All normalized game assets (lowercase tree). Never modify the original `../ChocolateThunder/`.
  - **`mcp_server/`** — `state_bridge.py` (file IPC) + `server.py` (FastMCP, 13 tools).
  - **`.implementations/`** — IPC JSON files written at runtime (`game_state.json`, `game_command.json`, `test_log.json`). **Git-ignored.** Never commit this directory.
  - **`tests/`** — `conftest.py`, `logger.py`, and all `test_*.py` files.
  - **`testscreenshots/`** — MCP-verify screenshots saved by tests. Committed to git as visual evidence.
  - **`docs/`**, **`agents/`**, **`commands/`**, **`prompts/`**, **`templates/`** — Project-level documentation and agent tooling.

---

## Code Generation Style Guide

When writing or modifying code, adhere to the following standards:

- **Variable / function naming:** `snake_case` throughout (Python convention).
- **Class naming:** `PascalCase`.
- **Constants:** `UPPER_SNAKE_CASE`, defined in `game/config.py` — never hardcoded elsewhere.
- **File naming:** `snake_case.py`.
- **Comments:** Only when the *why* is non-obvious. No docstring blocks on obvious code.
- **Linting:** Run `python -m pytest` before committing to catch import errors and basic test regressions.
- **Import style:** Absolute imports; avoid star imports.
- **No tkinter:** The original's dual-toolkit handoff is removed. All UI is pygame / pygame_gui only.
- **No `if/elif` level switches:** Levels are purely data-driven via `LevelSpec` in `game/levels.py`.

---

## Where it Lives on the Internet & Who its Friends Are

- **Hosting Provider:** Local machine only — this is a native desktop application, not deployed anywhere.
- **External Services:** None. No network calls, no analytics, no cloud backend. The game is fully offline.

---

## Where Your Data is Stored

- **Data Storage Method:** A single plain-text file, `scores.txt`, at the project root. Each line is `name,score`. The high-score parser tolerates malformed lines (Fixed Bug #5 from the original).
- **Important Notes:** `scores.txt` is public, local data — no PII, no encryption needed.
- **IPC files:** `.implementations/game_state.json` and `.implementations/game_command.json` are runtime-only scratch files; they are gitignored and ephemeral.
