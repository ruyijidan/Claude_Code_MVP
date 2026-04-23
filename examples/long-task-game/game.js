"use strict";

/* ══════════════════════════════════════════════════
   Void Breaker — Neon Breakout
   Pure vanilla JS, no dependencies.
   ══════════════════════════════════════════════════ */

// ── DOM refs ────────────────────────────────────
const canvas = document.getElementById("game-canvas");
const ctx = canvas.getContext("2d");
const arena = document.getElementById("arena");
const overlay = document.getElementById("overlay");
const overlayTitle = document.getElementById("overlay-title");
const overlayMsg = document.getElementById("overlay-msg");
const btnStart = document.getElementById("btn-start");
const btnPause = document.getElementById("btn-pause");
const btnSound = document.getElementById("btn-sound");
const btnHelp = document.getElementById("btn-help");
const scoreEl = document.getElementById("score");
const bestEl = document.getElementById("best");
const livesEl = document.getElementById("lives");
const levelEl = document.getElementById("level");
const touchZone = document.getElementById("touch-zone");
const comboBanner = document.getElementById("combo-banner");
const missionSelect = document.getElementById("mission-select");
const difficultyRow = document.getElementById("difficulty-row");
const modifierRow = document.getElementById("modifier-row");
const statusStrip = document.getElementById("status-strip");
const progressFill = document.getElementById("progress-fill");
const progressText = document.getElementById("progress-text");
const activeEffects = document.getElementById("active-effects");
const resultsScreen = document.getElementById("results-screen");
const resultsTitle = document.getElementById("results-title");
const resultsBadge = document.getElementById("results-badge");
const resultsStats = document.getElementById("results-stats");
const resultsChart = document.getElementById("results-chart");
const btnRetry = document.getElementById("btn-retry");

// ── Constants ───────────────────────────────────
const PADDLE_HEIGHT = 14;
const PADDLE_RADIUS = 7;
const BALL_RADIUS = 7;
const BRICK_PAD = 6;
const BRICK_TOP_OFFSET = 60;
const BRICK_HEIGHT = 18;
const BASE_SPEED = 320;
const SPEED_INCREMENT = 40;
const SPEED_CAP = 720;
const MIN_VERTICAL_ANGLE = 0.25;
const COMBO_WINDOW_MS = 1400;
const HIGH_SCORE_KEY = "voidBreaker.highScore";
const SOUND_PREF_KEY = "voidBreaker.sound";
const REDUCED_MOTION = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const PALETTE = [
  "#22d3ee", "#a855f7", "#f472b6", "#4ade80", "#fbbf24", "#60a5fa",
];

const CANVAS_FONT_STACK =
  '"SF Mono", "Cascadia Code", "Fira Code", "JetBrains Mono", monospace';

const LEVELS = [
  ["11111111", "11111111", "22222222", "22222222", "11111111"],
  [".111111.", "12222221", "12333321", "12222221", ".111111."],
  ["11.11.11", "22.22.22", "11222211", "22.22.22", "11.11.11"],
  ["33333333", "2.2.2.2.", ".2.2.2.2", "11111111", "11111111"],
  ["12321321", "21212121", "32132123", "21212121", "12321321"],
];

// ── Difficulty presets ──────────────────────────
const DIFFICULTIES = {
  easy:   { lives: 5, speedMul: 0.75, label: "EASY" },
  normal: { lives: 3, speedMul: 1.0,  label: "NORMAL" },
  hard:   { lives: 2, speedMul: 1.3,  label: "HARD" },
};

// ── Power-up definitions ────────────────────────
const POWERUP_TYPES = {
  wide:    { icon: "\u2194", color: "#22d3ee", label: "WIDE",  duration: 8000 },
  slow:    { icon: "\u23F3", color: "#4ade80", label: "SLOW",  duration: 6000 },
  multi:   { icon: "\u26AB", color: "#f472b6", label: "MULTI", duration: 0 },
  shield:  { icon: "\u2764", color: "#ef4444", label: "+LIFE", duration: 0 },
};
const POWERUP_DROP_CHANCE = 0.15;
const POWERUP_SIZE = 18;
const POWERUP_FALL_SPEED = 120;

// ── Game state ──────────────────────────────────
let W = 0;
let H = 0;
let paddle;
let balls = [];
let bricks = [];
let score = 0;
let lives = 3;
let level = 1;
let highScore = 0;
let playing = false;
let paused = false;
let gameOver = false;
let won = false;
let animId = null;
let particles = [];
let lastTime = 0;
let touchActiveId = null;
let paddleTarget = null;
let comboCount = 0;
let comboTimer = 0;
let soundOn = true;
let audioCtx = null;

// Mission config
let selectedDifficulty = "normal";
let activeMods = new Set();

// Power-up state
let powerups = [];     // falling power-up items
let activeBuffs = [];  // { type, remaining (ms) }

// Stats tracking
let stats = { bricksDestroyed: 0, maxCombo: 0, powerupsCollected: 0, ballsLost: 0, timeMs: 0, levelScores: [] };

// ── localStorage helpers ────────────────────────
function loadHighScore() {
  try {
    const v = parseInt(localStorage.getItem(HIGH_SCORE_KEY), 10);
    return Number.isFinite(v) && v >= 0 ? v : 0;
  } catch { return 0; }
}

function saveHighScore(v) {
  try { localStorage.setItem(HIGH_SCORE_KEY, String(v)); } catch { /* ignore */ }
}

function loadSoundPref() {
  try {
    const v = localStorage.getItem(SOUND_PREF_KEY);
    return v === null ? true : v === "1";
  } catch { return true; }
}

function saveSoundPref(on) {
  try { localStorage.setItem(SOUND_PREF_KEY, on ? "1" : "0"); } catch { /* ignore */ }
}

// ── Audio (Web Audio API) ───────────────────────
function ensureAudio() {
  if (audioCtx) return audioCtx;
  try {
    const Ctor = window.AudioContext || window.webkitAudioContext;
    if (!Ctor) return null;
    audioCtx = new Ctor();
  } catch { audioCtx = null; }
  return audioCtx;
}

function beep(freq, duration, type = "sine", gainAmt = 0.08) {
  if (!soundOn) return;
  const ac = ensureAudio();
  if (!ac) return;
  if (ac.state === "suspended") ac.resume().catch(() => {});
  const now = ac.currentTime;
  const osc = ac.createOscillator();
  const gain = ac.createGain();
  osc.type = type;
  osc.frequency.setValueAtTime(freq, now);
  gain.gain.setValueAtTime(0, now);
  gain.gain.linearRampToValueAtTime(gainAmt, now + 0.005);
  gain.gain.exponentialRampToValueAtTime(0.0001, now + duration);
  osc.connect(gain).connect(ac.destination);
  osc.start(now);
  osc.stop(now + duration + 0.02);
}

const sfx = {
  paddle: () => beep(420, 0.08, "square", 0.06),
  brick: () => beep(680, 0.06, "triangle", 0.07),
  brickBreak: () => beep(880, 0.12, "sawtooth", 0.08),
  wall: () => beep(300, 0.04, "sine", 0.04),
  miss: () => {
    if (!soundOn) return;
    beep(220, 0.18, "sawtooth", 0.1);
    setTimeout(() => beep(140, 0.22, "sawtooth", 0.09), 90);
  },
  level: () => {
    if (!soundOn) return;
    beep(520, 0.1, "triangle", 0.08);
    setTimeout(() => beep(780, 0.14, "triangle", 0.08), 80);
  },
  win: () => {
    if (!soundOn) return;
    [440, 660, 880, 1100].forEach((f, i) => {
      setTimeout(() => beep(f, 0.16, "triangle", 0.08), i * 110);
    });
  },
  powerup: () => {
    if (!soundOn) return;
    beep(600, 0.08, "sine", 0.07);
    setTimeout(() => beep(900, 0.1, "sine", 0.06), 60);
  },
};

// ── Resize ──────────────────────────────────────
function resize() {
  const rect = canvas.parentElement.getBoundingClientRect();
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  W = Math.floor(rect.width);
  H = Math.floor(rect.height);
  canvas.width = Math.floor(W * dpr);
  canvas.height = Math.floor(H * dpr);
  canvas.style.width = W + "px";
  canvas.style.height = H + "px";
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

  if (paddle) {
    paddle.w = getPaddleWidth();
    paddle.x = Math.min(Math.max(paddle.x, 0), W - paddle.w);
    paddle.y = H - 40;
  }
}

function getPaddleWidth() {
  let base = Math.max(80, Math.min(W * 0.2, 160));
  if (activeMods.has("bigPaddle") || hasActiveBuff("wide")) {
    base = Math.min(base * 1.5, W * 0.4);
  }
  return base;
}

// ── Brick layout ────────────────────────────────
function buildBricks() {
  const pattern = LEVELS[Math.min(level - 1, LEVELS.length - 1)];
  const rows = pattern.length;
  const cols = pattern[0].length;
  const totalPadX = BRICK_PAD * (cols + 1);
  const bw = (W - totalPadX) / cols;
  const arr = [];

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const ch = pattern[r][c];
      if (ch === ".") continue;
      const hits = parseInt(ch, 10);
      if (!Number.isFinite(hits) || hits <= 0) continue;
      arr.push({
        x: BRICK_PAD + c * (bw + BRICK_PAD),
        y: BRICK_TOP_OFFSET + r * (BRICK_HEIGHT + BRICK_PAD),
        w: bw,
        h: BRICK_HEIGHT,
        color: PALETTE[(r + c) % PALETTE.length],
        hits,
        maxHits: hits,
        alive: true,
        flash: 0,
      });
    }
  }
  return arr;
}

// ── Ball helpers ────────────────────────────────
function makeBall() {
  const diff = DIFFICULTIES[selectedDifficulty];
  const speed = Math.min((BASE_SPEED + (level - 1) * SPEED_INCREMENT) * diff.speedMul, SPEED_CAP);
  const slowBuff = hasActiveBuff("slow");
  const finalSpeed = slowBuff ? speed * 0.65 : speed;
  const angle = -Math.PI / 2 + (Math.random() - 0.5) * 0.6;
  return {
    x: W / 2,
    y: H - 60,
    r: BALL_RADIUS,
    dx: Math.cos(angle) * finalSpeed,
    dy: Math.sin(angle) * finalSpeed,
    speed: finalSpeed,
    trail: [],
  };
}

// ── Init / Reset ────────────────────────────────
function init() {
  resize();

  const diff = DIFFICULTIES[selectedDifficulty];
  score = 0;
  lives = diff.lives;
  level = 1;
  playing = false;
  paused = false;
  gameOver = false;
  won = false;
  particles = [];
  comboCount = 0;
  comboTimer = 0;
  powerups = [];
  activeBuffs = [];
  stats = { bricksDestroyed: 0, maxCombo: 0, powerupsCollected: 0, ballsLost: 0, timeMs: 0, levelScores: [] };

  paddle = {
    x: W / 2 - 50,
    y: H - 40,
    w: getPaddleWidth(),
  };

  balls = [makeBall()];
  if (activeMods.has("multiball")) {
    balls.push(makeBall());
    balls[1].dx = -balls[1].dx;
  }

  bricks = buildBricks();
  updateHud();
  updateStatusStrip();
  showOverlay("Void Breaker", instructionText(), "START");
  missionSelect.classList.remove("hide-mission");
  resultsScreen.classList.add("hidden");
}

function resetBalls() {
  balls = [makeBall()];
  comboCount = 0;
  comboTimer = 0;
  hideCombo();
}

function nextLevel() {
  stats.levelScores.push(score);
  level++;
  resetBalls();
  bricks = buildBricks();
  powerups = [];
  playing = false;
  sfx.level();
  updateHud();
  showOverlay(`LEVEL ${level}`, "\u51C6\u5907\u597D\u4E86\u5417\uFF1F<br/>\u7A7A\u683C\u7EE7\u7EED", "GO");
  missionSelect.classList.add("hide-mission");
}

// ── HUD ─────────────────────────────────────────
function updateHud() {
  scoreEl.textContent = score;
  livesEl.textContent = lives;
  levelEl.textContent = level;
  bestEl.textContent = highScore;
}

function pulseHud(el) {
  if (REDUCED_MOTION) return;
  el.classList.remove("pulse");
  void el.offsetWidth;
  el.classList.add("pulse");
  setTimeout(() => el.classList.remove("pulse"), 160);
}

// ── Status Strip ────────────────────────────────
function updateStatusStrip() {
  if (!playing && !paused) {
    statusStrip.classList.remove("visible");
    return;
  }
  statusStrip.classList.add("visible");

  // Progress
  const totalBricks = bricks.length;
  const destroyed = totalBricks > 0 ? bricks.filter(b => !b.alive).length : 0;
  const pct = totalBricks > 0 ? Math.round((destroyed / totalBricks) * 100) : 0;
  progressFill.style.width = pct + "%";
  progressText.textContent = pct + "%";

  // Active effects
  activeEffects.innerHTML = "";
  for (const buff of activeBuffs) {
    const def = POWERUP_TYPES[buff.type];
    if (!def || def.duration === 0) continue;
    const pill = document.createElement("span");
    pill.className = "effect-pill buff-active";
    if (buff.remaining < 2000) pill.classList.add("expiring");
    const secs = Math.ceil(buff.remaining / 1000);
    pill.textContent = `${def.icon} ${def.label} ${secs}s`;
    pill.style.borderColor = def.color;
    pill.style.background = def.color + "22";
    pill.style.setProperty("--pill-glow", def.color + "66");
    activeEffects.appendChild(pill);
  }

  // Show modifier badges
  const modBadges = {
    bigPaddle: "\u2194 BIG PAD",
    multiball: "\u26AB 2-BALL",
    noPowerups: "\u26A0 NO PWR",
  };
  for (const mod of activeMods) {
    const text = modBadges[mod];
    if (!text) continue;
    const pill = document.createElement("span");
    pill.className = "effect-pill modifier";
    pill.textContent = text;
    activeEffects.appendChild(pill);
  }
}

// ── Overlay ─────────────────────────────────────
function showOverlay(title, msg, btnText) {
  overlayTitle.textContent = title;
  overlayMsg.innerHTML = msg;
  btnStart.textContent = btnText;
  overlay.classList.remove("hidden");
}

function hideOverlay() {
  overlay.classList.add("hidden");
}

function instructionText() {
  const best = highScore > 0 ? `<br/><span style="color:var(--neon-amber)">\u6700\u9AD8\u5206\uFF1A${highScore}</span>` : "";
  return (
    "\u63A7\u5236\u6321\u677F\u53CD\u5F39\u80FD\u91CF\u7403\uFF0C\u51FB\u788E\u6240\u6709\u865A\u7A7A\u7816\u5757\u3002<br/>" +
    "\u952E\u76D8\uFF1A\u2190 \u2192 \u6216 A/D \u00B7 \u7A7A\u683C / Enter \u5F00\u59CB \u00B7 P \u6682\u505C \u00B7 M \u9759\u97F3 \u00B7 H \u5E2E\u52A9<br/>" +
    "\u89E6\u5C4F\uFF1A\u5728\u753B\u9762\u6216\u4E0B\u65B9\u89E6\u63A7\u533A\u62D6\u52A8\u63A7\u5236\u6321\u677F" +
    best
  );
}

// ── Combo ───────────────────────────────────────
function showCombo(n) {
  if (n < 2) return;
  comboBanner.textContent = `COMBO \u00D7${n}`;
  comboBanner.classList.add("show");
}

function hideCombo() {
  comboBanner.classList.remove("show");
}

// ── Power-ups ───────────────────────────────────
function hasActiveBuff(type) {
  return activeBuffs.some(b => b.type === type);
}

function maybeDropPowerup(x, y) {
  if (activeMods.has("noPowerups")) return;
  if (Math.random() > POWERUP_DROP_CHANCE) return;
  const types = Object.keys(POWERUP_TYPES);
  const type = types[Math.floor(Math.random() * types.length)];
  powerups.push({ x, y, type, vy: POWERUP_FALL_SPEED });
}

function collectPowerup(pu) {
  const def = POWERUP_TYPES[pu.type];
  sfx.powerup();
  stats.powerupsCollected++;
  spawnParticles(pu.x, pu.y, def.color, 12);

  if (pu.type === "shield") {
    lives = Math.min(lives + 1, 9);
    updateHud();
    pulseHud(livesEl);
    return;
  }
  if (pu.type === "multi") {
    const extra = makeBall();
    extra.x = balls[0] ? balls[0].x : W / 2;
    extra.y = balls[0] ? balls[0].y : H / 2;
    extra.dx = -extra.dx;
    balls.push(extra);
    return;
  }
  // Timed buff
  const existing = activeBuffs.find(b => b.type === pu.type);
  if (existing) {
    existing.remaining = def.duration;
  } else {
    activeBuffs.push({ type: pu.type, remaining: def.duration });
  }
  if (pu.type === "wide") {
    paddle.w = getPaddleWidth();
  }
}

function updatePowerups(dt) {
  for (let i = powerups.length - 1; i >= 0; i--) {
    const pu = powerups[i];
    pu.y += pu.vy * dt;

    // Collect on paddle
    if (
      pu.y + POWERUP_SIZE >= paddle.y &&
      pu.y <= paddle.y + PADDLE_HEIGHT &&
      pu.x + POWERUP_SIZE / 2 >= paddle.x &&
      pu.x - POWERUP_SIZE / 2 <= paddle.x + paddle.w
    ) {
      collectPowerup(pu);
      powerups.splice(i, 1);
      continue;
    }

    // Off screen
    if (pu.y > H + POWERUP_SIZE) {
      powerups.splice(i, 1);
    }
  }
}

function updateBuffs(dt) {
  const dtMs = dt * 1000;
  for (let i = activeBuffs.length - 1; i >= 0; i--) {
    const buff = activeBuffs[i];
    if (POWERUP_TYPES[buff.type].duration === 0) continue;
    buff.remaining -= dtMs;
    if (buff.remaining <= 0) {
      activeBuffs.splice(i, 1);
      if (buff.type === "wide") {
        paddle.w = getPaddleWidth();
      }
    }
  }
}

function drawPowerups() {
  for (const pu of powerups) {
    const def = POWERUP_TYPES[pu.type];
    ctx.save();

    // Glowing capsule
    ctx.shadowColor = def.color;
    ctx.shadowBlur = 10;
    ctx.fillStyle = def.color + "33";
    ctx.strokeStyle = def.color;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc(pu.x, pu.y, POWERUP_SIZE / 2, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Icon
    ctx.shadowBlur = 0;
    ctx.fillStyle = def.color;
    ctx.font = `700 10px ${CANVAS_FONT_STACK}`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(def.icon, pu.x, pu.y);

    ctx.restore();
  }
}

// ── Particles ───────────────────────────────────
function spawnParticles(x, y, color, count) {
  const cap = REDUCED_MOTION ? Math.ceil(count / 3) : count;
  for (let i = 0; i < cap; i++) {
    const angle = Math.random() * Math.PI * 2;
    const speed = 40 + Math.random() * 180;
    particles.push({
      x, y,
      dx: Math.cos(angle) * speed,
      dy: Math.sin(angle) * speed,
      life: 1,
      decay: 1.4 + Math.random() * 1.4,
      color,
      size: 2 + Math.random() * 3,
    });
  }
}

function updateParticles(dt) {
  for (let i = particles.length - 1; i >= 0; i--) {
    const p = particles[i];
    p.x += p.dx * dt;
    p.y += p.dy * dt;
    p.life -= p.decay * dt;
    if (p.life <= 0) particles.splice(i, 1);
  }
}

function drawParticles() {
  for (const p of particles) {
    ctx.globalAlpha = Math.max(0, p.life);
    ctx.fillStyle = p.color;
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.size * Math.max(0.1, p.life), 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.globalAlpha = 1;
}

// ── Drawing ─────────────────────────────────────
function drawBackground() {
  ctx.fillStyle = "#12121e";
  ctx.fillRect(0, 0, W, H);

  ctx.strokeStyle = "rgba(30, 30, 58, 0.5)";
  ctx.lineWidth = 0.5;
  const gridSize = 40;
  for (let x = 0; x < W; x += gridSize) {
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
  }
  for (let y = 0; y < H; y += gridSize) {
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
  }
}

function drawPaddle() {
  const p = paddle;
  const gradient = ctx.createLinearGradient(p.x, p.y, p.x + p.w, p.y);
  gradient.addColorStop(0, "#22d3ee");
  gradient.addColorStop(1, "#a855f7");

  ctx.shadowColor = "#22d3ee";
  ctx.shadowBlur = 15;
  roundRect(p.x, p.y, p.w, PADDLE_HEIGHT, PADDLE_RADIUS, gradient);
  ctx.shadowBlur = 0;
}

function drawBall(b) {
  for (let i = 0; i < b.trail.length; i++) {
    const t = b.trail[i];
    const alpha = (i / b.trail.length) * 0.3;
    ctx.globalAlpha = alpha;
    ctx.fillStyle = "#22d3ee";
    ctx.beginPath();
    ctx.arc(t.x, t.y, b.r * (i / b.trail.length), 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.globalAlpha = 1;

  ctx.shadowColor = "#22d3ee";
  ctx.shadowBlur = 12;
  ctx.fillStyle = "#fff";
  ctx.beginPath();
  ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
  ctx.fill();
  ctx.shadowBlur = 0;
}

function drawBricks() {
  for (const br of bricks) {
    if (!br.alive) continue;
    const healthRatio = br.hits / br.maxHits;
    const baseColor = br.color;

    if (healthRatio >= 1) {
      ctx.shadowColor = baseColor;
      ctx.shadowBlur = 8;
    }

    ctx.globalAlpha = 0.4 + healthRatio * 0.6;
    roundRect(br.x, br.y, br.w, br.h, 4, baseColor);

    if (br.flash > 0) {
      ctx.globalAlpha = br.flash;
      roundRect(br.x, br.y, br.w, br.h, 4, "#ffffff");
    }

    ctx.globalAlpha = healthRatio * 0.3;
    const shineGrad = ctx.createLinearGradient(br.x, br.y, br.x, br.y + br.h);
    shineGrad.addColorStop(0, "rgba(255,255,255,0.3)");
    shineGrad.addColorStop(1, "transparent");
    roundRect(br.x, br.y, br.w, br.h / 2, 4, shineGrad);

    ctx.globalAlpha = 1;
    ctx.shadowBlur = 0;
  }
}

function drawPauseOverlay() {
  ctx.fillStyle = "rgba(10, 10, 18, 0.55)";
  ctx.fillRect(0, 0, W, H);
  ctx.fillStyle = "#c8c8e0";
  ctx.font = `700 22px ${CANVAS_FONT_STACK}`;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText("PAUSED", W / 2, H / 2 - 10);
  ctx.font = `12px ${CANVAS_FONT_STACK}`;
  ctx.fillStyle = "#6a6a8a";
  ctx.fillText("\u6309 P \u6216\u70B9\u51FB \u25B6 \u7EE7\u7EED", W / 2, H / 2 + 16);
}

function roundRect(x, y, w, h, r, fill) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + r);
  ctx.lineTo(x + w, y + h - r);
  ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  ctx.lineTo(x + r, y + h);
  ctx.quadraticCurveTo(x, y + h, x, y + h - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
  ctx.fillStyle = fill;
  ctx.fill();
}

// ── Angle clamp ─────────────────────────────────
function clampBallAngle(b) {
  const sp = Math.hypot(b.dx, b.dy) || b.speed;
  let angle = Math.atan2(b.dy, b.dx);
  if (Math.abs(Math.sin(angle)) < MIN_VERTICAL_ANGLE) {
    const sign = b.dy >= 0 ? 1 : -1;
    angle = Math.atan2(Math.sin(MIN_VERTICAL_ANGLE) * sign, Math.cos(angle));
  }
  b.dx = Math.cos(angle) * sp;
  b.dy = Math.sin(angle) * sp;
}

// ── Collision ───────────────────────────────────
function collidePaddle(b) {
  const p = paddle;
  if (
    b.dy > 0 &&
    b.y + b.r >= p.y &&
    b.y - b.r <= p.y + PADDLE_HEIGHT &&
    b.x >= p.x - b.r &&
    b.x <= p.x + p.w + b.r
  ) {
    const hitPos = Math.max(0, Math.min(1, (b.x - p.x) / p.w));
    const angle = -Math.PI / 2 + (hitPos - 0.5) * 1.3;
    const sp = b.speed;
    b.dx = Math.cos(angle) * sp;
    b.dy = Math.sin(angle) * sp;
    b.y = p.y - b.r - 0.5;
    spawnParticles(b.x, b.y, "#22d3ee", 6);
    sfx.paddle();
    comboCount = 0;
    hideCombo();
  }
}

function collideBricks(b) {
  for (const br of bricks) {
    if (!br.alive) continue;
    if (
      b.x + b.r > br.x &&
      b.x - b.r < br.x + br.w &&
      b.y + b.r > br.y &&
      b.y - b.r < br.y + br.h
    ) {
      const overlapLeft = b.x + b.r - br.x;
      const overlapRight = br.x + br.w - (b.x - b.r);
      const overlapTop = b.y + b.r - br.y;
      const overlapBottom = br.y + br.h - (b.y - b.r);
      const minX = Math.min(overlapLeft, overlapRight);
      const minY = Math.min(overlapTop, overlapBottom);

      if (minX < minY) {
        b.dx = -b.dx;
        if (overlapLeft < overlapRight) b.x = br.x - b.r;
        else b.x = br.x + br.w + b.r;
      } else {
        b.dy = -b.dy;
        if (overlapTop < overlapBottom) b.y = br.y - b.r;
        else b.y = br.y + br.h + b.r;
      }

      br.hits--;
      br.flash = 1;
      comboCount++;
      comboTimer = COMBO_WINDOW_MS;
      if (comboCount > stats.maxCombo) stats.maxCombo = comboCount;
      const comboBonus = Math.max(1, comboCount);

      if (br.hits <= 0) {
        br.alive = false;
        score += 100 * level * comboBonus;
        stats.bricksDestroyed++;
        spawnParticles(br.x + br.w / 2, br.y + br.h / 2, br.color, 14);
        sfx.brickBreak();
        maybeDropPowerup(br.x + br.w / 2, br.y + br.h / 2);
      } else {
        score += 25 * level * comboBonus;
        spawnParticles(br.x + br.w / 2, br.y + br.h / 2, br.color, 6);
        sfx.brick();
      }

      if (score > highScore) {
        const isNewMilestone = Math.floor(score / 1000) > Math.floor(highScore / 1000);
        highScore = score;
        saveHighScore(highScore);
        if (isNewMilestone) pulseHud(bestEl);
      }
      updateHud();
      pulseHud(scoreEl);
      if (comboCount >= 2) showCombo(comboCount);
      return;
    }
  }
}

function collideWalls(b) {
  let hit = false;
  if (b.x - b.r <= 0) { b.x = b.r; b.dx = Math.abs(b.dx); hit = true; }
  if (b.x + b.r >= W) { b.x = W - b.r; b.dx = -Math.abs(b.dx); hit = true; }
  if (b.y - b.r <= 0) { b.y = b.r; b.dy = Math.abs(b.dy); hit = true; }
  if (hit) sfx.wall();
}

function triggerShake() {
  if (REDUCED_MOTION) return;
  arena.classList.remove("shake");
  arena.classList.remove("flash");
  void arena.offsetWidth;
  arena.classList.add("shake");
  arena.classList.add("flash");
  setTimeout(() => {
    arena.classList.remove("shake");
    arena.classList.remove("flash");
  }, 320);
}

function checkBallsLost() {
  for (let i = balls.length - 1; i >= 0; i--) {
    if (balls[i].y - balls[i].r > H) {
      balls.splice(i, 1);
      stats.ballsLost++;
    }
  }

  if (balls.length === 0) {
    lives--;
    pulseHud(livesEl);
    updateHud();
    spawnParticles(W / 2, H - 4, "#ef4444", 24);
    sfx.miss();
    triggerShake();
    comboCount = 0;
    hideCombo();

    if (lives <= 0) {
      gameOver = true;
      playing = false;
      stats.levelScores.push(score);
      showResultsScreen(false);
    } else {
      resetBalls();
    }
  }
}

function checkWin() {
  if (bricks.length === 0) return;
  if (bricks.every(b => !b.alive)) {
    if (level >= LEVELS.length) {
      won = true;
      playing = false;
      sfx.win();
      stats.levelScores.push(score);
      showResultsScreen(true);
    } else {
      playing = false;
      nextLevel();
    }
  }
}

// ── Results Screen ──────────────────────────────
function showResultsScreen(didWin) {
  hideOverlay();
  statusStrip.classList.remove("visible");
  resultsScreen.classList.remove("hidden");

  resultsTitle.textContent = didWin ? "YOU WIN!" : "GAME OVER";

  // Difficulty label below title
  const diffLabel = DIFFICULTIES[selectedDifficulty].label;
  const modsStr = activeMods.size > 0 ? " + " + [...activeMods].map(m => {
    if (m === "bigPaddle") return "BIG PAD";
    if (m === "multiball") return "2-BALL";
    if (m === "noPowerups") return "NO PWR";
    return m;
  }).join(", ") : "";
  let diffEl = resultsScreen.querySelector(".results-difficulty");
  if (!diffEl) {
    diffEl = document.createElement("div");
    diffEl.className = "results-difficulty";
    resultsTitle.insertAdjacentElement("afterend", diffEl);
  }
  diffEl.textContent = diffLabel + modsStr;

  // Badge
  const isBest = score >= highScore && score > 0;
  let badgeHtml = "";
  if (didWin && isBest) {
    badgeHtml = `<span class="badge-text" style="border-color:var(--neon-amber);color:var(--neon-amber)">\u2605 NEW RECORD \u2605</span>`;
  } else if (didWin) {
    badgeHtml = `<span class="badge-text" style="border-color:var(--neon-green);color:var(--neon-green)">\u2713 ALL CLEAR</span>`;
  } else if (isBest) {
    badgeHtml = `<span class="badge-text" style="border-color:var(--neon-amber);color:var(--neon-amber)">\u2605 NEW RECORD</span>`;
  } else {
    badgeHtml = `<span class="badge-text" style="border-color:var(--text-dim);color:var(--text-dim)">LEVEL ${level}</span>`;
  }
  resultsBadge.innerHTML = badgeHtml;

  // Stats
  const timeSec = Math.round(stats.timeMs / 1000);
  const timeStr = timeSec >= 60 ? `${Math.floor(timeSec / 60)}m ${timeSec % 60}s` : `${timeSec}s`;

  const statItems = [
    { label: "SCORE", value: score.toLocaleString(), highlight: isBest },
    { label: "BEST", value: highScore.toLocaleString(), highlight: false },
    { label: "BRICKS", value: stats.bricksDestroyed, highlight: false },
    { label: "MAX COMBO", value: `\u00D7${stats.maxCombo}`, highlight: stats.maxCombo >= 5 },
    { label: "POWER-UPS", value: stats.powerupsCollected, highlight: false },
    { label: "TIME", value: timeStr, highlight: false },
  ];

  resultsStats.innerHTML = statItems.map(s =>
    `<div class="stat-card ${s.highlight ? "highlight" : ""}">
       <span class="stat-label">${s.label}</span>
       <span class="stat-value">${s.value}</span>
     </div>`
  ).join("");

  // Bar chart: score per level
  const scores = stats.levelScores;
  const maxLevelScore = Math.max(1, ...scores.map((s, i) => i === 0 ? s : s - (scores[i - 1] || 0)));
  resultsChart.innerHTML = "";
  for (let i = 0; i < scores.length; i++) {
    const levelScore = i === 0 ? scores[0] : scores[i] - scores[i - 1];
    const heightPct = Math.max(8, (levelScore / maxLevelScore) * 100);
    const color = PALETTE[i % PALETTE.length];
    resultsChart.innerHTML += `
      <div class="chart-bar">
        <div class="chart-bar-fill" style="height:${heightPct}%;background:${color};"></div>
        <span class="chart-bar-label">L${i + 1}</span>
      </div>`;
  }

  btnRetry.textContent = "PLAY AGAIN";
}

function hideResults() {
  resultsScreen.classList.add("hidden");
}

// ── Mission Select Logic ────────────────────────
difficultyRow.addEventListener("click", (e) => {
  const btn = e.target.closest(".diff-btn");
  if (!btn) return;
  difficultyRow.querySelectorAll(".diff-btn").forEach(b => b.classList.remove("selected"));
  btn.classList.add("selected");
  selectedDifficulty = btn.dataset.diff;
});

modifierRow.addEventListener("click", (e) => {
  const btn = e.target.closest(".mod-btn");
  if (!btn) return;
  const mod = btn.dataset.mod;
  if (activeMods.has(mod)) {
    activeMods.delete(mod);
    btn.classList.remove("active");
  } else {
    activeMods.add(mod);
    btn.classList.add("active");
  }
});

// ── Input ───────────────────────────────────────
const keys = Object.create(null);

window.addEventListener("keydown", (e) => {
  const k = e.key;
  keys[k] = true;

  if (k === " " || k === "Enter") {
    e.preventDefault();
    if (gameOver || won) { startGame(); }
    else if (paused) { togglePause(); }
    else if (!playing) { startGame(); }
    return;
  }

  if (k === "p" || k === "P" || k === "Escape") {
    e.preventDefault();
    if (playing || paused) togglePause();
    return;
  }

  if (k === "m" || k === "M") { e.preventDefault(); toggleSound(); return; }
  if (k === "h" || k === "H") { e.preventDefault(); showHelp(); }
});

window.addEventListener("keyup", (e) => { keys[e.key] = false; });

// ── Pointer controls ───────────────────────────
function canvasX(clientX) {
  const rect = canvas.getBoundingClientRect();
  return Math.max(0, Math.min(W, clientX - rect.left));
}

function startPointer(e) {
  if (e.target && e.target.closest(".controls")) return;
  e.preventDefault();
  const id = e.pointerId ?? "mouse";
  touchActiveId = id;
  if (e.target && typeof e.target.setPointerCapture === "function") {
    try { e.target.setPointerCapture(e.pointerId); } catch { /* ignore */ }
  }
  if (gameOver || won) { startGame(); return; }
  if (!playing && !paused) { startGame(); }
  if (playing && !paused) {
    paddleTarget = canvasX(e.clientX) - paddle.w / 2;
  }
}

function movePointer(e) {
  if (touchActiveId === null) return;
  const id = e.pointerId ?? "mouse";
  if (id !== touchActiveId) return;
  if (!playing || paused) return;
  e.preventDefault();
  paddleTarget = canvasX(e.clientX) - paddle.w / 2;
}

function endPointer(e) {
  const id = e.pointerId ?? "mouse";
  if (id !== touchActiveId) return;
  touchActiveId = null;
  paddleTarget = null;
}

canvas.addEventListener("pointerdown", startPointer);
canvas.addEventListener("pointermove", movePointer);
canvas.addEventListener("pointerup", endPointer);
canvas.addEventListener("pointercancel", endPointer);

touchZone.addEventListener("pointerdown", startPointer);
touchZone.addEventListener("pointermove", movePointer);
touchZone.addEventListener("pointerup", endPointer);
touchZone.addEventListener("pointercancel", endPointer);

btnStart.addEventListener("click", (e) => { e.stopPropagation(); startGame(); });
btnPause.addEventListener("click", (e) => { e.stopPropagation(); if (playing || paused) togglePause(); });
btnSound.addEventListener("click", (e) => { e.stopPropagation(); toggleSound(); });
btnHelp.addEventListener("click", (e) => { e.stopPropagation(); showHelp(); });
btnRetry.addEventListener("click", (e) => { e.stopPropagation(); startGame(); });

document.addEventListener("visibilitychange", () => {
  if (document.hidden && playing && !paused && !gameOver && !won) togglePause();
});

window.addEventListener("resize", resize);
window.addEventListener("orientationchange", resize);

// ── Toggles ─────────────────────────────────────
function togglePause() {
  if (gameOver || won) return;
  paused = !paused;
  if (paused) {
    playing = false;
    btnPause.querySelector("span").textContent = "\u25B6";
    showOverlay("PAUSED", "\u6309 P \u6216\u70B9\u51FB \u25B6 \u7EE7\u7EED<br/>M \u9759\u97F3 \u00B7 H \u5E2E\u52A9", "RESUME");
    missionSelect.classList.add("hide-mission");
  } else {
    playing = true;
    btnPause.querySelector("span").textContent = "\u23F8";
    hideOverlay();
    lastTime = performance.now();
  }
}

function toggleSound() {
  soundOn = !soundOn;
  saveSoundPref(soundOn);
  btnSound.setAttribute("aria-pressed", soundOn ? "true" : "false");
  btnSound.querySelector("span").textContent = soundOn ? "\uD83D\uDD0A" : "\uD83D\uDD07";
  if (soundOn) beep(520, 0.08, "sine", 0.05);
}

function showHelp() {
  if (playing && !paused) {
    paused = true;
    playing = false;
    btnPause.querySelector("span").textContent = "\u25B6";
  }
  const btnText = paused ? "RESUME" : gameOver || won ? "RETRY" : "START";
  showOverlay("HELP", instructionText(), btnText);
  missionSelect.classList.add("hide-mission");
}

// ── Start ───────────────────────────────────────
function startGame() {
  if (gameOver || won) {
    hideResults();
    init();
  }
  ensureAudio();
  if (audioCtx && audioCtx.state === "suspended") audioCtx.resume().catch(() => {});

  paused = false;
  btnPause.querySelector("span").textContent = "\u23F8";
  hideOverlay();
  playing = true;
  lastTime = performance.now();
  statusStrip.classList.add("visible");
  if (animId === null) {
    animId = requestAnimationFrame(loop);
  }
}

// ── Update ──────────────────────────────────────
function update(dt) {
  if (!playing) return;

  stats.timeMs += dt * 1000;

  // Paddle movement — keyboard
  const paddleSpeed = 520;
  if (keys["ArrowLeft"] || keys["a"] || keys["A"]) { paddle.x -= paddleSpeed * dt; paddleTarget = null; }
  if (keys["ArrowRight"] || keys["d"] || keys["D"]) { paddle.x += paddleSpeed * dt; paddleTarget = null; }

  // Paddle movement — pointer target
  if (paddleTarget !== null) {
    const diff = paddleTarget - paddle.x;
    paddle.x += diff * Math.min(1, dt * 14);
  }
  paddle.x = Math.max(0, Math.min(W - paddle.w, paddle.x));

  // Update each ball
  for (const b of balls) {
    b.trail.push({ x: b.x, y: b.y });
    if (b.trail.length > 8) b.trail.shift();

    const stepMax = b.r * 0.8;
    const dist = Math.hypot(b.dx * dt, b.dy * dt);
    const steps = Math.max(1, Math.ceil(dist / stepMax));
    const sdt = dt / steps;
    for (let i = 0; i < steps; i++) {
      b.x += b.dx * sdt;
      b.y += b.dy * sdt;
      collideWalls(b);
      collidePaddle(b);
      collideBricks(b);
      if (!playing) break;
    }
    clampBallAngle(b);
  }

  // Combo timer
  if (comboTimer > 0) {
    comboTimer -= dt * 1000;
    if (comboTimer <= 0) { comboCount = 0; hideCombo(); }
  }

  // Brick flash decay
  for (const br of bricks) {
    if (br.flash > 0) br.flash = Math.max(0, br.flash - dt * 4);
  }

  updatePowerups(dt);
  updateBuffs(dt);
  checkBallsLost();
  checkWin();
  updateParticles(dt);
  updateStatusStrip();
}

// ── Render ──────────────────────────────────────
function render() {
  drawBackground();
  drawBricks();
  drawPaddle();
  if (!gameOver) {
    for (const b of balls) drawBall(b);
  }
  drawPowerups();
  drawParticles();
  if (paused) drawPauseOverlay();
}

// ── Loop ────────────────────────────────────────
function loop(timestamp) {
  animId = requestAnimationFrame(loop);
  let dt = (timestamp - lastTime) / 1000;
  lastTime = timestamp;
  if (!Number.isFinite(dt) || dt <= 0) return;
  if (dt > 0.1) dt = 0.1;

  if (playing) update(dt);
  render();
}

// ── Boot ────────────────────────────────────────
highScore = loadHighScore();
soundOn = loadSoundPref();
btnSound.setAttribute("aria-pressed", soundOn ? "true" : "false");
btnSound.querySelector("span").textContent = soundOn ? "\uD83D\uDD0A" : "\uD83D\uDD07";

init();
render();
animId = requestAnimationFrame(loop);
