import os
import pygame

from settings import ASSETS_DIR


def load_sprite(filename, size, fallback_color, border_radius=8):
    path = os.path.join(ASSETS_DIR, filename)
    if os.path.isfile(path):
        try:
            image = pygame.image.load(path).convert_alpha()
            if image.get_size() != size:
                image = pygame.transform.smoothscale(image, size)
            return image
        except pygame.error:
            pass
    surface = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(surface, fallback_color, surface.get_rect(), border_radius=border_radius)
    return surface


def make_enemy_sprite(size, color, style):
    """Draw a visually distinct enemy sprite for each enemy type."""
    surf = pygame.Surface(size, pygame.SRCALPHA)
    W, H = size
    cx = W // 2
    DARK  = tuple(max(0,   c - 65) for c in color)
    LIGHT = tuple(min(255, c + 65) for c in color)
    SKIN  = (210, 170, 125)

    if style == 'basic':
        # Human grunt — helmet, armour vest, gun
        pygame.draw.rect(surf, DARK,         (cx - 8,  1, 16, 7),  border_radius=3)  # helmet
        pygame.draw.rect(surf, SKIN,         (cx - 6,  6, 12, 9),  border_radius=3)  # face
        pygame.draw.rect(surf, (40, 40, 50), (cx - 5,  8,  4, 3))                    # left eye
        pygame.draw.rect(surf, (40, 40, 50), (cx + 1,  8,  4, 3))                    # right eye
        pygame.draw.rect(surf, color,        (cx - 10,15, 20,17),  border_radius=3)  # body/vest
        pygame.draw.rect(surf, LIGHT,        (cx - 6, 18,  3, 8))                    # badge stripe
        pygame.draw.rect(surf, DARK,         (cx - 15,16,  6,12),  border_radius=2)  # left arm
        pygame.draw.rect(surf, DARK,         (cx + 9, 16,  6,12),  border_radius=2)  # right arm
        pygame.draw.rect(surf, (55, 55, 60), (cx + 13,21,  9, 4))                    # gun barrel
        pygame.draw.rect(surf, DARK,         (cx - 9, 32,  8,12),  border_radius=2)  # left leg
        pygame.draw.rect(surf, DARK,         (cx + 1, 32,  8,12),  border_radius=2)  # right leg
        pygame.draw.rect(surf, (55, 55, 60), (cx - 10,42, 10, 4))                    # boot L
        pygame.draw.rect(surf, (55, 55, 60), (cx,     42, 10, 4))                    # boot R

    elif style == 'shooter':
        # Robot — boxy head, antenna, LED eyes, gun arm
        pygame.draw.line(surf, LIGHT,        (cx, 0), (cx, 5), 2)                    # antenna
        pygame.draw.circle(surf, LIGHT,      (cx, 0), 3)                             # antenna tip
        pygame.draw.rect(surf, color,        (cx - 9, 4, 18, 13), border_radius=2)   # head
        pygame.draw.rect(surf, (255, 50, 50),(cx - 7, 8, 14,  5), border_radius=1)   # visor
        pygame.draw.rect(surf, (255,150,150),(cx - 5, 9, 10,  3), border_radius=1)   # visor glow
        pygame.draw.rect(surf, color,        (cx -12,17, 24,18),  border_radius=2)   # torso
        pygame.draw.rect(surf, DARK,         (cx - 7,20, 14, 9),  border_radius=1)   # chest plate
        pygame.draw.circle(surf, (255,70,70),(cx, 24), 3)                            # power core
        pygame.draw.rect(surf, DARK,         (cx -19,18,  8, 9),  border_radius=2)   # gun arm
        pygame.draw.rect(surf, (45, 45, 55), (cx -24,21,  6, 4))                     # barrel
        pygame.draw.rect(surf, DARK,         (cx +11,18,  8,10),  border_radius=2)   # right arm
        pygame.draw.rect(surf, DARK,         (cx -10,35,  8,11),  border_radius=2)   # leg L
        pygame.draw.rect(surf, DARK,         (cx + 2,35,  8,11),  border_radius=2)   # leg R
        pygame.draw.rect(surf, (45, 45, 55), (cx -12,44, 11, 4))                     # foot L
        pygame.draw.rect(surf, (45, 45, 55), (cx + 1,44, 11, 4))                     # foot R

    elif style == 'miniboss':
        # Monster — horns, wide head, fangs, claws, massive body
        # Horns
        pygame.draw.polygon(surf, DARK, [(cx-22,18),(cx-15, 2),(cx-10,18)])
        pygame.draw.polygon(surf, DARK, [(cx+10, 18),(cx+15, 2),(cx+22,18)])
        # Head (wide)
        pygame.draw.ellipse(surf, color,         (cx-18,12, 36,26))
        # Eyes (yellow, menacing)
        pygame.draw.circle(surf, (255,215, 0),   (cx - 8,22),  5)
        pygame.draw.circle(surf, (255,215, 0),   (cx + 8,22),  5)
        pygame.draw.circle(surf, (20, 10,  5),   (cx - 8,22),  2)
        pygame.draw.circle(surf, (20, 10,  5),   (cx + 8,22),  2)
        # Mouth + fangs
        pygame.draw.rect(surf, (18,  8,  8),     (cx-10,32, 20, 7))
        for i in range(4):
            pygame.draw.polygon(surf, (230,220,210),
                [(cx-8+i*5, 32),(cx-6+i*5,32),(cx-7+i*5,38)])
        # Body (massive)
        pygame.draw.rect(surf, color,            (cx-20,38, 40,22), border_radius=5)
        pygame.draw.ellipse(surf, DARK,          (cx-12,42, 24,14))  # belly
        # Arms (muscular)
        pygame.draw.rect(surf, DARK,             (cx-30,38, 12,20), border_radius=3)
        pygame.draw.rect(surf, DARK,             (cx+18,38, 12,20), border_radius=3)
        # Claws
        for ox, sign in ((-30, -1), (18, 1)):
            for f in range(3):
                pygame.draw.polygon(surf, LIGHT, [
                    (cx+ox+f*4+2, 58),
                    (cx+ox+f*4+4, 58),
                    (cx+ox+f*4+3, 65)])
        # Legs
        pygame.draw.rect(surf, DARK,             (cx-15,60, 12,10), border_radius=3)
        pygame.draw.rect(surf, DARK,             (cx+ 3,60, 12,10), border_radius=3)

    elif style == 'boss':
        # Final boss — armoured giant, crown, glowing visor, cape, gauntlets
        # Cape (behind everything)
        pygame.draw.ellipse(surf, DARK,          (cx-38,22, 76,55))
        # Shoulder spikes
        for sx in (-30, 30):
            pygame.draw.polygon(surf, DARK, [
                (cx+sx-6,28),(cx+sx,10),(cx+sx+6,28)])
        # Body armour
        pygame.draw.rect(surf, color,            (cx-24,32, 48,38), border_radius=6)
        pygame.draw.rect(surf, DARK,             (cx-18,36, 36,26), border_radius=4)
        # Glowing core
        pygame.draw.circle(surf, (255, 40, 40),  (cx, 50), 9)
        pygame.draw.circle(surf, (255,140,140),  (cx, 50), 5)
        pygame.draw.circle(surf, (255,240,240),  (cx, 50), 2)
        # Head / helmet
        pygame.draw.rect(surf, DARK,             (cx-16,10, 32,24), border_radius=5)
        # Crown spikes
        for i in range(5):
            px = cx - 14 + i * 7
            pygame.draw.polygon(surf, (180,25,25), [(px,10),(px+3,1),(px+6,10)])
        # Visor
        pygame.draw.rect(surf, (210, 0,  0),     (cx-13,16, 26, 9), border_radius=3)
        pygame.draw.rect(surf, (255, 90, 90),    (cx-11,17, 22, 5), border_radius=2)
        # Arms (massive)
        pygame.draw.rect(surf, DARK,             (cx-40,34, 18,26), border_radius=4)
        pygame.draw.rect(surf, DARK,             (cx+22,34, 18,26), border_radius=4)
        # Gauntlets
        pygame.draw.rect(surf, color,            (cx-42,58, 20,14), border_radius=4)
        pygame.draw.rect(surf, color,            (cx+22,58, 20,14), border_radius=4)
        # Knuckle studs
        for kx, ky in [(cx-38,68),(cx-32,68),(cx+26,68),(cx+32,68)]:
            pygame.draw.circle(surf, LIGHT, (kx, ky), 2)
        # Legs
        pygame.draw.rect(surf, DARK,             (cx-20,70, 16,22), border_radius=4)
        pygame.draw.rect(surf, DARK,             (cx+ 4,70, 16,22), border_radius=4)
        # Boots
        pygame.draw.rect(surf, color,            (cx-22,88, 20, 10), border_radius=3)
        pygame.draw.rect(surf, color,            (cx+ 2,88, 20, 10), border_radius=3)

    return surf


def make_character_sprite(size, body_color, style='rookie'):
    """Draw a distinct player sprite for each character class."""
    surf = pygame.Surface(size, pygame.SRCALPHA)
    W, H = size
    cx = W // 2

    SKIN  = (218, 182, 138)
    DARK  = tuple(max(0,   c - 55) for c in body_color)
    LIGHT = tuple(min(255, c + 55) for c in body_color)

    # ── Shared base: legs → body → head → eyes ───────────────────────────────
    def draw_base(head_y=2, body_y=15):
        # Legs
        pygame.draw.rect(surf, DARK, (cx - 11, H - 16, 10, 16), border_radius=3)
        pygame.draw.rect(surf, DARK, (cx +  1, H - 16, 10, 16), border_radius=3)
        # Body
        pygame.draw.rect(surf, body_color, (cx - 13, body_y, 26, 20), border_radius=4)
        # Head
        pygame.draw.rect(surf, SKIN, (cx - 7, head_y, 14, 13), border_radius=4)
        # Eyes
        pygame.draw.rect(surf, (40, 40, 55), (cx - 5, head_y + 4, 3, 3))
        pygame.draw.rect(surf, (40, 40, 55), (cx + 2, head_y + 4, 3, 3))

    # ── Per-class styles ──────────────────────────────────────────────────────
    if style == 'rookie':
        draw_base()
        # White chest stripe
        pygame.draw.rect(surf, (210, 210, 220), (cx - 4, 19, 8, 2))
        pygame.draw.rect(surf, (210, 210, 220), (cx - 4, 23, 8, 2))

    elif style == 'cadet':
        draw_base()
        # Gold star badge on chest
        pygame.draw.circle(surf, (255, 215, 0), (cx, 24), 5)
        pygame.draw.circle(surf, body_color,    (cx, 24), 3)
        # Collar stripe
        pygame.draw.rect(surf, LIGHT, (cx - 13, 15, 26, 3))

    elif style == 'scout':
        draw_base()
        # Blue scarf at neck
        pygame.draw.rect(surf, (70, 110, 215), (cx - 9, 15, 18, 5), border_radius=2)
        # Small backpack
        pygame.draw.rect(surf, DARK, (cx + 11, 17, 5, 13), border_radius=2)
        pygame.draw.rect(surf, LIGHT, (cx + 12, 18, 3, 5))

    elif style == 'soldier':
        draw_base()
        # Shoulder pads (drawn before body so body covers the gap)
        pygame.draw.rect(surf, (145, 155, 165), (cx - 18, 15, 7, 9), border_radius=3)
        pygame.draw.rect(surf, (145, 155, 165), (cx + 11, 15, 7, 9), border_radius=3)
        # Dark visor over eyes
        pygame.draw.rect(surf, (25, 35, 105), (cx - 7, 6, 14, 5), border_radius=2)
        # Chest plate highlight
        pygame.draw.rect(surf, LIGHT, (cx - 8, 18, 16, 3), border_radius=1)

    elif style == 'gunslinger':
        # Hat drawn first (behind head)
        pygame.draw.rect(surf, (90, 58, 22), (cx - 12, 3, 24, 3))   # brim
        pygame.draw.rect(surf, (90, 58, 22), (cx - 7,  0, 14, 6), border_radius=2)  # crown
        draw_base(head_y=4)
        # Red neckerchief
        pygame.draw.rect(surf, (200, 45, 45), (cx - 6, 15, 12, 5), border_radius=2)
        # Gun holster stripe on leg
        pygame.draw.rect(surf, (80, 50, 20), (cx + 1, H - 15, 4, 10))

    elif style == 'ranger':
        draw_base()
        # Dark hood over head
        hood = tuple(max(0, c - 75) for c in body_color)
        pygame.draw.rect(surf, hood, (cx - 9, 1, 18, 16), border_radius=5)
        # Eye slit
        pygame.draw.rect(surf, SKIN, (cx - 5, 6,  10, 5))
        pygame.draw.rect(surf, (40, 40, 55), (cx - 4, 7, 3, 3))
        pygame.draw.rect(surf, (40, 40, 55), (cx + 1, 7, 3, 3))
        # Quiver on back
        pygame.draw.rect(surf, (115, 75, 35), (cx + 11, 16, 5, 14), border_radius=2)
        pygame.draw.line(surf, (200, 160, 80), (cx + 13, 16), (cx + 13, 29), 1)

    elif style == 'commander':
        # Cape behind body
        pygame.draw.rect(surf, DARK, (cx - 16, 17, 32, 20), border_radius=4)
        draw_base()
        # Chest gold emblem
        pygame.draw.circle(surf, (255, 200, 0), (cx, 24), 5)
        pygame.draw.circle(surf, body_color,    (cx, 24), 3)
        # Crown spikes above head
        pygame.draw.rect(surf, (255, 200, 0), (cx - 7, 3, 14, 3))
        for px in (cx - 5, cx, cx + 5):
            pygame.draw.polygon(surf, (255, 200, 0),
                                [(px - 2, 3), (px + 2, 3), (px, -1)])
        # Epaulettes
        pygame.draw.circle(surf, (255, 200, 0), (cx - 13, 18), 3)
        pygame.draw.circle(surf, (255, 200, 0), (cx + 13, 18), 3)

    return surf
