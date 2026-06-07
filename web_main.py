"""Web (WASM) entry point for ChocolateThunder2: ElectricBoogaloo.

This is the file pygbag compiles to WebAssembly:

    python -m pygbag --build web_main.py   # produce build/web/
    python -m pygbag web_main.py           # build + serve at http://localhost:8000

It is deliberately minimal and imports nothing desktop-only — no argparse, no
``mcp_server``, no ``main`` — because those rely on a local filesystem and a
sidecar process that the browser sandbox does not provide. The MCP harness and
the desktop entry point live in ``main.py``; this file drives the async loop.
"""

import asyncio


async def main() -> None:
    from game.app import App

    await App().run_async()


asyncio.run(main())
