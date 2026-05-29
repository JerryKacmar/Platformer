import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS, FONT_NAME

# Colour shorthands used in page lines
_W  = (240, 240, 240)   # white  — default body text
_Y  = (255, 220,  60)   # yellow — key names / values
_G  = ( 80, 220, 120)   # green  — item / pickup info
_R  = (255, 110, 110)   # red    — danger / hazard
_B  = (110, 195, 255)   # blue   — weapon / character info
_O  = (255, 160,  40)   # orange — enemy / boss info


# Each page is a dict with "title" and "lines".
# A line is either a plain string (drawn in _W) or a tuple (text, colour).
PAGES = [
    # ── 1. Controls ──────────────────────────────────────────────────────────
    {
        "title": "Controls",
        "lines": [
            ("Movement",                                    _Y),
            ("  LEFT / RIGHT  or  A / D  — move",          _W),
            ("  SPACE / UP / W           — jump",          _W),
            ("  (Double-jump available on some classes)",   _W),
            "",
            ("Combat",                                      _Y),
            ("  Z  — shoot current weapon",                 _W),
            ("  G  — throw grenade (in facing direction)",   _W),
            "",
            ("Other",                                       _Y),
            ("  R  — restart after Game Over",              _W),
            "",
            ("Goal:  Kill every enemy → portal opens",      _G),
            ("       Walk into the portal to advance.",     _G),
        ],
    },

    # ── 2. Weapons ───────────────────────────────────────────────────────────
    {
        "title": "Weapons",
        "lines": [
            ("Pick up glowing blue boxes to swap weapons.", _W),
            "",
            ("PISTOL    — 1 dmg  |  fast fire  |  30 ammo",   _B),
            ("BLASTER   — 2 dmg  |  medium     |  25 ammo",   _B),
            ("RIFLE     — 1 dmg  |  very fast  |  40 ammo",   _B),
            ("SHOTGUN   — 3 dmg  |  slow fire  |  15 ammo",   _B),
            "",
            ("Cadet gets 1.5× ammo for every weapon.",        _G),
            ("Ranger deals +1 damage per bullet.",            _G),
            ("Gunslinger fires at 2× the normal rate.",       _G),
        ],
    },

    # ── 3. Grenades ──────────────────────────────────────────────────────────
    {
        "title": "Grenades  (G key)",
        "lines": [
            ("Grenades fly in the direction you are facing.",   _W),
            "",
            ("Grenades explode on contact with enemies",       _W),
            ("or after a short fuse.",                         _W),
            ("Explosion deals  6 damage  in a large radius.", (_Y)),
            ("(Equal to two shotgun shots.)",                  _W),
            "",
            ("Grenade supply per level:",                      _Y),
            ("  Cadet / Scout         — 1 grenade",           _G),
            ("  Soldier / Gunslinger  — 2 grenades",          _G),
            ("  Ranger / Commander   — 3 grenades",           _G),
        ],
    },

    # ── 4. Characters & powers ───────────────────────────────────────────────
    {
        "title": "Characters & Powers  (Run 1)",
        "lines": [
            ("Each level you play as a new character.",        _W),
            "",
            ("ROOKIE      —  8 HP  |  no special power",       _B),
            ("CADET       —  9 HP  |  1.5× ammo for all guns", _B),
            ("SCOUT       — 10 HP  |  double jump",            _B),
            ("SOLDIER     — 12 HP  |  −1 damage taken",        _B),
            ("GUNSLINGER  — 13 HP  |  2× fire rate",           _B),
            ("RANGER      — 14 HP  |  +1 damage per bullet",   _B),
            ("COMMANDER   — 16 HP  |  ALL powers combined",    _Y),
            "",
            ("Your weapon & ammo carry over between levels.", _G),
        ],
    },
    {
        "title": "Characters & Powers  (Run 2)",
        "lines": [
            ("After the lobby you play 7 stronger characters.", _W),
            "",
            ("VANGUARD  — 14 HP  |  triple jump  +1 dmg",      _B),
            ("TANK      — 22 HP  |  −2 dmg taken",             _B),
            ("BLITZER   — 15 HP  |  4× fire rate  +1 dmg",     _B),
            ("MARKSMAN  — 16 HP  |  +3 dmg per bullet",        _B),
            ("WARLORD   — 18 HP  |  Jump+Armor+Rapid+Power",   _B),
            ("PHANTOM   — 17 HP  |  Jump+2×Ammo+2 dmg",        _B),
            ("APEX      — 24 HP  |  ALL powers maximised",      _Y),
            "",
            ("Apex has 2 extra jumps, −2 armor, 4× fire",      _G),
            ("rate, +3 dmg, 5 grenades, and 2× ammo.",         _G),
        ],
    },

    # ── 5. Enemies ───────────────────────────────────────────────────────────
    {
        "title": "Enemies",
        "lines": [
            ("BASIC  (red)     — patrols, jumps, shoots",       _O),
            ("                   6 HP  |  contact: 1 dmg",      _W),
            "",
            ("SHOOTER  (purple) — stays back and fires at you", _O),
            ("                   8 HP  |  contact: 1 dmg",      _W),
            "",
            ("MINI-BOSS  (orange) — dashes, jumps, spread fire", _O),
            ("                   18 HP  |  contact: 2 dmg",     _W),
            "",
            ("FINAL BOSS  (dark red) — appears in Level 7",      _R),
            ("                   45 HP  |  all attack patterns", _W),
            ("  SPIRAL: fires 10 magenta bullets in all",        _R),
            ("  directions — rotates each volley, pierces walls",_W),
            "",
            ("Kill all enemies to activate the portal.",        _G),
        ],
    },

    # ── 6. Biomes & Hazards ──────────────────────────────────────────────────
    {
        "title": "Biomes & Hazards",
        "lines": [
            ("Every level has a unique biome with hazards:", _W),
            "",
            ("JUNGLE   — thorn spikes on the ground",        _G),
            ("MOUNTAIN — rock spikes between platforms",      _B),
            ("DESERT   — quicksand patches (slows movement)", _Y),
            ("VOLCANO  — lava pools on ground AND platforms",  _R),
            ("           (2 dmg / 1.5 s — watch every surface!)", _W),
            ("SWAMP    — toxic water floor (2 dmg / 1.5 s)", _R),
            ("ARCTIC   — icy platforms (you slide!)",         _B),
            ("RUINS    — spike traps on the floor",           _O),
            "",
            ("Spikes & lava also damage enemies,",            _W),
            ("but less effectively than the player.",         _W),
            "",
            ("Run 2 adds 7 harder biomes:",                   _Y),
            ("  Space · Ocean · Crystal Cave · Infernal",     _B),
            ("  Mushroom Forest · Storm · Hellscape",         _R),
        ],
    },

    # ── 6b. Biomes & Hazards (Run 2) ────────────────────────────────────────
    {
        "title": "Biomes & Hazards  (Run 2)",
        "lines": [
            ("Run 2 has 7 new biomes with harder hazards:",       _W),
            "",
            ("SPACE          — debris spikes  (1 dmg / 0.5 s)",   _B),
            ("OCEAN          — electric zones  (2 dmg / 1.5 s)",  _B),
            ("CRYSTAL CAVE   — crystal shards  (1 dmg / 0.5 s)",  _B),
            ("INFERNAL       — lava on ground AND platforms",      _R),
            ("                 (2 dmg / 1.5 s — nowhere safe!)",  _W),
            ("MUSHROOM FOREST — toxic spores  (slows movement)",   _G),
            ("STORM          — icy platforms  (you slide!)",       _B),
            ("HELLSCAPE      — fire floor AND fire pools",         _R),
            ("                 (2 dmg / 1.5 s — deadliest biome)", _W),
            "",
            ("Run 2 spikes deal damage twice as fast as Run 1.",  _Y),
            ("Hazards also damage enemies.",                       _W),
        ],
    },

    # ── 7. Biome Items (Run 1) ───────────────────────────────────────────────
    {
        "title": "Biome Items  (glowing orbs)  — Run 1",
        "lines": [
            ("One glowing orb spawns each level. Walk into it.",  _W),
            ("A banner confirms what you collected and its effect.", _W),
            "",
            ("JUNGLE   Vine Boost    — 3× speed for 5 s",         _G),
            ("MOUNTAIN Eagle Wings   — free flight for 5 s",      _B),
            ("DESERT   Heat Mirage   — shield: absorbs 5 hits",   _Y),
            ("VOLCANO  Magma Core    — 2× bullet damage, 5 s",    _R),
            ("SWAMP    Spore Burst   — 3× fire rate for 5 s",     _O),
            ("ARCTIC   Frost Blast   — freeze all enemies, 4 s",  _B),
            ("RUINS    Ancient Power — speed+flight+power, 6 s",  _Y),
            "",
            ("Active buffs appear in the top-left HUD (yellow).", _G),
        ],
    },

    # ── 8. Biome Items (Run 2) ───────────────────────────────────────────────
    {
        "title": "Biome Items  (glowing orbs)  — Run 2",
        "lines": [
            ("Run 2 has seven new biome items:",                      _W),
            "",
            ("SPACE    Meteor Strike  — instant damage to all foes",  _B),
            ("OCEAN    Tidal Wave     — full ammo refill",            _B),
            ("CRYSTAL  Crystal Armor  — shield: absorbs 10 hits",     _B),
            ("INFERNAL Infernal Power — 2× bullet damage for 8 s",   _R),
            ("MUSHROOM Mycelium       — 3× fire rate for 6 s",       _G),
            ("STORM    Thunder Shot   — speed + 2× damage for 5 s",  _B),
            ("HELL     Hell Mode      — ALL powers for 12 s",        _R),
            "",
            ("Grab the orb before fighting the boss!",               _Y),
        ],
    },

    # ── 8. Lobby, Coins & Upgrades ───────────────────────────────────────────
    {
        "title": "Lobby, Coins & Second Run",
        "lines": [
            ("After clearing Level 7 you enter the Lobby.",   _W),
            ("You instantly receive  30 coins.",              _Y),
            "",
            ("Upgrade Shop  (UP/DOWN + ENTER to buy):",       _Y),
            ("  Extra HP       (+3 max health)          10 coins", _G),
            ("  Extra Ammo     (+10 per weapon)          8 coins", _G),
            ("  Power Up       (+1 bullet damage)       15 coins", _G),
            ("  Extra Grenade  (+1 max grenade slot)    12 coins", _G),
            ("  Body Armor     (-1 damage taken)        15 coins", _G),
            ("  Extra Jump     (+1 air jump)            12 coins", _G),
            ("  Speed Boost    (+25% movement speed)   14 coins", _G),
            ("  Shield Charge  (2 shields per level)   14 coins", _G),
            "",
            ("Then choose your next challenge:",               _Y),
            ("  [R]  Speedrun levels 1-7 — 4-minute limit",   _B),
            ("  [N]  Continue to levels 8-14 — harder run",   _O),
        ],
    },

    # ── 9. Accounts, Pause & Sound ───────────────────────────────────────────
    {
        "title": "Accounts, Pause & Sound",
        "lines": [
            ("At startup you choose how to play:",             _Y),
            ("  [G]  Guest  — progress saved to save.json",   _W),
            ("  [S]  Sign In — create an account",            _B),
            ("  [L]  Log In  — load an existing account",     _B),
            ("Accounts remember your coins, upgrades",         _W),
            ("and lobby progress across sessions.",            _W),
            "",
            ("Pause:  press  P  or  ESC  during gameplay.",   _Y),
            ("The pause screen shows your account name.",     _W),
            "",
            ("Music:",                                         _Y),
            ("  Action music loops during gameplay",          _W),
            ("  Calm ambient music plays in the lobby",       _W),
            ("Sound effects play for:",                       _Y),
            ("  Jumping, shooting, grenades, explosions",     _W),
            ("  Enemy hits & deaths, pickups, portal open",   _W),
            ("  Level complete, coins, game over",            _W),
        ],
    },

    {
        "title": "HUD & Tips",
        "lines": [
            ("Top-left HUD:",                                     _Y),
            ("  Health bar + HP  |  Weapon  |  Ammo",            _W),
            ("  Grenades          |  Active buffs (yellow)",      _W),
            ("Top-right HUD:",                                    _Y),
            ("  Level number  |  Character name  |  Power",      _W),
            "",
            ("Tips:",                                             _Y),
            ("  • Stay mobile — standing still gets you shot.",  _W),
            ("  • Use grenades on clustered enemies.",           _W),
            ("  • Grab biome items before fighting bosses.",     _W),
            ("  • On ice levels — use short taps to control",   _W),
            ("    your slide direction.",                         _W),
            ("  • Falling off the screen is instant death.",     _R),
            "",
            ("Good luck, Commander!",                            _G),
        ],
    },
]


class TutorialScreen:
    def __init__(self):
        self.page = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return True              # skip entire tutorial
            elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self.page += 1
                if self.page >= len(PAGES):
                    return True          # signal: tutorial done
            elif event.key == pygame.K_BACKSPACE and self.page > 0:
                self.page -= 1
        elif event.type == pygame.QUIT:
            return "quit"
        return False

    def draw(self, surface):
        # Dark background
        surface.fill((10, 12, 22))

        title_font = pygame.font.Font(FONT_NAME, 30)
        body_font  = pygame.font.Font(FONT_NAME, 17)
        hint_font  = pygame.font.Font(FONT_NAME, 15)

        page_data = PAGES[self.page]

        # Title bar
        title_surf = title_font.render(page_data["title"], True, (255, 220, 60))
        tx = SCREEN_WIDTH // 2 - title_surf.get_width() // 2
        surface.blit(title_surf, (tx, 30))
        pygame.draw.line(surface, (255, 220, 60), (40, 72), (SCREEN_WIDTH - 40, 72), 1)

        # Body lines
        y = 90
        for line in page_data["lines"]:
            if line == "":
                y += 10
                continue
            if isinstance(line, tuple):
                text, color = line
            else:
                text, color = line, _W
            surf = body_font.render(text, True, color)
            surface.blit(surf, (55, y))
            y += 26

        # Navigation hints
        nav = "BACKSPACE — back    |    SPACE / ENTER — next    |    ESC — skip tutorial"
        nav_surf = hint_font.render(nav, True, (140, 140, 160))
        surface.blit(nav_surf,
                     (SCREEN_WIDTH // 2 - nav_surf.get_width() // 2,
                      SCREEN_HEIGHT - 36))

        # Page counter
        counter = f"{self.page + 1} / {len(PAGES)}"
        c_surf = hint_font.render(counter, True, (140, 140, 160))
        surface.blit(c_surf, (SCREEN_WIDTH - c_surf.get_width() - 20,
                               SCREEN_HEIGHT - 36))
