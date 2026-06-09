# Software Bill of Materials (SBOM)

Purpose: This file lists all approved technologies, libraries, and dependencies for ChocolateThunder2: ElectricBoogaloo, with their pinned version ranges and licenses.

> **Conflict priority:** This file and `security.md` are Priority 1 — they override all other context documents. Do not add, remove, or upgrade a dependency without updating this file.

---

## 0. Technology Stack Overview

| Category | Component | Version Constraint | License | Usage |
|:---|:---|:---|:---|:---|
| **Language** | Python | `>=3.10, developed on 3.13` | PSF-2.0 | Runtime; `mcp` requires ≥3.10 |
| **Game Engine** | `pygame-ce` | `>=2.5, <3` | LGPL-2.1 | Rendering, event loop, audio mixer, sprite management |
| **UI Widgets** | `pygame_gui` | `>=0.6, <0.7` | MIT | Managed UI elements where a widget genuinely helps; depends on `pygame-ce` |
| **MCP Sidecar** | `mcp` (FastMCP) | `>=1.2` | MIT | Game State MCP server; `mcp.server.fastmcp.FastMCP` |
| **Test Runner** | `pytest` | `>=8.0` | MIT | Unit tests + MCP-roundtrip screenshot tests |

### Build Tooling (Phase 7 — WASM/iPad path, build-only)

These are **not** runtime dependencies. They live in `requirements-build.txt` (not
`requirements.txt`) and are installed only when producing the WebAssembly bundle.

| Category | Component | Version Constraint | License | Usage |
|:---|:---|:---|:---|:---|
| **WASM Packager** | `pygbag` | `>=0.9, <1` | MIT | Compiles the Python/pygame-ce game to WebAssembly (Emscripten + CPython-wasm) for the browser/iPad build. Build-only; never imported by the desktop game. |

> **LGPL obligation (now live for Phase 7):** the pygbag WASM artifact bundles `pygame-ce`
> (LGPL-2.1). Any distributed web/iPad build **must ship the LGPL-2.1 notice**. Confirm
> dynamic-vs-static linking obligations before public distribution (see §3).

---

## 1. Dependency Rules

- **`pygame-ce` vs upstream `pygame`:** These two packages share the `pygame` namespace and **will collide** if both are installed. Only `pygame-ce` is permitted.
- **`pygame_gui` depends on `pygame-ce`:** Installing `pygame_gui` pulls in `pygame-ce` automatically; never swap in upstream `pygame`.
- **No new runtime dependencies** without updating this file and reviewing licenses.
- **Dev-only tools** (linters, type checkers, formatters) do not need to appear here but should be separate from `requirements.txt` if added.

---

## 2. Version Management & Updates

- **Strategy:** Manual, conservative. Before bumping a version range, run the full `pytest` suite locally.
- **Major bumps** (e.g., `pygame-ce` 3.x) require explicit review — API surface changes are common between major versions.
- **Security scanning:** Run `pip-audit` periodically against `requirements.txt`. There are no network-facing dependencies, so the attack surface is low.

---

## 3. Licenses Summary

| License | Components | Obligation |
|:---|:---|:---|
| PSF-2.0 | Python | Attribution in distribution |
| LGPL-2.1 | pygame-ce | Dynamic linking OK; ship LGPL notice if distributing binaries |
| MIT | pygame_gui, mcp, pytest | Attribution in distribution |

> For the iPad packaging milestone (Phase 7), LGPL compliance for `pygame-ce` will need to be revisited if the pygbag/Capacitor build statically links the library.

---

## 4. Asset Provenance

### 4a. Fonts

| Font | Version | License | Source | Path |
|------|---------|---------|--------|------|
| Alfa Slab One | v21 | OFL-1.1 (SIL Open Font License) | Google Fonts / fonts.gstatic.com | `assets/fonts/AlfaSlabOne-Regular.ttf` |

The OFL-1.1 permits use, embedding, and redistribution in applications without fee, provided the font is not sold by itself.

### 4b. Sprites, Maps, Music & SFX

All game assets (sprites, spritesheets, maps, music, SFX) are reused unchanged from the original Chocolate Thunder CS3021 class project. They are stored in `assets/` (normalized lowercase tree). The original folder (`../ChocolateThunder/`) is never modified.

> **Audio format note (T114):** The music and SFX assets were transcoded from their original MP3 form to **OGG (Vorbis, `-q:a 5`)** via `ffmpeg`. The pygbag/WASM build ships an SDL_mixer without MP3 support, so MP3 decoding aborts the browser runtime; OGG decodes on both desktop pygame-ce and in-browser. The MP3 originals were removed from the repo after conversion. No new third-party dependency is introduced — the transcode is a one-time, dev-time step.

> Licensing of these assets follows the original course project's terms. They are not redistributed publicly and are used solely for this private rebuild.

### 4c. PixelLab-generated assets (Artwork Upgrade phase — pre-iOS ship)

| Asset set | Tool | License / Terms | Source | Path |
|------|------|---------|--------|------|
| Upgraded backgrounds, character/NPC spritesheets, obstacle sprites, transition + start-screen art | PixelLab MCP | Per PixelLab terms (confirm before public distribution) | https://www.pixellab.ai/mcp | `pixellab/` (mirrors `assets/` layout) |

> **Dev-time generation, not a runtime dependency.** PixelLab is invoked only during
> development to produce static PNGs that are committed to the repo. The shipped game performs
> **no outbound calls** to PixelLab and the `mcp` runtime dependency list above is unchanged.
> The PixelLab art set is **optional**, selected via the `ART_SET` toggle in `game/config.py`;
> the original assets in §4b remain the canonical default. Confirm PixelLab's output-licensing
> terms before any public distribution of the iOS build.

**Generated to date (T131 `art_backgrounds`):** the 4 level backgrounds at `pixellab/maps/level{1..4}.png`
(1184×736), each composed by `scripts/compose_level.py` from a 32px top-down Wang floor tileset + a
procedural themed wall band + per-level perimeter decor objects (all baked-in, non-collidable;
collidable furniture remains T133). Raw inputs + composition manifests are committed under
`pixellab/_src/level{1..4}/` for provenance/resumability. v3 floor tileset IDs (re-downloadable via
`get_topdown_tileset`): L1 house `0eda8992-8985-470d-8ec4-fa61a168cfb6`, L2 gym
`0caa1ea8-dada-413c-a8e9-44cf955cc5a0`, L3 japanese `5ee48de7-6ca0-4212-8a7d-25c0e27347c0`,
L4 backyard `7a2d7116-5e0a-4b20-bb06-1d3cab0837ab`. Decor objects generated via `create_map_object`
(object IDs recorded per level in `pixellab/_src/level*/manifest.json` git history; PixelLab map
objects auto-expire after 8h, so the committed PNGs are the durable artifact).

**Generated to date (T131 `art_characters`):** directional walk-cycle spritesheets (low top-down,
selective outline, detailed shading, 4 dirs × 4 frames) at `pixellab/characters/` (Sally) and
`pixellab/npc/char{1..4}/`, fetched via `scripts/fetch_character.py` (maps PixelLab
south/north/east/west → game down/up/right/left). PixelLab character IDs (re-fetchable via
`get_character`): Sally white terrier `11093d1b-d1c2-4d4d-a84a-61b3179a2cc7` (quadruped/dog);
char1 casual man `0a5b2a1a-76b4-439d-af85-27fd37cde5d4`; char2 businessman
`2cba1c7a-90a2-4ad1-927f-b20172652ffc`; char3 older man `c6ba5279-9d1e-4ed8-8d9f-dcb2e9e36f61`;
char4 T-rex `96ada53a-044d-41dd-a7c1-075e17f0623a`. char4 is a pixellab-only bonus tenant on
Level 4 — `game/levels.py` lists it but `PlayScreen` skips tenants with no art in the active set
(`assets.npc_available`), so the original set is unchanged.

---

## 5. Documentation & Resources

- pygame-ce: https://pyga.me/docs/
- pygame_gui: https://pygame-gui.readthedocs.io/
- FastMCP (mcp package): https://github.com/jlowin/fastmcp
- pytest: https://docs.pytest.org/
- Python: https://docs.python.org/3/
