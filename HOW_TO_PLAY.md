# Python Platformer Adventure

A 2D platformer game built with Pygame where you defeat enemies, collect weapons, and advance through 5 progressively harder levels.

## How to Play

### Controls

- **Arrow Keys** or **A/D**: Move left and right
- **Up Arrow**, **W**, or **Space**: Jump
- **Z**: Shoot your weapon
- **G**: Throw a grenade
- **P** or **ESC**: Pause / resume
- **R**: Restart (when game over or victory)
- **C**: Continue into Endless Mode (on the final victory screen)

### Objective

Each level requires you to:
1. **Defeat all enemies** on the map
2. **Collect weapon pickups** (light blue boxes) to upgrade your firepower
3. **Reach the portal** that appears after all enemies are defeated
4. **Advance to the next level**

### Enemies

The game features different enemy types with distinct attack patterns:

#### **Basic Enemy** (Red)
- Patrols back and forth
- Occasionally shoots at you
- Easy target for beginners
- Health: 6 points

#### **Shooter Enemy** (Purple)
- Constantly shoots projectiles
- Stays in place while shooting
- Requires dodging
- Health: 8 points

#### **Mini-Boss** (Orange)
- Appears once per level (except the last)
- Stronger and faster
- Uses a combination of patrol, spread fire, and dash attacks
- Health: 18 points

#### **Final Boss** (Dark Red)
- Appears only on Level 5
- Most powerful enemy type
- Uses all attack types: shooting, spread fire, dashing, and resting
- Health: 45 points

### Attack Patterns

Each enemy type cycles through a fixed sequence of attacks. Understanding the pattern helps you plan your moves:

- **Patrol**: Enemy moves side to side (safe time to attack)
- **Shoot**: Enemy fires projectiles at you (dodge and counterattack)
- **Dash**: Enemy moves quickly across the screen (avoid contact)
- **Spread**: Enemy fires projectiles in multiple directions (take cover behind platforms)
- **Rest**: Enemy pauses (perfect time to attack)

### Weapons

#### **Pistol**
- Default weapon
- Fire rate: 16 frames between shots
- Damage: 1 point per bullet
- Speed: Normal

#### **Blaster**
- Upgraded weapon (find in levels)
- Fire rate: 26 frames between shots
- Damage: 2 points per bullet
- Speed: Faster than pistol

### Health System

- **Starting Health**: 12 points
- **Health Indicator**: Displayed in the top-left corner (red bar)
- **Enemy Damage**: 1-2 points per hit (depends on enemy type)
- **Game Over**: When health reaches 0

### Level Progression

| Level | Difficulty | Enemies | Mini-Boss | Challenge |
|-------|-----------|---------|-----------|-----------|
| 1 | Beginner | 3 | Yes | Introduction to enemies and controls |
| 2 | Easy | 4 | Yes | More enemies, tighter platforming |
| 3 | Medium | 5 | Yes | Complex level layout |
| 4 | Hard | 5 | Yes | Difficult platform navigation |
| 5 | Expert | 5 | Yes (Boss) | Final boss encounter |

### Gameplay Tips

1. **Learn Enemy Patterns**: Each enemy has a predictable attack cycle. Watch and wait for safe moments.

2. **Use Platforms**: Platforms are your friends—jump to higher areas to avoid fire and position yourself for attacks.

3. **Don't Panic**: Enemy projectiles are slow. Keep moving and dodging rather than standing still.

4. **Weapon Upgrades**: Always grab the Blaster upgrade when you find it. The increased damage helps significantly.

5. **Health Management**: Avoid taking unnecessary damage. It's better to spend time dodging than healing later (you can't heal—only prevent damage).

6. **Multitask**: While dodging, look for opportunities to return fire. Offense and defense go hand in hand.

7. **Portal Puzzle**: The portal doesn't appear until ALL enemies are defeated. Make sure you've cleared the level before searching for it.

## Endless Mode (Levels 15+)

After you clear all 14 campaign levels, the victory screen offers **Press C to continue in Endless Mode**. Endless Mode generates an unlimited series of procedurally created levels:

- **Random biome** each level (any of the 14 existing themes, with its hazards and background)
- **Random platform layout** — three tiered, jump-reachable height zones
- **Random enemies** — composition scales with difficulty (more enemies, then minibosses, then bosses)
- **Random weapon pickups** placed on the platforms

Difficulty rises every level: enemy count grows from 4 up to a cap of 12, and the mix shifts toward minibosses and (eventually) bosses. You play as **Apex**, the strongest character, for the whole endless run. Levels are numbered 15, 16, 17, … and shown as `Level N (Endless)`.

## High Score (Farthest Level)

The game tracks a single **global record**: the farthest level any **signed-in** account has cleared, attributed to that user (e.g. `Record: Level 22 by Alice`). It is shown on the title screen, the lobby, and the game over / victory screens.

- Only signed-in users can set the record (play via **Sign In** / **Log In**, not Guest).
- The record is stored in `highscore.json` and persists across restarts and a full reset — it is independent of any single account's save data.

## Running the Game

### Requirements
- Python 3.10+
- Pygame 2.1+

### Installation

1. Navigate to the game directory:
   ```bash
   cd "c:\Users\jaros\Downloads\AI\Game1"
   ```

2. (If not already installed) Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the game:
   ```bash
   python main.py
   ```

The game will start with a tutorial screen explaining all the controls and mechanics.

## Game Structure

```
Game1/
├── main.py                 # Main game loop
├── tutorial.py             # Tutorial screen
├── settings.py             # Game constants and configuration
├── assets.py               # Asset loading utilities
├── requirements.txt        # Python dependencies
├── entities/
│   ├── player.py           # Player class
│   ├── enemy.py            # Enemy classes
│   ├── projectile.py       # Bullet class
│   └── pickup.py           # Weapon pickup class
├── levels/
│   └── level_data.py       # Level definitions
└── assets/                 # Sprite images (PNG files)
    ├── hero.png
    ├── enemy_robot.png
    ├── enemy_human.png
    ├── enemy_monster.png
    ├── weapon_blaster.png
    └── portal.png
```

## Future Enhancements

- Custom sprite artwork to replace placeholders
- Sound effects and background music
- Additional weapon types
- Secret collectibles
- Difficulty settings

## Troubleshooting

**Game won't run**: Make sure Pygame is installed (`pip install pygame`)

**Characters appear as solid blocks**: This is normal—placeholder graphics are used. They work perfectly fine!

**Game is too easy/hard**: Try restarting with improved strategy. Learn enemy patterns and use platforms effectively.

**Controls feel unresponsive**: The game runs at 60 FPS. Ensure you're running it with a compatible Python version.

---

Good luck, and have fun clearing all 5 levels!
