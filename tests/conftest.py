"""Shared pytest fixtures for ChocolateThunder2.

- ``pygame_env``: headless pygame (dummy SDL drivers) so tests run without a
  display or audio device.
- ``clean_bridge``: wipes the IPC files around a test (used by MCP-verify tests).
- ``log_meta`` marker: auto-logs each test's outcome via tests/logger.py.
"""

from __future__ import annotations

import os

import pytest

# Force headless BEFORE pygame is imported anywhere.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH, STATE_FILE, COMMAND_FILE  # noqa: E402
from tests.logger import log_test  # noqa: E402


@pytest.fixture(scope="module")
def pygame_env():
    """A headless display surface shared across a test module."""
    pygame.init()
    surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    yield surface
    pygame.quit()


@pytest.fixture
def clean_bridge():
    """Clear the IPC files before and after each test."""
    for f in (STATE_FILE, COMMAND_FILE):
        f.unlink(missing_ok=True)
    yield
    for f in (STATE_FILE, COMMAND_FILE):
        f.unlink(missing_ok=True)


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "log_meta(phase, subtask, action): attach metadata for structured test logging",
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Log pass/fail for tests carrying the @log_meta marker (call phase only)."""
    outcome = yield
    report = outcome.get_result()
    if report.when != "call":
        return
    marker = item.get_closest_marker("log_meta")
    if marker is None:
        return
    log_test(item.nodeid, report.outcome, **marker.kwargs)
