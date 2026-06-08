# PixelLab Art Set

This directory holds the **optional, dev-time-generated** art set produced via the
[PixelLab](https://www.pixellab.ai) hosted MCP server. It is selected at runtime by
the `ART_SET` toggle:

```bash
CT2_ART_SET=pixellab
```

When that toggle is **not** set, the game uses the default art under `assets/`.

This tree **mirrors the image subdirectories of `assets/` only** — PixelLab generates
art (no fonts, no audio), so there are no `fonts/` or `sounds/` directories here.

## Connecting to the PixelLab MCP

PixelLab is a **hosted** MCP server; we connect to it, we do not run it. The Bearer
token comes from the `PIXELLAB_API_KEY` environment variable (kept in a git-ignored
`.env`) — **never paste a literal token** into any committed file.

Equivalent one-shot connect command (token still read from your environment):

```bash
claude mcp add pixellab https://api.pixellab.ai/mcp -t http -H "Authorization: Bearer $PIXELLAB_API_KEY"
```

The committed `.mcp.json` at the repo root already wires this up via env-var
expansion (`${PIXELLAB_API_KEY}`), so in normal use you only need
`PIXELLAB_API_KEY` available in Claude Code's environment — no manual `add` step
required. See `.env.example` for how to populate it.

## PixelLab tool -> asset-dir mapping

| PixelLab tool(s)                          | Target directory                                              | Notes                              |
| ----------------------------------------- | ------------------------------------------------------------- | ---------------------------------- |
| `create_topdown_tileset`                  | `pixellab/maps/`                                              | Level backgrounds                  |
| `create_character` + `animate_character`  | `pixellab/characters/<dir>`, `pixellab/npc/<charN>/<dir>`     | Player + NPC walk cycles per dir   |
| `create_map_object`                       | `pixellab/obstacles/<room>/`, `pixellab/powerups/`, `pixellab/surprises/*` | Room props, power-ups, surprises   |
| `create_character` / `create_map_object`  | `pixellab/endscreens/`                                        | Transition + start-screen art      |

Where `<dir>` is one of `down`, `left`, `right`, `up`; `<charN>` is `char1`..`char3`;
and `<room>` is one of `genericroom`, `gym`, `japaneseroom`.

## Before you generate anything

**Generation is gated on sign-off.** BEFORE generating any art, the visual direction
**must be agreed with the user** — including style, palette, top-down perspective,
reference imagery, and sizes. Do not call any PixelLab tool until that direction has
been confirmed.
