#!/usr/bin/env bash
# Build the pygbag/WASM bundle into build/web/ (T113).
#
# We do NOT run `pygbag --build` here, for two reasons found the hard way:
#   * pygbag's loader always sources assets/main.py from the archive, so a
#     root-dir build packs the DESKTOP main.py as the web entry — its
#     `if __name__ == "__main__"` guard never fires and the game silently
#     never starts (gray screen).
#   * pygbag's template fetch retries forever on macOS (urllib SSL
#     CERTIFICATE_VERIFY_FAILED), hanging the build after packing.
# Instead: stage web_main.py AS main.py, tar the staging tree ourselves, and
# pair it with the committed pygbag 0.9.3 loader in web/.
#
# COPYFILE_DISABLE=1 keeps macOS AppleDouble (._*) files out of the archive.
# Python's tarfile extracts those as real files in the browser FS, where they
# shadow real art in the obstacle glob and crash pygame.image.load.
set -euo pipefail
cd "$(dirname "$0")/.."

STAGE=$(mktemp -d)
trap 'rm -rf "$STAGE"' EXIT

mkdir -p "$STAGE/assets"
cp web_main.py "$STAGE/assets/main.py"
cp -R game assets pixellab "$STAGE/assets/"
find "$STAGE" -name '__pycache__' -type d -prune -exec rm -rf {} +

mkdir -p build/web
COPYFILE_DISABLE=1 tar -C "$STAGE" -czf build/web/chocothunder2.tar.gz assets
rm -f build/web/chocothunder2.apk
(cd "$STAGE" && zip -qr - assets) > build/web/chocothunder2.apk
cp web/index.html web/favicon.png build/web/

# Local serving: on localhost the loader rewrites the package CDN to
# http://localhost:8000/cdn/, so mirror the pygame-ce wheel beside the bundle
# and serve build/web on port 8000 specifically.
mkdir -p build/web/cdn/cp312
WHEEL=pygame_ce-2.5.7-cp312-cp312-wasm32_bi_emscripten.whl
if [ ! -f "build/web/cdn/cp312/$WHEEL" ]; then
    curl -sSL "https://pygame-web.github.io/cdn/cp312/$WHEEL" \
        -o "build/web/cdn/cp312/$WHEEL"
fi

echo "Built build/web/ — serve with: python3 -m http.server 8000 -d build/web"
