"""High-score persistence — read/write top-10 scores from scores.txt.

Bug #5 fix: tolerant parsing skips malformed lines instead of crashing.
Format: one ``name,score`` entry per line (``name`` may contain commas;
the score is always the last comma-separated token).
"""

from __future__ import annotations

from game import config


def load_scores() -> list[tuple[str, int]]:
    """Return up to MAX_HIGH_SCORES entries sorted highest-first.

    Malformed lines are silently skipped (Bug #5 fix).
    """
    if not config.SCORES_FILE.exists():
        return []
    entries: list[tuple[str, int]] = []
    for line in config.SCORES_FILE.read_text(encoding="utf-8").splitlines():
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
    """Persist entries to scores.txt (overwrites)."""
    config.SCORES_FILE.parent.mkdir(parents=True, exist_ok=True)
    config.SCORES_FILE.write_text(
        "\n".join(f"{name},{score}" for name, score in entries),
        encoding="utf-8",
    )


def add_score(name: str, score: int) -> list[tuple[str, int]]:
    """Append an entry, re-sort, trim to top-10, save, and return the list."""
    entries = load_scores()
    entries.append((name, score))
    entries = sorted(entries, key=lambda e: e[1], reverse=True)[: config.MAX_HIGH_SCORES]
    save_scores(entries)
    return entries
