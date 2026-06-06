"""Phase 1 gate: validate the Game State MCP harness before any screens exist.

Covers the IPC primitives and the game-side command dispatcher (poll_mcp_command)
so every later screen can rely on this plumbing.
"""

from __future__ import annotations

import pytest

import main
from game.state_machine import GameState, StateMachine
from mcp_server import state_bridge as bridge


pytestmark = pytest.mark.usefixtures("clean_bridge")


# --- IPC primitives --------------------------------------------------------
def test_read_state_sentinel_when_missing():
    assert bridge.read_state() == {"state": "UNKNOWN", "running": False}


@pytest.mark.log_meta(phase="phase_1", subtask="1.1", action="state roundtrip")
def test_state_roundtrip():
    bridge.write_state("RUNNING", score=42, level=2)
    state = bridge.read_state()
    assert state["state"] == "RUNNING"
    assert state["running"] is True
    assert state["score"] == 42
    assert state["level"] == 2


@pytest.mark.log_meta(phase="phase_1", subtask="1.2", action="command roundtrip")
def test_command_roundtrip_and_clear():
    assert bridge.read_command_full() is None
    bridge.write_command("jump_to_running")
    assert bridge.read_command() == "jump_to_running"
    cmd, args = bridge.read_command_full()
    assert cmd == "jump_to_running" and args == {}
    bridge.clear_command()
    assert bridge.read_command_full() is None


def test_command_with_args():
    bridge.write_command_with_args("set_level", n=3)
    cmd, args = bridge.read_command_full()
    assert cmd == "set_level" and args == {"n": 3}


# --- poll_mcp_command: state jumps ----------------------------------------
@pytest.mark.parametrize(
    "command,expected",
    [
        ("jump_to_start", GameState.START),
        ("jump_to_transition", GameState.TRANSITION),
        ("jump_to_running", GameState.RUNNING),
        ("jump_to_end", GameState.END),
        ("jump_to_scoreboard", GameState.SCOREBOARD),
    ],
)
@pytest.mark.log_meta(phase="phase_1", subtask="1.3", action="jump dispatch")
def test_poll_jumps(command, expected):
    sm = StateMachine(GameState.START)
    bridge.write_command(command)
    main.poll_mcp_command(sm)
    assert sm.state is expected
    assert bridge.read_command_full() is None  # consumed


# --- poll_mcp_command: screen-specific + audio dispatch -------------------
class _FakeScreen:
    def __init__(self):
        self.calls = []

    def set_level(self, n):
        self.calls.append(("set_level", n))

    def spawn_powerup(self):
        self.calls.append(("spawn_powerup",))

    def spawn_npc(self):
        self.calls.append(("spawn_npc",))

    def drop_poo(self):
        self.calls.append(("drop_poo",))

    def set_invincible(self, on):
        self.calls.append(("set_invincible", on))


class _FakeAudio:
    def __init__(self):
        self.music = self.sfx = None

    def toggle_music(self):
        self.music = True

    def toggle_sfx(self):
        self.sfx = True


@pytest.mark.log_meta(phase="phase_1", subtask="1.4", action="screen dispatch")
def test_poll_screen_actions():
    sm = StateMachine(GameState.RUNNING)
    screen = _FakeScreen()

    for cmd, args in [
        ("set_level", {"n": 2}),
        ("spawn_powerup", {}),
        ("spawn_npc", {}),
        ("drop_poo", {}),
        ("set_invincible", {"on": True}),
    ]:
        bridge.write_command_with_args(cmd, **args)
        main.poll_mcp_command(sm, active_screen=screen)

    assert screen.calls == [
        ("set_level", 2),
        ("spawn_powerup",),
        ("spawn_npc",),
        ("drop_poo",),
        ("set_invincible", True),
    ]


def test_poll_audio_toggles():
    sm = StateMachine(GameState.RUNNING)
    audio = _FakeAudio()
    bridge.write_command("toggle_music")
    main.poll_mcp_command(sm, audio_manager=audio)
    bridge.write_command("toggle_sfx")
    main.poll_mcp_command(sm, audio_manager=audio)
    assert audio.music is True and audio.sfx is True


def test_poll_noop_when_no_command():
    sm = StateMachine(GameState.START)
    main.poll_mcp_command(sm)  # nothing queued -> no error, no change
    assert sm.state is GameState.START
