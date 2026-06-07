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

---

## 5. Documentation & Resources

- pygame-ce: https://pyga.me/docs/
- pygame_gui: https://pygame-gui.readthedocs.io/
- FastMCP (mcp package): https://github.com/jlowin/fastmcp
- pytest: https://docs.pytest.org/
- Python: https://docs.python.org/3/
