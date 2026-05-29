import pygame

from entities.enemy import BasicEnemy, ShooterEnemy, MiniBoss, FinalBoss
from entities.pickup import WeaponPickup

# Enemy heights:  basic=46  shooter=48  miniboss=70  boss=100
# Ground top:     y=580
# On-ground y:    basic=534  shooter=532  miniboss=510  boss=480
# Platform y:     enemy_y = platform_top - enemy_height

LEVEL_DEFINITIONS = [
    # ── Level 1 ── Rookie (8 HP, no power)
    # 2 enemies: 2 basic — gentle intro, wide open layout
    {
        "platforms": [
            (0,   580, 1024, 60),   # ground
            (200, 480,  200, 20),   # left mid    top=480
            (650, 480,  200, 20),   # right mid   top=480
        ],
        "enemies": [
            ("basic", 340,  534),   # ground centre
            ("basic", 220,  434),   # left-mid platform  (480-46)
        ],
        "pickups": [("pistol", 680, 440)],   # right-mid platform
        "portal": (950, 520),
    },

    # ── Level 2 ── Cadet (9 HP, extra ammo)
    # 3 enemies: 2 basic, 1 shooter — one elevated shooter for first ranged threat
    {
        "platforms": [
            (0,   580, 1024, 60),
            (150, 490,  170, 20),   # left        top=490
            (450, 410,  170, 20),   # centre      top=410
            (750, 490,  170, 20),   # right       top=490
        ],
        "enemies": [
            ("basic",   200,  534),   # ground left
            ("basic",   770,  444),   # right platform  (490-46)
            ("shooter", 470,  362),   # centre platform (410-48)
        ],
        "pickups": [("rifle", 470, 370)],
        "portal": (940, 520),
    },

    # ── Level 3 ── Scout (10 HP, double jump)
    # 4 enemies: 2 basic, 1 shooter, 1 miniboss  ← difficulty ramps up here
    {
        "platforms": [
            (0,   580, 1024, 60),   # ground
            (150, 460,  130, 20),   # left mid      top=460
            (420, 370,  130, 20),   # center high   top=370
            (700, 450,  130, 20),   # right mid     top=450
        ],
        "enemies": [
            ("basic",    250,  534),   # ground, centre-left
            ("basic",    170,  414),   # left-mid platform  (460-46)
            ("shooter",  720,  402),   # right-mid platform (450-48)
            ("miniboss", 870,  510),   # ground, far right
        ],
        "pickups": [("rifle", 450, 330)],   # centre-high platform
        "portal": (950, 520),
    },

    # ── Level 2 ── Soldier (12 HP, armor)
    # 6 enemies: 2 basic, 3 shooter, 1 miniboss
    {
        "platforms": [
            (0,   580, 1024, 60),
            (100, 500,  110, 20),   # top=500
            (310, 420,  110, 20),   # top=420
            (560, 340,  110, 20),   # top=340
            (800, 420,  110, 20),   # top=420
            (920, 300,   90, 20),   # top=300
        ],
        "enemies": [
            ("basic",    180,  534),
            ("basic",    660,  534),
            ("shooter",  330,  372),   # (310,420)  420-48
            ("shooter",  580,  292),   # (560,340)  340-48
            ("shooter",  820,  372),   # (800,420)  420-48
            ("miniboss", 935,  230),   # (920,300)  300-70
        ],
        "pickups": [("blaster", 575, 300)],
        "portal": (30, 520),
    },

    # ── Level 3 ── Gunslinger (13 HP, rapid fire)
    # 7 enemies: 2 basic, 3 shooter, 2 miniboss
    {
        "platforms": [
            (0,   580, 1024, 60),
            (120, 490,  110, 20),   # top=490
            (320, 410,  100, 20),   # top=410
            (530, 330,  100, 20),   # top=330
            (750, 420,  100, 20),   # top=420
            (870, 300,  100, 20),   # top=300
            (420, 510,  100, 20),   # top=510
        ],
        "enemies": [
            ("basic",    200,  534),
            ("basic",    440,  464),   # (420,510)  510-46
            ("shooter",  340,  362),   # (320,410)  410-48
            ("shooter",  550,  282),   # (530,330)  330-48
            ("shooter",  770,  372),   # (750,420)  420-48
            ("miniboss", 885,  230),   # (870,300)  300-70
            ("miniboss", 660,  510),   # ground
        ],
        "pickups": [("shotgun", 545, 290)],
        "portal": (880, 240),          # on (870,300) platform  300-60
    },

    # ── Level 4 ── Ranger (14 HP, power shot)
    # 8 enemies: 2 basic, 3 shooter, 3 miniboss
    {
        "platforms": [
            (0,   580, 1024, 60),
            ( 80, 500,  100, 20),   # top=500
            (260, 420,  100, 20),   # top=420
            (460, 340,  100, 20),   # top=340
            (670, 260,  100, 20),   # top=260
            (830, 340,  100, 20),   # top=340
            (490, 500,  100, 20),   # top=500
        ],
        "enemies": [
            ("basic",    160,  534),
            ("basic",    510,  454),   # (490,500)  500-46
            ("shooter",  280,  372),   # (260,420)  420-48
            ("shooter",  480,  292),   # (460,340)  340-48
            ("shooter",  690,  212),   # (670,260)  260-48
            ("miniboss",  95,  430),   # (80,500)   500-70
            ("miniboss", 845,  270),   # (830,340)  340-70
            ("miniboss", 380,  510),   # ground
        ],
        "pickups": [("rifle", 470, 300)],
        "portal": (90, 440),           # on (80,500) platform  500-60
    },

    # ── Level 5 ── Commander (16 HP, all powers)
    # 8 enemies: 2 basic, 3 shooter, 2 miniboss, 1 boss
    # Vertical tower — boss guards the top platform
    {
        "platforms": [
            (0,   580, 1024, 60),
            ( 80, 510,  100, 20),   # top=510
            (260, 430,   90, 20),   # top=430
            (150, 350,   90, 20),   # top=350
            (450, 350,   90, 20),   # top=350
            (640, 270,   90, 20),   # top=270
            (600, 180,  200, 20),   # top=180  boss arena (wide)
            (860, 420,   90, 20),   # top=420
        ],
        "enemies": [
            ("basic",    200,  534),
            ("basic",    875,  374),   # (860,420)  420-46
            ("shooter",  280,  382),   # (260,430)  430-48
            ("shooter",  170,  302),   # (150,350)  350-48
            ("shooter",  470,  302),   # (450,350)  350-48
            ("miniboss", 655,  200),   # (640,270)  270-70
            ("miniboss", 500,  510),   # ground
            ("boss",     654,   80),   # (600,180)  180-100
        ],
        "pickups": [("blaster", 460, 310)],
        "portal": (950, 520),
    },

    # ══════════════════════════════════════════════════════════════════════════
    #  SECOND RUN  —  Levels 8-14  (indices 7-13)  harder versions
    # ══════════════════════════════════════════════════════════════════════════

    # ── Level 8 ── Jungle II  (biome cycles back to 0)
    {
        "platforms": [
            (0,   580, 1024, 60),
            (150, 470,  180, 20),   # top=470
            (450, 380,  180, 20),   # top=380
            (720, 470,  180, 20),   # top=470
            ( 80, 290,  120, 20),   # top=290
            (820, 290,  120, 20),   # top=290
        ],
        "enemies": [
            ("basic",    300,  534),
            ("basic",    700,  534),
            ("shooter",  230,  424),   # (150,470) 470-46
            ("shooter",  790,  424),   # (720,470) 470-46
            ("shooter",  510,  334),   # (450,380) 380-46
            ("miniboss", 465,  310),   # (450,380) 380-70
            ("miniboss", 130,  220),   # (80,290)  290-70
        ],
        "pickups": [("shotgun", 480, 340)],
        "portal": (950, 520),
    },

    # ── Level 9 ── Mountain II
    {
        "platforms": [
            (0,   580, 1024, 60),
            (120, 490,  130, 20),   # top=490
            (330, 410,  130, 20),   # top=410
            (560, 330,  130, 20),   # top=330
            (780, 410,  130, 20),   # top=410
            (900, 280,  110, 20),   # top=280
            (200, 280,  110, 20),   # top=280
        ],
        "enemies": [
            ("basic",    200,  534),
            ("basic",    800,  534),
            ("shooter",  185,  444),   # (120,490) 490-46
            ("shooter",  395,  364),   # (330,410) 410-46
            ("shooter",  625,  284),   # (560,330) 330-46
            ("miniboss", 795,  340),   # (780,410) 410-70
            ("miniboss", 955,  210),   # (900,280) 280-70
            ("miniboss", 255,  210),   # (200,280) 280-70
        ],
        "pickups": [("rifle", 575, 290)],
        "portal": (35, 520),
    },

    # ── Level 10 ── Desert II
    {
        "platforms": [
            (0,   580, 1024, 60),
            (100, 490,  120, 20),   # top=490
            (300, 400,  120, 20),   # top=400
            (520, 320,  120, 20),   # top=320
            (740, 400,  120, 20),   # top=400
            (880, 290,  120, 20),   # top=290
            (450, 500,  100, 20),   # top=500
        ],
        "enemies": [
            ("basic",    500,  454),   # (450,500) 500-46
            ("basic",    600,  534),
            ("shooter",  160,  444),   # (100,490) 490-46
            ("shooter",  360,  354),   # (300,400) 400-46
            ("shooter",  580,  274),   # (520,320) 320-46
            ("miniboss", 800,  330),   # (740,400) 400-70
            ("miniboss", 895,  220),   # (880,290) 290-70
            ("miniboss", 700,  534),
        ],
        "pickups": [("blaster", 535, 280)],
        "portal": (50, 520),
    },

    # ── Level 11 ── Volcano II
    {
        "platforms": [
            (0,   580, 1024, 60),
            (100, 500,  110, 20),   # top=500
            (310, 420,  110, 20),   # top=420
            (560, 340,  110, 20),   # top=340
            (800, 420,  110, 20),   # top=420
            (920, 300,   90, 20),   # top=300
        ],
        "enemies": [
            ("basic",    200,  534),
            ("basic",    650,  534),
            ("shooter",  330,  372),   # (310,420) 420-48
            ("shooter",  580,  292),   # (560,340) 340-48
            ("shooter",  820,  372),   # (800,420) 420-48
            ("miniboss", 115,  430),   # (100,500) 500-70
            ("miniboss", 815,  350),   # (800,420) 420-70
            ("miniboss", 935,  230),   # (920,300) 300-70
            ("boss",     575,  240),   # (560,340) 340-100
        ],
        "pickups": [("shotgun", 590, 300)],
        "portal": (35, 520),
    },

    # ── Level 12 ── Swamp II
    {
        "platforms": [
            (0,   580, 1024, 60),
            ( 80, 500,  110, 20),   # top=500
            (260, 420,   90, 20),   # top=420
            (460, 340,   90, 20),   # top=340
            (660, 260,   90, 20),   # top=260
            (840, 340,   90, 20),   # top=340
            (480, 500,  100, 20),   # top=500
        ],
        "enemies": [
            ("basic",    530,  454),   # (480,500) 500-46
            ("basic",    200,  534),
            ("shooter",   95,  452),   # (80,500)  500-48
            ("shooter",  275,  372),   # (260,420) 420-48
            ("shooter",  475,  292),   # (460,340) 340-48
            ("miniboss", 675,  190),   # (660,260) 260-70
            ("miniboss", 855,  270),   # (840,340) 340-70
            ("miniboss", 400,  534),
            ("boss",     475,  240),   # (460,340) 340-100
        ],
        "pickups": [("rifle", 670, 220)],
        "portal": (950, 520),
    },

    # ── Level 13 ── Arctic II
    {
        "platforms": [
            (0,   580, 1024, 60),
            (100, 510,  100, 20),   # top=510
            (280, 430,   90, 20),   # top=430
            (480, 350,   90, 20),   # top=350
            (680, 270,   90, 20),   # top=270
            (860, 350,   90, 20),   # top=350
            (500, 500,   90, 20),   # top=500
            (150, 360,   80, 20),   # top=360
        ],
        "enemies": [
            ("basic",    150,  534),
            ("basic",    900,  534),
            ("basic",    545,  454),   # (500,500) 500-46
            ("shooter",  150,  462),   # (100,510) 510-48
            ("shooter",  325,  382),   # (280,430) 430-48
            ("shooter",  525,  302),   # (480,350) 350-48
            ("miniboss", 695,  200),   # (680,270) 270-70
            ("miniboss", 875,  280),   # (860,350) 350-70
            ("miniboss", 190,  290),   # (150,360) 360-70
            ("boss",     495,  250),   # (480,350) 350-100
        ],
        "pickups": [("shotgun", 690, 230)],
        "portal": (35, 520),
    },

    # ── Level 14 ── Ruins Final II  (2 bosses)
    {
        "platforms": [
            (0,   580, 1024, 60),
            ( 80, 510,  100, 20),   # top=510
            (260, 430,   90, 20),   # top=430
            (150, 350,   90, 20),   # top=350
            (450, 350,   90, 20),   # top=350
            (640, 270,   90, 20),   # top=270
            (600, 180,  200, 20),   # top=180  boss arena
            (860, 420,   90, 20),   # top=420
        ],
        "enemies": [
            ("basic",    200,  534),
            ("basic",    400,  534),
            ("basic",    875,  374),   # (860,420) 420-46
            ("shooter",  280,  382),   # (260,430) 430-48
            ("shooter",  170,  302),   # (150,350) 350-48
            ("shooter",  470,  302),   # (450,350) 350-48
            ("miniboss", 655,  200),   # (640,270) 270-70
            ("miniboss", 500,  510),   # ground
            ("boss",     630,   80),   # (600,180) 180-100  left boss
            ("boss",     730,   80),   # (600,180) 180-100  right boss
        ],
        "pickups": [("shotgun", 700, 140)],
        "portal": (950, 520),
    },
]
