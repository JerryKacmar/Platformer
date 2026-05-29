import pygame

from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed=12, damage=1, color=(255, 255, 255), owner="player"):
        super().__init__()
        self.image = pygame.Surface((12, 8), pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, self.image.get_rect(), border_radius=4)
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = pygame.Vector2(direction)
        if self.velocity.length_squared() == 0:
            self.velocity = pygame.Vector2(1, 0)
        self.velocity = self.velocity.normalize() * speed
        self.damage = damage
        self.owner = owner

    def update(self):
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y
        if (
            self.rect.right < 0
            or self.rect.left > SCREEN_WIDTH
            or self.rect.bottom < 0
            or self.rect.top > SCREEN_HEIGHT
        ):
            self.kill()
