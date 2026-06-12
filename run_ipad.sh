#!/usr/bin/env bash
# Test the iPad ship: build the Capacitor app and run it in the iOS simulator.
# Pairs with the `ct2_ipad` zsh alias (like run.sh/ct2_desktop, run_test.sh/ct2_test).
#
# Override the simulator with CT2_IPAD_DEVICE, e.g.:
#   CT2_IPAD_DEVICE="iPad Pro 13-inch (M4)" ./run_ipad.sh
set -euo pipefail
cd "$(dirname "$0")"

DEVICE="${CT2_IPAD_DEVICE:-iPad Air 11-inch (M2)}"
APP_ID="com.erickcap.chocothunder2"
APP_PATH="ios-app/ios/App/build/Build/Products/Debug-iphonesimulator/App.app"

./scripts/build_ios.sh

# Boot is a no-op error if already booted; bootstatus blocks until ready.
xcrun simctl boot "$DEVICE" 2>/dev/null || true
xcrun simctl bootstatus "$DEVICE" -b >/dev/null

xcrun simctl terminate "$DEVICE" "$APP_ID" 2>/dev/null || true
xcrun simctl install "$DEVICE" "$APP_PATH"
open -a Simulator
xcrun simctl launch "$DEVICE" "$APP_ID"

echo "Launched $APP_ID on '$DEVICE' — the game takes ~20s to boot to the start screen."
