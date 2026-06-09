"""Unit tests for the splat transform on the Poo entity (headless).

A powered surprise stepped on by a tenant turns into a one-shot splat: it swaps
to the splat animation and fades itself off the floor after SPLAT_FADE_SECONDS.
"""

from __future__ import annotations

import pytest
import pygame

from game.entities.poo import Poo
from game import config


@pytest.mark.log_meta(phase="phase_3", subtask="splat", action="splat swaps frames")
def test_splat_swaps_to_splat_frames(pygame_env):
    """splat() flips is_splat and replaces the frame list with the 18-frame splat anim."""
    poo = Poo((100, 100), powered=True)
    original = poo.frames
    poo.splat()
    assert poo.is_splat is True
    assert poo.frames is not original
    assert len(poo.frames) == 18


@pytest.mark.log_meta(phase="phase_3", subtask="splat", action="splat fades and kills self")
def test_splat_kills_itself_after_fade(pygame_env):
    """After SPLAT_FADE_SECONDS of updates the splat removes itself from its group."""
    poo = Poo((100, 100), powered=True)
    group = pygame.sprite.Group(poo)
    poo.splat()
    assert poo.alive() is True
    # Advance time past the fade window in small steps.
    elapsed = 0.0
    while elapsed <= config.SPLAT_FADE_SECONDS:
        poo.update(0.1)
        elapsed += 0.1
    assert poo.alive() is False
    assert poo not in group
