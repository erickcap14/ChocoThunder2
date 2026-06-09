"""High-score persistence — read/write top-10 scores.

Bug #5 fix: tolerant parsing skips malformed lines instead of crashing.
Format: one ``name,score`` entry per line (``name`` may contain commas;
the score is always the last comma-separated token).

Storage backend (T115):
- Desktop (CPython): a plain text file at ``config.SCORES_FILE``.
- Browser (pygbag/Emscripten): ``window.localStorage`` under ``SCORES_KEY``,
  because pygbag's MEMFS is ephemeral and a file would not survive a reload.

The two backends share the same newline-delimited ``name,score`` blob, so the
public interface (:func:`load_scores`, :func:`save_scores`, :func:`add_score`)
is identical on both platforms.
"""

from __future__ import annotations

import sys

from game import config

# localStorage key used under WASM. Stable so scores survive reloads.
SCORES_KEY = "ct2_scores"


def _read_blob() -> str:
    """Return the raw newline-delimited scores text from the active backend.

    Returns an empty string when no data exists or the backend is unavailable.
    All failures degrade gracefully (mirrors the tolerant parsing style).
    """
    if sys.platform == "emscripten":
        try:
            import platform  # pygbag exposes the browser window here

            value = platform.window.localStorage.getItem(SCORES_KEY)
            # localStorage.getItem returns null (→ None) when the key is unset.
            return value if value else ""
        except Exception:
            return ""

    if not config.SCORES_FILE.exists():
        return ""
    return config.SCORES_FILE.read_text(encoding="utf-8")


def _write_blob(blob: str) -> None:
    """Persist the raw scores text to the active backend.

    Browser failures degrade silently to in-memory (nothing persisted) rather
    than crashing the game.
    """
    if sys.platform == "emscripten":
        try:
            import platform  # pygbag exposes the browser window here

            platform.window.localStorage.setItem(SCORES_KEY, blob)
        except Exception:
            pass
        return

    config.SCORES_FILE.parent.mkdir(parents=True, exist_ok=True)
    config.SCORES_FILE.write_text(blob, encoding="utf-8")


def load_scores() -> list[tuple[str, int]]:
    """Return up to MAX_HIGH_SCORES entries sorted highest-first.

    Malformed lines are silently skipped (Bug #5 fix).
    """
    entries: list[tuple[str, int]] = []
    for line in _read_blob().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            last_comma = line.rindex(",")
            name = line[:last_comma].strip()
            score = int(line[last_comma + 1:].strip())
            if name:
                entries.append((name, score))
        except (ValueError, IndexError):
            pass
    return sorted(entries, key=lambda e: e[1], reverse=True)[: config.MAX_HIGH_SCORES]


def save_scores(entries: list[tuple[str, int]]) -> None:
    """Persist entries to the active backend (overwrites)."""
    _write_blob("\n".join(f"{name},{score}" for name, score in entries))


def add_score(name: str, score: int) -> list[tuple[str, int]]:
    """Append an entry, re-sort, trim to top-10, save, and return the list."""
    entries = load_scores()
    entries.append((name, score))
    entries = sorted(entries, key=lambda e: e[1], reverse=True)[: config.MAX_HIGH_SCORES]
    save_scores(entries)
    return entries
