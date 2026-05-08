# Halo Drift / 环轨漂移

`Halo Drift` is a standalone browser mini-game built with vanilla HTML/CSS/JS.
It runs directly from `index.html` with no build step and no external assets.

## What It Is

You control a small orbital runner circling a glowing core. Rotate around the
ring, shift between orbit lanes, collect bright motes, and pulse to clear out
void hazards before they hit your hull. The new marathon run mode adds
permanent upgrade drafts between phases so the game can keep evolving over a
long session instead of ending after a short burst.

## Play

Open `examples/halo-drift/index.html` in a modern browser. The game works from
`file://` and does not require a server.

## Controls

| Input | Action |
|-------|--------|
| <kbd>←</kbd> <kbd>→</kbd> / <kbd>A</kbd> <kbd>D</kbd> | Rotate around the core |
| <kbd>↑</kbd> <kbd>↓</kbd> / <kbd>W</kbd> <kbd>S</kbd> | Move to inner / outer ring |
| <kbd>Space</kbd> | Pulse to clear nearby hazards |
| <kbd>P</kbd> | Pause / resume |
| <kbd>1</kbd> <kbd>2</kbd> <kbd>3</kbd> | Pick an upgrade during marathon drafts |
| On-screen buttons | Touch controls for rotation, orbit shifts, and pulse |

## Features

- Four orbital lanes with a responsive ring layout
- Three difficulty modes: CALM, STANDARD, and STORM
- Classic and marathon run modes
- Charge-based phase progression with a permanent upgrade draft in marathon
  mode
- A visible session timer for long-run validation
- Marathon surge phases every few stages
- Keyboard shortcut upgrade selection with 1/2/3
- Combo scoring for back-to-back mote collection
- Local high score persisted in `localStorage` as `haloDrift.bestScore`
- Pause handling plus tab visibility auto-pause
- Canvas rendering with a luminous core, pulses, motes, hazards, and bursts
- Mobile-friendly touch buttons and responsive layout

## Quick Checks

- [ ] Open `index.html` directly via `file://`
- [ ] Choose a difficulty mode and press `Start game`
- [ ] Rotate with arrow keys or A/D
- [ ] Change rings with arrow keys or W/S
- [ ] Press Space to pulse nearby hazards
- [ ] Collect motes to fill the charge bar
- [ ] Reach the next phase banner
- [ ] In marathon mode, clear a phase and choose one of three upgrade cards
- [ ] In marathon mode, watch the session timer continue while the run evolves
- [ ] Lose all health and see the results overlay
- [ ] Reload the page and confirm the best score persists

## Files

- `index.html` - page shell, HUD, overlay, and touch controls
- `styles.css` - cosmic layout and responsive presentation
- `game.js` - game loop, orbit logic, hazards, score, and persistence
