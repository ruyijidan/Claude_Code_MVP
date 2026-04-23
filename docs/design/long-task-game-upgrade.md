---
last_updated: 2026-04-23
status: active
owner: core
---

# Long Task Game Upgrade / 600 秒小游戏升级记录

## Summary / 摘要

`examples/long-task-game` is the browser mini-game artifact produced and refined
through delegated long-task runs. The final game is `Void Breaker`, a
dependency-free breakout-style arcade game that runs directly from
`examples/long-task-game/index.html`.

The latest visible-upgrade rerun focused on making the improvement obvious on
first open, not only hidden in implementation details.

## User-Visible Upgrades / 用户可见升级

- **Mission Select**: the start overlay now shows a clear `MISSION SELECT`
  section before the player starts.
- **Difficulty Choices**: players can choose `EASY`, `NORMAL`, or `HARD`,
  with visible lives and speed multipliers.
- **Modifiers**: players can toggle `BIG PAD`, `2-BALL`, and `NO PWR` before
  launching a run.
- **Power-Up Legend**: the start screen previews all four power-ups with icons
  and effects.
- **Power-Up Drops**: destroyed bricks can drop `WIDE`, `SLOW`, `MULTI`, or
  `+LIFE` capsules.
- **Status Strip**: the playfield shows level progress and active effect /
  modifier pills.
- **Results Screen**: win and loss states now show detailed stats, badges, and
  a per-level score chart instead of a simple message.

## Core Gameplay Upgrades / 核心玩法升级

- 5 levels with varied brick layouts.
- Combo scoring for chained brick hits.
- Local high score persistence through `localStorage`.
- Web Audio sound effects with a mute toggle.
- Pause / resume controls and auto-pause on tab hide.
- Keyboard, mouse, and touch controls.
- Frame-rate independent physics with sub-stepped collision checks.
- Reduced-motion support and ARIA labels for better accessibility.

## Files / 文件

- [`../../examples/long-task-game/index.html`](../../examples/long-task-game/index.html)
- [`../../examples/long-task-game/styles.css`](../../examples/long-task-game/styles.css)
- [`../../examples/long-task-game/game.js`](../../examples/long-task-game/game.js)
- [`../../examples/long-task-game/README.md`](../../examples/long-task-game/README.md)

## Verification / 验证

The final local checks should confirm:

```bash
node --check examples/long-task-game/game.js
```

Expected properties:

- `examples/long-task-game/index.html` opens directly through `file://`.
- `index.html` references only local `./styles.css` and `./game.js`.
- No external URL, build step, or server is required.
- `examples/web-game` remains untouched.
- The first screen visibly includes mission select, modifiers, power-up legend,
  status systems, and a results-screen path.

## Acceptance Notes / 验收备注

The latest rerun used delegated provider execution for more than 600 seconds of
effective provider time:

- visible-upgrade pass: about 405 seconds
- follow-up polish pass: about 284 seconds
- total effective provider time: about 689 seconds

The purpose of this run was not only to spend time, but to ensure the extra time
produced visible product-level differences that a user can notice immediately.
