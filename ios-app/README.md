# ChocoThunder2 — iPad app (Capacitor shell, T112)

A native iOS wrapper around the pygbag/WASM web build. The WKWebView loads the
fully-offline bundle from `www/` (a copy of `build/web/` — game archive,
pygbag loader, CPython runtime, pygame wheel; zero network requests at play
time).

## Layout

- `capacitor.config.json` — app id `com.erickcap.chocothunder2`, webDir `www`,
  webview debugging + console forwarding enabled.
- `ios/App/` — the Xcode project (Capacitor 8, Swift Package Manager — no
  CocoaPods). Committed customizations:
  - `App/GameViewController.swift` — allows media playback without a user
    gesture so the game (and its music) starts without pygbag's
    "click/touch to start" gate.
  - `App/Info.plist` — landscape-only orientations.
  - `App/AppDelegate.swift` — Universal-Links proxy call removed (Capacitor
    8.4 template doesn't compile; the game never handles links).
  - App icon: Sally on grass (`scripts/make_icons.py`).
- `www/` and `ios/App/App/public/` are **generated** (gitignored) — rebuilt by
  `scripts/build_ios.sh`.

## Build (simulator)

```bash
./scripts/build_ios.sh
xcrun simctl boot "iPad Air 11-inch (M2)"
xcrun simctl install "iPad Air 11-inch (M2)" \
    ios-app/ios/App/build/Build/Products/Debug-iphonesimulator/App.app
xcrun simctl launch com.erickcap.chocothunder2
```

> The web bundle is baked into the .app at build time. After ANY change to
> `game/`, `web/`, or the build scripts, rerun `build_ios.sh` and reinstall —
> `npx cap copy` alone does not update an installed app.

## Install on a real iPad — free provisioning (no paid Apple account)

A free Apple ID can sign and sideload the app onto your own device. The app
expires after **7 days**; just re-deploy from Xcode to renew.

1. `./scripts/build_ios.sh` (ensures `www/` + `public/` are current).
2. `open ios-app/ios/App/App.xcodeproj` in Xcode.
3. Xcode ▸ Settings ▸ Accounts ▸ "+" ▸ sign in with your Apple ID
   (creates a free "Personal Team").
4. Select the **App** target ▸ *Signing & Capabilities* ▸ check
   *Automatically manage signing* ▸ Team = your Personal Team.
   If the bundle id collides, change it (e.g. append `.dev`).
5. Connect the iPad via USB, unlock it, tap **Trust** on the pairing prompt.
6. On the iPad enable **Developer Mode** (Settings ▸ Privacy & Security ▸
   Developer Mode — appears after the first deploy attempt; requires reboot).
7. Pick the iPad as the run destination in Xcode and press **Run** (⌘R).
8. First launch: Settings ▸ General ▸ VPN & Device Management ▸ trust your
   developer certificate.

Alternative without Xcode at all: the **PWA route** — serve `build/web/` over
the LAN (`python3 -m http.server 8000 -d build/web` — port 8000 required),
open it in Safari on the iPad, then *Share ▸ Add to Home Screen*. The service
worker precaches everything, so the installed PWA runs fully offline.
