import math
import pygame

# (display name, effect key, colour, duration)
# duration = frames for timed buffs, hit-count for shield, freeze seconds for freeze
_ITEM_DATA = {
    # ── First run (levels 1-7) ───────────────────────────────────────────────
    0: ("Vine Boost",    "speed",   ( 60, 210,  80), 300),
    1: ("Eagle Wings",   "flight",  (110, 185, 255), 300),
    2: ("Heat Mirage",   "shield",  (235, 185,  45),   5),
    3: ("Magma Core",    "damage",  (225,  65,  10), 300),
    4: ("Spore Burst",   "rapid",   (130,  65, 185), 300),
    5: ("Frost Blast",   "freeze",  ( 85, 210, 245), 240),
    6: ("Ancient Power", "all",     (165,  85, 225), 360),
    # ── Second run (levels 8-14) — new biomes ────────────────────────────────
    7:  ("Meteor Strike", "meteor",   (200, 210, 255), 0),    # instant
    8:  ("Tidal Wave",    "ammo",     ( 30, 160, 230), 0),    # instant
    9:  ("Crystal Armor", "crystal",  (190, 100, 255),  10),  # 10 charges
    10: ("Infernal Power","infernal", (255,  45,   5), 480),  # 8 s
    11: ("Mycelium",      "toxic",    (100, 210,  50), 360),  # 6 s
    12: ("Thunder Shot",  "thunder",  (210, 230, 255), 300),  # 5 s
    13: ("Hell Mode",     "hell",     (220,   0,  50), 720),  # 12 s
}

SIZE = 30


class BiomeItem(pygame.sprite.Sprite):
    def __init__(self, biome, x, y):
        super().__init__()
        self.biome    = biome
        name, effect, color, duration = _ITEM_DATA[biome]
        self.name     = name
        self.effect   = effect
        self.color    = color
        self.duration = duration
        self._tick    = 0
        self._base_y  = y
        self.image    = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
        self.rect     = self.image.get_rect(center=(x, y))
        self._render()

    def _render(self):
        img = self.image
        img.fill((0, 0, 0, 0))
        c = SIZE // 2
        r = c - 2
        pulse = 0.5 + 0.5 * math.sin(self._tick * 0.08)
        alpha = int(180 + 75 * pulse)

        # Outer glow ring
        pygame.draw.circle(img, (*self.color, int(55 * pulse)), (c, c), r + 5)
        # Main circle
        pygame.draw.circle(img, (*self.color, alpha), (c, c), r)

        # Per-biome inner symbol
        if self.biome == 0:  # Speed — right arrow
            pygame.draw.polygon(img, (255, 255, 100), [
                (c-6, c-4), (c+1, c-4), (c+1, c-8),
                (c+8, c), (c+1, c+8), (c+1, c+4), (c-6, c+4)])

        elif self.biome == 1:  # Flight — two wing arcs + dot
            pygame.draw.arc(img, (220, 242, 255),
                            pygame.Rect(c-11, c-5, 11, 11), 0, math.pi, 2)
            pygame.draw.arc(img, (220, 242, 255),
                            pygame.Rect(c, c-5, 11, 11), 0, math.pi, 2)
            pygame.draw.circle(img, (255, 255, 255), (c, c+4), 2)

        elif self.biome == 2:  # Shield — hexagon
            pts = [(c + int(8*math.cos(math.radians(90 + i*60))),
                    c + int(8*math.sin(math.radians(90 + i*60)))) for i in range(6)]
            pygame.draw.polygon(img, (255, 232, 80), pts, 2)
            pygame.draw.circle(img, (255, 232, 80), (c, c), 3)

        elif self.biome == 3:  # Damage — 8-ray starburst
            for i in range(8):
                ang = math.radians(i * 45)
                pygame.draw.line(img, (255, 220, 50),
                                 (c, c), (c + int(8*math.cos(ang)),
                                          c + int(8*math.sin(ang))), 2)
            pygame.draw.circle(img, (255, 190, 30), (c, c), 4)

        elif self.biome == 4:  # Rapid Fire — lightning bolt
            pygame.draw.polygon(img, (255, 242, 50), [
                (c+3, c-8), (c-1, c-1), (c+4, c-1),
                (c-3, c+8), (c+1, c+1), (c-4, c+1)])

        elif self.biome == 5:  # Freeze — snowflake
            for i in range(6):
                ang = math.radians(i * 60)
                pygame.draw.line(img, (215, 248, 255),
                                 (c, c), (c + int(9*math.cos(ang)),
                                          c + int(9*math.sin(ang))), 2)
            pygame.draw.circle(img, (255, 255, 255), (c, c), 3)

        elif self.biome == 6:  # All Powers — 5-point star
            pts = []
            for i in range(5):
                a_out = math.radians(-90 + i * 72)
                a_in  = math.radians(-90 + i * 72 + 36)
                pts += [(c + int(9*math.cos(a_out)), c + int(9*math.sin(a_out))),
                        (c + int(4*math.cos(a_in)),  c + int(4*math.sin(a_in)))]
            pygame.draw.polygon(img, (255, 220, 60), pts)

        elif self.biome == 7:  # Meteor Strike — falling meteor
            pygame.draw.circle(img, (255, 240, 200), (c+3, c-3), 5)
            pygame.draw.line(img, (255, 200, 100), (c-1, c+1), (c-7, c+7), 3)
            pygame.draw.line(img, (255, 220, 150), (c-3, c-1), (c-8, c+4), 2)

        elif self.biome == 8:  # Ammo Refill — bullet stack
            for row in range(3):
                pygame.draw.rect(img, (220, 220, 100),
                                 (c-6, c-5+row*4, 12, 3), border_radius=1)
                pygame.draw.circle(img, (255, 240, 120), (c+6, c-4+row*4), 2)

        elif self.biome == 9:  # Crystal Armor — diamond
            pts = [(c, c-9), (c+7, c), (c, c+9), (c-7, c)]
            pygame.draw.polygon(img, (220, 160, 255), pts)
            pygame.draw.polygon(img, (255, 200, 255), pts, 1)
            pygame.draw.line(img, (240, 200, 255), (c, c-9), (c, c+9), 1)
            pygame.draw.line(img, (240, 200, 255), (c-7, c), (c+7, c), 1)

        elif self.biome == 10:  # Infernal Power — triple flame
            for ox in (-4, 0, 4):
                pygame.draw.ellipse(img, (255, 80, 0),
                                    (c+ox-2, c-6, 5, 10))
                pygame.draw.ellipse(img, (255, 200, 50),
                                    (c+ox-1, c-3, 3, 6))

        elif self.biome == 11:  # Mycelium — mushroom
            pygame.draw.ellipse(img, (180, 255, 100), (c-7, c-4, 14, 8))
            pygame.draw.rect(img, (230, 210, 180), (c-2, c+3, 4, 6))
            pygame.draw.circle(img, (220, 255, 150), (c-3, c), 2)
            pygame.draw.circle(img, (220, 255, 150), (c+3, c-1), 2)

        elif self.biome == 12:  # Thunder Shot — double lightning
            pygame.draw.polygon(img, (220, 240, 255), [
                (c+2, c-8),(c-2, c-1),(c+3, c-1),(c-2, c+8),(c+2, c+1),(c-3, c+1)])
            pygame.draw.polygon(img, (180, 210, 255), [
                (c+6, c-6),(c+2, c+1),(c+7, c+1),(c+2, c+8),(c+6, c+1),(c+1, c+1)])

        else:  # biome 13 — Hell Mode — skull outline
            pygame.draw.circle(img, (255, 50, 50), (c, c-1), 7)
            pygame.draw.rect(img, (255, 50, 50), (c-5, c+4, 10, 5))
            pygame.draw.rect(img, (0, 0, 0, 0), (c-3, c+6, 2, 3))
            pygame.draw.rect(img, (0, 0, 0, 0), (c+1, c+6, 2, 3))
            pygame.draw.rect(img, (30, 0, 0), (c-3, c-2, 2, 3))
            pygame.draw.rect(img, (30, 0, 0), (c+1, c-2, 2, 3))

    def update(self):
        self._tick += 1
        self.rect.centery = self._base_y + int(4 * math.sin(self._tick * 0.07))
        self._render()
