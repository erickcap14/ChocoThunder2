"""Game state machine.

Replaces the original string-based ``self.gameState`` flags with a small enum
and an explicit transition helper. ``force_state`` is what the MCP bridge calls
to teleport the running game to any screen for testing.
"""

from __future__ import annotations

from enum import Enum


class GameState(Enum):
    START = "START"
    TRANSITION = "TRANSITION"
    RUNNING = "RUNNING"
    END = "END"
    SCOREBOARD = "SCOREBOARD"


class StateMachine:
    def __init__(self, initial: GameState = GameState.START):
        self.state = initial
        self.previous = initial

    def force_state(self, state: GameState) -> None:
        """Jump directly to ``state`` (used by gameplay transitions and the MCP)."""
        if not isinstance(state, GameState):
            state = GameState(state)
        self.previous = self.state
        self.state = state

    def is_(self, state: GameState) -> bool:
        return self.state is state
