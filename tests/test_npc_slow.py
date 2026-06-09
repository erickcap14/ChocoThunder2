"""Unit tests for the tenant slow effect (headless).

Stepping on a splat slows an NPC to NPC_SLOW_MULTIPLIER of its normal speed for
NPC_SLOW_SECONDS, after which it recovers to full speed.
"""

from __future__ import annotations

import pytest
import pygame

from game.entities.npc import NPC
from game import assets, config


def _make_npc() -> NPC:
    """Build an NPC at a fixed spot with a generous patrol bounds."""
    char = next(c for c in ("char1", "char2", "char3") if assets.npc_available(c))
    bounds = pygame.Rect(0, 0, config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    return NPC(char, (200, 200), bounds)


# The NPC stores its position only in an integer ``rect`` and truncates each frame,
# so a sub-pixel per-frame step (NPC_SPEED * 0.4 = 0.88px) would never register as
# rect movement. To measure the slow *ratio* faithfully we raise NPC_SPEED for the
# duration of the test so both the full and slowed steps clear the 1px floor; the
# code under test is the same — speed = NPC_SPEED * (mult if slowed else 1).
_FRAMES = 12
_DT = 0.05  # 12 * 0.05 = 0.6s of motion — within NPC_SLOW_SECONDS (3.0)
_FAST_SPEED = 10  # px/frame, so 0.4x (4px) still clears integer truncation


def _player_far_right() -> pygame.Rect:
    p = pygame.Rect(0, 0, config.NPC_SIZE[0], config.NPC_SIZE[1])
    # On the same row, within NPC_CHASE_RADIUS (300) of the NPC's (200, 200) spawn so
    # it stays in chase mode (full steps), yet far enough not to be reached mid-test.
    p.center = (480, 200)
    return p


def _walk(npc: NPC, player: pygame.Rect, frames: int = _FRAMES) -> float:
    """Drive ``frames`` updates toward the player; return total x-distance covered."""
    start_x = npc.rect.centerx
    for _ in range(frames):
        npc.update(_DT, player)
    return abs(npc.rect.centerx - start_x)


@pytest.mark.log_meta(phase="phase_3", subtask="slow", action="slow reduces step to 40%")
def test_apply_slow_reduces_step(pygame_env, monkeypatch):
    """A slowed tenant covers ~NPC_SLOW_MULTIPLIER of the ground an un-slowed one does."""
    monkeypatch.setattr(config, "NPC_SPEED", _FAST_SPEED)
    player = _player_far_right()

    npc = _make_npc()
    full = _walk(npc, player)

    npc = _make_npc()
    npc.apply_slow()
    slowed = _walk(npc, player)

    assert slowed == pytest.approx(full * config.NPC_SLOW_MULTIPLIER, rel=0.1)


@pytest.mark.log_meta(phase="phase_3", subtask="slow", action="slow clears after duration")
def test_slow_clears_after_duration(pygame_env, monkeypatch):
    """Once NPC_SLOW_SECONDS elapse the timer hits zero and full speed resumes."""
    monkeypatch.setattr(config, "NPC_SPEED", _FAST_SPEED)
    player = _player_far_right()

    # Baseline full-speed distance over _FRAMES of motion.
    npc = _make_npc()
    full = _walk(npc, player)

    # Slow, then let the whole slow window expire.
    npc = _make_npc()
    npc.apply_slow()
    elapsed = 0.0
    while elapsed < config.NPC_SLOW_SECONDS:
        npc.update(0.1, player)
        elapsed += 0.1
    assert npc._slow_remaining == 0.0

    # Movement after the window matches the un-slowed baseline again.
    recovered = _walk(npc, player)
    assert recovered == pytest.approx(full, rel=0.1)
