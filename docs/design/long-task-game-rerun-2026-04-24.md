---
last_updated: 2026-04-24
status: active
owner: core
---

# Long Task Game Rerun 2026-04-24 / 长任务小游戏续跑记录

## Summary / 摘要

This rerun adds a **new** standalone browser mini-game at
`examples/long-task-game-2026-04-24`.

It does **not** modify or overwrite:

- `examples/long-task-game`
- `examples/web-game`

The new artifact is `Starforge Relay`, a dependency-free vanilla
HTML/CSS/JS top-down arcade courier game that opens directly from
`index.html` via `file://`.

## Product Direction / 产物方向

The goal of this rerun was to produce something clearly different from the
existing breakout-style artifact while still feeling like a polished product
demo rather than a placeholder.

Chosen direction:

- top-down arcade + light strategy loop instead of brick-breaking
- strong sci-fi recovery theme with a central relay objective
- visible sector progression and upgrade drafting between rounds
- immediate first-open polish through a title presentation, layered HUD, and
  finished results flow

## Core Gameplay / 核心玩法

`Starforge Relay` is built around a simple but readable loop:

- move through the arena to collect energy cells
- bank collected cells into the central relay ring
- avoid or pulse back hostile drones
- meet the charge target for the current sector
- choose one permanent upgrade before the next sector begins

The run ends either when:

- sector 5 is cleared, or
- player integrity reaches zero

## User-Visible Systems / 用户可见系统

- **Title Screen**: product-style introduction, control hints, and feature cards
- **In-Game HUD**: sector target, relay charge, hull meter, score, cargo, chain, pulse cooldown, and installed upgrades
- **Upgrade Draft**: one-of-three permanent upgrade selection between sectors
- **Results Screen**: score, best score, sector reached, deliveries, pulse usage, and upgrade count
- **Persistence**: best score and sound preference stored in local storage when available

## Files / 文件

- [`../../examples/long-task-game-2026-04-24/index.html`](../../examples/long-task-game-2026-04-24/index.html)
- [`../../examples/long-task-game-2026-04-24/styles.css`](../../examples/long-task-game-2026-04-24/styles.css)
- [`../../examples/long-task-game-2026-04-24/game.js`](../../examples/long-task-game-2026-04-24/game.js)
- [`../../examples/long-task-game-2026-04-24/README.md`](../../examples/long-task-game-2026-04-24/README.md)

## Verification / 验证

Lightweight local verification target:

```bash
node --check examples/long-task-game-2026-04-24/game.js
```

Expected acceptance properties:

- the new game opens directly from `file://`
- `index.html` references only local `./styles.css` and `./game.js`
- no external URLs, package installs, build step, or server are required
- `examples/long-task-game` remains untouched
- `examples/web-game` remains untouched
- the new artifact is visibly different from the existing breakout-style game

## Rerun Outcome / 续跑结果

This rerun preserves previous long-task results exactly as prior artifacts while
adding a fresh product-style output for `2026-04-24`.
