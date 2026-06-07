"""Procedural level generation for Endless Mode (levels 15+).

`generate_level(difficulty, biome)` returns a plain dict in the same format as
the entries in `levels/level_data.py` (LEVEL_DEFINITIONS):

    {
        "platforms": [(x, y, w, h), ...],
        "enemies":   [(kind, x, y), ...],   # kind: basic/shooter/miniboss/boss
        "pickups":   [(weapon, x, y), ...],
        "portal":    (x, y),
    }

`Level.__init__` (main.py) converts these tuples to pygame.Rect / sprites, so no
pygame import is needed here.

Difficulty starts at 0 on the first endless level (displayed as level 15) and
rises by 1 each level. Biome is 0-13, selecting one of the existing themes.
"""

import random

# Enemy collision heights (must match entities/enemy.py); enemy_y = platform_top - height
_ENEMY_HEIGHTS = {"basic": 46, "shooter": 48, "miniboss": 70, "boss": 100}

_WEAPONS = ["pistol", "blaster", "rifle", "shotgun"]

_GROUND = (0, 580, 1024, 60)   # always present; ground top = y 580


def _generate_platforms(rng, difficulty):
    """Three tiered, reachable height zones plus the ground.

    Player max jump height is ~140px (JUMP_SPEED=-15, GRAVITY=0.8), so each tier
    sits within ~130px of the one below, guaranteeing reachability.
    """
    platforms = [_GROUND]

    # (y_min, y_max, x_left, x_right, min_count, max_count)
    zone_specs = [
        (460, 510,  60, 400, 1, 2),   # low-left   (gap from ground top 580 → 70-120px)
        (360, 440, 250, 770, 1, 2),   # mid-center (gap from low → ~100px)
        (250, 340, 550, 970, 1, 2),   # high-right (gap from mid → ~110px)
        (460, 510, 550, 970, 1, 1),   # low-right  (portal access)
    ]

    for y_min, y_max, x_left, x_right, min_c, max_c in zone_specs:
        count = rng.randint(min_c, max_c)
        placed, attempts = 0, 0
        while placed < count and attempts < 30:
            attempts += 1
            w = rng.randint(80, 200)
            x = rng.randint(x_left, max(x_left + 1, x_right - w))
            y = rng.randint(y_min, y_max)
            # Reject heavy overlap with existing elevated platforms.
            overlaps = any(
                abs(ex - x) < w - 30 and abs(ey - y) < 60
                for ex, ey, ew, eh in platforms[1:]
            )
            if not overlaps:
                platforms.append((x, y, w, 20))
                placed += 1

    return platforms


def _enemy_counts(difficulty):
    """Return (bosses, minibosses, shooters, basics) totalling <= total cap."""
    total      = min(4 + difficulty, 12)
    bosses     = min(max(0, (difficulty - 1) // 4), 2)
    minibosses = min(1 + difficulty // 2, 4)
    shooters   = min(2 + difficulty // 2, 4)
    basics     = total - bosses - minibosses - shooters

    if basics < 0:
        # Over-allocated: trim from basics (already <0 → 0), then shooters.
        excess = -basics
        basics = 0
        shooters = max(0, shooters - excess)

    return bosses, minibosses, shooters, basics


def _generate_enemies(rng, platforms, difficulty):
    bosses, minibosses, shooters, basics = _enemy_counts(difficulty)
    queue = (["boss"] * bosses + ["miniboss"] * minibosses +
             ["shooter"] * shooters + ["basic"] * basics)
    rng.shuffle(queue)

    elevated = [p for p in platforms if p[1] < 560]
    enemies = []

    for kind in queue:
        h = _ENEMY_HEIGHTS[kind]
        # Big enemies prefer platforms wide enough to stand on; small ones 50/50.
        candidates = [p for p in elevated if p[2] >= h + 20]
        use_platform = bool(candidates) and (kind in ("boss", "miniboss") or rng.random() < 0.5)
        if use_platform:
            px, py, pw, ph = rng.choice(candidates)
            ex = rng.randint(px + 10, px + pw - 10)
            ey = py - h
        else:
            ex = rng.randint(80, 940)
            ey = 580 - h   # stand on the ground (ground top = 580)
        enemies.append((kind, ex, ey))

    return enemies


def _generate_pickups(rng, platforms):
    elevated = [p for p in platforms if p[1] < 560 and p[2] >= 60]
    if not elevated:
        return []
    count = rng.randint(2, 3)
    chosen = rng.sample(elevated, min(count, len(elevated)))
    pickups = []
    for px, py, pw, ph in chosen:
        wx = rng.randint(px + 15, px + pw - 15)
        wy = py - 30
        pickups.append((rng.choice(_WEAPONS), wx, wy))
    return pickups


def _generate_portal(platforms):
    # Prefer the highest platform on the right side; portal is 50x60.
    right_high = [p for p in platforms if p[0] + p[2] > 700 and p[1] < 400]
    if right_high:
        right_high.sort(key=lambda p: p[1])   # smallest y = highest
        px, py, pw, ph = right_high[0]
        return (px + pw - 55, max(60, py - 60))
    return (950, 520)   # fallback: ground-level right side


def generate_level(difficulty: int, biome: int) -> dict:
    """Generate a random level definition dict.

    Args:
        difficulty: 0 = first endless level, increases each level.
        biome: 0-13, selects the biome (drives hazards/background in Level).

    Returns:
        dict with keys "platforms", "enemies", "pickups", "portal".
    """
    seed = difficulty * 1000 + biome * 37 + random.randint(0, 999)
    rng = random.Random(seed)

    platforms = _generate_platforms(rng, difficulty)
    return {
        "platforms": platforms,
        "enemies":   _generate_enemies(rng, platforms, difficulty),
        "pickups":   _generate_pickups(rng, platforms),
        "portal":    _generate_portal(platforms),
    }
