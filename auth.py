import hashlib
import json
import os
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_NAME

ACCOUNTS_PATH = os.path.join(os.path.dirname(__file__), "accounts.json")

# ── Helpers ───────────────────────────────────────────────────────────────────

def _hash(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def load_accounts():
    try:
        with open(ACCOUNTS_PATH) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}

def save_accounts(accounts):
    with open(ACCOUNTS_PATH, "w") as f:
        json.dump(accounts, f, indent=2)

def load_user_save(username):
    """Return the save-dict for a user, or {} if none."""
    return load_accounts().get(username, {}).get("save", {})

def write_user_save(username, save_data):
    """Persist save_data under accounts[username]['save']."""
    accounts = load_accounts()
    if username in accounts:
        accounts[username]["save"] = save_data
        save_accounts(accounts)

# ── Auth screen ───────────────────────────────────────────────────────────────

_W  = (235, 235, 235)
_Y  = (255, 220,  55)
_G  = ( 80, 210, 110)
_B  = (100, 180, 255)
_P  = (180, 100, 255)
_R  = (255,  90,  90)
_D  = (110, 110, 135)


class AuthScreen:
    """Shown before the tutorial.  Returns via handle_event:
        ("guest",  None)         — play without account
        ("user",   username)     — signed-in or logged-in
    """

    def __init__(self):
        self._mode    = "choose"   # "choose" | "signin" | "login"
        self.username = ""
        self.password = ""
        self._field   = "username"
        self._msg     = ""
        self._msg_t   = 0

    # ── event handling ────────────────────────────────────────────────────────

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None

        if self._mode == "choose":
            if event.key == pygame.K_g:
                return ("guest", None)
            elif event.key == pygame.K_s:
                self._mode = "signin"
                self._reset_fields()
            elif event.key == pygame.K_l:
                self._mode = "login"
                self._reset_fields()

        else:  # signin or login
            if event.key == pygame.K_ESCAPE:
                self._mode = "choose"
            elif event.key == pygame.K_TAB:
                self._field = "password" if self._field == "username" else "username"
            elif event.key == pygame.K_RETURN:
                if self._field == "username":
                    self._field = "password"
                else:
                    return self._submit()
            elif event.key == pygame.K_BACKSPACE:
                if self._field == "username":
                    self.username = self.username[:-1]
                else:
                    self.password = self.password[:-1]
            else:
                ch = event.unicode
                if ch and ch.isprintable():
                    if self._field == "username" and len(self.username) < 20:
                        self.username += ch
                    elif self._field == "password" and len(self.password) < 30:
                        self.password += ch
        return None

    def _reset_fields(self):
        self.username = self.password = ""
        self._field = "username"
        self._msg   = ""

    def _flash(self, msg):
        self._msg   = msg
        self._msg_t = 150

    def _submit(self):
        accounts = load_accounts()
        u, p = self.username.strip(), self.password

        if self._mode == "signin":
            if len(u) < 3:
                self._flash("Username must be at least 3 characters.")
                return None
            if len(p) < 4:
                self._flash("Password must be at least 4 characters.")
                return None
            if u in accounts:
                self._flash("Username already taken — try logging in.")
                return None
            accounts[u] = {"password_hash": _hash(p), "save": {}}
            save_accounts(accounts)
            return ("user", u)

        else:  # login
            if u not in accounts:
                self._flash("Account not found.")
                return None
            if accounts[u]["password_hash"] != _hash(p):
                self._flash("Wrong password.")
                return None
            return ("user", u)

    def update(self):
        if self._msg_t > 0:
            self._msg_t -= 1

    # ── drawing ───────────────────────────────────────────────────────────────

    def draw(self, surface):
        surface.fill((8, 10, 28))
        W, H = SCREEN_WIDTH, SCREEN_HEIGHT

        tf = pygame.font.Font(FONT_NAME, 34)
        hf = pygame.font.Font(FONT_NAME, 22)
        bf = pygame.font.Font(FONT_NAME, 18)
        sf = pygame.font.Font(FONT_NAME, 15)

        def ct(font, text, color, y):
            s = font.render(text, True, color)
            surface.blit(s, (W // 2 - s.get_width() // 2, y))

        ct(tf, "Python Platformer Adventure", _Y, 28)
        pygame.draw.line(surface, _Y, (40, 76), (W - 40, 76), 1)

        if self._mode == "choose":
            ct(hf, "Welcome!  Choose how to play:", _W, 108)

            bw, bh, gap = 260, 56, 30
            total = bw * 3 + gap * 2
            bx = (W - total) // 2

            def btn(x, label, hint, color):
                pygame.draw.rect(surface, (18, 20, 42), (x, 180, bw, bh), border_radius=8)
                pygame.draw.rect(surface, color,        (x, 180, bw, bh), 2, border_radius=8)
                s = bf.render(label, True, color)
                surface.blit(s, (x + bw // 2 - s.get_width() // 2, 194))
                sh = sf.render(hint, True, _D)
                surface.blit(sh, (x + bw // 2 - sh.get_width() // 2, 248))

            btn(bx,          "[G]  Guest",            "Local save only",              _G)
            btn(bx+bw+gap,   "[S]  Sign In  (new)",   "Create account — saves online", _B)
            btn(bx+2*(bw+gap),"[L]  Log In",           "Load existing account",        _P)

            ct(sf, "G — Guest      S — Sign In      L — Log In", _D, H - 38)

        else:
            label = "Create Account" if self._mode == "signin" else "Log In to Account"
            ct(hf, label, _W, 108)

            fw = 360
            fx = W // 2 - fw // 2

            def field(y, caption, value, active, secret=False):
                bc = _Y if active else _D
                pygame.draw.rect(surface, (18, 20, 42), (fx, y, fw, 44), border_radius=6)
                pygame.draw.rect(surface, bc,            (fx, y, fw, 44), 2, border_radius=6)
                disp = ("*" * len(value) if secret else value) + ("|" if active else "")
                s = bf.render(f"{caption}:  {disp}", True, bc)
                surface.blit(s, (fx + 12, y + 12))

            field(170, "Username", self.username, self._field == "username")
            field(228, "Password", self.password, self._field == "password", secret=True)

            sc = _G if self._mode == "signin" else _P
            pygame.draw.rect(surface, (18, 20, 42), (W//2-100, 292, 200, 44), border_radius=6)
            pygame.draw.rect(surface, sc,            (W//2-100, 292, 200, 44), 2, border_radius=6)
            ct(bf, "ENTER — Submit", sc, 304)

            if self._msg and self._msg_t > 0:
                ct(bf, self._msg, _R, 356)

            ct(sf, "TAB — switch field      ESC — back", _D, H - 38)
