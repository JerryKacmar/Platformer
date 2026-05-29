import pygame
from assets import load_sprite
from settings import COLORS


class HealthPickup(pygame.sprite.Sprite):
    def __init__(self, x, y, amount=1):
        super().__init__()
        self.amount = amount
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        color = (220, 100, 100) if amount == 2 else (180, 70, 70)
        pygame.draw.rect(self.image, color, self.image.get_rect(), border_radius=4)
        pygame.draw.line(self.image, (255, 255, 255), (12, 6), (12, 18), 2)
        pygame.draw.line(self.image, (255, 255, 255), (6, 12), (18, 12), 2)
        self.rect = self.image.get_rect(center=(x, y))
        self.lifetime = 300
        self.age = 0

    def update(self):
        self.age += 1
        if self.age >= self.lifetime:
            self.kill()
        alpha = int(255 * (1 - (self.age / self.lifetime) ** 2))
        self.image.set_alpha(alpha)
