import math
import json
import os
import pygame
import sys
import random

_SAVE_PATH = os.path.join(os.path.dirname(__file__), "save.json")

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, COLORS, LEVEL_COUNT, FIRST_RUN_LEVELS, WEAPONS
from settings import FONT_NAME
from entities.player import CHARACTERS
from entities.grenade import EXPLOSION_RADIUS, EXPLOSION_DAMAGE
from entities.biome_item import BiomeItem
from entities.enemy import BasicEnemy, ShooterEnemy, MiniBoss, FinalBoss
from entities.pickup import WeaponPickup
from entities.health_pickup import HealthPickup
from levels.level_data import LEVEL_DEFINITIONS
from tutorial import TutorialScreen
from lobby import LobbyScreen, UPGRADES
from auth import AuthScreen, load_user_save, write_user_save, load_highscore, submit_highscore
import sounds as _sounds
from sounds import play_music as _play_music, stop_music as _stop_music

pygame.init()
_sounds.init()
pygame.display.set_caption("Python Platformer Adventure")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(FONT_NAME, 20)
large_font = pygame.font.Font(FONT_NAME, 44)


def draw_text(surface, text, size, x, y, color):
    font_obj = pygame.font.Font(FONT_NAME, size)
    text_obj = font_obj.render(text, True, color)
    surface.blit(text_obj, (x, y))


class Level:
    def __init__(self, number, definition, biome_override=None):
        self.number = number
        # 0-13 across both runs; endless mode passes an explicit biome.
        self.biome = biome_override if biome_override is not None else number - 1
        self.platforms = [pygame.Rect(*rect) for rect in definition["platforms"]]
        self.enemies = pygame.sprite.Group()
        self.pickups = pygame.sprite.Group()
        self.health_pickups = pygame.sprite.Group()
        self.portal = pygame.Rect(*definition["portal"], 50, 60)
        self.portal_active = False
        self.pickup_timer = 0
        self._lava_tick = 0
        self.spikes     = self._build_spikes()     if self.biome in (0,1,6,7,9)    else []
        self.lava_pools = self._build_lava_pools() if self.biome in (3,8,10,13)   else []
        self.lava_y     = (545 if self.biome == 10 else
                           540 if self.biome == 13 else
                           562 if self.biome == 4  else None)
        self.is_icy     = self.biome in (5, 12)
        self.quicksand  = self._build_quicksand() if self.biome in (2, 11)      else []
        self._build_enemies(definition["enemies"])
        self._build_pickups(definition.get("pickups", []))

    def _build_spikes(self):
        rng = random.Random(101 + self.biome * 7)
        elev = [p for p in self.platforms if p.top < 570]
        centers, attempts = [], 0
        while len(centers) < 4 and attempts < 100:
            x = rng.randint(60, SCREEN_WIDTH - 60)
            if not any(p.left - 30 <= x <= p.right + 30 for p in elev):
                centers.append(x)
            attempts += 1
        spikes = []
        for cx in centers:
            for _ in range(rng.randint(3, 5)):
                x = max(16, min(SCREEN_WIDTH - 16, cx + rng.randint(-28, 28)))
                spikes.append(pygame.Rect(x - 8, 556, 16, 24))
        return spikes

    def _build_lava_pools(self):
        rng = random.Random(83 + self.biome * 11)
        elev = [p for p in self.platforms if p.top < 570]
        pools = []
        # Ground-level pools (avoid spots directly under elevated platforms)
        max_ground = 2 if self.biome == 10 else 4
        for _ in range(30):
            w = rng.randint(60, 130)
            x = rng.randint(20, SCREEN_WIDTH - w - 20)
            if not any(p.left - 15 <= x + w // 2 <= p.right + 15 for p in elev):
                pools.append(pygame.Rect(x, 562, w, 18))
            if len(pools) == max_ground:
                break
        # One lava pool on top of each elevated platform (skipped for Infernal)
        if self.biome != 10:
            for plat in elev:
                if plat.width < 50:
                    continue
                pw = rng.randint(28, min(plat.width - 14, 65))
                px = rng.randint(plat.left + 6, plat.right - pw - 6)
                pools.append(pygame.Rect(px, plat.top - 8, pw, 20))
        return pools

    def _build_quicksand(self):
        rng = random.Random(55 + self.biome * 13)
        elev = [p for p in self.platforms if p.top < 570]
        patches = []
        for _ in range(20):
            w = rng.randint(80, 160)
            x = rng.randint(40, SCREEN_WIDTH - w - 40)
            cx = x + w // 2
            if not any(p.left - 15 <= cx <= p.right + 15 for p in elev):
                patches.append(pygame.Rect(x, 562, w, 18))
            if len(patches) == 5:
                break
        return patches

    def _build_enemies(self, enemy_data):
        for kind, x, y in enemy_data:
            if kind == "basic":
                self.enemies.add(BasicEnemy(x, y))
            elif kind == "shooter":
                self.enemies.add(ShooterEnemy(x, y))
            elif kind == "miniboss":
                self.enemies.add(MiniBoss(x, y))
            elif kind == "boss":
                self.enemies.add(FinalBoss(x, y))

    def _build_pickups(self, pickup_data):
        for weapon_type, x, y in pickup_data:
            self.pickups.add(WeaponPickup(weapon_type, x, y))

    def update(self, player, enemy_projectiles):
        for enemy in self.enemies:
            enemy.update(player, enemy_projectiles, self.platforms)
        self._lava_tick += 1
        self.pickup_timer += 1
        if self.pickup_timer >= 360:
            platform = random.choice(self.platforms)
            x = random.randint(platform.left + 20, platform.right - 20)
            y = platform.top - 40
            pickup_type = random.choice(["health1", "health2", "weapon"])
            if pickup_type == "health1":
                self.health_pickups.add(HealthPickup(x, y, 1))
            elif pickup_type == "health2":
                self.health_pickups.add(HealthPickup(x, y, 2))
            else:
                weapon_type = random.choice(["pistol", "blaster", "rifle", "shotgun"])
                self.pickups.add(WeaponPickup(weapon_type, x, y))
            self.pickup_timer = 0
        
        self.pickups.update()
        self.health_pickups.update()

    def draw(self, surface, platform_color=None):
        col = platform_color if platform_color else COLORS["platform"]
        for platform in self.platforms:
            pygame.draw.rect(surface, col, platform)

        # Ice overlay on platforms
        if self.is_icy:
            for platform in self.platforms:
                pygame.draw.rect(surface, (165, 215, 245),
                                 (platform.left, platform.top, platform.width, 5))
                pygame.draw.rect(surface, (210, 238, 255),
                                 (platform.left + 2, platform.top + 1, platform.width - 4, 2))

        # Floor hazard: lava / toxic water / infernal / hellscape
        if self.lava_y:
            anim_shift = (self._lava_tick // 8) % 20
            if self.biome in (3, 10):    # volcano / infernal
                fill_col  = (195, 45, 0)
                surf_col  = (255, 130, 0)
                glow_col  = (255, 215, 50)
                blob_col  = (255, 160, 10)
            elif self.biome == 13:       # hellscape — deep crimson
                fill_col  = (140, 0, 0)
                surf_col  = (220, 20, 0)
                glow_col  = (255, 80, 20)
                blob_col  = (200, 40, 0)
            else:                        # swamp toxic water
                fill_col  = (14, 38, 18)
                surf_col  = (32, 72, 36)
                glow_col  = (52, 105, 48)
                blob_col  = (38, 85, 42)
            pygame.draw.rect(surface, fill_col,
                             (0, self.lava_y, SCREEN_WIDTH, SCREEN_HEIGHT - self.lava_y))
            pygame.draw.rect(surface, surf_col,
                             (0, self.lava_y, SCREEN_WIDTH, 10))
            pygame.draw.rect(surface, glow_col,
                             (0, self.lava_y + 2, SCREEN_WIDTH, 3))
            for i in range(0, SCREEN_WIDTH, 20):
                bx = (i + anim_shift * 4) % SCREEN_WIDTH
                pygame.draw.circle(surface, blob_col, (bx, self.lava_y + 5), 6)

        # Lava pools (volcano)
        anim_shift = (self._lava_tick // 8) % 20
        for pool in self.lava_pools:
            if self.biome == 8:   # ocean — electric jellyfish zones
                pygame.draw.rect(surface, (0, 60, 140), pool)
                pygame.draw.rect(surface, (20, 140, 255),
                                 (pool.x, pool.y, pool.width, 5))
                pygame.draw.rect(surface, (180, 230, 255),
                                 (pool.x, pool.y + 1, pool.width, 2))
                bx = pool.x + (anim_shift * 3) % max(1, pool.width)
                pygame.draw.circle(surface, (100, 200, 255), (bx, pool.y+4), 5)
            elif self.biome == 13: # hellscape — fire pools
                pygame.draw.rect(surface, (120, 0, 0), pool)
                pygame.draw.rect(surface, (220, 20, 0),
                                 (pool.x, pool.y, pool.width, 6))
                pygame.draw.rect(surface, (255, 80, 20),
                                 (pool.x, pool.y + 1, pool.width, 2))
                bx = pool.x + (anim_shift * 3) % max(1, pool.width)
                pygame.draw.circle(surface, (200, 40, 0), (bx, pool.y+4), 5)
            else:                  # volcano / infernal — lava
                pygame.draw.rect(surface, (185, 40, 0), pool)
                pygame.draw.rect(surface, (255, 125, 0),
                                 (pool.x, pool.y, pool.width, 6))
                pygame.draw.rect(surface, (255, 210, 45),
                                 (pool.x, pool.y + 1, pool.width, 2))
                bx = pool.x + (anim_shift * 3) % max(1, pool.width)
                pygame.draw.circle(surface, (255, 155, 5), (bx, pool.y+4), 5)

        # Quicksand patches (desert)
        for qs in self.quicksand:
            pygame.draw.rect(surface, (195, 162, 75), qs)
            pygame.draw.rect(surface, (218, 185, 98),
                             (qs.x + 5, qs.y + 3, qs.width - 10, 4))

        # Spikes — colour varies by biome
        if   self.biome == 0:  spike_col, spike_hi = (50, 130, 38),  (90, 175, 60)   # jungle thorns
        elif self.biome == 1:  spike_col, spike_hi = (165, 55, 45),  (220, 100, 80)  # mountain — red rock (contrast vs snowy bg)
        elif self.biome == 7:  spike_col, spike_hi = (90, 105, 145), (150, 165, 210) # space debris
        elif self.biome == 9:  spike_col, spike_hi = (145, 60, 215), (205, 125, 255) # crystal shards
        else:                  spike_col, spike_hi = (110, 70, 65),  (160, 105, 90)  # ruins / hell traps
        for spike in self.spikes:
            cx = spike.centerx
            pts = [(cx, spike.top), (spike.left, spike.bottom), (spike.right, spike.bottom)]
            # Orange-red warning glow that peeks out around the spike
            warn_pts = [(cx, spike.top - 3), (spike.left - 3, spike.bottom), (spike.right + 3, spike.bottom)]
            pygame.draw.polygon(surface, (210, 45, 0), warn_pts)
            pygame.draw.polygon(surface, spike_col, pts)
            pygame.draw.polygon(surface, spike_hi,
                                [(cx, spike.top + 4), (cx - 3, spike.top + 10),
                                 (cx + 3, spike.top + 10)])
            pygame.draw.polygon(surface, (15, 10, 10), pts, 1)

        portal_color = COLORS["portal_active"] if self.portal_active else COLORS["portal_inactive"]
        pygame.draw.rect(surface, portal_color, self.portal)
        self.pickups.draw(surface)
        self.health_pickups.draw(surface)
        self.enemies.draw(surface)
        
        for enemy in self.enemies:
            health_bar_width = enemy.rect.width
            health_bar_height = 4
            bar_x = enemy.rect.x
            bar_y = enemy.rect.y - 8
            
            pygame.draw.rect(surface, COLORS["health_bg"], (bar_x, bar_y, health_bar_width, health_bar_height))
            
            health_ratio = enemy.health / enemy.max_health
            filled_width = int(health_bar_width * health_ratio)
            pygame.draw.rect(surface, COLORS["health_fg"], (bar_x, bar_y, filled_width, health_bar_height))


class Game:
    _EFFECT_DESCRIPTIONS = {
        "speed":    "3× Speed  (5 s)",
        "flight":   "Free Flight  (5 s)",
        "shield":   "Shield: absorbs 5 hits",
        "damage":   "2× Bullet Damage  (5 s)",
        "rapid":    "3× Fire Rate  (5 s)",
        "freeze":   "All Enemies Frozen  (4 s)",
        "all":      "Speed + Flight + Power  (6 s)",
        "meteor":   "Instant damage to all enemies",
        "ammo":     "Full Ammo Refill",
        "crystal":  "Crystal Shield: 10 hits",
        "infernal": "2× Bullet Damage  (8 s)",
        "toxic":    "3× Fire Rate  (6 s)",
        "thunder":  "Speed + 2× Damage  (5 s)",
        "hell":     "All Powers  (12 s)",
    }

    def __init__(self):
        self.current_index = 0
        self.level = Level(1, LEVEL_DEFINITIONS[0])
        self.player = CHARACTERS[0](80, 520)
        self.enemy_projectiles = pygame.sprite.Group()
        self.grenades = pygame.sprite.Group()
        self.game_over = False
        self.victory = False
        self.auth_screen  = AuthScreen()
        self.auth_done    = False
        self.current_user = None          # None = guest
        self.tutorial     = TutorialScreen()
        self.tutorial_done = False
        self.paused       = False
        self._bg, self._platform_color = self._build_background(0)
        self._lava_dmg_tick   = 0
        self._spike_dmg_tick  = 0
        self._in_spikes       = False
        self._in_lava_hazard  = False
        self.biome_items = pygame.sprite.Group()
        self.biome_items.add(BiomeItem(0, *self._ITEM_XY[0]))
        self.coins          = 0
        self.upgrades       = {u["key"]: False for u in UPGRADES}
        self.in_lobby       = False
        self.lobby          = LobbyScreen()
        self.speedrun_timer = 0    # frames remaining; 0 = inactive
        self.timed_out      = False
        self.on_second_run  = False
        self.lobby_reached  = False
        self._item_banner   = None     # (name, desc, frames_remaining) or None
        # Endless mode (procedurally generated levels 15+)
        self.in_endless_mode   = False
        self.procedural_count  = 0     # completed endless levels (0-based)
        self.display_level_num = None  # overrides level text when set
        self.highscore = load_highscore()   # global {'best_level', 'best_user'}
        self._load_state()         # restore lobby / coins / upgrades if saved

    @staticmethod
    def _build_background(level_index):
        import random
        rng = random.Random(42 + level_index * 17)
        bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        W, H = SCREEN_WIDTH, SCREEN_HEIGHT

        def sky(top, bot):
            for y in range(H):
                t = y / H
                pygame.draw.line(bg, (
                    int(top[0] + (bot[0] - top[0]) * t),
                    int(top[1] + (bot[1] - top[1]) * t),
                    int(top[2] + (bot[2] - top[2]) * t),
                ), (0, y), (W, y))

        if level_index == 0:  # ── Jungle ──────────────────────────────────
            sky((8, 22, 8), (18, 38, 14))

            def jungle_tree(x, height, spread, c_can, c_trunk):
                tw = max(7, spread // 6)
                pygame.draw.rect(bg, c_trunk, (x - tw // 2, H - height, tw, height))
                for _ in range(rng.randint(4, 7)):
                    cx = x + rng.randint(-spread // 2, spread // 2)
                    cy = H - height + rng.randint(0, height // 2)
                    pygame.draw.circle(bg, c_can, (cx, cy),
                                       rng.randint(spread // 3, spread // 2))

            for _ in range(22):
                jungle_tree(rng.randint(0, W), rng.randint(160, 320),
                            rng.randint(80, 130), (24, 54, 22), (28, 42, 20))
            for _ in range(15):
                jungle_tree(rng.randint(-30, W + 30), rng.randint(260, 460),
                            rng.randint(100, 155), (17, 44, 15), (19, 33, 12))
            for _ in range(10):
                jungle_tree(rng.randint(-50, W + 50), rng.randint(360, 560),
                            rng.randint(120, 175), (12, 34, 10), (13, 25, 8))
            for _ in range(45):
                x = rng.randint(0, W)
                w, h = rng.randint(28, 75), rng.randint(22, 65)
                pygame.draw.ellipse(bg, (10, 30, 8), (x - w // 2, H - h + 12, w, h))
            platform_color = (65, 88, 45)

        elif level_index == 1:  # ── Mountains / Snow ────────────────────
            sky((110, 155, 200), (175, 210, 235))

            # Clouds
            for _ in range(8):
                cx, cy = rng.randint(50, W - 50), rng.randint(30, 180)
                for _ in range(rng.randint(3, 5)):
                    ox, oy = rng.randint(-40, 40), rng.randint(-15, 15)
                    pygame.draw.ellipse(bg, (230, 235, 242),
                                       (cx + ox - 30, cy + oy - 15, 60, 30))

            def mountain(x, peak_y, width, col, snow=(220, 230, 245)):
                pygame.draw.polygon(bg, col,
                                    [(x - width // 2, H), (x, peak_y), (x + width // 2, H)])
                sh = (H - peak_y) // 4
                pygame.draw.polygon(bg, snow,
                                    [(x - width // 6, peak_y + sh),
                                     (x, peak_y),
                                     (x + width // 6, peak_y + sh)])

            for _ in range(6):
                mountain(rng.randint(-40, W + 40), rng.randint(80, 250),
                         rng.randint(200, 350), (130, 130, 142))
            for _ in range(5):
                mountain(rng.randint(-30, W + 30), rng.randint(180, 380),
                         rng.randint(280, 420), (95, 95, 110))
            for _ in range(25):
                x = rng.randint(0, W)
                w, h = rng.randint(50, 120), rng.randint(15, 42)
                pygame.draw.ellipse(bg, (218, 228, 242), (x - w // 2, H - h + 10, w, h))
            platform_color = (118, 112, 130)

        elif level_index == 2:  # ── Desert ──────────────────────────────
            sky((195, 125, 40), (242, 198, 95))

            pygame.draw.circle(bg, (255, 242, 140), (820, 75), 55)
            pygame.draw.circle(bg, (255, 255, 205), (820, 75), 40)

            for _ in range(9):
                x = rng.randint(-60, W + 60)
                w, h = rng.randint(260, 520), rng.randint(80, 200)
                pygame.draw.ellipse(bg, (172, 135, 68), (x - w // 2, H - h + 20, w, h))
            for _ in range(6):
                x = rng.randint(-40, W + 40)
                w, h = rng.randint(200, 420), rng.randint(50, 130)
                pygame.draw.ellipse(bg, (152, 115, 52), (x - w // 2, H - h + 30, w, h))

            def cactus(x, base_y, height):
                tw = 12
                pygame.draw.rect(bg, (52, 98, 42), (x - tw // 2, base_y - height, tw, height))
                ay = base_y - height * 2 // 3
                pygame.draw.rect(bg, (52, 98, 42), (x - tw // 2 - 26, ay - 22, 10, 32))
                pygame.draw.rect(bg, (52, 98, 42), (x - tw // 2 - 26, ay - 22, 26, 10))
                pygame.draw.rect(bg, (52, 98, 42), (x + tw // 2 + 16, ay - 28, 10, 36))
                pygame.draw.rect(bg, (52, 98, 42), (x + tw // 2, ay - 28, 26, 10))

            for _ in range(7):
                cactus(rng.randint(60, W - 60), H + 10, rng.randint(60, 130))
            platform_color = (180, 148, 86)

        elif level_index == 3:  # ── Volcano ─────────────────────────────
            sky((22, 6, 4), (52, 16, 6))

            for y in range(H - 85, H):
                t = (y - (H - 85)) / 85
                pygame.draw.line(bg, (int(130 + t * 125), int(38 + t * 28), 0),
                                 (0, y), (W, y))

            def volcano(x, peak_y, width, col):
                pygame.draw.polygon(bg, col,
                                    [(x - width // 2, H),
                                     (x - width // 8, peak_y + 42),
                                     (x + width // 8, peak_y + 42),
                                     (x + width // 2, H)])
                pygame.draw.ellipse(bg, (78, 22, 8),
                                    (x - width // 8 - 6, peak_y + 22, width // 4 + 12, 28))
                pygame.draw.ellipse(bg, (215, 75, 8),
                                    (x - width // 10, peak_y + 30, width // 5, 16))

            for _ in range(3):
                volcano(rng.randint(50, W - 50), rng.randint(100, 320),
                        rng.randint(280, 500), (36, 16, 10))
            for _ in range(2):
                volcano(rng.randint(0, W), rng.randint(200, 400),
                        rng.randint(200, 380), (26, 10, 6))

            for _ in range(18):
                cx, cy = rng.randint(0, W), rng.randint(30, H - 100)
                r = rng.randint(15, 40)
                s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (58, 52, 52, rng.randint(28, 75)), (r, r), r)
                bg.blit(s, (cx - r, cy - r))

            for _ in range(6):
                x = rng.randint(100, W - 100)
                y0 = rng.randint(H // 3, H // 2)
                for seg in range(8):
                    x += rng.randint(-10, 10)
                    pygame.draw.circle(bg, (195 + rng.randint(0, 55), 58, 0),
                                       (x, y0 + seg * 25), rng.randint(3, 7))
            platform_color = (70, 40, 30)

        elif level_index == 4:  # ── Swamp ───────────────────────────────
            sky((16, 22, 12), (26, 34, 18))

            for y in range(H - 70, H):
                t = (y - (H - 70)) / 70
                pygame.draw.line(bg,
                                 (int(10 + t * 5), int(26 + t * 10), int(14 + t * 6)),
                                 (0, y), (W, y))
            for _ in range(12):
                x = rng.randint(0, W)
                y = rng.randint(H - 65, H - 10)
                pygame.draw.line(bg, (22, 48, 28), (x, y),
                                 (x + rng.randint(20, 60), y), 1)

            def dead_tree(x, height, col):
                tw = rng.randint(5, 10)
                pygame.draw.rect(bg, col, (x - tw // 2, H - height, tw, height))
                for _ in range(rng.randint(3, 6)):
                    by = H - rng.randint(height // 4, height * 3 // 4)
                    bdir = rng.choice([-1, 1])
                    blen = rng.randint(25, 60)
                    pygame.draw.line(bg, col, (x, by),
                                     (x + bdir * blen, by - rng.randint(10, 30)), 3)

            for _ in range(18):
                dead_tree(rng.randint(0, W), rng.randint(200, 480), (26, 36, 20))
            for _ in range(10):
                dead_tree(rng.randint(-30, W + 30), rng.randint(280, 560), (18, 26, 14))

            for _ in range(15):
                x = rng.randint(0, W)
                y = rng.randint(H // 2, H - 20)
                w, h = rng.randint(80, 200), rng.randint(15, 35)
                s = pygame.Surface((w, h), pygame.SRCALPHA)
                pygame.draw.ellipse(s, (175, 195, 165, 22), (0, 0, w, h))
                bg.blit(s, (x - w // 2, y))
            platform_color = (50, 66, 33)

        elif level_index == 5:  # ── Arctic / Ice ────────────────────────
            sky((148, 198, 232), (205, 228, 248))

            for i, col in enumerate([(80, 220, 150, 32), (60, 180, 230, 26),
                                      (140, 100, 220, 20)]):
                y = 55 + i * 52
                s = pygame.Surface((W, 42), pygame.SRCALPHA)
                pygame.draw.ellipse(s, col, (0, 0, W, 42))
                bg.blit(s, (0, y))

            for y in range(H - 55, H):
                t = (y - (H - 55)) / 55
                pygame.draw.line(bg,
                                 (int(198 + t * 32), int(218 + t * 26), int(238 + t * 16)),
                                 (0, y), (W, y))

            def ice_spike(x, height, width, col):
                hw = width // 2
                pygame.draw.polygon(bg, col,
                                    [(x - hw, H + 5), (x, H + 5 - height), (x + hw, H + 5)])

            for _ in range(28):
                ice_spike(rng.randint(0, W), rng.randint(40, 165),
                          rng.randint(20, 58), (178, 212, 238))
            for _ in range(16):
                ice_spike(rng.randint(0, W), rng.randint(65, 210),
                          rng.randint(26, 68), (155, 198, 228))
            for _ in range(22):
                x = rng.randint(0, W)
                w, h = rng.randint(55, 145), rng.randint(18, 48)
                pygame.draw.ellipse(bg, (218, 230, 244), (x - w // 2, H - h + 8, w, h))
            platform_color = (98, 152, 205)

        elif level_index == 6:  # ── Night / Ancient Ruins ─────────────────
            sky((4, 4, 16), (10, 8, 24))

            for _ in range(130):
                x, y = rng.randint(0, W), rng.randint(0, H * 2 // 3)
                br = rng.randint(155, 255)
                pygame.draw.circle(bg, (br, br, min(255, br + 25)), (x, y),
                                   rng.randint(1, 2))

            pygame.draw.circle(bg, (208, 214, 192), (880, 78), 52)
            pygame.draw.circle(bg, (8, 6, 20), (903, 65), 44)

            def pillar(x, height, width, col):
                pygame.draw.rect(bg, col, (x - width // 2, H - height, width, height))
                pygame.draw.rect(bg, col, (x - width // 2 - 6, H - height, width + 12, 14))
                pygame.draw.rect(bg, col, (x - width // 2 - 6, H - 14, width + 12, 14))

            for _ in range(14):
                pillar(rng.randint(30, W - 30), rng.randint(120, 430),
                       rng.randint(22, 46), (36, 32, 46))
            for _ in range(6):
                pillar(rng.randint(0, W), rng.randint(180, 530),
                       rng.randint(28, 56), (26, 22, 36))
            for _ in range(30):
                x = rng.randint(0, W)
                w, h = rng.randint(18, 58), rng.randint(7, 22)
                pygame.draw.ellipse(bg, (28, 24, 38), (x - w // 2, H - h + 10, w, h))
            platform_color = (80, 70, 94)

        elif level_index == 7:  # ── Space / Asteroid ─────────────────────
            sky((2, 2, 10), (6, 6, 22))
            # Stars
            for _ in range(220):
                sx, sy = rng.randint(0, W), rng.randint(0, H)
                br = rng.randint(140, 255)
                pygame.draw.circle(bg, (br, br, min(255, br + 30)), (sx, sy),
                                   rng.randint(0, 2))
            # Planets
            for pcol, pr, px, py in [
                ((100, 80, 200), 38, 820, 90),
                ((60, 130, 170), 22, 200, 130),
                ((180, 120, 60), 16, 600, 55),
            ]:
                pygame.draw.circle(bg, pcol, (px, py), pr)
                pygame.draw.circle(bg, tuple(min(255, c+50) for c in pcol),
                                   (px - pr//4, py - pr//4), pr//3)
                # ring on biggest planet
                if pr > 30:
                    pygame.draw.ellipse(bg, (*pcol, 120),
                                        pygame.Rect(px-pr-18, py-8, (pr+18)*2, 16))
            # Asteroid rubble on ground
            for _ in range(18):
                ax = rng.randint(0, W)
                aw, ah = rng.randint(18, 55), rng.randint(10, 28)
                pygame.draw.ellipse(bg, (48, 52, 62), (ax - aw//2, H - ah + 10, aw, ah))
            platform_color = (55, 60, 72)

        elif level_index == 8:  # ── Deep Ocean ────────────────────────────
            sky((4, 14, 48), (8, 38, 88))
            # Bioluminescent glow on floor
            for y in range(H - 55, H):
                t = (y - (H - 55)) / 55
                pygame.draw.line(bg, (int(8+t*10), int(38+t*20), int(70+t*30)),
                                 (0, y), (W, y))
            # Kelp strands
            for _ in range(22):
                kx = rng.randint(0, W)
                for seg in range(rng.randint(5, 12)):
                    ky = H - seg * 38 - 10
                    kx += rng.randint(-8, 8)
                    pygame.draw.ellipse(bg, (0, 85, 42), (kx - 4, ky - 14, 9, 28))
            # Bubbles
            for _ in range(35):
                bx, by = rng.randint(0, W), rng.randint(0, H)
                br = rng.randint(2, 7)
                s = pygame.Surface((br*2+2, br*2+2), pygame.SRCALPHA)
                pygame.draw.circle(s, (100, 180, 230, 55), (br, br), br, 1)
                bg.blit(s, (bx - br, by - br))
            # Fish silhouettes
            for _ in range(10):
                fx, fy = rng.randint(50, W-50), rng.randint(H//4, H*3//4)
                pygame.draw.ellipse(bg, (0, 38, 78), (fx-14, fy-5, 28, 10))
                pygame.draw.polygon(bg, (0, 38, 78),
                                    [(fx-14, fy), (fx-24, fy-7), (fx-24, fy+7)])
            platform_color = (20, 70, 88)

        elif level_index == 9:  # ── Crystal Cave ──────────────────────────
            sky((4, 0, 18), (12, 4, 32))
            # Crystal spires from ground
            for _ in range(24):
                cx = rng.randint(0, W)
                ch = rng.randint(55, 210)
                cw = rng.randint(14, 38)
                col = rng.choice([(95,45,200),(145,75,255),(75,25,155),(190,95,255)])
                pygame.draw.polygon(bg, col,
                                    [(cx, H - ch), (cx - cw//2, H), (cx + cw//2, H)])
                pygame.draw.polygon(bg, tuple(min(255, c+65) for c in col),
                                    [(cx, H-ch), (cx-2, H-ch+28), (cx+2, H-ch+28)])
            # Stalactites from ceiling
            for _ in range(16):
                cx = rng.randint(0, W)
                ch = rng.randint(25, 95)
                cw = rng.randint(8, 22)
                pygame.draw.polygon(bg, (70, 28, 145),
                                    [(cx, ch), (cx - cw//2, 0), (cx + cw//2, 0)])
            # Glow patches
            for _ in range(22):
                gx, gy = rng.randint(0, W), rng.randint(H//2, H)
                gr = rng.randint(14, 42)
                s = pygame.Surface((gr*2, gr*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (115, 45, 195, 38), (gr, gr), gr)
                bg.blit(s, (gx-gr, gy-gr))
            platform_color = (88, 42, 128)

        elif level_index == 10:  # ── Infernal Lava World ───────────────────
            sky((28, 4, 0), (65, 18, 4))
            # Extreme lava horizon glow
            for y in range(H - 110, H):
                t = (y - (H - 110)) / 110
                pygame.draw.line(bg,
                                 (int(160 + t*90), int(28 + t*18), 0),
                                 (0, y), (W, y))
            # Fire pillars
            for _ in range(9):
                fx = rng.randint(30, W - 30)
                fh = rng.randint(90, 280)
                pygame.draw.rect(bg, (170, 45, 0), (fx - 7, H - fh, 14, fh))
                pygame.draw.ellipse(bg, (255, 115, 0),
                                    (fx - 18, H - fh - 28, 36, 56))
                pygame.draw.ellipse(bg, (255, 200, 50),
                                    (fx - 9, H - fh - 14, 18, 28))
            # Lava veins background
            for _ in range(8):
                lx, ly = rng.randint(50, W-50), rng.randint(H//3, H*2//3)
                pygame.draw.line(bg, (255, 90, 0),
                                 (lx, ly),
                                 (lx + rng.randint(-70, 70), ly + 70), 5)
            platform_color = (200, 155, 90)

        elif level_index == 11:  # ── Mushroom Forest ──────────────────────
            sky((4, 7, 4), (10, 16, 8))
            # Giant mushrooms
            def shroom(x, base, h, cap_col):
                sw = max(8, h // 6)
                pygame.draw.rect(bg, (175, 155, 125), (x-sw//2, base-h, sw, h))
                cw, ch = h // 2, h // 4
                pygame.draw.ellipse(bg, cap_col, (x-cw//2, base-h-ch, cw, ch*2))
                pygame.draw.ellipse(bg, tuple(min(255, c+55) for c in cap_col),
                                    (x-cw//4, base-h-ch//2, cw//2, ch))
            for _ in range(18):
                col = rng.choice([(175,45,45),(45,95,195),(145,45,175),
                                  (195,95,45),(45,175,45),(175,145,45)])
                shroom(rng.randint(0, W), H+10, rng.randint(80, 280), col)
            # Bioluminescent glow
            for _ in range(28):
                gx, gy = rng.randint(0, W), rng.randint(H//3, H)
                gr = rng.randint(10, 32)
                gcol = rng.choice([(75,195,75),(95,95,215),(175,75,175)])
                s = pygame.Surface((gr*2, gr*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*gcol, 32), (gr, gr), gr)
                bg.blit(s, (gx-gr, gy-gr))
            # Spore particles
            for _ in range(40):
                sx, sy = rng.randint(0, W), rng.randint(0, H)
                pygame.draw.circle(bg, (180, 220, 140), (sx, sy), 2)
            platform_color = (88, 58, 32)

        elif level_index == 12:  # ── Storm Tundra ──────────────────────────
            sky((95, 105, 125), (135, 148, 162))
            # Storm clouds
            for _ in range(9):
                cx, cy = rng.randint(50, W-50), rng.randint(15, 145)
                for _ in range(rng.randint(4, 7)):
                    ox, oy = rng.randint(-50, 50), rng.randint(-20, 20)
                    pygame.draw.ellipse(bg, (75, 82, 98),
                                        (cx+ox-35, cy+oy-18, 70, 36))
            # Lightning bolts
            for _ in range(4):
                lx, ly = rng.randint(100, W-100), rng.randint(0, H//3)
                pts = [(lx, ly)]
                for _ in range(5):
                    lx += rng.randint(-22, 22)
                    ly += rng.randint(45, 80)
                    pts.append((lx, ly))
                pygame.draw.lines(bg, (215, 228, 255), False, pts, 2)
                pygame.draw.lines(bg, (255, 255, 255), False, pts[:2], 1)
            # Ice/snow ground
            for _ in range(28):
                sx = rng.randint(0, W)
                sw, sh = rng.randint(35, 90), rng.randint(12, 32)
                pygame.draw.ellipse(bg, (195, 212, 228), (sx-sw//2, H-sh+8, sw, sh))
            # Snow particles
            for _ in range(55):
                sx, sy = rng.randint(0, W), rng.randint(0, H)
                pygame.draw.circle(bg, (220, 230, 242), (sx, sy),
                                   rng.randint(1, 3))
            platform_color = (128, 148, 168)

        else:  # level_index == 13  ── Hellscape / Final ────────────────────
            sky((12, 0, 0), (38, 4, 4))
            # Ground glow
            for y in range(H - 65, H):
                t = (y - (H - 65)) / 65
                pygame.draw.line(bg, (int(95+t*95), 0, 0), (0, y), (W, y))
            # Fire pillars
            for _ in range(14):
                fx = rng.randint(20, W-20)
                fh = rng.randint(75, 245)
                pygame.draw.rect(bg, (115, 0, 0), (fx-5, H-fh, 10, fh))
                pygame.draw.ellipse(bg, (215, 25, 0),
                                    (fx-14, H-fh-18, 28, 36))
                pygame.draw.ellipse(bg, (255, 75, 0),
                                    (fx-7, H-fh-9, 14, 18))
            # Ground cracks glowing
            for _ in range(22):
                cx = rng.randint(0, W)
                cy = H - rng.randint(0, 38)
                pygame.draw.line(bg, (195, 15, 0), (cx, cy),
                                 (cx+rng.randint(-32, 32), cy-rng.randint(8, 28)), 2)
            # Embers
            for _ in range(45):
                ex, ey = rng.randint(0, W), rng.randint(H//3, H)
                pygame.draw.circle(bg, (255, rng.randint(28, 75), 0), (ex, ey), 2)
            platform_color = (72, 10, 8)

        return bg, platform_color

    def reset_player(self):
        char_idx = min(self.current_index, len(CHARACTERS) - 1)
        self.player = CHARACTERS[char_idx](80, 520)
        self.enemy_projectiles.empty()
        # Apply permanent shop upgrades
        if self.upgrades.get("hp"):
            self.player.max_health += 3
            self.player.health = self.player.max_health
        if self.upgrades.get("ammo"):
            for wt in self.player.ammo:
                self.player.ammo[wt] += 10
        if self.upgrades.get("damage"):
            self.player.damage_bonus += 1
        if self.upgrades.get("grenades"):
            self.player.max_grenades += 1
        if self.upgrades.get("armor"):
            self.player.damage_reduction += 1
        if self.upgrades.get("jump"):
            self.player.max_air_jumps += 1
        if self.upgrades.get("speed"):
            self.player.speed_mult = 1.25
        if self.upgrades.get("shield"):
            self.player.shield_charges += 2

    # Grenades granted at level start (Rookie = none; second run gets +1 extra)
    _LEVEL_GRENADES = {
        1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3,
        7: 2, 8: 2, 9: 3, 10: 3, 11: 3, 12: 3, 13: 3,
    }

    # Biome item positions — 7 per run, cycling
    _ITEM_XY = [
        # Run 1 (levels 1-7, indices 0-6)
        (140, 558), (230, 468), (215, 438), (155, 478),
        (175, 468), (130, 478), (305, 408),
        # Run 2 (levels 8-14, indices 7-13) — first platform near spawn
        (215, 448), (175, 468), (155, 468), (150, 478),
        (130, 478), (145, 488), (130, 488),
    ]

    def _save_data(self):
        return {
            "lobby_reached": self.lobby_reached,
            "coins":         self.coins,
            "upgrades":      self.upgrades,
        }

    def _apply_save(self, data):
        self.lobby_reached = data.get("lobby_reached", False)
        self.coins         = data.get("coins", 0)
        self.upgrades      = {u["key"]: data.get("upgrades", {}).get(u["key"], False)
                              for u in UPGRADES}
        if self.lobby_reached:
            self.in_lobby = True
            self.lobby    = LobbyScreen()

    def _save_state(self):
        if self.current_user:
            write_user_save(self.current_user, self._save_data())
        else:
            try:
                with open(_SAVE_PATH, "w") as f:
                    json.dump(self._save_data(), f)
            except OSError:
                pass

    def _load_state(self):
        if self.current_user:
            data = load_user_save(self.current_user)
        else:
            try:
                with open(_SAVE_PATH) as f:
                    data = json.load(f)
            except (OSError, json.JSONDecodeError):
                return
        self.highscore = load_highscore()   # refresh global record on (re)load
        try:
            self._apply_save(data)
        except (KeyError, TypeError):
            pass

    def _draw_buff_effects(self, surface, glow_only=True):
        p     = self.player
        tick  = pygame.time.get_ticks()
        pulse = (math.sin(tick * 0.006) + 1) / 2   # 0→1 smoothly

        def glow(color, px=12, py=8):
            if not glow_only:
                return
            alpha = int(65 + 85 * pulse)
            s = pygame.Surface((p.rect.width + px*2, p.rect.height + py*2), pygame.SRCALPHA)
            pygame.draw.ellipse(s, (*color, alpha), s.get_rect())
            surface.blit(s, (p.rect.x - px, p.rect.y - py))

        # ── Speed — yellow glow | trailing lines ─────────────────────────────
        if p.speed_timer > 0:
            glow((255, 220, 0))
            if not glow_only:
                for i in range(4):
                    lx = p.rect.centerx - p.facing * (16 + i * 9)
                    ly = p.rect.top + 8 + i * 9
                    pygame.draw.line(surface, (255, 200, 50),
                                     (lx, ly), (lx - p.facing * 14, ly), 2)

        # ── Flight — sky-blue glow | animated wings ───────────────────────────
        if p.flight_timer > 0:
            glow((80, 160, 255), px=18, py=14)
            if not glow_only:
                wing_flap = int(8 * pulse)
                for side in (-1, 1):
                    wx = p.rect.centerx + side * (p.rect.width // 2)
                    wy = p.rect.centery
                    pts = [
                        (wx,             wy + 4),
                        (wx + side * 22, wy - 10 - wing_flap),
                        (wx + side * 26, wy),
                        (wx + side * 16, wy + 16 + wing_flap),
                    ]
                    pygame.draw.polygon(surface, (120, 195, 255), pts)
                    pygame.draw.polygon(surface, (200, 230, 255), pts, 1)

        # ── Shield — gold glow | hexagonal barrier ────────────────────────────
        if p.shield_charges > 0:
            glow((255, 215, 0), px=14, py=10)
            if not glow_only:
                r  = max(p.rect.width, p.rect.height) // 2 + 12
                cx, cy = p.rect.center
                pts = [(cx + int(r * math.cos(math.radians(i * 60 - 30))),
                        cy + int(r * math.sin(math.radians(i * 60 - 30)))) for i in range(6)]
                alpha = int(45 + 80 * pulse)
                sh = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                pygame.draw.polygon(sh, (255, 215, 0, alpha), pts)
                pygame.draw.polygon(sh, (255, 245, 120, min(255, alpha + 90)), pts, 2)
                surface.blit(sh, (0, 0))

        # ── Damage boost — red glow | shoulder flames ─────────────────────────
        if p.dmg_boost_timer > 0:
            glow((255, 70, 15))
            if not glow_only:
                fh = 9 + int(9 * pulse)
                for fx in (p.rect.left + 4, p.rect.centerx - 4, p.rect.right - 12):
                    pygame.draw.ellipse(surface, (255, 110, 20),
                                        (fx, p.rect.top - fh, 9, fh + 4))
                    pygame.draw.ellipse(surface, (255, 225, 55),
                                        (fx + 1, p.rect.top - fh + 3, 7, fh - 1))

        # ── Rapid fire — green glow | floating spore bubbles ─────────────────
        if p.rapid_timer > 0:
            glow((60, 210, 80))
            if not glow_only:
                rng = random.Random(tick // 120)
                for i in range(6):
                    bx = p.rect.left + rng.randint(0, p.rect.width)
                    rise = (tick // 4 + i * 40) % (p.rect.height + 20)
                    by   = p.rect.bottom - rise
                    r    = rng.randint(3, 6)
                    alpha = max(0, 200 - rise * 5)
                    bs = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
                    pygame.draw.circle(bs, (80, 230, 90, alpha), (r, r), r)
                    surface.blit(bs, (bx - r, by - r))

        # ── Ancient Power (all timers equal & active) — golden star burst ─────
        all_active = (p.speed_timer > 0 and p.flight_timer > 0 and p.dmg_boost_timer > 0
                      and p.speed_timer == p.flight_timer == p.dmg_boost_timer)
        if all_active:
            glow((255, 215, 0), px=22, py=16)
            if not glow_only:
                cx, cy = p.rect.center
                rays = 12
                for i in range(rays):
                    angle = math.radians(i * (360 / rays) + tick * 0.1)
                    r_out = 28 + int(8 * pulse)
                    r_in  = 14
                    ox = cx + int(r_out * math.cos(angle))
                    oy = cy + int(r_out * math.sin(angle))
                    ix = cx + int(r_in  * math.cos(angle))
                    iy = cy + int(r_in  * math.sin(angle))
                    col = (255, 215, 0) if i % 2 == 0 else (255, 255, 160)
                    pygame.draw.line(surface, col, (ix, iy), (ox, oy), 2)
                pygame.draw.circle(surface, (255, 255, 200), (cx, cy), 6)
                pygame.draw.circle(surface, (255, 215, 0),   (cx, cy), 4)

    def _apply_buff(self, item):
        p = self.player
        if item.effect == "speed":
            p.speed_timer = item.duration
        elif item.effect == "flight":
            p.flight_timer = item.duration
        elif item.effect == "shield":
            p.shield_charges += item.duration
        elif item.effect == "damage":
            p.dmg_boost_timer = item.duration
        elif item.effect == "rapid":
            p.rapid_timer = item.duration
        elif item.effect == "freeze":
            for enemy in self.level.enemies:
                enemy.frozen_timer = item.duration
        elif item.effect == "all":
            p.speed_timer = p.flight_timer = p.dmg_boost_timer = item.duration
        # ── Second-run biome effects ──────────────────────────────────────────
        elif item.effect == "meteor":
            for enemy in self.level.enemies:
                enemy.take_damage(EXPLOSION_DAMAGE)
        elif item.effect == "ammo":
            for wt in p.ammo:
                p.ammo[wt] = WEAPONS[wt]["ammo"]
        elif item.effect == "crystal":
            p.shield_charges += item.duration   # 10 charges
        elif item.effect == "infernal":
            p.dmg_boost_timer = item.duration    # 8 s of 2x damage
        elif item.effect == "toxic":
            p.rapid_timer = item.duration        # 6 s of 3x fire rate
        elif item.effect == "thunder":
            p.speed_timer = item.duration        # speed + damage combo
            p.dmg_boost_timer = item.duration
        elif item.effect == "hell":
            p.speed_timer = p.flight_timer = p.dmg_boost_timer = item.duration
            p.rapid_timer = item.duration        # all four for 12 s
        desc = self._EFFECT_DESCRIPTIONS.get(item.effect, "")
        self._item_banner = (item.name, desc, 240)  # show banner for 4 s

    def load_level(self, index):
        prev_weapon = self.player.weapon
        prev_ammo   = dict(self.player.ammo)

        self.current_index = index
        self.level = Level(index + 1, LEVEL_DEFINITIONS[index])
        self._bg, self._platform_color = self._build_background(index)
        if self.tutorial_done and not self.in_lobby:
            _play_music(f"music_{index}")
        self.grenades.empty()
        self.biome_items.empty()
        self.biome_items.add(BiomeItem(index, *self._ITEM_XY[index]))
        self.reset_player()
        self.player.grenades = self._LEVEL_GRENADES.get(index, 0)
        self.player.weapon   = prev_weapon
        self.player.ammo     = prev_ammo

    def load_procedural_level(self):
        from levels.procedural import generate_level
        prev_weapon = self.player.weapon
        prev_ammo   = dict(self.player.ammo)

        biome      = random.randint(0, 13)
        difficulty = self.procedural_count
        definition = generate_level(difficulty, biome)

        self.current_index     = 13                          # stay on Apex character
        self.display_level_num = 15 + self.procedural_count  # Level 15, 16, 17...
        self.procedural_count += 1

        self.level = Level(14, definition, biome_override=biome)
        self._bg, self._platform_color = self._build_background(biome)
        if self.tutorial_done and not self.in_lobby:
            _play_music(f"music_{biome}")

        self.grenades.empty()
        self.biome_items.empty()
        self.biome_items.add(BiomeItem(biome, *self._ITEM_XY[biome]))

        self.reset_player()
        self.player.grenades = 3
        self.player.weapon   = prev_weapon
        self.player.ammo     = prev_ammo

    def update(self):
        if not self.auth_done:
            self.auth_screen.update()
            return
        if not self.tutorial_done:
            return
        if self.paused:
            return
        if self.in_lobby:
            self.lobby.update()
            return
        if self.game_over or self.victory:
            return
        if self.speedrun_timer > 0:
            self.speedrun_timer -= 1
            if self.speedrun_timer == 0:
                self.timed_out = True
                self.game_over = True
        if self._item_banner:
            n, d, t = self._item_banner
            self._item_banner = (n, d, t - 1) if t > 1 else None
        keys = pygame.key.get_pressed()
        _prev_vx = self.player.vel.x
        self.player.handle_input(keys)
        # Ice: player slides on arctic platforms when not pressing movement keys
        if self.level.is_icy and self.player.on_ground:
            if not (keys[pygame.K_LEFT] or keys[pygame.K_a] or
                    keys[pygame.K_RIGHT] or keys[pygame.K_d]):
                self.player.vel.x = _prev_vx * 0.92
        # Quicksand / toxic spores — slow player before movement is applied
        for qs in self.level.quicksand:
            if self.player.rect.colliderect(qs):
                self.player.vel.x *= 0.20
                break
        self.player.update(self.level.platforms)
        self.level.update(self.player, self.enemy_projectiles)
        self.enemy_projectiles.update()

        self.biome_items.update()
        for item in pygame.sprite.spritecollide(self.player, self.biome_items, True):
            self._apply_buff(item)
            _sounds.play("pickup_item")

        weapon_pickups = pygame.sprite.spritecollide(self.player, self.level.pickups, True)
        for pickup in weapon_pickups:
            self.player.equip_weapon(pickup.weapon_type)
            _sounds.play("pickup_weapon")

        health_pickups = pygame.sprite.spritecollide(self.player, self.level.health_pickups, True)
        for pickup in health_pickups:
            self.player.health = min(self.player.max_health, self.player.health + pickup.amount)
            _sounds.play("pickup_health")

        bullet_hits = pygame.sprite.groupcollide(self.player.bullets, self.level.enemies, True, False)
        for bullet, enemies in bullet_hits.items():
            for enemy in enemies:
                enemy.take_damage(bullet.damage)
                if enemy.health <= 0:
                    _sounds.play("enemy_death")
                else:
                    _sounds.play("enemy_hit")

        hits = pygame.sprite.spritecollide(self.player, self.enemy_projectiles, True)
        for bullet in hits:
            self.player.take_damage(bullet.damage)
            _sounds.play("player_hit")

        # Spike hazards — player only (enemies are immune to traps)
        now_in_spikes = any(self.player.rect.colliderect(s) for s in self.level.spikes)
        if now_in_spikes:
            if not self._in_spikes:
                self.player.take_damage(1)
                self._spike_dmg_tick = 0
            else:
                self._spike_dmg_tick += 1
                spike_rate = 60 if self.level.biome in (0, 1) else 30
                if self._spike_dmg_tick >= spike_rate:
                    self.player.take_damage(1)
                    self._spike_dmg_tick = 0
        else:
            self._spike_dmg_tick = 0
        self._in_spikes = now_in_spikes

        # Lava / swamp / floor hazards — player only (enemies are immune to traps)
        in_lava  = any(self.player.rect.colliderect(p.inflate(-10, -4)) for p in self.level.lava_pools)
        in_swamp = (self.level.lava_y is not None and
                    self.player.rect.bottom >= self.level.lava_y)
        now_in_lava_hazard = in_lava or in_swamp
        if now_in_lava_hazard:
            if not self._in_lava_hazard:
                self.player.take_damage(2)
                self._lava_dmg_tick = 0
            else:
                self._lava_dmg_tick += 1
                if self._lava_dmg_tick >= 90:
                    self.player.take_damage(2)
                    self._lava_dmg_tick = 0
        else:
            self._lava_dmg_tick = 0
        self._in_lava_hazard = now_in_lava_hazard

        # Grenades: physics + explosion damage
        self.grenades.update(self.level.platforms)
        for grenade in list(self.grenades):
            if not grenade.exploded:
                for enemy in self.level.enemies:
                    if grenade.rect.colliderect(enemy.rect):
                        grenade._start_explosion()
                        break
        for grenade in self.grenades:
            if grenade.exploded and not grenade.damage_applied:
                grenade.damage_applied = True
                _sounds.play("explosion")
                blast = pygame.Vector2(grenade.rect.center)
                for enemy in self.level.enemies:
                    if blast.distance_to(pygame.Vector2(enemy.rect.center)) <= EXPLOSION_RADIUS:
                        enemy.take_damage(EXPLOSION_DAMAGE)

        enemy_contacts = pygame.sprite.spritecollide(self.player, self.level.enemies, False)
        for enemy in enemy_contacts:
            self.player.take_damage(2)
            direction = 1 if self.player.rect.centerx > enemy.rect.centerx else -1
            self.player.vel.x = direction * 8
            self.player.vel.y = -8
            enemy.take_damage(0, knockback_dir=-direction)

        # Safety sweep: kill any enemy whose health hit 0 but wasn't removed yet
        # (covers edge cases where take_damage's kill() path was skipped)
        for enemy in list(self.level.enemies):
            if enemy.health <= 0:
                enemy.kill()
                _sounds.play("enemy_death")
            elif enemy.rect.top > SCREEN_HEIGHT:
                enemy.kill()  # fell off screen bottom — unrescuable

        was_active = self.level.portal_active
        self.level.portal_active = len(self.level.enemies) == 0
        if self.level.portal_active and not was_active:
            _sounds.play("portal_open")

        if self.level.portal_active and self.player.rect.colliderect(self.level.portal):
            self.coins += 5
            _sounds.play("coin")
            _sounds.play("level_complete")
            idx = self.current_index

            # Global high-score: only signed-in users set the record.
            cleared_num = self.display_level_num if self.in_endless_mode else self.level.number
            if self.current_user and submit_highscore(self.current_user, cleared_num):
                self.highscore = load_highscore()

            if self.in_endless_mode:
                self.load_procedural_level()
            elif idx == FIRST_RUN_LEVELS - 1 and self.speedrun_timer == 0 and not self.on_second_run:
                # First completion of levels 1-7 → lobby
                self.coins += 30     # lobby bonus (on top of the 5)
                self.lobby_reached = True
                self.in_lobby = True
                self.lobby = LobbyScreen()
                self._save_state()
                _play_music("music_lobby")
            elif self.speedrun_timer > 0 and idx == FIRST_RUN_LEVELS - 1:
                self.victory = True
                self.speedrun_timer = 0
                _stop_music()
            elif idx + 1 < LEVEL_COUNT:
                self.load_level(idx + 1)
            else:
                self.victory = True
                _stop_music()

        if self.player.health <= 0:
            self.game_over = True
            _sounds.play("game_over")
            _stop_music()

    def draw_ui(self, surface):
        health_text = f"Health: {self.player.health}/{self.player.max_health}"
        weapon_text = f"Weapon: {self.player.weapon.title()}"
        ammo_text = f"Ammo: {self.player.ammo[self.player.weapon]}"
        if self.in_endless_mode:
            level_text = f"Level {self.display_level_num}  (Endless)"
        elif self.on_second_run:
            run_lvl = self.level.number - FIRST_RUN_LEVELS
            level_text = f"Level {run_lvl}/7  (Run 2)"
        elif self.speedrun_timer > 0:
            level_text = f"Level {self.level.number}/7  (Speedrun)"
        else:
            level_text = f"Level {self.level.number} / {FIRST_RUN_LEVELS}"
        char_text = f"{self.player.NAME}"
        power_text = f"Power: {self.player.POWER_NAME}"
        draw_text(surface, health_text, 22, 12, 12, COLORS["text"])
        draw_text(surface, weapon_text, 22, 12, 38, COLORS["text"])
        draw_text(surface, ammo_text, 22, 12, 64, COLORS["text"])
        grenade_text = f"Grenades: {self.player.grenades}"
        draw_text(surface, grenade_text, 22, 12, 116, COLORS["text"])
        draw_text(surface, f"Coins: {self.coins}", 20, SCREEN_WIDTH - 170, 88, (255, 215, 0))
        if self.speedrun_timer > 0:
            secs = self.speedrun_timer // 60
            m, s = divmod(secs, 60)
            col = (255, 70, 70) if secs < 60 else (255, 220, 60)
            draw_text(surface, f"TIME  {m}:{s:02d}", 26,
                      SCREEN_WIDTH // 2 - 55, 10, col)

        p = self.player
        buffs = []
        if p.speed_timer     > 0: buffs.append(f"Speed {p.speed_timer // 60 + 1}s")
        if p.flight_timer    > 0: buffs.append(f"Flight {p.flight_timer // 60 + 1}s")
        if p.shield_charges  > 0: buffs.append(f"Shield x{p.shield_charges}")
        if p.dmg_boost_timer > 0: buffs.append(f"Power {p.dmg_boost_timer // 60 + 1}s")
        if p.rapid_timer     > 0: buffs.append(f"Rapid {p.rapid_timer // 60 + 1}s")
        if buffs:
            draw_text(surface, " | ".join(buffs), 17, 12, 142, (255, 220, 60))
        draw_text(surface, level_text, 22, SCREEN_WIDTH - 170, 12, COLORS["text"])
        draw_text(surface, char_text, 22, SCREEN_WIDTH - 170, 38, COLORS["text"])
        draw_text(surface, power_text, 18, SCREEN_WIDTH - 170, 62, COLORS["text"])

        total_width = 200
        fill_width = int((self.player.health / self.player.max_health) * total_width)
        pygame.draw.rect(surface, COLORS["health_bg"], (12, 90, total_width, 18))
        pygame.draw.rect(surface, COLORS["health_fg"], (12, 90, fill_width, 18))

        if self._item_banner:
            bname, bdesc, _ = self._item_banner
            panel_w, panel_h = 460, 72
            bx = SCREEN_WIDTH // 2 - panel_w // 2
            by = SCREEN_HEIGHT // 2 - 60
            panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            panel.fill((0, 0, 0, 190))
            surface.blit(panel, (bx, by))
            draw_text(surface, f"Collected:  {bname}", 22, bx + 14, by + 8,  (255, 215, 0))
            draw_text(surface, bdesc,                  17, bx + 14, by + 42, (180, 220, 255))

    def draw(self, surface):
        surface.blit(self._bg, (0, 0))

        if not self.auth_done:
            self.auth_screen.draw(surface)
            return

        if not self.tutorial_done:
            self.tutorial.draw(surface)
            return

        if self.in_lobby:
            self.lobby.draw(surface, self.coins, self.upgrades, self.highscore)
            return
        
        self.level.draw(surface, self._platform_color)

        # Ice overlay on frozen enemies (arctic orb)
        for enemy in self.level.enemies:
            if enemy.frozen_timer > 0:
                pulse = (math.sin(pygame.time.get_ticks() * 0.007) + 1) / 2
                # Blue tint overlay
                ice = pygame.Surface(enemy.rect.size, pygame.SRCALPHA)
                ice.fill((140, 210, 255, int(70 + 50 * pulse)))
                surface.blit(ice, enemy.rect.topleft)
                # Icy border
                pygame.draw.rect(surface, (180, 235, 255), enemy.rect, 2, border_radius=4)
                # Snowflake at enemy centre
                cx, cy = enemy.rect.center
                for i in range(6):
                    ang = math.radians(i * 60)
                    ex  = cx + int(9 * math.cos(ang))
                    ey  = cy + int(9 * math.sin(ang))
                    pygame.draw.line(surface, (220, 245, 255), (cx, cy), (ex, ey), 1)
                pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 3)

        self._draw_buff_effects(surface, glow_only=True)   # glow behind player
        surface.blit(self.player.image, self.player.rect)
        self._draw_buff_effects(surface, glow_only=False)  # wings/flames in front

        # Facing arrow
        f  = self.player.facing
        ax = self.player.rect.centerx + f * (self.player.rect.width // 2 + 7)
        ay = self.player.rect.centery
        s  = 7   # arrowhead size
        pygame.draw.polygon(surface, (255, 225, 60), [
            (ax + f * s, ay),
            (ax - f * s, ay - s),
            (ax - f * s, ay + s),
        ])

        self.player.bullets.draw(surface)
        self.enemy_projectiles.draw(surface)
        self.grenades.draw(surface)
        self.biome_items.draw(surface)
        self.draw_ui(surface)

        if self.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            surface.blit(overlay, (0, 0))
            draw_text(surface, "PAUSED", 52,
                      SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 - 40, (255, 220, 60))
            draw_text(surface, "Press P or ESC to resume", 22,
                      SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 + 24, (200, 200, 200))
            user_label = f"Signed in as: {self.current_user}" if self.current_user else "Playing as Guest"
            draw_text(surface, user_label, 18,
                      SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 56, (130, 130, 160))
            return

        if self.game_over:
            msg = "Time's Up!" if self.timed_out else "Game Over"
            draw_text(surface, msg, 48, SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 30, COLORS["text"])
            draw_text(surface, "R - Restart from level 1", 22, SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 25, COLORS["text"])
            draw_text(surface, "M - Main Menu", 22, SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 50, COLORS["text"])
            self._draw_record(surface, SCREEN_HEIGHT // 2 + 80)
        elif self.victory:
            if self.on_second_run:
                msg = "All 14 Levels Cleared!"
            else:
                secs = (14400 - self.speedrun_timer) // 60 if self.speedrun_timer == 0 else 0
                m, s = divmod(secs, 60) if secs else (0, 0)
                msg = f"Speedrun Complete!  {m}:{s:02d}" if not self.on_second_run else "Victory!"
            draw_text(surface, msg, 38, SCREEN_WIDTH // 2 - 240, SCREEN_HEIGHT // 2 - 40, COLORS["text"])
            draw_text(surface, "Press R to play again", 24, SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 10, COLORS["text"])
            if self.on_second_run and not self.in_endless_mode:
                draw_text(surface, "Press C to continue in Endless Mode", 22,
                          SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 45, (100, 220, 140))
            self._draw_record(surface, SCREEN_HEIGHT // 2 + 80)

    def _draw_record(self, surface, y):
        hs = self.highscore
        if hs["best_level"]:
            record = f"Record: Level {hs['best_level']} by {hs['best_user']}"
        else:
            record = "Record: none yet"
        draw_text(surface, record, 22, SCREEN_WIDTH // 2 - 130, y, (255, 215, 90))

    def handle_event(self, event):
        if not self.auth_done:
            result = self.auth_screen.handle_event(event)
            if result is not None:
                _, username = result
                self.current_user = username
                self.auth_done    = True
                self._load_state()   # load account or guest save
            return

        if not self.tutorial_done:
            result = self.tutorial.handle_event(event)
            if result is True:
                self.tutorial_done = True
                _play_music(f"music_{self.level.biome}")
            elif result == "quit":
                pygame.quit()
                sys.exit()
            return

        # Pause toggle (P or ESC during gameplay)
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_p, pygame.K_ESCAPE):
                if not self.game_over and not self.victory and not self.in_lobby:
                    self.paused = not self.paused
                    return

        if self.in_lobby:
            cmd = self.lobby.handle_event(event, self.coins, self.upgrades)
            if cmd:
                if cmd[0] == "buy":
                    _, key, cost = cmd
                    self.upgrades[key] = True
                    self.coins -= cost
                    self._save_state()
                elif cmd[0] == "speedrun":
                    self.in_lobby = False
                    self.speedrun_timer = 14400
                    self.on_second_run = False
                    self.load_level(0)
                    _play_music(f"music_{self.level.biome}")
                elif cmd[0] == "continue":
                    self.in_lobby = False
                    self.on_second_run = True
                    self.load_level(FIRST_RUN_LEVELS)
                    _play_music(f"music_{self.level.biome}")
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z and not self.game_over and not self.victory:
                if self.player.ammo[self.player.weapon] > 0 and self.player.fire_delay == 0:
                    _sounds.play(f"shoot_{self.player.weapon}", volume=0.6)
                self.player.shoot(self.player.bullets)
            if event.key == pygame.K_g and not self.game_over and not self.victory:
                if self.player.grenades > 0:
                    _sounds.play("throw_grenade")
                self.player.throw_grenade(self.grenades)
            # if event.key == pygame.K_t:
            #     if self.game_over:
            #         self.game_over = False
            #         self.timed_out = False
            #         self.load_level(self.current_index)
            #         _play_music(f"music_{self.current_index}")
            if event.key == pygame.K_m:
                if self.game_over:
                    _stop_music()
                    self.__init__()   # fresh state → AuthScreen (main menu)
                    return
            if event.key == pygame.K_c:
                if self.victory and self.on_second_run and not self.in_endless_mode:
                    self.victory          = False
                    self.in_endless_mode  = True
                    self.procedural_count = 0
                    self.load_procedural_level()
                    _play_music(f"music_{self.level.biome}")
            if event.key == pygame.K_r:
                if (self.game_over or self.victory) and self.lobby_reached:
                    self.game_over      = False
                    self.victory        = False
                    self.in_lobby       = True
                    self.speedrun_timer = 0
                    self.on_second_run  = False
                    self.in_endless_mode   = False
                    self.procedural_count  = 0
                    self.display_level_num = None
                    self.lobby          = LobbyScreen()
                    _play_music("music_lobby")
                else:
                    _auth_done    = self.auth_done
                    _current_user = self.current_user
                    _tutorial_done = self.tutorial_done
                    try:
                        os.remove(_SAVE_PATH)
                    except OSError:
                        pass
                    self.__init__()
                    self.auth_done     = _auth_done
                    self.current_user  = _current_user
                    self.tutorial_done = _tutorial_done
                    self._load_state()


def main():
    global screen
    game = Game()
    game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fullscreen = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            game.handle_event(event)

        game.update()
        game.draw(game_surface)

        if fullscreen:
            sw, sh = screen.get_size()
            scale = min(sw / SCREEN_WIDTH, sh / SCREEN_HEIGHT)
            scaled_w = int(SCREEN_WIDTH * scale)
            scaled_h = int(SCREEN_HEIGHT * scale)
            scaled = pygame.transform.scale(game_surface, (scaled_w, scaled_h))
            screen.fill((0, 0, 0))
            screen.blit(scaled, ((sw - scaled_w) // 2, (sh - scaled_h) // 2))
        else:
            screen.blit(game_surface, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
