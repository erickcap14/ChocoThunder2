"""PlayScreen — core gameplay screen.

Draws the level room map, renders all entity groups (Player, Poos, Obstacles,
NPCs, PowerUps), shows a HUD (score + countdown timer), manages the per-level
timer, wires entity collisions, handles cake spawn cadence, and implements the
MCP poll handler methods expected by main.poll_mcp_command.

Bug #4 fix: MOUSEBUTTONDOWN is handled directly; the original nonsensical
MOUSEBUTTONDOWN != UI_BUTTON_PRESSED guard is gone.
"""

from __future__ import annotations

import random

import pygame

from game import assets, config
from game.entities import NPC, Obstacle, Player, Poo, PowerUp
from game.state_machine import GameState

_HUD_H = 50  # px reserved at the top for score + timer

_LEVELS: dict[int, dict] = {
    1: {
        "map":   "level1.png",
        "room":  "genericroom",
        "music": "A1-Thunderstruck_01.mp3",
        "npcs":  ["char1"],
    },
    2: {
        "map":   "level2.png",
        "room":  "gym",
        "music": "05 I Wanna Rock.mp3",
        "npcs":  ["char1", "char2"],
    },
    3: {
        "map":   "level3.png",
        "room":  "japaneseroom",
        "music": "14 Angel.mp3",
        "npcs":  ["char1", "char2", "char3"],
    },
}


class PlayScreen:
    def __init__(self, screen: pygame.Surface, state_machine, audio):
        self.screen = screen
        self.sm = state_machine
        self.audio = audio
        self.score: int = 0
        self.level: int = 1

        self._font_hud = pygame.font.Font(None, 40)

        self._play_bounds = pygame.Rect(
            0, _HUD_H, config.SCREEN_WIDTH, config.SCREEN_HEIGHT - _HUD_H
        )

        self._build_level(self.level)

    # ------------------------------------------------------------------
    # Level loading
    # ------------------------------------------------------------------

    def _build_level(self, n: int) -> None:
        spec = _LEVELS.get(n, _LEVELS[1])

        self._map = assets.load_image(
            str(assets.map_image(spec["map"])),
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT),
        )

        self._player = Player(
            (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
        )

        self._obstacles = pygame.sprite.Group()
        obs_folder = assets.obstacle_dir(spec["room"])
        obs_images = sorted(obs_folder.glob("*.png"), key=lambda p: p.name)
        positions = [(x, y) for x in config.OBSTACLE_X for y in config.OBSTACLE_Y]
        random.shuffle(positions)
        for i, img_path in enumerate(obs_images[: config.NUM_OBSTACLES]):
            surf = assets.load_image(str(img_path), config.OBSTACLE_SIZE)
            self._obstacles.add(Obstacle(surf, positions[i % len(positions)]))

        self._npcs = pygame.sprite.Group()
        for char in spec["npcs"]:
            self._npcs.add(NPC(char, self._random_pos(), self._play_bounds))

        self._poos: pygame.sprite.Group = pygame.sprite.Group()
        self._powerups: pygame.sprite.Group = pygame.sprite.Group()

        self._level_time_remaining: float = float(config.LEVEL_SECONDS)
        self._poo_cooldown_remaining: float = 0.0
        self._powerup_spawn_timer: float = config.POWERUP_SPAWN_SECONDS

        self.audio.play_music(spec["music"])

    def _random_pos(self) -> tuple[int, int]:
        x = random.randint(self._play_bounds.left + 50, self._play_bounds.right - 50)
        y = random.randint(self._play_bounds.top + 50, self._play_bounds.bottom - 50)
        return (x, y)

    # ------------------------------------------------------------------
    # MCP poll handler methods (called by main.poll_mcp_command)
    # ------------------------------------------------------------------

    def set_level(self, n: int) -> None:
        self.level = max(1, min(n, len(_LEVELS)))
        self.score = 0
        self.audio.stop_music()
        self._build_level(self.level)

    def spawn_powerup(self) -> None:
        self._powerups.add(PowerUp(self._random_pos()))
        self._powerup_spawn_timer = config.POWERUP_SPAWN_SECONDS

    def spawn_npc(self) -> None:
        spec = _LEVELS.get(self.level, _LEVELS[1])
        char = random.choice(spec["npcs"])
        self._npcs.add(NPC(char, self._random_pos(), self._play_bounds))

    def drop_poo(self) -> None:
        """Force-drop a poo at Sally's position (MCP tool; bypasses cooldown)."""
        self._place_poo()

    def set_invincible(self, on: bool) -> None:
        self._player.set_invincible(on)

    # ------------------------------------------------------------------
    # Game loop
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._player.set_target(event.pos)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if self._poo_cooldown_remaining <= 0.0:
                self._place_poo()

    def _place_poo(self) -> None:
        powered = self._player.is_invincible
        self._poos.add(Poo(self._player.rect.center, powered))
        self.score += config.SCORE_BONUS if powered else config.SCORE_DEFAULT
        self.audio.play_sfx("powerup_fart" if powered else "unpowered_fart")
        self._poo_cooldown_remaining = config.POO_COOLDOWN_SECONDS

    def update(self, dt: float) -> None:
        self._poo_cooldown_remaining = max(0.0, self._poo_cooldown_remaining - dt)
        self._level_time_remaining -= dt

        if self._level_time_remaining <= 0.0:
            self._level_time_remaining = 0.0
            self.audio.stop_music()
            self.sm.force_state(GameState.TRANSITION)
            return

        self._powerup_spawn_timer -= dt
        if self._powerup_spawn_timer <= 0.0 and not self._powerups:
            self.spawn_powerup()

        self._player.update(dt, self._play_bounds)
        for npc in self._npcs:
            npc.update(dt, self._player.rect)
        for poo in self._poos:
            poo.update(dt)
        for pu in self._powerups:
            pu.update(dt)

        for obs in self._obstacles:
            obs.push_out(self._player.rect)
        for npc in self._npcs:
            for obs in self._obstacles:
                obs.push_out(npc.rect)

        collected = pygame.sprite.spritecollide(self._player, self._powerups, True)
        if collected:
            self._player.set_invincible(True)
            self.audio.play_sfx("powerup_fart")

        if not self._player.is_invincible:
            if pygame.sprite.spritecollide(self._player, self._npcs, False):
                self.audio.play_sfx("lose_life")
                self.audio.stop_music()
                self.sm.force_state(GameState.END)

    def draw(self) -> None:
        self.screen.blit(self._map, (0, 0))

        self._poos.draw(self.screen)
        self._obstacles.draw(self.screen)
        self._powerups.draw(self.screen)
        self._npcs.draw(self.screen)
        self._player.draw(self.screen)

        hud = pygame.Surface((config.SCREEN_WIDTH, _HUD_H), pygame.SRCALPHA)
        hud.fill((20, 20, 20, 200))
        self.screen.blit(hud, (0, 0))

        score_surf = self._font_hud.render(f"Score: {self.score}", True, config.WHITE)
        self.screen.blit(score_surf, (16, (_HUD_H - score_surf.get_height()) // 2))

        secs = max(0, int(self._level_time_remaining))
        timer_surf = self._font_hud.render(
            f"Time: {secs // 60}:{secs % 60:02d}", True, config.WHITE
        )
        self.screen.blit(
            timer_surf,
            (config.SCREEN_WIDTH - timer_surf.get_width() - 16,
             (_HUD_H - timer_surf.get_height()) // 2),
        )

        if self._player.is_invincible:
            inv_surf = self._font_hud.render("INVINCIBLE!", True, config.GREEN)
            self.screen.blit(
                inv_surf,
                ((config.SCREEN_WIDTH - inv_surf.get_width()) // 2,
                 (_HUD_H - inv_surf.get_height()) // 2),
            )
