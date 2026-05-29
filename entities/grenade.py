import pygame

from settings import GRAVITY, SCREEN_WIDTH, SCREEN_HEIGHT

EXPLOSION_RADIUS = 120
EXPLOSION_DAMAGE = 6   # two shotgun shots (3 damage each)
_FUSE_FRAMES    = 90   # 1.5 s at 60 FPS
_EXPLOSION_SHOW = 18   # frames the blast visual stays visible


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, vel):
        super().__init__()
        self._make_idle_image()
        self.rect = self.image.get_rect(center=(x, y))
        self.vel  = pygame.Vector2(vel)
        self.fuse = _FUSE_FRAMES
        self.exploded      = False
        self.damage_applied = False
        self._exp_timer    = 0

    # ── visuals ──────────────────────────────────────────────────────────────

    def _make_idle_image(self):
        self.image = pygame.Surface((14, 14), pygame.SRCALPHA)
        pygame.draw.circle(self.image, ( 60, 180,  60), (7, 7), 6)
        pygame.draw.circle(self.image, ( 30, 100,  30), (7, 7), 6, 2)
        pygame.draw.line  (self.image, (200, 200,  50), (7, 1), (7, 4), 2)

    def _start_explosion(self):
        self.exploded   = True
        self._exp_timer = _EXPLOSION_SHOW
        center = self.rect.center
        r = EXPLOSION_RADIUS
        self.image = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        self._draw_blast(1.0)
        self.rect = self.image.get_rect(center=center)

    def _draw_blast(self, alpha_factor):
        r = EXPLOSION_RADIUS
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, (255, 120,  20, int(180 * alpha_factor)), (r, r), r)
        pygame.draw.circle(self.image, (255, 220,  80, int(240 * alpha_factor)), (r, r), r // 2)
        pygame.draw.circle(self.image, (255, 255, 200, int(255 * alpha_factor)), (r, r), r // 5)

    # ── update ───────────────────────────────────────────────────────────────

    def update(self, platforms):
        if self.exploded:
            self._exp_timer -= 1
            if self._exp_timer <= 0:
                self.kill()
            else:
                self._draw_blast(self._exp_timer / _EXPLOSION_SHOW)
            return

        self.fuse -= 1
        self.vel.y += GRAVITY

        # Horizontal movement + platform bounce
        self.rect.x += int(self.vel.x)
        for p in platforms:
            if self.rect.colliderect(p):
                if self.vel.x > 0:
                    self.rect.right = p.left
                else:
                    self.rect.left  = p.right
                self.vel.x *= -0.55

        # Screen side edges
        if self.rect.left < 0:
            self.rect.left = 0
            self.vel.x = abs(self.vel.x) * 0.55
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.vel.x = -abs(self.vel.x) * 0.55

        # Vertical movement + platform bounce
        self.rect.y += int(self.vel.y)
        for p in platforms:
            if self.rect.colliderect(p):
                if self.vel.y > 0:
                    self.rect.bottom = p.top
                    self.vel.y *= -0.45
                    self.vel.x *= 0.80
                else:
                    self.rect.top = p.bottom
                    self.vel.y    = 0

        if self.fuse <= 0:
            self._start_explosion()
