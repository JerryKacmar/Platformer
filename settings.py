import os

BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 640
FPS = 60
GRAVITY = 0.8
PLAYER_SPEED = 5
JUMP_SPEED = -15
BULLET_SPEED = 12
ENEMY_BULLET_SPEED = 4
PLAYER_MAX_HEALTH = 12
LEVEL_COUNT = 14
FIRST_RUN_LEVELS = 7   # lobby triggers after this many levels

COLORS = {
    "bg": (12, 28, 12),
    "platform": (65, 88, 45),
    "player": (220, 200, 90),
    "enemy": (220, 90, 90),
    "shooter": (180, 120, 220),
    "miniboss": (220, 140, 55),
    "boss": (200, 60, 90),
    "bullet_player": (230, 230, 110),
    "bullet_enemy": (255, 110, 110),
    "weapon": (100, 210, 240),
    "portal_inactive": (90, 90, 130),
    "portal_active": (100, 220, 140),
    "text": (240, 240, 240),
    "health_bg": (90, 20, 30),
    "health_fg": (220, 50, 50),
}

WEAPONS = {
    "pistol": {
        "fire_delay": 16,
        "damage": 1,
        "speed": BULLET_SPEED,
        "color": (240, 240, 160),
        "ammo": 30,
    },
    "blaster": {
        "fire_delay": 26,
        "damage": 2,
        "speed": BULLET_SPEED * 1.3,
        "color": (110, 220, 240),
        "ammo": 25,
    },
    "rifle": {
        "fire_delay": 12,
        "damage": 1,
        "speed": BULLET_SPEED * 1.5,
        "color": (120, 200, 120),
        "ammo": 40,
    },
    "shotgun": {
        "fire_delay": 40,
        "damage": 3,
        "speed": BULLET_SPEED,
        "color": (255, 140, 60),
        "ammo": 15,
    },
}

FONT_NAME = "freesansbold.ttf"
