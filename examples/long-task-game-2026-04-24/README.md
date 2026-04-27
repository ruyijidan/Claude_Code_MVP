# Starforge Relay

`Starforge Relay` is a brand-new browser mini-game created for the `2026-04-24`
600-second long-task rerun. It is a standalone dependency-free vanilla
HTML/CSS/JS artifact that opens directly from `index.html` over `file://`.

This rerun intentionally does **not** modify:

- `examples/long-task-game`
- `examples/web-game`

## Concept

Top-down arcade courier game with a strong “star-yard recovery” identity:

- collect luminous energy cells around the arena
- deliver them into the central relay ring
- dodge or pulse back hostile swarm drones
- clear 5 sectors with rising targets and pressure
- choose one permanent upgrade between sectors

## Run

Open `examples/long-task-game-2026-04-24/index.html` in a modern browser.

No build step, no server, no external assets, no network access.

## Controls

| Input | Action |
|---|---|
| `WASD` or arrow keys | Move |
| `Space` | Trigger pulse burst |
| `P` or `Esc` | Pause / resume |
| `M` | Toggle sound |
| `Enter` | Start from title screen |

## Features

- polished title screen with product-style presentation
- responsive single-page layout with a large canvas stage and side HUD
- visible progression system across 5 sectors
- between-sector upgrade draft with permanent run bonuses
- in-game HUD for sector target, hull integrity, score, cargo, combo, and pulse cooldown
- pause flow, results flow, restart flow, and persistent best score
- no dependencies, no modules, no bundler, no remote URLs

## Files

- `index.html` — structure, overlays, HUD, buttons
- `styles.css` — responsive presentation, visual system, polished panels
- `game.js` — rendering, input, progression, enemies, upgrades, audio, persistence
- `README.md` — controls, features, QA checklist

## QA Checklist

- [ ] Open `examples/long-task-game-2026-04-24/index.html` with `file://`
- [ ] Title screen appears with game name, feature cards, controls, and launch button
- [ ] `examples/long-task-game` remains unchanged
- [ ] `examples/web-game` remains unchanged
- [ ] Press `Enter` or click `Launch Relay Run` to start
- [ ] Move with `WASD` or arrow keys
- [ ] Collect floating cells and see cargo increase
- [ ] Enter the central relay ring with cargo and see sector charge increase
- [ ] Press `Space` to emit a pulse and knock back nearby enemies
- [ ] Reach the sector target and see the upgrade draft overlay
- [ ] Pick an upgrade and confirm the next sector starts
- [ ] Press `P` or `Esc` during play to pause and resume
- [ ] Lose all integrity and confirm the results screen appears
- [ ] Clear sector 5 and confirm the victory results screen appears
- [ ] Reload and confirm best score persists when local storage is available

## Lightweight Verification

Recommended local syntax check:

```bash
node --check examples/long-task-game-2026-04-24/game.js
```
