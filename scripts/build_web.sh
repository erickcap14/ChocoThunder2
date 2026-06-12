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
cp web/index.html web/favicon.png web/manifest.webmanifest build/web/
mkdir -p build/web/icons
cp web/icons/*.png build/web/icons/

# Fully self-contained bundle (T112): mirror the entire pygbag CDN subset the
# loader touches, so the app makes ZERO network requests (required for the
# wrapped iPad app and by security.md). index.html loads pythons.js from this
# local mirror; on a "localhost" origin (http://localhost:8000 AND Capacitor's
# capacitor://localhost) pythons.js then resolves the whole runtime relative
# to wherever it was loaded from. Files are cached across builds.
CDN_BASE=https://pygame-web.github.io/cdn
# NOTE: browserfs.min.js is deliberately absent — it does not exist on the
# upstream CDN (404; the stock template's URL was broken too) and pygbag boots
# without it ("PyMain: BrowserFS not found" is non-fatal).
CDN_FILES=(
    0.9.3/pythons.js
    0.9.3/empty.html
    0.9.3/empty.ogg
    0.9.3/cpythonrc.py
    0.9.3/cpython312/main.js
    0.9.3/cpython312/main.data
    0.9.3/cpython312/main.wasm
    vtx.js
    vt/xterm.css
    vt/xterm.js
    vt/xterm-addon-image.js
    index-0.9.3-cp312.json
    lib/index.html
    cp312/pygame_ce-2.5.7-cp312-cp312-wasm32_bi_emscripten.whl
)
for f in "${CDN_FILES[@]}"; do
    dest="build/web/cdn/$f"
    if [ ! -s "$dest" ]; then
        mkdir -p "$(dirname "$dest")"
        curl -sSL "$CDN_BASE/$f" -o "$dest"
    fi
done

# Patch the mirrored cpythonrc.py to force the wheel repository (index json +
# wheel downloads, via the PYGPI env var read by aio.pep0723.async_repos) to
# our local cdn/ mirror. cpythonrc.py runs at VM postrun — the only hook early
# enough: pygbag's pep0723 dependency scan of the page's embedded script fires
# async_repos() before that script itself executes. Keyed off location.href so
# it works on http://localhost:8000 and Capacitor's capacitor://localhost.
RC=build/web/cdn/0.9.3/cpythonrc.py
if ! grep -q "ChocoThunder2 T112" "$RC"; then
    cat >> "$RC" <<'PYEOF'

# --- ChocoThunder2 T112: force the wheel repo to the local cdn/ mirror ---
try:
    import os as _t112_os
    from platform import window as _t112_window
    _t112_loc = _t112_window.location
    # Build scheme://host + dirname(path). Don't derive from href: under
    # Capacitor it is "capacitor://localhost" with no path at all, and
    # rsplit("/") would mangle it into "capacitor://cdn/".
    _t112_path = str(_t112_loc.pathname) or "/"
    _t112_base = (
        str(_t112_loc.protocol) + "//" + str(_t112_loc.host)
        + _t112_path.rsplit("/", 1)[0]
    )
    _t112_os.environ.setdefault("PYGPI", _t112_base + "/cdn/")
except Exception as _t112_e:  # pragma: no cover - non-browser interpreters
    print("T112 PYGPI patch skipped:", _t112_e)
PYEOF
fi

# Generate the PWA service worker: precache every bundle file, with the cache
# name keyed to the game archive's checksum so a rebuild invalidates old caches.
VERSION=$(shasum build/web/chocothunder2.tar.gz | cut -c1-12)
{
    printf 'const CACHE = "ct2-%s";\n' "$VERSION"
    printf 'const ASSETS = [\n'
    (cd build/web && find . -type f ! -name 'sw.js' | sort | sed 's|^\./|    "./|; s|$|",|')
    cat <<'JSEOF'
];
self.addEventListener("install", (e) => {
    e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ASSETS)));
    self.skipWaiting();
});
self.addEventListener("activate", (e) => {
    e.waitUntil(caches.keys().then((keys) => Promise.all(
        keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))
    )).then(() => self.clients.claim()));
});
self.addEventListener("fetch", (e) => {
    if (e.request.method !== "GET") return;
    e.respondWith(caches.match(e.request, {ignoreSearch: true}).then(
        (hit) => hit || fetch(e.request)
    ));
});
JSEOF
} > build/web/sw.js

echo "Built build/web/ — serve with: python3 -m http.server 8000 -d build/web"
