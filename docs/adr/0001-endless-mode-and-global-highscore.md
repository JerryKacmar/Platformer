# ADR-0001: Endless Mode (Procedural Levels) and Global High Score

**Date:** 2026-06-07
**Status:** Accepted

## Context
The campaign ended at level 14 with a dead-end victory screen, giving players no reason to keep playing once they finished. We wanted (a) endless replayability after the campaign and (b) a way to track and compare how far players get.

Two design questions had to be resolved:
1. How to generate unlimited levels that are varied yet always completable.
2. How to scope the high score — per-user vs. a single shared record.

## Options Considered

### Procedural level generation
- **Option A — Tiered-zone random placement (chosen):** Place platforms in three fixed, vertically-tiered height zones (low/mid/high) with gaps ≤130px, the player's max jump height. Reachability is guaranteed structurally without a pathfinding/reachability check.
- **Option B — Fully random platforms + reachability graph:** Place platforms anywhere, then verify reachability with a graph search and regenerate on failure. More organic layouts, but much more code and a risk of slow/failed generation.

### High score scope
- **Option A — Global, user-attributed record (chosen):** One shared record of the farthest level any signed-in user reached, stored in its own `highscore.json`. Guests excluded (no identity to attribute).
- **Option B — Per-user best level:** Store `best_level` in each account's save. Simpler social comparison is lost; also wiped by the existing guest-save reset.

## Decision
We chose **Option A** for both.

Procedural generation lives in `levels/procedural.py` as `generate_level(difficulty, biome)`, returning the same dict shape as `LEVEL_DEFINITIONS`, so the existing `Level` class consumes it unchanged (with a new `biome_override` parameter to decouple biome from level number). Difficulty scales enemy count (4→12 cap) and composition (basics → shooters → minibosses → bosses).

The high score is global and user-attributed, stored in a dedicated `highscore.json` via `load_highscore()` / `submit_highscore()` in `auth.py`. It is recorded at portal-touch in the main update loop and displayed on the title, lobby, and end screens.

## Consequences
- **Easier:** Infinite content with one small, dependency-free module; layouts are always completable by construction; the record survives the guest-save reset because it is a separate file.
- **Harder/limited:** Layouts are somewhat formulaic (three tiers) rather than organic. Guests cannot set the record by design. The global record is a single entry, not a multi-row leaderboard.
- **Watch out for:** `biome_override` must be passed for endless levels (level number is fixed at 14 internally while the displayed number is `15 + procedural_count`); enemy y-placement assumes the ground top at y=580 and the enemy heights in `_ENEMY_HEIGHTS`, which must stay in sync with `entities/enemy.py`.
