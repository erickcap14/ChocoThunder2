<img src="web/icons/icon-192.png" align="right" width="96" alt="App icon — Sally on grass">

# Sally's Revenge

You are **Sally**, an adorable white terrier. Sneak around the house, leave
"chocolate surprises" for points, eat cake for a real invincibility boost, and
dodge the tenants — across four themed levels (living room, gym, Japanese
room, backyard… featuring a T-rex tenant).

Runs as a **native desktop game** (Python + pygame-ce), in the **browser**
(WebAssembly via pygbag), and as an **iPad app** (Capacitor shell or
installable PWA) with a full touch-control layer.

An improved rebuild of the original *Chocolate Thunder* class project. The
original in `../ChocolateThunder/` is **ground truth** (feel, audio) and is
never modified; the art was upgraded to a PixelLab-generated set.

## Screenshots

| | |
|:---:|:---:|
| <img src="testscreenshots/touch_btn_start.png" width="420" alt="Animated start screen"><br>**Start screen** — Sally flees the tenants (and the T-rex) | <img src="testscreenshots/t136_pixellab_level1.png" width="420" alt="Level 1 gameplay"><br>**Level 1** — leave surprises, dodge the tenant |
| <img src="testscreenshots/touch_btn_prelevel.png" width="420" alt="Level intro card"><br>**Level intro card** (touch build: tap buttons) | <img src="testscreenshots/t136_pixellab_level4.png" width="420" alt="Level 4 garden"><br>**Level 4** — the backyard, 4 tenants incl. the T-rex |
| <img src="testscreenshots/pixellab_win.png" width="420" alt="Win screen"><br>**Win screen** | <img src="testscreenshots/pixellab_scoreboard.png" width="420" alt="High scores"><br>**Top-10 leaderboard** |

## Requirements

- **Python ≥ 3.10** (developed on 3.13). Uses `pygame-ce` — do not also install upstream `pygame`.
- For the iPad app only: macOS with Xcode (free), Node.js, and an iOS
  simulator runtime (`xcodebuild -downloadPlatform iOS`).

## Setup

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## How to play

| Desktop | iPad / touch |
|---|---|
| Click (or click-drag, or arrow keys) — move Sally | Tap or drag — Sally follows your finger |
| **Space** — leave a chocolate surprise | **Tap Sally** — she puffs up and leaves a surprise |
| Eat a cake — invincibility (+5 per surprise while powered) | same |
| **Easy**: tenants can't end the game · **Hard**: caught = game over | same — pick on the start screen |

Tenants step on a *powered* surprise → splat, and they slow to a crawl.
Survive each level's countdown to advance; top-10 scores persist.

## Run it

```bash
./run.sh          # desktop game            (zsh alias: ct2_desktop)
./run_test.sh     # 16-screen UI walkthrough (zsh alias: ct2_test)
./run_ipad.sh     # build + launch in iPad simulator (zsh alias: ct2_ipad)
```

**Browser (WASM):** build once, then serve — port 8000 is required:

```bash
./scripts/build_web.sh
python3 -m http.server 8000 -d build/web    # open http://localhost:8000
```

The bundle is fully self-contained (the pygbag runtime is mirrored into
`build/web/cdn/` at build time) — the shipped game makes **zero network
requests**.

**iPad simulator:** `./run_ipad.sh` builds the web bundle, wraps it with
Capacitor, boots the simulator (default *iPad Air 11-inch (M2)* — override
with `CT2_IPAD_DEVICE="iPad Pro 13-inch (M4)"`), installs, and launches.
The game takes ~20 s to boot to the start screen.

## Install on a real iPad

Two routes — full details in [`ios-app/README.md`](ios-app/README.md).

### Route 1 — native app via free provisioning (no paid Apple account)

A free Apple ID can sideload the app onto your own iPad. It expires after
**7 days**; re-deploy from Xcode to renew.

1. `./scripts/build_ios.sh` — builds the web bundle and stages it into the
   Xcode project.
2. `open ios-app/ios/App/App.xcodeproj`
3. Xcode ▸ Settings ▸ **Accounts** ▸ “+” ▸ sign in with your Apple ID
   (creates a free *Personal Team*).
4. Select the **App** target ▸ *Signing & Capabilities* ▸ check
   **Automatically manage signing** ▸ Team = your Personal Team.
   (If the bundle id collides, tweak it — e.g. append `.dev`.)
5. Connect the iPad via USB, unlock it, tap **Trust**.
6. On the iPad: Settings ▸ Privacy & Security ▸ **Developer Mode** → on
   (appears after the first deploy attempt; requires a reboot).
7. Pick the iPad as the run destination in Xcode and press **Run** (⌘R).
8. First launch only: Settings ▸ General ▸ **VPN & Device Management** ▸
   trust your developer certificate.

### Route 2 — PWA from Safari (no Xcode, no expiry)

1. `./scripts/build_web.sh`
2. Serve it where the iPad can reach it:
   `python3 -m http.server 8000 -d build/web` (Mac and iPad on the same Wi-Fi).
3. On the iPad, open `http://<your-mac-ip>:8000` in Safari.
4. **Share ▸ Add to Home Screen.** The service worker precaches everything,
   so the installed app runs fully offline afterwards.

## Test

```bash
pytest -q     # 176 headless pygame unit + MCP-verify tests
```

Screenshots from MCP-verify tests are written to `testscreenshots/`
(committed to git).

## Game State MCP (automated control & verification)

A FastMCP sidecar lets Claude Code drive the running game via file-based IPC.

```bash
python -m mcp_server.server     # start the MCP server (also wired via .claude/settings.json)
python main.py --smoke          # headless harness to validate the bridge without a window
```

Tools include `get_state`, `jump_to_{start,transition,running,end,scoreboard}`,
`set_level`, `spawn_powerup`, `spawn_npc`, `drop_poo`, `set_invincible`,
`toggle_music`, `toggle_sfx`.

## Project layout

| Path | Purpose |
|------|---------|
| `main.py` | Desktop entry point + game loop (`write_state` → `poll_mcp_command` each frame) |
| `web_main.py` | WASM/browser entry point (async loop) |
| `game/` | Engine: config, state machine, entities, screens, levels, audio, scores |
| `pixellab/` | PixelLab-generated art set (maps, characters, obstacles, transitions, UI) |
| `assets/` | Ground-truth fonts/audio + fallback art |
| `web/` | pygbag loader template, PWA manifest, icons |
| `ios-app/` | Capacitor iPad shell (Xcode project, SPM) |
| `scripts/` | `build_web.sh`, `build_ios.sh`, `make_icons.py`, render/dev tools |
| `mcp_server/` | `state_bridge.py` (IPC) + `server.py` (FastMCP tools) |
| `tests/` | Pure unit tests + MCP-verify (screenshot) tests |
| `testscreenshots/` | Committed verification screenshots |
| `.implementations/` | Runtime IPC + logs (gitignored) |

See `.claude/prd.md` for the full design and fixed-bug appendix, and
`.claude/changelog.md` for the development history.
