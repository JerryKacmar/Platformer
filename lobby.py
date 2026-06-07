import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_NAME

# Upgrades available in the shop
UPGRADES = [
    {"key": "hp",       "name": "Extra HP",       "desc": "+3 max health",                  "cost": 10},
    {"key": "ammo",     "name": "Extra Ammo",     "desc": "+10 ammo per weapon",            "cost":  8},
    {"key": "damage",   "name": "Power Up",       "desc": "+1 bullet damage",               "cost": 15},
    {"key": "grenades", "name": "Extra Grenade",  "desc": "+1 max grenade slot",            "cost": 12},
    {"key": "armor",    "name": "Body Armor",     "desc": "-1 damage taken",                "cost": 15},
    {"key": "jump",     "name": "Extra Jump",     "desc": "+1 air jump (all classes)",      "cost": 12},
    {"key": "speed",    "name": "Speed Boost",    "desc": "+25% movement speed",            "cost": 14},
    {"key": "shield",   "name": "Shield Charge",  "desc": "start each level with 2 shields","cost": 14},
]

_W = (235, 235, 235)
_Y = (255, 220,  55)
_G = ( 80, 215, 110)
_R = (255, 100, 100)
_D = (130, 130, 130)


class LobbyScreen:
    def __init__(self):
        self.selected   = 0
        self.flash_msg  = ""
        self.flash_tick = 0

    def _flash(self, msg):
        self.flash_msg  = msg
        self.flash_tick = 120

    def handle_event(self, event, coins, purchased):
        """Return a command tuple or None.
        Commands:  ("buy", key, cost)  |  ("speedrun",)  |  ("continue",)
        """
        if event.type != pygame.KEYDOWN:
            return None

        if event.key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(UPGRADES)

        elif event.key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(UPGRADES)

        elif event.key in (pygame.K_RETURN, pygame.K_z):
            upg = UPGRADES[self.selected]
            if purchased.get(upg["key"]):
                self._flash("Already purchased!")
            elif coins < upg["cost"]:
                self._flash(f"Need {upg['cost']} coins!")
            else:
                self._flash(f"Bought: {upg['name']}!")
                return ("buy", upg["key"], upg["cost"])

        elif event.key == pygame.K_r:
            return ("speedrun",)

        elif event.key == pygame.K_n:
            return ("continue",)

        return None

    def update(self):
        if self.flash_tick > 0:
            self.flash_tick -= 1

    def draw(self, surface, coins, purchased, highscore=None):
        surface.fill((8, 10, 30))

        title_f  = pygame.font.Font(FONT_NAME, 36)
        head_f   = pygame.font.Font(FONT_NAME, 22)
        body_f   = pygame.font.Font(FONT_NAME, 18)
        small_f  = pygame.font.Font(FONT_NAME, 15)

        def txt(font, text, color, cx=None, x=None, y=0):
            s = font.render(text, True, color)
            bx = (SCREEN_WIDTH // 2 - s.get_width() // 2) if cx else x
            surface.blit(s, (bx, y))

        # ── Title ────────────────────────────────────────────────────────────
        txt(title_f, "MISSION COMPLETE", _Y, cx=True, y=18)
        pygame.draw.line(surface, _Y, (40, 62), (SCREEN_WIDTH - 40, 62), 1)

        # ── Coin display ─────────────────────────────────────────────────────
        txt(head_f, f"Coins:  {coins}  ●", _G, cx=True, y=70)

        # ── Intro blurb ──────────────────────────────────────────────────────
        txt(small_f, "You earned 30 coins for completing the first 7 levels.", _W, cx=True, y=98)
        txt(small_f, "Spend coins below to upgrade your character before the next run.", _D, cx=True, y=114)

        # ── Upgrade shop ─────────────────────────────────────────────────────
        txt(head_f, "── Upgrade Shop ──", _W, cx=True, y=136)

        shop_x = SCREEN_WIDTH // 2 - 280
        for i, upg in enumerate(UPGRADES):
            y = 160 + i * 32
            is_sel    = (i == self.selected)
            is_bought = purchased.get(upg["key"], False)

            bg_col = (30, 35, 65) if is_sel else (15, 18, 40)
            pygame.draw.rect(surface, bg_col, (shop_x, y - 3, 560, 28), border_radius=5)
            if is_sel:
                pygame.draw.rect(surface, _Y, (shop_x, y - 3, 560, 28), 2, border_radius=5)

            name_col = _D if is_bought else (_Y if is_sel else _W)
            cost_col = _D if is_bought else _G
            status   = "PURCHASED" if is_bought else f"{upg['cost']} coins"

            txt(body_f,  upg["name"],  name_col, x=shop_x + 12,  y=y)
            txt(small_f, upg["desc"],  _D,        x=shop_x + 180, y=y + 4)
            s = small_f.render(status, True, cost_col)
            surface.blit(s, (shop_x + 560 - s.get_width() - 12, y + 4))

        # ── Flash message ────────────────────────────────────────────────────
        if self.flash_tick > 0:
            fc = (255, 220, 60) if "Bought" in self.flash_msg else (255, 100, 100)
            fs = head_f.render(self.flash_msg, True, fc)
            surface.blit(fs, (SCREEN_WIDTH // 2 - fs.get_width() // 2, 424))

        # ── Mode buttons ─────────────────────────────────────────────────────
        pygame.draw.line(surface, (60, 60, 90), (40, 444), (SCREEN_WIDTH - 40, 444), 1)
        txt(head_f, "Choose your next challenge:", _W, cx=True, y=452)

        # Speedrun button
        pygame.draw.rect(surface, (35, 70, 40), (80, 480, 390, 48), border_radius=8)
        pygame.draw.rect(surface, _G,            (80, 480, 390, 48), 2, border_radius=8)
        txt(head_f,  "[R]  Replay Levels 1-7",           _G, x=100, y=487)
        txt(small_f, "4-minute time limit — beat the clock!", _D, x=100, y=509)

        # Continue button
        pygame.draw.rect(surface, (35, 40, 80), (554, 480, 390, 48), border_radius=8)
        pygame.draw.rect(surface, _Y,             (554, 480, 390, 48), 2, border_radius=8)
        txt(head_f,  "[N]  Continue to Levels 8-14",     _Y, x=574, y=487)
        txt(small_f, "7 harder levels — no time limit.",      _D, x=574, y=509)

        # Controls hint
        txt(small_f, "UP/DOWN — select upgrade    ENTER / Z — buy", _D, cx=True, y=540)

        # Page counter placeholder
        s = small_f.render("LOBBY", True, (60, 60, 90))
        surface.blit(s, (SCREEN_WIDTH - s.get_width() - 16, SCREEN_HEIGHT - 24))

        # Global high-score record (farthest level by any signed-in user)
        if highscore and highscore.get("best_level"):
            rec = f"Record: Level {highscore['best_level']} by {highscore['best_user']}"
        else:
            rec = "Record: none yet"
        surface.blit(small_f.render(rec, True, _Y), (16, SCREEN_HEIGHT - 24))
