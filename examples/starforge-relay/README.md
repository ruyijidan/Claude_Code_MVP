# Starforge Relay / 星炉中继

Free-moving neon survival game built with vanilla HTML/CSS/JS. No build step,
no backend, and it is playable directly from `file://`.

## Play

Open `examples/starforge-relay/index.html` in a browser and press **Start**.

## Controls

| Input | Action |
|-------|--------|
| <kbd>W</kbd> <kbd>A</kbd> <kbd>S</kbd> <kbd>D</kbd> / Arrow keys | Move the ship |
| <kbd>Space</kbd> | Dash |
| <kbd>E</kbd> | Pulse |
| <kbd>P</kbd> / <kbd>Esc</kbd> | Pause / resume |
| Drag or touch on the arena | Steer the ship |
| On-screen buttons | Dash, Pulse, Pause |

## Loop

- Survive enemy waves and collect relay shards to fill the charge bar.
- When the charge target is reached, the game auto-selects a permanent module
  from the current draft. You can still press `1 / 2 / 3` quickly if you want to
  override the default pick.
- Keep stacking modules to improve speed, fire rate, pulse power, and survival.
- In `MARATHON`, the wave pressure keeps rising with no fixed cap.

## Features

- Two run modes: `CLASSIC` and `MARATHON`
- Three difficulty settings: `CALM`, `STANDARD`, `STORM`
- Auto-targeting shots
- Dash and pulse abilities
- Permanent modules between waves
- Persistent best score
- Canvas-only rendering with responsive resizing and touch steering

## Files

- `index.html` - layout, HUD, overlay, upgrade draft, controls
- `styles.css` - presentation, responsive layout, and visual language
- `game.js` - all game logic, rendering, upgrades, and persistence

## Smoke Checks

- Open the HTML file directly with `file://`
- Start a run from the menu
- Move with keyboard or drag/touch
- Use dash and pulse
- Finish a wave and watch the draft auto-resolve, or override it with `1 / 2 / 3`
- Lose all health and see the results screen
- Reload the page and verify best score persistence
