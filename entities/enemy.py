import math
import pygame

from assets import load_sprite, make_enemy_sprite
from settings import COLORS, ENEMY_BULLET_SPEED, GRAVITY
from entities.projectile import Projectile

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color, health, speed, pattern, damage, image_name=None):
        super().__init__()
        if image_name:
            self.image = load_sprite(image_name, (width, height), color, border_radius=8)
        else:
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(self.image, color, self.image.get_rect(), border_radius=8)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.color = color
        self.health = health
        self.max_health = health
        self.speed = speed
        self.pattern = pattern
        self.damage = damage
        self.contact_damage = damage
        self.direction = -1
        self.phase_index = 0
        self.phase_timer = 0
        self.phase_duration = 180
        self.fire_delay = 0
        self.vel = pygame.Vector2(0, 0)
        self.on_ground = False
        self.jump_cooldown = 0
        self.knockback_timer = 0
        self.frozen_timer = 0

    def update(self, player, projectile_group, platforms):
        if self.frozen_timer > 0:
            self.frozen_timer -= 1
            self._move(platforms)   # gravity still applies
            return

        self.phase_timer += 1
        self.fire_delay = max(0, self.fire_delay - 1)
        self.knockback_timer = max(0, self.knockback_timer - 1)

        if self.phase_timer >= self.phase_duration:
            self.phase_timer = 0
            self.phase_index = (self.phase_index + 1) % len(self.pattern)
            self._choose_direction(player)

        if self.knockback_timer == 0:
            phase = self.pattern[self.phase_index]
            if phase == "patrol":
                self._patrol()
            elif phase == "shoot":
                self._shoot(player, projectile_group)
            elif phase == "dash":
                self._dash()
            elif phase == "spread":
                self._spread(projectile_group, player)
            elif phase == "spiral":
                self._spiral(projectile_group)
            elif phase == "jump":
                self._jump()
            elif phase == "rest":
                self._rest()

        self._move(platforms)
        self.jump_cooldown = max(0, self.jump_cooldown - 1)
        if self.health <= 0:
            self.kill()

    def _choose_direction(self, player):
        if player.rect.centerx < self.rect.centerx:
            self.direction = -1
        else:
            self.direction = 1

    def _patrol(self):
        self.vel.x = self.speed * self.direction

    def _dash(self):
        self.vel.x = self.speed * 3 * self.direction

    def _shoot(self, player, projectile_group):
        self.vel.x = 0
        if self.fire_delay == 0 and abs(player.rect.centerx - self.rect.centerx) < 420:
            direction = 1 if player.rect.centerx > self.rect.centerx else -1
            self._fire(direction, projectile_group)
            self.fire_delay = 140

    def _spread(self, projectile_group, player):
        self.vel.x = 0
        if self.fire_delay == 0:
            for direction in (-1, 1):
                self._fire(direction, projectile_group)
            self._fire(1 if player.rect.centerx > self.rect.centerx else -1, projectile_group)
            self.fire_delay = 180

    def _jump(self):
        if self.on_ground and self.jump_cooldown == 0:
            self.vel.y = -12
            self.on_ground = False
            self.jump_cooldown = 30

    def _rest(self):
        self.vel.x = 0

    def _spiral(self, projectile_group):
        self.vel.x = 0
        if self.fire_delay == 0:
            angle_offset = getattr(self, '_spiral_angle', 0)
            for i in range(10):
                angle = math.radians(angle_offset + i * 36)   # 10 rays × 36° = full circle
                direction = pygame.Vector2(math.cos(angle), math.sin(angle))
                projectile_group.add(Projectile(
                    self.rect.centerx, self.rect.centery,
                    direction,
                    speed=ENEMY_BULLET_SPEED * 1.8,
                    damage=self.damage,
                    color=(220, 60, 255),   # bright magenta — visually distinct
                    owner="enemy",
                ))
            self._spiral_angle = (angle_offset + 18) % 360   # rotate 18° each volley
            self.fire_delay = 45

    def _fire(self, direction, projectile_group):
        bullet = Projectile(
            self.rect.centerx + direction * 30,
            self.rect.centery,
            pygame.Vector2(direction, 0),
            speed=ENEMY_BULLET_SPEED,
            damage=self.damage,
            color=COLORS["bullet_enemy"],
            owner="enemy",
        )
        projectile_group.add(bullet)

    def _move(self, platforms):
        self.vel.y += GRAVITY

        # Stop at platform edges so enemies don't fall off (skip during knockback)
        if self.on_ground and self.vel.x != 0 and self.knockback_timer == 0:
            if self.vel.x > 0:
                probe = pygame.Rect(self.rect.right, self.rect.bottom, 2, 4)
            else:
                probe = pygame.Rect(self.rect.left - 2, self.rect.bottom, 2, 4)
            if not any(probe.colliderect(p) for p in platforms):
                self.vel.x = 0
                self.direction *= -1

        self.rect.x += self.vel.x
        
        if self.rect.left < 0:
            self.rect.left = 0
            self.direction *= -1
        if self.rect.right > 1024:
            self.rect.right = 1024
            self.direction *= -1
        
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vel.x > 0:
                    self.rect.right = platform.left
                elif self.vel.x < 0:
                    self.rect.left = platform.right
                self.direction *= -1
        
        self.on_ground = False
        self.rect.y += self.vel.y
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vel.y > 0:
                    self.rect.bottom = platform.top
                    self.vel.y = 0
                    self.on_ground = True
                elif self.vel.y < 0:
                    self.rect.top = platform.bottom
                    self.vel.y = 0

    def take_damage(self, amount, knockback_dir=0):
        self.health -= amount
        if knockback_dir != 0:
            self.vel.x = knockback_dir * 6
            self.vel.y = -3
            self.knockback_timer = 8
        if self.health <= 0:
            self.kill()


class BasicEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 46, COLORS["enemy"], health=6, speed=1.2,
                         pattern=["patrol", "jump", "shoot", "rest"], damage=1)
        self.image = make_enemy_sprite((40, 46), COLORS["enemy"], 'basic')
        self.contact_damage = 1


class ShooterEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 42, 48, COLORS["shooter"], health=8, speed=1.2,
                         pattern=["shoot", "jump", "patrol"], damage=1)
        self.image = make_enemy_sprite((42, 48), COLORS["shooter"], 'shooter')
        self.contact_damage = 1


class MiniBoss(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 64, 70, COLORS["miniboss"], health=18, speed=1.5,
                         pattern=["patrol", "jump", "spread", "dash"], damage=2)
        self.image = make_enemy_sprite((64, 70), COLORS["miniboss"], 'miniboss')
        self.phase_duration = 200
        self.contact_damage = 2


class FinalBoss(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 92, 100, COLORS["boss"], health=45, speed=1.5,
                         pattern=["shoot", "jump", "spread", "spiral", "dash", "spiral", "rest"],
                         damage=2)
        self.image = make_enemy_sprite((92, 100), COLORS["boss"], 'boss')
        self.phase_duration = 200
        self.contact_damage = 2
        self._spiral_angle = 0
