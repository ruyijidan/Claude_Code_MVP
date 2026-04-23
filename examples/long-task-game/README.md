# Void Breaker

Neon-themed breakout game built with vanilla HTML/CSS/JS. Zero dependencies,
no build step, no server — directly playable by opening `index.html` from the
filesystem (`file://` works).

## Play

Open `examples/long-task-game/index.html` in any modern browser
(Chromium, Firefox, Safari). Click START or press <kbd>Space</kbd>.

## Controls

| Input | Action |
|-------|--------|
| <kbd>←</kbd> <kbd>→</kbd> / <kbd>A</kbd> <kbd>D</kbd> | Move paddle |
| <kbd>Space</kbd> / <kbd>Enter</kbd> | Start · Resume from pause · Retry on game over |
| <kbd>P</kbd> / <kbd>Esc</kbd> | Pause / Resume |
| <kbd>M</kbd> | Toggle sound |
| <kbd>H</kbd> | Show help (auto-pauses an active game) |
| Mouse drag | Move paddle (anywhere on canvas) |
| Touch drag | Move paddle (canvas or the touch strip below) |
| Tap screen | Start game on the title / game-over screen |
| On-screen buttons | ⏸ Pause · 🔊 Sound · ? Help |

## Features

### Mission Select & Modifiers (new)

On the start screen, choose a difficulty and toggle modifiers before launching:

- **Difficulty**: Easy (5 lives, 0.75× speed), Normal (3 lives, 1× speed), Hard (2 lives, 1.3× speed)
- **Modifiers** (toggle on/off):
  - **BIG PAD** — start with a 50% wider paddle
  - **2-BALL** — launch two balls simultaneously
  - **NO PWR** — disable all power-up drops
- **Power-Up Legend** — a 2×2 grid on the start screen previews all four power-up types with icons, names, and effect descriptions

### Power-Up System (new)

Destroyed bricks have a 15% chance to drop a glowing power-up capsule. Catch it
with the paddle to activate:

| Icon | Name | Effect |
|------|------|--------|
| ↔ | WIDE | Paddle becomes 50% wider for 8 seconds |
| ⏳ | SLOW | Ball speed reduced to 65% for 6 seconds |
| ⚫ | MULTI | Spawns an extra ball |
| ❤ | +LIFE | Gain one extra life (max 9) |

Active timed power-ups appear as glowing pills in the bottom status strip with
a countdown. Pills blink when about to expire.

### In-Game Status Strip (new)

A bottom-of-arena HUD shows:

- **Level progress bar** — percentage of bricks cleared on the current level
- **Active effect pills** — icons + countdown for timed buffs (WIDE, SLOW)
- **Active modifier badges** — shows BIG PAD, 2-BALL, NO PWR for each active modifier with amber glow

### Results Screen (new)

On game over or win, a detailed results screen appears instead of the old
simple overlay:

- **Difficulty + modifiers** shown below the title (e.g. "HARD + 2-BALL, NO PWR")
- **Title badge** — NEW RECORD, ALL CLEAR, or current level reached
- **Stats grid** — Score, Best, Bricks destroyed, Max combo, Power-ups
  collected, Time played
- **Per-level score chart** — colored bar chart showing score earned in each level
- **PLAY AGAIN** button returns to the mission select screen

### Core Features

- **5 levels** with varied brick layouts (some bricks take 2 or 3 hits, shown by saturation)
- **Combo system** — chain brick hits without touching the paddle for a score multiplier
- **High score** persisted in `localStorage` (`voidBreaker.highScore`)
- **Sound preference** persisted in `localStorage` (`voidBreaker.sound`)
- **Web Audio sound effects** for paddle, brick, wall, miss, level-up, win, power-up collect
- **Pause / resume** with auto-pause when the tab loses visibility
- **Visual feedback** — particles, ball trail, brick hit flash, screen shake on life loss
- **Frame-rate independent** physics with sub-stepped collision to avoid tunneling at high speed
- **Accessibility** — `prefers-reduced-motion` respected, focus-visible styles,
  ARIA labels and `aria-keyshortcuts` on control buttons
- **Mobile-first** — DPR-aware canvas, unified pointer events, dedicated touch strip below the
  arena on small screens (≤ 600 px wide)

## Rules

- Bounce the ball off the paddle to break all bricks
- Bricks have 1–3 hit points (shown by saturation / opacity)
- Lives depend on difficulty (2–5), 5 levels to clear
- Score = `base × level × combo` — higher combos = bigger rewards
  - Brick crack: `25 × level × combo`
  - Brick destroy: `100 × level × combo`
- Ball speed scales per level and difficulty setting, capped at `SPEED_CAP`
- New records are highlighted on the results screen with a gold badge

## Files

- `index.html` — page structure, HUD, mission select, status strip, results screen, overlay
- `styles.css` — neon dark theme, responsive layout, reduced-motion support
- `game.js` — game logic, rendering, input, audio, power-ups, persistence (single-file, no modules)
- `README.md` — this file

## QA Checklist

Quick smoke tests after any change:

- [ ] Open `index.html` directly via `file://` — game loads and shows START overlay with mission select panel
- [ ] Difficulty buttons (EASY / NORMAL / HARD) are visible and selectable with speed descriptions
- [ ] Modifier buttons (BIG PAD / 2-BALL / NO PWR) toggle on and off
- [ ] Power-up legend shows all 4 power-up types with icons and effect descriptions
- [ ] Press <kbd>Space</kbd> → ball launches; paddle responds to <kbd>←</kbd> / <kbd>→</kbd>
- [ ] Break bricks → glowing power-up capsules occasionally fall
- [ ] Catch a power-up → effect pill appears in bottom status strip with countdown
- [ ] Level progress bar fills as bricks are destroyed
- [ ] Press <kbd>P</kbd> → "PAUSED" overlay appears; press <kbd>P</kbd> again → resume
- [ ] Press <kbd>H</kbd> mid-play → HELP overlay appears, ball is paused
- [ ] Press <kbd>M</kbd> → 🔊 toggles to 🔇; reload page → preference persists
- [ ] Lose all lives → detailed results screen with difficulty label, stats, and per-level chart
- [ ] Beat all 5 levels → results screen with "YOU WIN!" and "ALL CLEAR" badge
- [ ] Results screen shows active modifiers next to difficulty (e.g. "HARD + 2-BALL")
- [ ] Select HARD difficulty → only 2 lives, ball noticeably faster
- [ ] Enable 2-BALL modifier → two balls launch at start
- [ ] Enable NO PWR → no power-ups drop from bricks
- [ ] Switch tab → game auto-pauses
- [ ] Resize the window → canvas stays crisp (DPR aware), paddle re-clamps
- [ ] On a touch device or DevTools touch emulation: drag in the canvas or in the
      bottom touch strip → paddle follows
- [ ] With `prefers-reduced-motion: reduce` enabled → no shake, reduced particles

## Storage

The game writes only two `localStorage` keys, both scoped with the
`voidBreaker.` prefix. To reset: open DevTools → Application → Local Storage →
remove `voidBreaker.highScore` and `voidBreaker.sound`.

## Browser Support

Targets evergreen browsers with support for:

- Pointer Events
- Web Audio API (degrades silently if unavailable or blocked)
- `localStorage` (degrades silently in privacy modes)
- Canvas 2D with `setTransform` for HiDPI scaling
