#!/usr/bin/env bash
# Build the Capacitor iPad app (T112): web bundle -> ios-app/www -> native
# project -> App.app for the iOS simulator.
#
# GOTCHA: the web bundle is baked into the .app at xcodebuild time (via
# ios/App/App/public). Changing game/, web/, or scripts/build_web.sh requires
# rerunning this whole script AND reinstalling the app — `npx cap copy` alone
# does not update an already-built .app.
#
# Run the result on the booted simulator:
#   xcrun simctl boot "iPad Air 11-inch (M2)"
#   xcrun simctl install "iPad Air 11-inch (M2)" \
#       ios-app/ios/App/build/Build/Products/Debug-iphonesimulator/App.app
#   xcrun simctl launch "iPad Air 11-inch (M2)" com.erickcap.chocothunder2
#
# For a real iPad (free provisioning), see ios-app/README.md.
set -euo pipefail
cd "$(dirname "$0")/.."

./scripts/build_web.sh
rsync -a --delete build/web/ ios-app/www/
(cd ios-app && npx cap copy ios)
(cd ios-app/ios/App && xcodebuild -project App.xcodeproj -scheme App \
    -destination 'generic/platform=iOS Simulator' \
    -derivedDataPath build CODE_SIGNING_ALLOWED=NO build | tail -1)

echo "Built ios-app/ios/App/build/Build/Products/Debug-iphonesimulator/App.app"
