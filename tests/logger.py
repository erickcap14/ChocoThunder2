"""Structured test logging -> .implementations/test_log.json.

Appends one JSON record per test so progress across sessions is inspectable.
Used automatically by the ``log_meta`` marker hook in conftest.py.
"""

from __future__ import annotations

import json
import time

from game.config import TEST_LOG_FILE


def _append(record: dict) -> None:
    TEST_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    log: list = []
    if TEST_LOG_FILE.exists():
        try:
            log = json.loads(TEST_LOG_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            log = []
    record["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    log.append(record)
    TEST_LOG_FILE.write_text(json.dumps(log, indent=2))


def log_test(name: str, outcome: str, **meta) -> None:
    """Record a pure unit-test result."""
    _append({"kind": "unit", "name": name, "outcome": outcome, **meta})


def log_mcp_verify(name: str, outcome: str, screenshot: str | None = None, **meta) -> None:
    """Record an MCP-roundtrip / screenshot verification result."""
    _append({"kind": "mcp_verify", "name": name, "outcome": outcome,
             "screenshot": screenshot, **meta})
