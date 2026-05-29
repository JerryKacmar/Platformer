import pygame

from assets import make_character_sprite
from settings import PLAYER_SPEED, JUMP_SPEED, GRAVITY, PLAYER_MAX_HEALTH, WEAPONS, COLORS
from entities.projectile import Projectile


class Player(pygame.sprite.Sprite):
    NAME = "Player"
    POWER_NAME = "None"

    def __init__(self, x, y):
        super().__init__()
        self.image = make_character_sprite((42, 52), COLORS["player"], 'rookie')
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel = pygame.Vector2(0, 0)
        self.on_ground = False
        self.health = PLAYER_MAX_HEALTH
        self.max_health = PLAYER_MAX_HEALTH
        self.weapon = "pistol"
        self.ammo = {wt: WEAPONS[wt]["ammo"] for wt in WEAPONS}
        self.fire_delay = 0
        self.facing = 1
        self.bullets = pygame.sprite.Group()

        # Power attributes — subclasses override these
        self.max_air_jumps = 0   # extra mid-air jumps
        self.air_jumps = 0
        self.damage_reduction = 0
        self.fire_rate_mult = 1.0
        self.damage_bonus = 0
        self._jump_held = False  # edge-detection so holding space doesn't chain jumps
        self.grenades     = 0
        self.max_grenades = 3
        self.speed_mult   = 1.0
        # Buff timers (frames remaining) / charges
        self.speed_timer     = 0
        self.flight_timer    = 0
        self.shield_charges  = 0
        self.dmg_boost_timer = 0
        self.rapid_timer     = 0

    def handle_input(self, keys):
        self.vel.x = 0
        speed = PLAYER_SPEED * self.speed_mult * (3 if self.speed_timer > 0 else 1)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel.x = -speed
            self.facing = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel.x = speed
            self.facing = 1

        if self.flight_timer > 0:
            if keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]:
                self.vel.y = -PLAYER_SPEED
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.vel.y = PLAYER_SPEED
            else:
                self.vel.y *= 0.75  # hover / decelerate
        else:
            jump_key = keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]
            if jump_key and not self._jump_held:
                self.jump()
            self._jump_held = jump_key

    def jump(self):
        if self.on_ground:
            self.vel.y = JUMP_SPEED
            self.on_ground = False
            self.air_jumps = self.max_air_jumps
            import sounds; sounds.play("jump", volume=0.5)
        elif self.air_jumps > 0:
            self.vel.y = JUMP_SPEED
            self.air_jumps -= 1
            import sounds; sounds.play("jump", volume=0.35)

    def update(self, platforms):
        if self.flight_timer == 0:
            self.vel.y += GRAVITY
        # Tick down buff timers
        self.speed_timer     = max(0, self.speed_timer     - 1)
        self.flight_timer    = max(0, self.flight_timer    - 1)
        self.dmg_boost_timer = max(0, self.dmg_boost_timer - 1)
        self.rapid_timer     = max(0, self.rapid_timer     - 1)
        self.rect.x += self.vel.x
        self._resolve_collisions(platforms, "horizontal")
        self.rect.y += self.vel.y
        self._resolve_collisions(platforms, "vertical")

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > 1024:
            self.rect.right = 1024
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > 640:
            self.health = 0

        self.fire_delay = max(0, self.fire_delay - 1)
        self.bullets.update()

    def _resolve_collisions(self, platforms, direction):
        for platform in platforms:
            if self.rect.colliderect(platform):
                if direction == "horizontal":
                    if self.vel.x > 0:
                        self.rect.right = platform.left
                    elif self.vel.x < 0:
                        self.rect.left = platform.right
                else:
                    if self.vel.y > 0:
                        self.rect.bottom = platform.top
                        self.on_ground = True
                        self.vel.y = 0
                    elif self.vel.y < 0:
                        self.rect.top = platform.bottom
                        self.vel.y = 0

    def shoot(self, bullet_group):
        if self.fire_delay > 0 or self.ammo[self.weapon] <= 0:
            return
        weapon = WEAPONS[self.weapon]
        dmg = (weapon["damage"] + self.damage_bonus) * (2 if self.dmg_boost_timer > 0 else 1)
        bullet = Projectile(
            self.rect.centerx + self.facing * 24,
            self.rect.centery,
            pygame.Vector2(self.facing, 0),
            speed=weapon["speed"],
            damage=dmg,
            color=weapon["color"],
            owner="player",
        )
        bullet_group.add(bullet)
        rate_mult = self.fire_rate_mult * (0.33 if self.rapid_timer > 0 else 1.0)
        self.fire_delay = max(1, int(weapon["fire_delay"] * rate_mult))
        self.ammo[self.weapon] -= 1

    def throw_grenade(self, group):
        from entities.grenade import Grenade
        if self.grenades > 0:
            group.add(Grenade(
                self.rect.centerx + self.facing * 20,
                self.rect.centery,
                pygame.Vector2(self.facing * 7, 0),
            ))
            self.grenades -= 1

    def equip_weapon(self, weapon_type):
        if weapon_type in WEAPONS:
            self.weapon = weapon_type
            self.ammo[weapon_type] = WEAPONS[weapon_type]["ammo"]

    def take_damage(self, amount):
        if self.shield_charges > 0:
            self.shield_charges -= 1
            return
        reduced = max(1, amount - self.damage_reduction)
        self.health = max(0, self.health - reduced)


# ── Characters ──────────────────────────────────────────────────────────────

class Rookie(Player):
    """Level 1 — bare-bones starter, no special power."""
    NAME = "Rookie"
    POWER_NAME = "None"

    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = make_character_sprite((42, 52), (180, 180, 190), 'rookie')
        self.health = self.max_health = 8


class Cadet(Player):
    """Level 2 — carries extra ammo for every weapon."""
    NAME = "Cadet"
    POWER_NAME = "Extra Ammo  (1.5x ammo)"

    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = make_character_sprite((42, 52), (100, 200, 170), 'cadet')
        self.health = self.max_health = 9
        for wt in self.ammo:
            self.ammo[wt] = int(self.ammo[wt] * 1.5)


class Scout(Player):
    """Level 1 — mobile starter with a double jump."""
    NAME = "Scout"
    POWER_NAME = "Double Jump"

    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = make_character_sprite((42, 52), (220, 200, 90), 'scout')
        self.health = self.max_health = 10
        self.max_air_jumps = 1


class Soldier(Player):
    """Level 2 — durable fighter who shrugs off 1 point of every hit."""
    NAME = "Soldier"
    POWER_NAME = "Armor  (-1 dmg taken)"

    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = make_character_sprite((42, 52), (80, 140, 220), 'soldier')
        self.health = self.max_health = 12
        self.damage_reduction = 1


class Gunslinger(Player):
    """Level 3 — blazing fire rate at the cost of raw health."""
    NAME = "Gunslinger"
    POWER_NAME = "Rapid Fire  (2x fire rate)"

    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = make_character_sprite((42, 52), (230, 130, 60), 'gunslinger')
        self.health = self.max_health = 13
        self.fire_rate_mult = 0.5


class Ranger(Player):
    """Level 4 — every bullet hits harder."""
    NAME = "Ranger"
    POWER_NAME = "Power Shot  (+1 dmg per bullet)"

    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = make_character_sprite((42, 52), (80, 190, 100), 'ranger')
        self.health = self.max_health = 14
        self.damage_bonus = 1


class Commander(Player):
    """Level 5 — all powers combined."""
    NAME = "Commander"
    POWER_NAME = "All Powers"

    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = make_character_sprite((42, 52), (190, 80, 200), 'commander')
        self.health = self.max_health = 16
        self.max_air_jumps = 1
        self.damage_reduction = 1
        self.fire_rate_mult = 0.5
        self.damage_bonus = 1


# ── Second-run characters (levels 8-14) ─────────────────────────────────────

class Vanguard(Player):
    """Run 2, Level 1 — elite scout, triple jump, power shot."""
    NAME = "Vanguard"
    POWER_NAME = "Triple Jump  (+1 dmg)"

    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = make_character_sprite((42, 52), (100, 230, 80), 'scout')
        self.health = self.max_health = 14
        self.max_air_jumps = 2
        self.damage_bonus = 1


class Tank(Player):
    """Run 2, Level 2 — heavily armoured, massive HP pool."""
    NAME = "Tank"
    POWER_NAME = "Heavy Armor  (-2 dmg taken)"

    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = make_character_sprite((42, 52), (105, 118, 138), 'soldier')
        self.health = self.max_health = 22
        self.damage_reduction = 2


class Blitzer(Player):
    """Run 2, Level 3 — extreme fire rate with extra punch."""
    NAME = "Blitzer"
    POWER_NAME = "Extreme Fire  (4x rate +1 dmg)"

    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = make_character_sprite((42, 52), (230, 60, 110), 'gunslinger')
        self.health = self.max_health = 15
        self.fire_rate_mult = 0.25
        self.damage_bonus = 1


class Marksman(Player):
    """Run 2, Level 4 — devastating shot power."""
    NAME = "Marksman"
    POWER_NAME = "Deadeye  (+3 dmg per bullet)"

    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = make_character_sprite((42, 52), (155, 75, 55), 'ranger')
        self.health = self.max_health = 16
        self.damage_bonus = 3


class Warlord(Player):
    """Run 2, Level 5 — powerful combo of all abilities."""
    NAME = "Warlord"
    POWER_NAME = "Warlord  (Jump+Armor+Rapid+Power)"

    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = make_character_sprite((42, 52), (210, 85, 45), 'commander')
        self.health = self.max_health = 18
        self.max_air_jumps = 1
        self.damage_reduction = 1
        self.fire_rate_mult = 0.5
        self.damage_bonus = 2


class Phantom(Player):
    """Run 2, Level 6 — agile and versatile with 2x ammo."""
    NAME = "Phantom"
    POWER_NAME = "Phantom  (Jump+2xAmmo+2 dmg)"

    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = make_character_sprite((42, 52), (55, 90, 175), 'ranger')
        self.health = self.max_health = 17
        self.max_air_jumps = 1
        self.damage_bonus = 2
        for wt in self.ammo:
            self.ammo[wt] = int(self.ammo[wt] * 2)


class Apex(Player):
    """Run 2, Level 7 — the ultimate warrior, all powers maximised."""
    NAME = "Apex"
    POWER_NAME = "Apex  (ALL powers, max stats)"

    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = make_character_sprite((42, 52), (220, 190, 0), 'commander')
        self.health = self.max_health = 24
        self.max_air_jumps = 2
        self.damage_reduction = 2
        self.fire_rate_mult = 0.25
        self.damage_bonus = 3
        self.max_grenades = 5
        for wt in self.ammo:
            self.ammo[wt] = int(self.ammo[wt] * 2)


CHARACTERS = [
    Rookie, Cadet, Scout, Soldier, Gunslinger, Ranger, Commander,  # run 1
    Vanguard, Tank, Blitzer, Marksman, Warlord, Phantom, Apex,     # run 2
]
