"""PlayScreen — core gameplay screen.

Draws the level room map, renders all entity groups (Player, Poos, Obstacles,
NPCs, PowerUps), shows a HUD (score + countdown timer), manages the per-level
timer, wires entity collisions, handles cake spawn cadence, and implements the
MCP poll handler methods expected by main.poll_mcp_command.

Bug #4 fix: MOUSEBUTTONDOWN is handled directly; the original nonsensical
MOUSEBUTTONDOWN != UI_BUTTON_PRESSED guard is gone.
"""

from __future__ import annotations

import math
import random

import pygame

from game import assets, config, fonts
from game.entities import NPC, Obstacle, Player, Poo, PowerUp, clamp_rect
from game.levels import LEVELS
from game.state_machine import GameState

_HUD_H = 50  # px reserved at the top for score + timer

_ARROW_KEYS = (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN)

_HELP_LINES = (
    "Controls",
    "Click or drag  —  send Sally to the cursor",
    "Arrow keys  —  steer Sally directly",
    "Space Bar  —  drop a chocolate surprise",
    "Eat a cake  —  become invincible (bonus points!)",
    "Dodge the tenants  —  caught = game over",
)


class PlayScreen:
    def __init__(
        self,
        screen: pygame.Surface,
        state_machine,
        audio,
        test_mode: bool = False,
        level: int = 1,
        score: int = 0,
    ):
        self.screen = screen
        self.sm = state_machine
        self.audio = audio
        self.score: int = score
        self.level: int = max(1, min(level, len(LEVELS)))
        self.test_mode: bool = test_mode

        self._font_hud  = fonts.load(40)
        self._font_help = fonts.load(22)
        self._font_help_btn = fonts.load(18)

        self._play_bounds = pygame.Rect(
            0, _HUD_H, config.SCREEN_WIDTH, config.SCREEN_HEIGHT - _HUD_H
        )

        # Hover-For-Help: button rect sits left of centre in the HUD bar, in the gap
        # between the score and the centred INVINCIBLE! text so it never overlaps them.
        # Width 176px comfortably holds "? Hover for Help" at font size 18 (155px).
        help_w, help_h = 176, 34
        self._help_btn = pygame.Rect(
            260,   # centred in the gap between the score (ends ~x241) and the
                   # centred INVINCIBLE! text (starts x456) so it overlaps neither
            (_HUD_H - help_h) // 2,
            help_w,
            help_h,
        )
        self._help_visible: bool = False

        # Control state: True while dragging Sally with the mouse held down, and the
        # set of arrow keys currently held for direct steering.
        self._mouse_held: bool = False
        self._held_dirs: set[int] = set()

        self._build_level(self.level)

    # ------------------------------------------------------------------
    # Level loading
    # ------------------------------------------------------------------

    def _build_level(self, n: int) -> None:
        idx = max(0, min(n - 1, len(LEVELS) - 1))
        spec = LEVELS[idx]

        self._map = assets.load_image(
            str(assets.map_image(spec.map_image)),
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT),
        )

        self._player = Player(
            (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
        )

        self._obstacles = pygame.sprite.Group()
        obs_folder = assets.obstacle_dir(spec.obstacle_room)
        obs_images = sorted(obs_folder.glob("*.png"), key=lambda p: p.name)[: config.NUM_OBSTACLES]
        positions = self._pick_obstacle_positions(len(obs_images), self._player.rect.center)
        for img_path, pos in zip(obs_images, positions):
            box = config.OBSTACLE_RENDER_OVERRIDES.get(img_path.stem, config.OBSTACLE_RENDER_MAX)
            surf = assets.load_image_fit(str(img_path), box)
            self._obstacles.add(Obstacle(surf, pos))

        self._npcs = pygame.sprite.Group()
        for char in spec.npcs:
            # Skip tenants with no art in the active set (e.g. char4 exists only in
            # the pixellab set) so the original art set stays unchanged and never raises.
            if not assets.npc_available(char):
                continue
            self._npcs.add(NPC(char, self._npc_spawn_pos(), self._play_bounds))

        self._poos: pygame.sprite.Group = pygame.sprite.Group()
        self._powerups: pygame.sprite.Group = pygame.sprite.Group()

        self._level_time_remaining: float = float(config.LEVEL_SECONDS)
        self._poo_cooldown_remaining: float = 0.0
        self._powerup_spawn_timer: float = config.POWERUP_SPAWN_SECONDS

        # Idempotent: continues the track the transition card already started for
        # this level; switches tracks only on a direct MCP set_level to a new level.
        self.audio.play_music(spec.music)

    def _random_pos(self) -> tuple[int, int]:
        x = random.randint(self._play_bounds.left + 50, self._play_bounds.right - 50)
        y = random.randint(self._play_bounds.top + 50, self._play_bounds.bottom - 50)
        return (x, y)

    def _pick_obstacle_positions(self, n: int, player_center) -> list[tuple[int, int]]:
        """Choose ``n`` placement points that clear the player's centre spawn and stay
        ``OBSTACLE_MIN_SPACING`` apart, so tenants/Sally have room to move. Retries a few
        shuffles to reliably find a fully-spaced set before any best-effort fallback."""
        cands = [
            (x, y)
            for x in config.OBSTACLE_X
            for y in config.OBSTACLE_Y
            if math.dist((x, y), player_center) >= config.OBSTACLE_PLAYER_CLEARANCE
        ]
        best: list[tuple[int, int]] = []
        for _ in range(40):
            random.shuffle(cands)
            chosen: list[tuple[int, int]] = []
            for pos in cands:
                if all(math.dist(pos, c) >= config.OBSTACLE_MIN_SPACING for c in chosen):
                    chosen.append(pos)
                    if len(chosen) >= n:
                        return chosen
            if len(chosen) > len(best):
                best = chosen
        # Grid can't fit n fully-spaced points — pad the best attempt with leftovers.
        for pos in cands:
            if len(best) >= n:
                break
            if pos not in best:
                best.append(pos)
        return best[:n]

    def _npc_spawn_pos(self) -> tuple[int, int]:
        """Random spawn that isn't on the player, an obstacle, or another tenant."""
        gap = config.NPC_SPAWN_CLEARANCE
        player_center = self._player.rect.center
        for _ in range(80):
            pos = self._random_pos()
            if math.dist(pos, player_center) < config.PLAYER_SIZE[0] + gap:
                continue
            rect = pygame.Rect(0, 0, *config.NPC_SIZE)
            rect.center = pos
            probe = rect.inflate(gap, gap)
            if any(probe.colliderect(o.bbox) for o in self._obstacles):
                continue
            if any(probe.colliderect(npc.rect) for npc in self._npcs):
                continue
            return pos
        return self._random_pos()

    # ------------------------------------------------------------------
    # MCP poll handler methods (called by main.poll_mcp_command)
    # ------------------------------------------------------------------

    def set_level(self, n: int) -> None:
        self.level = max(1, min(n, len(LEVELS)))
        self.score = 0
        self._build_level(self.level)

    def resume(self, level: int, score: int) -> None:
        """Advance to a new level carrying accumulated score (level transition)."""
        self.level = max(1, min(level, len(LEVELS)))
        self.score = score
        self._build_level(self.level)

    def spawn_powerup(self) -> None:
        self._powerups.add(PowerUp(self._random_pos()))
        self._powerup_spawn_timer = config.POWERUP_SPAWN_SECONDS

    def spawn_npc(self) -> None:
        char = random.choice(LEVELS[self.level - 1].npcs)
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
        if event.type == pygame.MOUSEMOTION:
            if self._mouse_held:
                # Click-drag: keep retargeting Sally to the latest cursor position.
                self._player.set_target(event.pos)
            else:
                self._help_visible = self._help_btn.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not self._help_visible:
                self._mouse_held = True
                self._player.set_target(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            self._mouse_held = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not self._help_visible and self._poo_cooldown_remaining <= 0.0:
                    self._place_poo()
            elif event.key in _ARROW_KEYS:
                self._held_dirs.add(event.key)
        elif event.type == pygame.KEYUP:
            self._held_dirs.discard(event.key)

    def _place_poo(self) -> None:
        powered = self._player.is_invincible
        self._poos.add(Poo(self._player.rect.center, powered))
        self.score += config.SCORE_BONUS if powered else config.SCORE_DEFAULT
        self.audio.play_sfx("powerup_fart" if powered else "unpowered_fart")
        self._poo_cooldown_remaining = config.POO_COOLDOWN_SECONDS

    def update(self, dt: float) -> None:
        if self._help_visible or self.test_mode:
            # Freeze game logic but keep sprites cycling their walk frames.
            self._player.animate(dt)
            for npc in self._npcs:
                npc.animate(dt)
            return

        self._poo_cooldown_remaining = max(0.0, self._poo_cooldown_remaining - dt)
        self._level_time_remaining -= dt

        if self._level_time_remaining <= 0.0:
            self._level_time_remaining = 0.0
            # Leave the music playing: it carries into the level-complete card.
            self.sm.force_state(GameState.TRANSITION)
            return

        self._powerup_spawn_timer -= dt
        if self._powerup_spawn_timer <= 0.0 and not self._powerups:
            self.spawn_powerup()

        # Translate held arrow keys into a steering direction (overrides click/drag).
        dx = (pygame.K_RIGHT in self._held_dirs) - (pygame.K_LEFT in self._held_dirs)
        dy = (pygame.K_DOWN in self._held_dirs) - (pygame.K_UP in self._held_dirs)
        self._player.set_move_dir(dx, dy)

        # Move each character, then resolve against the obstacle silhouettes with
        # move-and-slide so they glide around furniture instead of pinning on it.
        old_player = self._player.rect.copy()
        self._player.update(dt, self._play_bounds)
        self._slide_out(self._player.rect, old_player)

        npc_clear: dict = {}
        for npc in self._npcs:
            old = npc.rect.copy()
            npc.update(dt, self._player.rect)
            self._slide_out(npc.rect, old)
            npc_clear[npc] = npc.rect.copy()  # position now known clear of obstacles

        for poo in self._poos:
            poo.update(dt)
        for pu in self._powerups:
            pu.update(dt)

        # Tenants don't pile up: separate overlapping NPCs, then slide any that got
        # shoved into furniture back toward their just-cleared position.
        self._separate_npcs()
        for npc in self._npcs:
            self._slide_out(npc.rect, npc_clear[npc])

        # A powered surprise is a trap: the first tenant to step on the whippy poo
        # turns it into a splat and gets considerably slowed. Once it is a splat it
        # no longer affects anyone (it fades on its own).
        for npc in self._npcs:
            for poo in self._poos:
                if poo.powered and not poo.is_splat and npc.rect.colliderect(poo.rect):
                    poo.splat()
                    npc.apply_slow()

        collected = pygame.sprite.spritecollide(self._player, self._powerups, True)
        if collected:
            self._player.set_invincible(True)
            self.audio.play_sfx("powerup_fart")

        if not self._player.is_invincible:
            if pygame.sprite.spritecollide(self._player, self._npcs, False):
                # Losing keeps its original behaviour: cut the music on game over.
                self.audio.play_sfx("lose_life")
                self.audio.stop_music()
                self.sm.force_state(GameState.END)

    def _blocked(self, rect: pygame.Rect) -> bool:
        """True if rect overlaps any obstacle's visible shape (exact pixel mask)."""
        return any(obs.collides_rect(rect) for obs in self._obstacles)

    def _slide_out(self, rect: pygame.Rect, old_rect: pygame.Rect) -> None:
        """Resolve rect against obstacle silhouettes by moving and sliding from a
        known-clear ``old_rect`` (in-place). If the full move hits furniture, keep
        whichever single axis is free so the mover slides along the edge and rounds
        the obstacle; if both axes are blocked, hold at ``old_rect``. As a safety
        net (mover already inside the shape, e.g. after separation), eject to the
        nearest edge."""
        if not self._blocked(rect):
            return
        # Slide on X (revert Y), then on Y (revert X).
        slid_x = rect.copy()
        slid_x.y = old_rect.y
        if not self._blocked(slid_x):
            rect.y = old_rect.y
            return
        slid_y = rect.copy()
        slid_y.x = old_rect.x
        if not self._blocked(slid_y):
            rect.x = old_rect.x
            return
        # Both axes blocked: fall back to old position; if that was already inside
        # the shape, eject to the nearest free edge.
        rect.topleft = old_rect.topleft
        for obs in self._obstacles:
            obs.push_out(rect)

    def _separate_npcs(self, passes: int = 4) -> None:
        """Push apart any pair of NPCs whose hitboxes overlap (min-overlap axis),
        moving each half the overlap. Relaxed over a few passes so tight clusters
        (e.g. several tenants chasing the same spot) spread instead of stacking,
        then clamp everyone back inside the play bounds."""
        npcs = list(self._npcs)
        for _ in range(passes):
            moved = False
            for i in range(len(npcs)):
                for j in range(i + 1, len(npcs)):
                    a, b = npcs[i].rect, npcs[j].rect
                    if not a.colliderect(b):
                        continue
                    moved = True
                    ox = min(a.right - b.left, b.right - a.left)
                    oy = min(a.bottom - b.top, b.bottom - a.top)
                    if ox <= oy:
                        shift = ox // 2 + 1
                        a.x, b.x = (a.x - shift, b.x + shift) if a.centerx <= b.centerx else (a.x + shift, b.x - shift)
                    else:
                        shift = oy // 2 + 1
                        a.y, b.y = (a.y - shift, b.y + shift) if a.centery <= b.centery else (a.y + shift, b.y - shift)
            if not moved:
                break
        for npc in npcs:
            clamp_rect(npc.rect, self._play_bounds)

    def draw(self) -> None:
        self.screen.blit(self._map, (0, 0))

        # Draw each entity centered on its hitbox (the per-sprite draw()), not via
        # Group.draw which blits at rect.topleft and offsets art whose render size
        # differs from its hitbox (NPCs, obstacles) down-right of where it collides.
        for poo in self._poos:
            poo.draw(self.screen)
        for obs in self._obstacles:
            obs.draw(self.screen)
        for pu in self._powerups:
            pu.draw(self.screen)
        for npc in self._npcs:
            npc.draw(self.screen)
        self._player.draw(self.screen)

        hud = pygame.Surface((config.SCREEN_WIDTH, _HUD_H), pygame.SRCALPHA)
        hud.fill((20, 20, 20, 200))
        self.screen.blit(hud, (0, 0))

        score_surf = self._font_hud.render(f"Score: {self.score}", True, config.WHITE)
        self.screen.blit(score_surf, (16, (_HUD_H - score_surf.get_height()) // 2))

        if self.test_mode:
            timer_surf = self._font_hud.render("NO TIMER", True, (255, 180, 0))
        else:
            secs = max(0, int(self._level_time_remaining))
            timer_surf = self._font_hud.render(
                f"Time: {secs // 60}:{secs % 60:02d}", True, config.WHITE
            )
        self.screen.blit(
            timer_surf,
            (config.SCREEN_WIDTH - timer_surf.get_width() - 16,
             (_HUD_H - timer_surf.get_height()) // 2),
        )

        # Hover-For-Help button, left of centre in the HUD bar.
        btn_color = (80, 80, 180) if self._help_visible else (50, 50, 120)
        pygame.draw.rect(self.screen, btn_color, self._help_btn, border_radius=6)
        pygame.draw.rect(self.screen, config.WHITE, self._help_btn, width=1, border_radius=6)
        lbl = self._font_help_btn.render("? Hover for Help", True, config.WHITE)
        self.screen.blit(lbl, lbl.get_rect(center=self._help_btn.center))

        if self._player.is_invincible:
            inv_surf = self._font_hud.render("INVINCIBLE!", True, config.GREEN)
            self.screen.blit(
                inv_surf,
                ((config.SCREEN_WIDTH - inv_surf.get_width()) // 2,
                 (_HUD_H - inv_surf.get_height()) // 2),
            )

        if self._help_visible:
            self._draw_help_overlay()

    def _draw_help_overlay(self) -> None:
        line_h = self._font_help.get_linesize()
        pad = 28
        # Panel is 640px wide; at size 22 the longest line is 562px — fits with margin.
        panel_w = 640
        panel_h = line_h * len(_HELP_LINES) + pad * 2 + 12
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((10, 10, 30, 220))
        panel_rect = panel.get_rect(
            center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 30)
        )
        self.screen.blit(panel, panel_rect)
        pygame.draw.rect(self.screen, config.WHITE, panel_rect, width=2, border_radius=8)

        y = panel_rect.top + pad
        for i, line in enumerate(_HELP_LINES):
            color = (255, 220, 60) if i == 0 else config.WHITE
            surf = self._font_help.render(line, True, color)
            rect = surf.get_rect(centerx=config.SCREEN_WIDTH // 2, top=y)
            self.screen.blit(surf, rect)
            y += line_h + (8 if i == 0 else 2)
