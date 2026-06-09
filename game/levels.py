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
    map_image: str            # filename under the active art root (assets/ or pixellab/) maps/
    npcs: List[str]           # character dirs under the active art root (assets/ or pixellab/) npc/
    obstacle_room: str        # subdir under the active art root (assets/ or pixellab/) obstacles/
    music: str                # filename under assets/sounds/music/
    transition_subtitle: str  # punny subtitle for post-level TransitionScreen
    intro_subtitle: str       # teaser shown on pre-level PreLevelScreen


LEVELS: List[LevelSpec] = [
    LevelSpec(
        name="Level 1",
        map_image="level1.png",
        npcs=["char1"],
        obstacle_room="genericroom",
        music="A1-Thunderstruck_01.ogg",
        transition_subtitle="Living The Dream, Soiling The Scene",
        intro_subtitle="Working Out A Big One",
    ),
    LevelSpec(
        name="Level 2",
        map_image="level2.png",
        npcs=["char1", "char2"],
        obstacle_room="gym",
        music="05 I Wanna Rock.ogg",
        transition_subtitle="Number Two: Mission Accomplished",
        intro_subtitle="Gains Made, Mess Made",
    ),
    LevelSpec(
        name="Level 3",
        map_image="level3.png",
        npcs=["char1", "char2", "char3"],
        obstacle_room="japaneseroom",
        music="",  # TODO: no track yet — plays transition→complete once a file is set
        transition_subtitle="One With Nature, Two On The Matt",
        intro_subtitle="Sem-Poo-Ku",
    ),
    LevelSpec(
        name="Level 4",
        map_image="level4.png",
        npcs=["char1", "char2", "char3", "char4"],
        obstacle_room="garden",
        music="14 Angel.ogg",
        transition_subtitle="Fertile Ground, Fertile Hound",
        intro_subtitle="The Final Defecation",
    ),
]
