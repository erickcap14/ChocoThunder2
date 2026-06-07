"""Data-driven level manifest.

Each LevelSpec entry is the single source of truth for a level.
Adding a new level = appending one LevelSpec + dropping assets.
No if/elif chains anywhere in the codebase.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class LevelSpec:
    name: str
    map_image: str            # filename under assets/maps/
    npcs: List[str]           # character dirs under assets/npc/
    obstacle_room: str        # subdir under assets/obstacles/
    music: str                # filename under assets/sounds/music/
    transition_subtitle: str  # punny subtitle for post-level TransitionScreen
    intro_subtitle: str       # teaser shown on pre-level PreLevelScreen


LEVELS: List[LevelSpec] = [
    LevelSpec(
        name="Level 1",
        map_image="level1.png",
        npcs=["char1"],
        obstacle_room="genericroom",
        music="A1-Thunderstruck_01.mp3",
        transition_subtitle="Working Out A Big One",
        intro_subtitle="One Tenant. One Dog. Infinite Regrets.",
    ),
    LevelSpec(
        name="Level 2",
        map_image="level2.png",
        npcs=["char1", "char2"],
        obstacle_room="gym",
        music="05 I Wanna Rock.mp3",
        transition_subtitle="Sem-Poo-Ku",
        intro_subtitle="Double the Tenants. Double the Drama.",
    ),
    LevelSpec(
        name="Level 3",
        map_image="level3.png",
        npcs=["char1", "char2", "char3"],
        obstacle_room="japaneseroom",
        music="14 Angel.mp3",
        transition_subtitle="The Final Defecation",
        intro_subtitle="Three's a Crowd. And a Smell.",
    ),
    LevelSpec(
        name="Level 4",
        map_image="level4.png",
        npcs=["char2", "char3"],
        obstacle_room="genericroom",
        music="A1-Thunderstruck_01.mp3",
        transition_subtitle="Double Down Dirty Dog",
        intro_subtitle="The Grand Finale. Make It Count.",
    ),
]
