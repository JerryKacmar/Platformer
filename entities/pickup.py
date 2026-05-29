import pygame

from assets import load_sprite
from settings import COLORS

class WeaponPickup(pygame.sprite.Sprite):
    WEAPON_COLORS = {
        "pistol": (100, 180, 240),
        "blaster": (120, 230, 170),
        "rifle": (100, 200, 100),
        "shotgun": (255, 140, 60),
    }

    def __init__(self, weapon_type, x, y):
        super().__init__()
        self.weapon_type = weapon_type
        self.image = load_sprite("weapon_blaster.png", (30, 30), self.WEAPON_COLORS.get(weapon_type, COLORS["weapon"]), border_radius=6)
        self.rect = self.image.get_rect(center=(x, y))
        self.lifetime = 400
        self.age = 0

    def update(self):
        self.age += 1
        if self.age >= self.lifetime:
            self.kill()
        alpha = int(255 * (1 - (self.age / self.lifetime) ** 2))
        self.image.set_alpha(alpha)
