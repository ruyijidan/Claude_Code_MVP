// Starforge Relay / 星炉中继
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const overlay = document.getElementById("overlay");
const overlayTag = document.getElementById("overlayTag");
const overlayTitle = document.getElementById("overlayTitle");
const overlayText = document.getElementById("overlayText");
const startButton = document.getElementById("startButton");

const scoreLabel = document.getElementById("score");
const healthLabel = document.getElementById("health");
const waveLabel = document.getElementById("wave");
const chargeLabel = document.getElementById("charge");
const comboLabel = document.getElementById("combo");
const modulesLabel = document.getElementById("modules");
const bestBadge = document.getElementById("bestBadge");

const sessionStrip = document.getElementById("sessionStrip");
const sessionWave = document.getElementById("sessionWave");
const sessionCharge = document.getElementById("sessionCharge");
const sessionCombo = document.getElementById("sessionCombo");
const sessionModules = document.getElementById("sessionModules");
const sessionTempo = document.getElementById("sessionTempo");
const sessionFocus = document.getElementById("sessionFocus");

const upgradeSelect = document.getElementById("upgradeSelect");
const upgradeGrid = document.getElementById("upgradeGrid");
const modeButtons = Array.from(document.querySelectorAll(".mode-button"));
const runButtons = Array.from(document.querySelectorAll(".run-button"));
const touchButtons = Array.from(document.querySelectorAll(".touch-button"));

const STORAGE_KEY = "starforgeRelay.bestScore";
const TAU = Math.PI * 2;
const WORLD = { width: 1200, height: 760, centerX: 600, centerY: 380, arenaRadius: 240, coreRadius: 58 };

const MODE_CONFIG = {
  calm: {
    name: "CALM",
    spawnInterval: 1.08,
    enemySpeed: 118,
    enemyHealthMul: 0.9,
    bulletSpeed: 650,
    fireRate: 0.24,
    dashCooldown: 1.65,
    dashDuration: 0.2,
    pulseCooldown: 3.9,
    pulseRadius: 120,
    pulseDamage: 3,
    moveSpeed: 250,
    shield: 1,
  },
  standard: {
    name: "STANDARD",
    spawnInterval: 0.94,
    enemySpeed: 136,
    enemyHealthMul: 1,
    bulletSpeed: 675,
    fireRate: 0.19,
    dashCooldown: 1.45,
    dashDuration: 0.19,
    pulseCooldown: 3.5,
    pulseRadius: 132,
    pulseDamage: 3,
    moveSpeed: 265,
    shield: 0,
  },
  storm: {
    name: "STORM",
    spawnInterval: 0.84,
    enemySpeed: 154,
    enemyHealthMul: 1.18,
    bulletSpeed: 700,
    fireRate: 0.16,
    dashCooldown: 1.28,
    dashDuration: 0.18,
    pulseCooldown: 3.1,
    pulseRadius: 146,
    pulseDamage: 4,
    moveSpeed: 278,
    shield: 0,
  },
};

const RUN_CONFIG = {
  classic: {
    name: "CLASSIC",
    maxWaves: 8,
    chargeScale: 1,
    bossEvery: 4,
    draftBetweenWaves: true,
  },
  marathon: {
    name: "MARATHON",
    maxWaves: Infinity,
    chargeScale: 1.08,
    bossEvery: 4,
    draftBetweenWaves: true,
  },
};

const UPGRADE_POOL = [
  {
    id: "overclock",
    tag: "FIRE",
    name: "OVERCLOCK",
    description: "射速更快，自动锁定距离更远。",
    apply(state) {
      state.fireRateMul *= 0.84;
      state.targetRange += 30;
    },
  },
  {
    id: "magnet",
    tag: "PULL",
    name: "MAGNET FIELD",
    description: "碎片吸引半径扩大，收集中继更稳。",
    apply(state) {
      state.magnetMul += 0.28;
    },
  },
  {
    id: "dash",
    tag: "MOVE",
    name: "DASH THRUST",
    description: "冲刺更长、更快，躲避压力更轻松。",
    apply(state) {
      state.dashCooldownMul *= 0.86;
      state.dashDurationMul *= 1.12;
      state.moveSpeedMul += 0.06;
    },
  },
  {
    id: "pulse",
    tag: "BURST",
    name: "PULSE LENS",
    description: "脉冲半径和伤害提升，关键时刻更能清场。",
    apply(state) {
      state.pulseRadiusMul += 0.18;
      state.pulseDamageMul += 1;
      state.pulseCooldownMul *= 0.9;
    },
  },
  {
    id: "aegis",
    tag: "SURVIVE",
    name: "AEGIS SHELL",
    description: "最大生命 +1，波次完成时额外回复 1 点生命。",
    apply(state) {
      state.maxHealth += 1;
      state.health = Math.min(state.maxHealth, state.health + 1);
      state.aegisHeal += 1;
    },
  },
  {
    id: "chain",
    tag: "LINK",
    name: "CHAIN LINK",
    description: "击杀会向附近敌人弹链一次，清怪更连贯。",
    apply(state) {
      state.chainLightning += 1;
    },
  },
  {
    id: "tempo",
    tag: "FLOW",
    name: "TEMPO CORE",
    description: "连锁更容易维持，得分倍率增长更快。",
    apply(state) {
      state.comboWindowMul += 0.18;
      state.scoreMul += 0.14;
    },
  },
  {
    id: "relay",
    tag: "SYNC",
    name: "RELAY CORE",
    description: "每个碎片提供更多中继能量，推进波次更快。",
    apply(state) {
      state.chargeMul += 0.16;
    },
  },
  {
    id: "barrier",
    tag: "GUARD",
    name: "BARRIER BLOOM",
    description: "波次完成后生成一次护盾花环，抵消下一次碰撞。",
    apply(state) {
      state.waveBarrier += 1;
    },
  },
];

const state = {
  mode: "menu",
  difficulty: "standard",
  runMode: "marathon",
  bestScore: readBestScore(),
  score: 0,
  wave: 1,
  charge: 0,
  chargeTarget: 8,
  waveMinDuration: 0,
  health: 4,
  maxHealth: 4,
  combo: 1,
  comboTimer: 0,
  scoreMul: 1,
  chargeMul: 1,
  moveSpeedMul: 1,
  fireRateMul: 1,
  dashCooldownMul: 1,
  dashDurationMul: 1,
  pulseCooldownMul: 1,
  pulseRadiusMul: 1,
  pulseDamageMul: 0,
  targetRange: 260,
  magnetMul: 1,
  chainLightning: 0,
  aegisHeal: 0,
  waveBarrier: 0,
  fireCooldown: 0,
  dashCooldown: 0,
  dashActive: 0,
  pulseCooldown: 0,
  pulseActive: 0,
  invulnerable: 0,
  waveTimer: 0,
  spawnTimer: 0,
  spawnBurst: 0,
  draftTimer: 0,
  shake: 0,
  clearFlash: 0,
  bossSpawned: false,
  pointer: { active: false, x: 0, y: 0 },
  keyState: { left: false, right: false, up: false, down: false },
  dashQueued: false,
  pulseQueued: false,
  upgradeDraft: [],
  upgrades: [],
  player: { x: 600, y: 380, vx: 0, vy: 0, angle: 0, radius: 16 },
  enemies: [],
  bullets: [],
  shards: [],
  bursts: [],
  stars: [],
  phaseBanner: { text: "", life: 0 },
  lastTime: 0,
};

function readBestScore() {
  try {
    return Number(localStorage.getItem(STORAGE_KEY) || 0) || 0;
  } catch {
    return 0;
  }
}

function saveBestScore(score) {
  try {
    localStorage.setItem(STORAGE_KEY, String(score));
  } catch {
    // Ignore privacy-mode storage failures.
  }
}

function currentConfig() {
  return MODE_CONFIG[state.difficulty] || MODE_CONFIG.standard;
}

function currentRunConfig() {
  return RUN_CONFIG[state.runMode] || RUN_CONFIG.marathon;
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function lerp(a, b, t) {
  return a + (b - a) * t;
}

function length(x, y) {
  return Math.hypot(x, y);
}

function normalize(x, y) {
  const len = Math.hypot(x, y) || 1;
  return { x: x / len, y: y / len };
}

function randomRange(min, max) {
  return min + Math.random() * (max - min);
}

function randomChoice(items) {
  return items[Math.floor(Math.random() * items.length)];
}

function resizeCanvas() {
  const frame = canvas.parentElement;
  const width = frame.clientWidth;
  const height = Math.round(width * 760 / 1200);
  const dpr = window.devicePixelRatio || 1;

  canvas.style.height = `${height}px`;
  canvas.width = Math.round(width * dpr);
  canvas.height = Math.round(height * dpr);
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

  WORLD.width = width;
  WORLD.height = height;
  WORLD.centerX = width / 2;
  WORLD.centerY = height / 2;
  WORLD.arenaRadius = Math.min(width, height) * 0.34;
  WORLD.coreRadius = Math.max(52, Math.min(width, height) * 0.075);
}

function spawnStars() {
  const target = Math.round((WORLD.width + WORLD.height) / 22);
  while (state.stars.length < target) {
    state.stars.push({
      x: Math.random() * WORLD.width,
      y: Math.random() * WORLD.height,
      size: 0.8 + Math.random() * 2.4,
      speed: 0.02 + Math.random() * 0.08,
      hue: Math.random() > 0.75 ? "accent-2" : "accent",
      phase: Math.random() * TAU,
    });
  }
}

function resetGame() {
  const config = currentConfig();
  state.score = 0;
  state.wave = 1;
  state.charge = 0;
  state.chargeTarget = getChargeTarget();
  state.waveMinDuration = getWaveMinDuration();
  state.health = 4 + config.shield;
  state.maxHealth = state.health;
  state.combo = 1;
  state.comboTimer = 0;
  state.scoreMul = 1;
  state.chargeMul = 1;
  state.moveSpeedMul = 1;
  state.fireRateMul = 1;
  state.dashCooldownMul = 1;
  state.dashDurationMul = 1;
  state.pulseCooldownMul = 1;
  state.pulseRadiusMul = 1;
  state.pulseDamageMul = 0;
  state.targetRange = 260;
  state.magnetMul = 1;
  state.chainLightning = 0;
  state.aegisHeal = 0;
  state.waveBarrier = 0;
  state.fireCooldown = 0;
  state.dashCooldown = 0;
  state.dashActive = 0;
  state.pulseCooldown = 0;
  state.pulseActive = 0;
  state.invulnerable = 0;
  state.waveTimer = 0;
  state.spawnTimer = 0;
  state.spawnBurst = 0;
  state.shake = 0;
  state.clearFlash = 0;
  state.bossSpawned = false;
  state.upgradeDraft = [];
  state.upgrades = [];
  state.enemies = [];
  state.bullets = [];
  state.shards = [];
  state.bursts = [];
  state.phaseBanner = { text: "", life: 0 };
  state.player.x = WORLD.centerX;
  state.player.y = WORLD.centerY;
  state.player.vx = 0;
  state.player.vy = 0;
  state.player.angle = -Math.PI / 2;
  state.player.radius = 16;
  state.mode = "playing";
  state.lastTime = performance.now();
  state.pointer.active = false;
  hideOverlay();
  upgradeSelect.classList.add("hidden");
  updateHud();
  startWave();
}

function getChargeTarget() {
  const runConfig = currentRunConfig();
  return Math.max(12, Math.round((12 + state.wave * 4) * runConfig.chargeScale));
}

function getWaveMinDuration() {
  return Math.min(22, 8.5 + state.wave * 0.8);
}

function showOverlay(tag, title, text, buttonText) {
  overlay.classList.remove("hidden");
  overlayTag.textContent = tag;
  overlayTitle.textContent = title;
  overlayText.textContent = text;
  startButton.textContent = buttonText;
  startButton.hidden = false;
  updateSessionStrip();
}

function hideOverlay() {
  overlay.classList.add("hidden");
}

function updateSessionStrip() {
  sessionWave.textContent = `波次 ${state.wave}${state.runMode === "marathon" ? " / ∞" : ""}`;
  sessionCharge.textContent = `中继 ${Math.min(100, Math.round((state.charge / Math.max(1, state.chargeTarget)) * 100))}%`;
  sessionCombo.textContent = `连锁 ${state.combo}x`;
  sessionModules.textContent = `模块 ${state.upgrades.length}`;
  sessionTempo.textContent = state.combo >= 5 ? "节奏 热" : state.combo >= 3 ? "节奏 稳" : "节奏 冷静";
  sessionFocus.textContent = state.mode === "draft"
    ? `焦点 自动配装 ${Math.max(0, Math.ceil(state.draftTimer))}s`
    : state.mode === "results"
      ? "焦点 结算复盘"
      : state.mode === "paused"
        ? "焦点 暂停整理"
        : "焦点 波次推进";
}

function syncModeButtons() {
  modeButtons.forEach((button) => {
    button.classList.toggle("is-active", button.dataset.mode === state.difficulty);
  });
}

function syncRunButtons() {
  runButtons.forEach((button) => {
    button.classList.toggle("is-active", button.dataset.run === state.runMode);
  });
}

function updateHud() {
  scoreLabel.textContent = String(state.score);
  healthLabel.textContent = String(state.health);
  waveLabel.textContent = state.runMode === "marathon" ? `${state.wave} / ∞` : String(state.wave);
  chargeLabel.textContent = `${state.charge} / ${state.chargeTarget}`;
  comboLabel.textContent = `${state.combo}x`;
  modulesLabel.textContent = String(state.upgrades.length);
  bestBadge.textContent = `BEST ${state.bestScore}`;
  updateSessionStrip();
}

function setDifficulty(mode) {
  if (!MODE_CONFIG[mode] || state.difficulty === mode) {
    return;
  }
  state.difficulty = mode;
  syncModeButtons();
  if (state.mode === "menu") {
    updateOverlayForMenu();
  }
}

function setRunMode(mode) {
  if (!RUN_CONFIG[mode] || state.runMode === mode) {
    return;
  }
  state.runMode = mode;
  syncRunButtons();
  if (state.mode === "menu") {
    updateOverlayForMenu();
  }
}

function updateOverlayForMenu() {
  const config = currentConfig();
  const runConfig = currentRunConfig();
  const runText = runConfig.name === "MARATHON"
    ? "马拉松模式会不断拉高波次和敌人压力，适合看长任务能否持续收敛。"
    : "经典模式会在 8 波后收束，适合做完整的有限局验收。";
  overlay.classList.remove("hidden");
  overlay.classList.remove("drafting");
  showOverlay(
    "READY",
    "点燃中继核心，进入星域任务",
    `当前难度 ${config.name} · ${runConfig.name}。${runText} 用 WASD 或方向键移动，Space 冲刺，E 脉冲；拖动或触控也能引导飞船。波次结束后系统会自动配装模块，按 1 / 2 / 3 仍可快速覆盖默认选择。`,
    "开始任务"
  );
  updateSessionStrip();
}

function openUpgradeDraft() {
  state.mode = "draft";
  state.upgradeDraft = pickUpgradeChoices();
  state.draftTimer = 3.5;
  overlay.classList.add("hidden");
  overlay.classList.remove("drafting");
  startButton.hidden = true;
  upgradeSelect.classList.add("hidden");
  state.phaseBanner = {
    text: `第 ${state.wave - 1} 波完成 · 模块自动配装`,
    life: 1.6,
  };
  updateSessionStrip();
}

function renderUpgradeChoices(choices) {
  upgradeGrid.innerHTML = "";
  choices.forEach((upgrade, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "upgrade-card";
    button.innerHTML = `
      <div class="upgrade-top">
        <span class="upgrade-name">${upgrade.name}</span>
        <span class="upgrade-tag">${upgrade.tag}</span>
      </div>
      <p class="upgrade-desc">${upgrade.description}</p>
    `;
    button.addEventListener("click", () => chooseUpgrade(index));
    upgradeGrid.appendChild(button);
  });
}

function pickUpgradeChoices() {
  const available = UPGRADE_POOL.filter((upgrade) => !state.upgrades.some((owned) => owned.id === upgrade.id));
  const pool = available.length > 0 ? available : UPGRADE_POOL;
  const picks = [];
  const used = new Set();
  while (picks.length < Math.min(3, pool.length)) {
    const upgrade = randomChoice(pool);
    if (used.has(upgrade.id)) {
      continue;
    }
    used.add(upgrade.id);
    picks.push(upgrade);
  }
  return picks;
}

function chooseUpgrade(index) {
  if (state.mode !== "draft") {
    return;
  }
  const upgrade = state.upgradeDraft[index];
  if (!upgrade) {
    return;
  }
  upgrade.apply(state);
  state.upgrades.push(upgrade);
  state.upgradeDraft = [];
  state.draftTimer = 0;
  state.mode = "playing";
  state.lastTime = performance.now();
  hideOverlay();
  overlay.classList.remove("drafting");
  upgradeSelect.classList.add("hidden");
  state.combo = Math.min(8, state.combo + 1);
  state.comboTimer = 1.6 * state.comboWindowMul;
  if (state.waveBarrier > 0) {
    state.waveBarrier -= 1;
    state.invulnerable = Math.max(state.invulnerable, 1.1);
  }
  spawnWave();
  updateHud();
}

function scoreAutoUpgrade(upgrade) {
  const config = currentConfig();
  const liveEnemyCount = state.enemies.length;
  switch (upgrade.id) {
    case "aegis":
      return (state.health <= 2 ? 140 : 55) + state.wave;
    case "relay":
      return 88 + state.wave * 2 + Math.max(0, 10 - state.chargeTarget);
    case "magnet":
      return 76 + Math.max(0, 4 - Math.round(state.magnetMul * 2)) * 10;
    case "overclock":
      return 80 + Math.max(0, 6 - Math.round(state.fireRateMul * 6)) * 8;
    case "pulse":
      return 74 + Math.max(0, 5 - Math.round(state.pulseCooldownMul * 5)) * 8;
    case "dash":
      return 68 + Math.max(0, 5 - Math.round(state.moveSpeedMul * 5)) * 8;
    case "chain":
      return 66 + Math.min(20, liveEnemyCount * 2);
    case "tempo":
      return 72 + Math.max(0, 4 - Math.min(4, state.combo)) * 10 + config.enemySpeed * 0.01;
    case "barrier":
      return 84 + Math.max(0, 4 - state.health) * 16;
    default:
      return 1;
  }
}

function chooseAutoUpgrade() {
  if (state.mode !== "draft" || state.upgradeDraft.length === 0) {
    return;
  }
  let bestIndex = 0;
  let bestScore = -Infinity;
  state.upgradeDraft.forEach((upgrade, index) => {
    const score = scoreAutoUpgrade(upgrade);
    if (score > bestScore) {
      bestScore = score;
      bestIndex = index;
    }
  });
  chooseUpgrade(bestIndex);
}

function startWave() {
  state.spawnTimer = 0.3;
  state.waveTimer = 0;
  state.bossSpawned = false;
  state.chargeTarget = getChargeTarget();
  state.waveMinDuration = getWaveMinDuration();
  state.enemies = [];
  state.shards = [];
  state.clearFlash = 0.18;
  state.phaseBanner = {
    text: state.wave % currentRunConfig().bossEvery === 0 ? `第 ${state.wave} 波 · 中继增压` : `第 ${state.wave} 波 · 星域稳定`,
    life: 1.7,
  };
  addBurst(WORLD.centerX, WORLD.centerY, "#8ef2ff", 22);
  addBurst(WORLD.centerX, WORLD.centerY, "#c6ff9a", 14);
  const bossWave = state.wave % currentRunConfig().bossEvery === 0;
  const base = 4 + Math.floor(state.wave * 1.3);
  for (let i = 0; i < Math.min(3, base); i += 1) {
    spawnEnemy("seeker", true);
  }
  if (bossWave) {
    spawnEnemy("brute", true);
  }
  updateHud();
}

function spawnWave() {
  startWave();
}

function spawnEnemy(kind = "seeker", seeded = false) {
  const config = currentConfig();
  const bossWave = state.wave % currentRunConfig().bossEvery === 0;
  const angle = Math.random() * TAU;
  const edge = Math.floor(Math.random() * 4);
  const radius = Math.max(WORLD.width, WORLD.height) * 0.58;
  const baseX = WORLD.centerX + Math.cos(angle) * radius;
  const baseY = WORLD.centerY + Math.sin(angle) * radius;
  const isBrute = kind === "brute";
  const hp = isBrute ? Math.round((5 + state.wave * 0.8) * config.enemyHealthMul) : Math.round((1 + state.wave * 0.18) * config.enemyHealthMul);
  const speed = isBrute ? config.enemySpeed * 0.68 : config.enemySpeed * (0.92 + Math.random() * 0.25);
  state.enemies.push({
    x: seeded ? WORLD.centerX + randomRange(-radius * 0.5, radius * 0.5) : baseX,
    y: seeded ? WORLD.centerY + randomRange(-radius * 0.5, radius * 0.5) : baseY,
    vx: 0,
    vy: 0,
    hp,
    maxHp: hp,
    speed,
    radius: isBrute ? 23 + state.wave * 0.22 : 14 + Math.min(8, state.wave * 0.1),
    kind,
    drift: randomRange(0.15, 0.55),
    value: isBrute ? 8 : 3,
    hue: isBrute || bossWave ? "#ff9bb7" : "#8ef2ff",
  });
}

function spawnShard(x, y, value = 1, hue = "#c6ff9a") {
  state.shards.push({
    x,
    y,
    vx: randomRange(-42, 42),
    vy: randomRange(-42, 42),
    value,
    hue,
    life: 9,
    radius: 7 + value,
  });
}

function addBurst(x, y, color, count = 8) {
  for (let i = 0; i < count; i += 1) {
    const angle = (TAU * i) / count + Math.random() * 0.18;
    const speed = 70 + Math.random() * 170;
    state.bursts.push({
      x,
      y,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      life: 0.35 + Math.random() * 0.45,
      color,
      size: 1.5 + Math.random() * 2.8,
    });
  }
}

function addPulse(x, y, color, radius) {
  state.bursts.push({
    x,
    y,
    vx: 0,
    vy: 0,
    life: 0.28,
    color,
    size: radius,
    pulse: true,
  });
}

function fireBullet(target) {
  const config = currentConfig();
  const { x, y, angle } = state.player;
  const aim = normalize(target.x - x, target.y - y);
  const speed = config.bulletSpeed * (1 + state.scoreMul * 0.03);
  state.bullets.push({
    x: x + Math.cos(angle) * 20,
    y: y + Math.sin(angle) * 20,
    vx: aim.x * speed,
    vy: aim.y * speed,
    life: 1.1,
    damage: 1,
    trail: [],
    targetId: target.id,
  });
  addBurst(x, y, "#8ef2ff", 5);
}

function triggerDash() {
  const config = currentConfig();
  if (state.dashCooldown > 0 || state.mode !== "playing") {
    return;
  }
  const facing = normalize(state.player.vx || Math.cos(state.player.angle), state.player.vy || Math.sin(state.player.angle));
  state.dashActive = config.dashDuration * state.dashDurationMul;
  state.dashCooldown = config.dashCooldown * state.dashCooldownMul;
  state.invulnerable = Math.max(state.invulnerable, 0.28 + state.dashActive);
  state.player.vx += facing.x * 260;
  state.player.vy += facing.y * 260;
  state.shake = Math.max(state.shake, 3);
  addBurst(state.player.x, state.player.y, "#c6ff9a", 10);
}

function triggerPulse() {
  const config = currentConfig();
  if (state.pulseCooldown > 0 || state.mode !== "playing") {
    return;
  }
  state.pulseActive = 0.24;
  state.pulseCooldown = config.pulseCooldown * state.pulseCooldownMul;
  const radius = config.pulseRadius * state.pulseRadiusMul;
  const damage = config.pulseDamage + state.pulseDamageMul;
  addPulse(state.player.x, state.player.y, "#8ef2ff", radius);
  addPulse(state.player.x, state.player.y, "#c6ff9a", radius * 0.72);
  state.enemies.forEach((enemy) => {
    const dx = enemy.x - state.player.x;
    const dy = enemy.y - state.player.y;
    const dist = Math.hypot(dx, dy);
    if (dist <= radius + enemy.radius) {
      enemy.hp -= damage;
      const away = normalize(dx || 1, dy || 0);
      enemy.vx += away.x * 200;
      enemy.vy += away.y * 200;
    }
  });
  addBurst(state.player.x, state.player.y, "#f4ff8e", 18);
}

function completeEnemyKill(enemy) {
  state.score += Math.round((enemy.kind === "brute" ? 85 : 24) * state.scoreMul * state.combo);
  state.charge += Math.max(1, Math.round((enemy.value + 1) * state.chargeMul));
  state.combo = Math.min(9, state.combo + 1);
  state.comboTimer = 2.2 * state.comboWindowMul;
  state.bestScore = Math.max(state.bestScore, state.score);
  saveBestScore(state.bestScore);
  addBurst(enemy.x, enemy.y, enemy.hue, enemy.kind === "brute" ? 22 : 14);
  spawnShard(enemy.x, enemy.y, enemy.kind === "brute" ? 3 : 1, enemy.kind === "brute" ? "#ff9bb7" : "#c6ff9a");
  if (enemy.kind === "brute") {
    spawnShard(enemy.x + 12, enemy.y - 6, 2, "#8ef2ff");
    spawnShard(enemy.x - 14, enemy.y + 8, 2, "#f4ff8e");
  }
  if (state.chainLightning > 0) {
    const chainCount = Math.min(state.chainLightning, 3);
    const nearby = state.enemies
      .filter((other) => other !== enemy)
      .map((other) => ({ enemy: other, dist: Math.hypot(other.x - enemy.x, other.y - enemy.y) }))
      .filter((entry) => entry.dist < 130)
      .sort((a, b) => a.dist - b.dist)
      .slice(0, chainCount);
    nearby.forEach((entry) => {
      entry.enemy.hp -= 1;
      addBurst(entry.enemy.x, entry.enemy.y, "#8ef2ff", 6);
    });
  }
}

function endGame(victory) {
  state.mode = "results";
  state.upgradeDraft = [];
  if (state.score > state.bestScore) {
    state.bestScore = state.score;
    saveBestScore(state.bestScore);
  }
  updateHud();
  upgradeSelect.classList.add("hidden");
  overlay.classList.remove("drafting");
  showOverlay(
    victory ? "COMPLETE" : "RUN ENDED",
    victory ? "星炉中继完成" : "中继失稳",
    victory
      ? `任务完成。本轮波次 ${state.wave}，收集了 ${state.upgrades.length} 个永久模块，连锁最高 ${state.combo}x。可以重新进入更高强度的循环。`
      : `中继失稳后结束。本轮波次 ${state.wave}，收集了 ${state.upgrades.length} 个永久模块。下次可以继续朝更高的收敛推进。`,
    "重新开始"
  );
  updateSessionStrip();
}

function updateTargeting(delta) {
  state.fireCooldown = Math.max(0, state.fireCooldown - delta);
  if (state.mode !== "playing" || state.enemies.length === 0) {
    return;
  }
  const nearest = state.enemies
    .map((enemy) => ({ enemy, dist: Math.hypot(enemy.x - state.player.x, enemy.y - state.player.y) }))
    .filter((entry) => entry.dist <= state.targetRange)
    .sort((a, b) => a.dist - b.dist)[0];
  if (!nearest || state.fireCooldown > 0) {
    return;
  }
  fireBullet(nearest.enemy);
  state.fireCooldown = currentConfig().fireRate * state.fireRateMul;
}

function updatePlayer(delta) {
  const config = currentConfig();
  const moveSpeed = config.moveSpeed * state.moveSpeedMul;
  const accel = 8.5;
  let inputX = 0;
  let inputY = 0;

  if (state.pointer.active) {
    inputX += state.pointer.x - state.player.x;
    inputY += state.pointer.y - state.player.y;
  } else {
    if (state.keyState.left) inputX -= 1;
    if (state.keyState.right) inputX += 1;
    if (state.keyState.up) inputY -= 1;
    if (state.keyState.down) inputY += 1;
  }

  if (inputX !== 0 || inputY !== 0) {
    const dir = normalize(inputX, inputY);
    state.player.vx += dir.x * accel * moveSpeed * delta;
    state.player.vy += dir.y * accel * moveSpeed * delta;
    state.player.angle = Math.atan2(dir.y, dir.x);
  } else {
    state.player.vx *= Math.pow(0.86, delta * 60);
    state.player.vy *= Math.pow(0.86, delta * 60);
  }

  const velocityLimit = moveSpeed * (state.dashActive > 0 ? 1.9 : 1);
  const vel = length(state.player.vx, state.player.vy);
  if (vel > velocityLimit) {
    const norm = normalize(state.player.vx, state.player.vy);
    state.player.vx = norm.x * velocityLimit;
    state.player.vy = norm.y * velocityLimit;
  }

  state.player.x += state.player.vx * delta;
  state.player.y += state.player.vy * delta;

  const bounds = WORLD.arenaRadius - 16;
  const dx = state.player.x - WORLD.centerX;
  const dy = state.player.y - WORLD.centerY;
  const dist = Math.hypot(dx, dy);
  if (dist > bounds) {
    const norm = normalize(dx, dy);
    state.player.x = WORLD.centerX + norm.x * bounds;
    state.player.y = WORLD.centerY + norm.y * bounds;
    state.player.vx *= 0.3;
    state.player.vy *= 0.3;
  }

  state.player.x = clamp(state.player.x, 18, WORLD.width - 18);
  state.player.y = clamp(state.player.y, 18, WORLD.height - 18);

  state.dashCooldown = Math.max(0, state.dashCooldown - delta);
  state.dashActive = Math.max(0, state.dashActive - delta);
  state.pulseCooldown = Math.max(0, state.pulseCooldown - delta);
  state.pulseActive = Math.max(0, state.pulseActive - delta);
  state.invulnerable = Math.max(0, state.invulnerable - delta);
  state.shake = Math.max(0, state.shake - delta * 4);
  state.clearFlash = Math.max(0, state.clearFlash - delta * 2);

  if (state.dashQueued) {
    state.dashQueued = false;
    triggerDash();
  }
  if (state.pulseQueued) {
    state.pulseQueued = false;
    triggerPulse();
  }

  updateTargeting(delta);
}

function updateEnemies(delta) {
  const config = currentConfig();
  const player = state.player;
  const survivors = [];
  for (const enemy of state.enemies) {
    const dx = player.x - enemy.x;
    const dy = player.y - enemy.y;
    const dir = normalize(dx, dy);
    const speedMul = enemy.kind === "brute" ? 0.84 : 1;
    enemy.vx += dir.x * enemy.speed * speedMul * delta;
    enemy.vy += dir.y * enemy.speed * speedMul * delta;
    enemy.vx *= Math.pow(0.86, delta * 60);
    enemy.vy *= Math.pow(0.86, delta * 60);
    enemy.x += enemy.vx * delta;
    enemy.y += enemy.vy * delta;
    enemy.x += Math.sin(state.waveTimer * enemy.drift + enemy.radius) * 8 * delta;
    enemy.y += Math.cos(state.waveTimer * enemy.drift * 0.8 + enemy.radius) * 7 * delta;
    enemy.life = (enemy.life || 8) - delta;

    const hitDist = Math.hypot(enemy.x - player.x, enemy.y - player.y);
    if (hitDist < enemy.radius + player.radius + 4 && state.invulnerable <= 0) {
      if (state.waveBarrier > 0) {
        state.waveBarrier -= 1;
        state.invulnerable = 0.6;
        addBurst(player.x, player.y, "#c6ff9a", 14);
      } else {
        state.health -= 1;
        state.combo = 1;
        state.comboTimer = 0;
        state.shake = 4;
        state.invulnerable = 0.55;
        addBurst(player.x, player.y, "#ff819e", 18);
        if (state.health <= 0) {
          endGame(false);
          return;
        }
      }
    }

    if (enemy.hp <= 0 || enemy.life <= 0) {
      completeEnemyKill(enemy);
      continue;
    }
    survivors.push(enemy);
  }
  state.enemies = survivors;

  if (state.enemies.length === 0 && state.mode === "playing") {
    state.phaseBanner = { text: "中继区已净空", life: 1.2 };
  }
}

function updateBullets(delta) {
  const next = [];
  for (const bullet of state.bullets) {
    const driftTarget = state.enemies
      .map((enemy) => ({ enemy, dist: Math.hypot(enemy.x - bullet.x, enemy.y - bullet.y) }))
      .filter((entry) => entry.dist < 140)
      .sort((a, b) => a.dist - b.dist)[0];
    if (driftTarget) {
      const dir = normalize(driftTarget.enemy.x - bullet.x, driftTarget.enemy.y - bullet.y);
      bullet.vx = lerp(bullet.vx, dir.x * 680, 0.12);
      bullet.vy = lerp(bullet.vy, dir.y * 680, 0.12);
    }
    bullet.x += bullet.vx * delta;
    bullet.y += bullet.vy * delta;
    bullet.life -= delta;
    bullet.trail.push({ x: bullet.x, y: bullet.y, life: 0.22 });
    bullet.trail = bullet.trail.filter((segment) => (segment.life -= delta) > 0);
    let hit = false;
    for (const enemy of state.enemies) {
      const dist = Math.hypot(enemy.x - bullet.x, enemy.y - bullet.y);
      if (dist <= enemy.radius + 5) {
        enemy.hp -= bullet.damage;
        addBurst(bullet.x, bullet.y, "#8ef2ff", 6);
        hit = true;
        break;
      }
    }
    if (!hit && bullet.life > 0) {
      next.push(bullet);
    }
  }
  state.bullets = next;
}

function updateShards(delta) {
  const next = [];
  for (const shard of state.shards) {
    const dx = state.player.x - shard.x;
    const dy = state.player.y - shard.y;
    const dist = Math.hypot(dx, dy);
    const pullRange = 92 * state.magnetMul;
    if (dist < pullRange) {
      const dir = normalize(dx, dy);
      shard.vx += dir.x * 260 * delta;
      shard.vy += dir.y * 260 * delta;
    }
    shard.vx *= Math.pow(0.93, delta * 60);
    shard.vy *= Math.pow(0.93, delta * 60);
    shard.x += shard.vx * delta;
    shard.y += shard.vy * delta;
    shard.life -= delta;
    if (dist <= state.player.radius + shard.radius + 4) {
      state.charge += Math.max(1, shard.value);
      state.score += Math.round(10 * state.scoreMul * state.combo);
      state.combo = Math.min(9, state.combo + 0.15);
      state.comboTimer = 2.3 * state.comboWindowMul;
      state.bestScore = Math.max(state.bestScore, state.score);
      saveBestScore(state.bestScore);
      addBurst(shard.x, shard.y, shard.hue, 8);
      continue;
    }
    if (shard.life > 0) {
      next.push(shard);
    }
  }
  state.shards = next;
}

function updateBursts(delta) {
  const next = [];
  for (const burst of state.bursts) {
    burst.life -= delta;
    if (!burst.pulse) {
      burst.x += burst.vx * delta;
      burst.y += burst.vy * delta;
      burst.vx *= Math.pow(0.9, delta * 60);
      burst.vy *= Math.pow(0.9, delta * 60);
    }
    if (burst.life > 0) {
      next.push(burst);
    }
  }
  state.bursts = next;
}

function updateCombo(delta) {
  if (state.comboTimer > 0) {
    state.comboTimer = Math.max(0, state.comboTimer - delta);
    if (state.comboTimer === 0) {
      state.combo = 1;
    }
  }
}

function drawBackground() {
  const w = WORLD.width;
  const h = WORLD.height;
  const glow = ctx.createRadialGradient(WORLD.centerX, WORLD.centerY, 40, WORLD.centerX, WORLD.centerY, Math.max(w, h) * 0.7);
  glow.addColorStop(0, "rgba(142, 242, 255, 0.12)");
  glow.addColorStop(0.42, "rgba(255, 129, 158, 0.04)");
  glow.addColorStop(1, "rgba(4, 8, 18, 0.95)");
  ctx.fillStyle = glow;
  ctx.fillRect(0, 0, w, h);
  ctx.save();
  ctx.translate(WORLD.centerX, WORLD.centerY);
  ctx.strokeStyle = "rgba(142, 242, 255, 0.08)";
  ctx.lineWidth = 1;
  for (let i = 1; i <= 5; i += 1) {
    ctx.beginPath();
    ctx.arc(0, 0, WORLD.coreRadius + i * 34, 0, TAU);
    ctx.stroke();
  }
  ctx.strokeStyle = "rgba(198, 255, 154, 0.08)";
  for (let i = 0; i < 12; i += 1) {
    const angle = (TAU * i) / 12 + state.waveTimer * 0.08;
    ctx.beginPath();
    ctx.moveTo(Math.cos(angle) * 68, Math.sin(angle) * 68);
    ctx.lineTo(Math.cos(angle) * WORLD.arenaRadius, Math.sin(angle) * WORLD.arenaRadius);
    ctx.stroke();
  }
  ctx.restore();

  state.stars.forEach((star) => {
    const twinkle = 0.55 + Math.sin(state.waveTimer * star.speed + star.phase) * 0.35;
    ctx.fillStyle = star.hue === "accent-2" ? `rgba(198, 255, 154, ${0.5 + twinkle * 0.4})` : `rgba(142, 242, 255, ${0.45 + twinkle * 0.4})`;
    ctx.beginPath();
    ctx.arc(star.x, star.y, star.size * (0.8 + twinkle * 0.6), 0, TAU);
    ctx.fill();
  });
}

function drawCore() {
  const t = state.waveTimer;
  ctx.save();
  ctx.translate(WORLD.centerX, WORLD.centerY);
  const pulse = 1 + Math.sin(t * 2.2) * 0.04 + state.clearFlash * 0.18;
  ctx.scale(pulse, pulse);
  const gradient = ctx.createRadialGradient(0, 0, 6, 0, 0, WORLD.coreRadius * 1.6);
  gradient.addColorStop(0, "rgba(244, 255, 142, 0.9)");
  gradient.addColorStop(0.34, "rgba(198, 255, 154, 0.55)");
  gradient.addColorStop(1, "rgba(142, 242, 255, 0)");
  ctx.fillStyle = gradient;
  ctx.beginPath();
  ctx.arc(0, 0, WORLD.coreRadius * 1.5, 0, TAU);
  ctx.fill();
  ctx.strokeStyle = "rgba(142, 242, 255, 0.56)";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.arc(0, 0, WORLD.coreRadius, 0, TAU);
  ctx.stroke();
  ctx.strokeStyle = "rgba(198, 255, 154, 0.42)";
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.arc(0, 0, WORLD.coreRadius - 10, 0, TAU);
  ctx.stroke();
  ctx.restore();
}

function drawPlayer() {
  const p = state.player;
  ctx.save();
  ctx.translate(p.x, p.y);
  ctx.rotate(p.angle + Math.PI / 2);
  const glow = state.dashActive > 0 ? "#c6ff9a" : "#8ef2ff";
  ctx.shadowColor = glow;
  ctx.shadowBlur = 22;
  ctx.fillStyle = "rgba(8, 16, 28, 0.95)";
  ctx.beginPath();
  ctx.moveTo(0, -18);
  ctx.lineTo(14, 14);
  ctx.lineTo(0, 8);
  ctx.lineTo(-14, 14);
  ctx.closePath();
  ctx.fill();
  ctx.strokeStyle = glow;
  ctx.lineWidth = 2;
  ctx.stroke();
  ctx.fillStyle = glow;
  ctx.beginPath();
  ctx.arc(0, 2, 4, 0, TAU);
  ctx.fill();
  if (state.invulnerable > 0) {
    ctx.strokeStyle = "rgba(255,255,255,0.55)";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc(0, 0, 22 + Math.sin(state.waveTimer * 12) * 2, 0, TAU);
    ctx.stroke();
  }
  ctx.restore();
}

function drawEnemy(enemy) {
  ctx.save();
  ctx.translate(enemy.x, enemy.y);
  const pulse = enemy.kind === "brute" ? 1 + Math.sin(state.waveTimer * 3 + enemy.x * 0.01) * 0.08 : 1;
  ctx.scale(pulse, pulse);
  ctx.shadowColor = enemy.hue;
  ctx.shadowBlur = 18;
  ctx.fillStyle = "rgba(9, 14, 24, 0.95)";
  ctx.beginPath();
  const sides = enemy.kind === "brute" ? 8 : 6;
  for (let i = 0; i < sides; i += 1) {
    const a = (TAU * i) / sides + (enemy.kind === "brute" ? state.waveTimer * 0.25 : 0);
    const r = i % 2 === 0 ? enemy.radius : enemy.radius * 0.72;
    const x = Math.cos(a) * r;
    const y = Math.sin(a) * r;
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  }
  ctx.closePath();
  ctx.fill();
  ctx.strokeStyle = enemy.hue;
  ctx.lineWidth = 2;
  ctx.stroke();
  ctx.fillStyle = enemy.hue;
  ctx.beginPath();
  ctx.arc(0, 0, 3.5, 0, TAU);
  ctx.fill();
  ctx.restore();
}

function drawShard(shard) {
  ctx.save();
  ctx.translate(shard.x, shard.y);
  ctx.rotate(state.waveTimer * 2 + shard.x * 0.01);
  ctx.shadowColor = shard.hue;
  ctx.shadowBlur = 14;
  ctx.fillStyle = shard.hue;
  ctx.beginPath();
  ctx.moveTo(0, -shard.radius);
  ctx.lineTo(shard.radius * 0.9, 0);
  ctx.lineTo(0, shard.radius);
  ctx.lineTo(-shard.radius * 0.9, 0);
  ctx.closePath();
  ctx.fill();
  ctx.restore();
}

function drawBullet(bullet) {
  ctx.save();
  ctx.strokeStyle = "#f4ff8e";
  ctx.shadowColor = "#8ef2ff";
  ctx.shadowBlur = 14;
  ctx.lineWidth = 2;
  const trail = bullet.trail.slice(-4);
  trail.forEach((segment, index) => {
    const alpha = (index + 1) / trail.length;
    ctx.strokeStyle = `rgba(142, 242, 255, ${0.15 + alpha * 0.35})`;
    ctx.beginPath();
    ctx.moveTo(segment.x, segment.y);
    ctx.lineTo(bullet.x, bullet.y);
    ctx.stroke();
  });
  ctx.fillStyle = "#f4ff8e";
  ctx.beginPath();
  ctx.arc(bullet.x, bullet.y, 3.5, 0, TAU);
  ctx.fill();
  ctx.restore();
}

function drawBurst(burst) {
  ctx.save();
  ctx.globalAlpha = Math.max(0, burst.life / 0.45);
  if (burst.pulse) {
    ctx.strokeStyle = burst.color;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(burst.x, burst.y, burst.size * (1 - burst.life / 0.28), 0, TAU);
    ctx.stroke();
  } else {
    ctx.fillStyle = burst.color;
    ctx.beginPath();
    ctx.arc(burst.x, burst.y, burst.size, 0, TAU);
    ctx.fill();
  }
  ctx.restore();
}

function drawPulse() {
  if (state.pulseActive <= 0) {
    return;
  }
  ctx.save();
  const radius = currentConfig().pulseRadius * state.pulseRadiusMul * (1.0 - state.pulseActive / 0.24);
  ctx.globalAlpha = Math.max(0, state.pulseActive / 0.24);
  ctx.strokeStyle = "#c6ff9a";
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.arc(state.player.x, state.player.y, radius, 0, TAU);
  ctx.stroke();
  ctx.strokeStyle = "#8ef2ff";
  ctx.beginPath();
  ctx.arc(state.player.x, state.player.y, radius * 0.78, 0, TAU);
  ctx.stroke();
  ctx.restore();
}

function render() {
  ctx.clearRect(0, 0, WORLD.width, WORLD.height);
  drawBackground();
  drawCore();
  state.shards.forEach(drawShard);
  state.bullets.forEach(drawBullet);
  state.enemies.forEach(drawEnemy);
  drawPulse();
  state.bursts.forEach(drawBurst);
  drawPlayer();
  drawBanner();
}

function drawBanner() {
  if (state.phaseBanner.life <= 0) {
    return;
  }
  const alpha = Math.min(1, state.phaseBanner.life);
  ctx.save();
  ctx.translate(WORLD.centerX, WORLD.centerY - 120);
  ctx.globalAlpha = alpha;
  ctx.fillStyle = "rgba(6, 12, 22, 0.82)";
  ctx.strokeStyle = "rgba(142, 242, 255, 0.4)";
  ctx.lineWidth = 1;
  const width = Math.min(400, 180 + state.phaseBanner.text.length * 9);
  ctx.beginPath();
  ctx.roundRect(-width / 2, -18, width, 36, 16);
  ctx.fill();
  ctx.stroke();
  ctx.fillStyle = "#f6fbff";
  ctx.font = "700 16px Avenir Next, sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(state.phaseBanner.text, 0, 0);
  ctx.restore();
}

function loop(timestamp) {
  if (state.lastTime === 0) {
    state.lastTime = timestamp;
  }
  const delta = Math.min(0.033, (timestamp - state.lastTime) / 1000);
  state.lastTime = timestamp;

  if (state.mode === "playing") {
    mainUpdate(delta);
  } else if (state.mode === "draft") {
    updateDraft(delta);
  } else if (state.mode === "paused") {
    updateBursts(delta * 0.2);
    updatePhaseBanner(delta);
  } else {
    updateBursts(delta * 0.15);
    updatePhaseBanner(delta);
  }
  render();
  requestAnimationFrame(loop);
}

function togglePause() {
  if (state.mode === "playing") {
    state.mode = "paused";
    showOverlay("PAUSED", "星炉已冻结", "按 P、Esc 或暂停按钮恢复当前战况。暂停时你可以读一眼当前波次的收敛节奏。", "继续");
  } else if (state.mode === "paused") {
    state.mode = "playing";
    hideOverlay();
  }
  updateSessionStrip();
}

function handleKeyDown(event) {
  const key = event.key.toLowerCase();
  if (state.mode === "draft") {
    if (key === "1" || key === "2" || key === "3") {
      event.preventDefault();
      chooseUpgrade(Number(key) - 1);
    }
    return;
  }
  if (key === "arrowleft" || key === "a") {
    state.keyState.left = true;
    event.preventDefault();
  } else if (key === "arrowright" || key === "d") {
    state.keyState.right = true;
    event.preventDefault();
  } else if (key === "arrowup" || key === "w") {
    state.keyState.up = true;
    event.preventDefault();
  } else if (key === "arrowdown" || key === "s") {
    state.keyState.down = true;
    event.preventDefault();
  } else if (key === " " || key === "spacebar") {
    event.preventDefault();
    if (state.mode === "menu" || state.mode === "results") {
      startGame();
    } else if (state.mode === "paused") {
      togglePause();
    } else {
      state.dashQueued = true;
    }
  } else if (key === "e") {
    event.preventDefault();
    if (state.mode === "menu" || state.mode === "results") {
      startGame();
    } else {
      state.pulseQueued = true;
    }
  } else if (key === "p" || key === "escape") {
    if (state.mode === "playing" || state.mode === "paused") {
      event.preventDefault();
      togglePause();
    }
  }
}

function handleKeyUp(event) {
  const key = event.key.toLowerCase();
  if (key === "arrowleft" || key === "a") {
    state.keyState.left = false;
  } else if (key === "arrowright" || key === "d") {
    state.keyState.right = false;
  } else if (key === "arrowup" || key === "w") {
    state.keyState.up = false;
  } else if (key === "arrowdown" || key === "s") {
    state.keyState.down = false;
  }
}

function handlePointerMove(event) {
  if (!state.pointer.active) {
    return;
  }
  const rect = canvas.getBoundingClientRect();
  state.pointer.x = clamp(event.clientX - rect.left, 0, rect.width);
  state.pointer.y = clamp(event.clientY - rect.top, 0, rect.height);
}

function handlePointerDown(event) {
  const rect = canvas.getBoundingClientRect();
  state.pointer.active = true;
  state.pointer.x = clamp(event.clientX - rect.left, 0, rect.width);
  state.pointer.y = clamp(event.clientY - rect.top, 0, rect.height);
  canvas.setPointerCapture?.(event.pointerId);
  if (state.mode === "menu" || state.mode === "results") {
    startGame();
  } else if (state.mode === "paused") {
    togglePause();
  }
}

function handlePointerUp(event) {
  state.pointer.active = false;
  canvas.releasePointerCapture?.(event.pointerId);
}

function handleTouchAction(action) {
  if (action === "dash") {
    if (state.mode === "menu" || state.mode === "results") {
      startGame();
    } else if (state.mode === "playing") {
      triggerDash();
    } else if (state.mode === "paused") {
      togglePause();
    }
  } else if (action === "pulse") {
    if (state.mode === "menu" || state.mode === "results") {
      startGame();
    } else if (state.mode === "playing") {
      triggerPulse();
    }
  } else if (action === "pause") {
    if (state.mode === "playing" || state.mode === "paused") {
      togglePause();
    } else {
      startGame();
    }
  }
}

function bindEvents() {
  window.addEventListener("resize", resizeCanvas);
  window.addEventListener("keydown", handleKeyDown);
  window.addEventListener("keyup", handleKeyUp);
  document.addEventListener("visibilitychange", () => {
    if (document.hidden && state.mode === "playing") {
      togglePause();
    }
  });

  startButton.addEventListener("click", () => {
    if (state.mode === "paused") {
      togglePause();
    } else {
      startGame();
    }
  });

  modeButtons.forEach((button) => {
    button.addEventListener("click", () => setDifficulty(button.dataset.mode));
  });

  runButtons.forEach((button) => {
    button.addEventListener("click", () => setRunMode(button.dataset.run));
  });

  touchButtons.forEach((button) => {
    button.addEventListener("pointerdown", (event) => {
      event.preventDefault();
      button.setPointerCapture?.(event.pointerId);
      handleTouchAction(button.dataset.action);
    });
  });

  canvas.addEventListener("pointerdown", handlePointerDown);
  canvas.addEventListener("pointermove", handlePointerMove);
  canvas.addEventListener("pointerup", handlePointerUp);
  canvas.addEventListener("pointerleave", handlePointerUp);
  canvas.addEventListener("pointercancel", handlePointerUp);
}

function startGame() {
  resetGame();
  beginTask();
}

function beginTask() {
  state.mode = "playing";
  hideOverlay();
  upgradeSelect.classList.add("hidden");
  state.lastTime = performance.now();
  startWave();
  updateHud();
}

function applyEndOfWaveSetup() {
  if (state.runMode === "classic" && state.wave > currentRunConfig().maxWaves) {
    endGame(true);
    return;
  }
  if (currentRunConfig().draftBetweenWaves) {
    openUpgradeDraft();
  } else {
    state.mode = "playing";
    startWave();
  }
}

function maybeAdvanceAfterCharge() {
  if (state.charge < state.chargeTarget || state.mode !== "playing" || state.waveTimer < state.waveMinDuration) {
    return;
  }
  state.score += Math.round((150 + state.wave * 32) * state.scoreMul * Math.max(1, state.combo));
  state.bestScore = Math.max(state.bestScore, state.score);
  saveBestScore(state.bestScore);
  state.mode = "draft";
  state.wave += 1;
  state.charge = 0;
  state.enemies = [];
  state.bullets = [];
  state.shards = [];
  state.clearFlash = 0.22;
  state.phaseBanner = {
    text: state.wave % currentRunConfig().bossEvery === 0 ? `第 ${state.wave - 1} 波完成 · 中继进入增压` : `第 ${state.wave - 1} 波完成 · 中继稳定`,
    life: 1.7,
  };
  if (state.aegisHeal > 0) {
    state.health = Math.min(state.maxHealth, state.health + state.aegisHeal);
  }
  addBurst(WORLD.centerX, WORLD.centerY, "#8ef2ff", 18);
  addBurst(WORLD.centerX, WORLD.centerY, "#c6ff9a", 10);
  updateHud();
  applyEndOfWaveSetup();
}

function mainUpdate(delta) {
  if (state.mode !== "playing") {
    return;
  }
  state.waveTimer += delta;
  updateCombo(delta);
  updatePlayer(delta);
  updateBullets(delta);
  updateEnemies(delta);
  updateShards(delta);
  updateBursts(delta);
  updatePhaseBanner(delta);
  maybeAdvanceAfterCharge();
  updateHud();
}

function updateDraft(delta) {
  if (state.mode !== "draft") {
    return;
  }
  state.draftTimer = Math.max(0, state.draftTimer - delta);
  updatePhaseBanner(delta);
  if (state.draftTimer === 0) {
    chooseAutoUpgrade();
  } else {
    updateHud();
  }
}

function updateBullets(delta) {
  const next = [];
  for (const bullet of state.bullets) {
    bullet.x += bullet.vx * delta;
    bullet.y += bullet.vy * delta;
    bullet.life -= delta;
    bullet.trail.push({ x: bullet.x, y: bullet.y, life: 0.24 });
    bullet.trail = bullet.trail.filter((segment) => (segment.life -= delta) > 0);
    let hit = false;
    for (const enemy of state.enemies) {
      const dist = Math.hypot(enemy.x - bullet.x, enemy.y - bullet.y);
      if (dist <= enemy.radius + 5) {
        enemy.hp -= bullet.damage;
        addBurst(bullet.x, bullet.y, "#8ef2ff", 5);
        hit = true;
        break;
      }
    }
    if (!hit && bullet.life > 0 && bullet.x > -60 && bullet.x < WORLD.width + 60 && bullet.y > -60 && bullet.y < WORLD.height + 60) {
      next.push(bullet);
    }
  }
  state.bullets = next;
}

function updateEnemies(delta) {
  const player = state.player;
  const survivors = [];
  for (const enemy of state.enemies) {
    const dx = player.x - enemy.x;
    const dy = player.y - enemy.y;
    const dir = normalize(dx, dy);
    enemy.vx += dir.x * enemy.speed * delta;
    enemy.vy += dir.y * enemy.speed * delta;
    enemy.vx *= Math.pow(0.88, delta * 60);
    enemy.vy *= Math.pow(0.88, delta * 60);
    enemy.x += enemy.vx * delta;
    enemy.y += enemy.vy * delta;
    enemy.x += Math.sin(state.waveTimer * enemy.drift + enemy.radius) * 6 * delta;
    enemy.y += Math.cos(state.waveTimer * enemy.drift * 0.7 + enemy.radius) * 5 * delta;

    const dist = Math.hypot(enemy.x - player.x, enemy.y - player.y);
    if (dist <= enemy.radius + player.radius + 4) {
      if (state.invulnerable > 0) {
        enemy.hp -= 1;
        addBurst(enemy.x, enemy.y, "#c6ff9a", 4);
      } else if (state.waveBarrier > 0) {
        state.waveBarrier -= 1;
        state.invulnerable = 0.6;
        addBurst(player.x, player.y, "#c6ff9a", 14);
      } else {
        state.health -= 1;
        state.combo = 1;
        state.comboTimer = 0;
        state.shake = 4;
        state.invulnerable = 0.55;
        addBurst(player.x, player.y, "#ff819e", 16);
        if (state.health <= 0) {
          endGame(false);
          return;
        }
      }
    }

    if (enemy.hp <= 0) {
      completeEnemyKill(enemy);
      continue;
    }
    survivors.push(enemy);
  }
  state.enemies = survivors;
  state.spawnTimer -= delta;
  const config = currentConfig();
  if (state.spawnTimer <= 0) {
    const bossWave = state.wave % currentRunConfig().bossEvery === 0;
    const kind = bossWave && !state.bossSpawned ? "brute" : Math.random() > 0.76 ? "brute" : "seeker";
    if (kind === "brute") {
      state.bossSpawned = true;
    }
    if (state.enemies.length < 16 + state.wave * 1.2) {
      spawnEnemy(kind, false);
    }
    state.spawnTimer = Math.max(0.42, config.spawnInterval / (1 + state.wave * 0.06));
  }
}

function updateShards(delta) {
  const next = [];
  for (const shard of state.shards) {
    const dx = state.player.x - shard.x;
    const dy = state.player.y - shard.y;
    const dist = Math.hypot(dx, dy);
    const pull = 92 * state.magnetMul;
    if (dist < pull) {
      const dir = normalize(dx, dy);
      shard.vx += dir.x * 240 * delta;
      shard.vy += dir.y * 240 * delta;
    }
    shard.vx *= Math.pow(0.92, delta * 60);
    shard.vy *= Math.pow(0.92, delta * 60);
    shard.x += shard.vx * delta;
    shard.y += shard.vy * delta;
    shard.life -= delta;
    if (dist <= state.player.radius + shard.radius + 4) {
      state.charge += Math.max(1, Math.round(shard.value * state.chargeMul));
      state.score += Math.round(10 * state.scoreMul * Math.max(1, state.combo));
      state.combo = Math.min(9, state.combo + 0.15);
      state.comboTimer = 2.4 * state.comboWindowMul;
      state.bestScore = Math.max(state.bestScore, state.score);
      saveBestScore(state.bestScore);
      addBurst(shard.x, shard.y, shard.hue, 8);
      continue;
    }
    if (shard.life > 0) {
      next.push(shard);
    }
  }
  state.shards = next;
}

function updateBursts(delta) {
  const next = [];
  for (const burst of state.bursts) {
    burst.life -= delta;
    if (!burst.pulse) {
      burst.x += burst.vx * delta;
      burst.y += burst.vy * delta;
      burst.vx *= Math.pow(0.9, delta * 60);
      burst.vy *= Math.pow(0.9, delta * 60);
    }
    if (burst.life > 0) {
      next.push(burst);
    }
  }
  state.bursts = next;
}

function updatePhaseBanner(delta) {
  state.phaseBanner.life = Math.max(0, state.phaseBanner.life - delta);
}

function updateCombo(delta) {
  if (state.comboTimer > 0) {
    state.comboTimer = Math.max(0, state.comboTimer - delta);
    if (state.comboTimer === 0) {
      state.combo = 1;
    }
  }
}

function drawBackground() {
  const w = WORLD.width;
  const h = WORLD.height;
  const bg = ctx.createLinearGradient(0, 0, 0, h);
  bg.addColorStop(0, "rgba(4, 9, 18, 1)");
  bg.addColorStop(1, "rgba(18, 11, 36, 1)");
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, w, h);

  const glow = ctx.createRadialGradient(WORLD.centerX, WORLD.centerY, 10, WORLD.centerX, WORLD.centerY, WORLD.arenaRadius * 1.4);
  glow.addColorStop(0, "rgba(142, 242, 255, 0.16)");
  glow.addColorStop(0.4, "rgba(255, 129, 158, 0.06)");
  glow.addColorStop(1, "rgba(4, 9, 18, 0)");
  ctx.fillStyle = glow;
  ctx.fillRect(0, 0, w, h);

  state.stars.forEach((star) => {
    const twinkle = 0.5 + Math.sin(state.waveTimer * star.speed + star.phase) * 0.35;
    ctx.fillStyle = star.hue === "accent-2" ? `rgba(198, 255, 154, ${0.45 + twinkle * 0.42})` : `rgba(142, 242, 255, ${0.42 + twinkle * 0.42})`;
    ctx.beginPath();
    ctx.arc(star.x, star.y, star.size * (0.8 + twinkle * 0.5), 0, TAU);
    ctx.fill();
  });

  ctx.save();
  ctx.translate(WORLD.centerX, WORLD.centerY);
  ctx.strokeStyle = "rgba(142, 242, 255, 0.07)";
  ctx.lineWidth = 1;
  for (let i = 1; i <= 4; i += 1) {
    ctx.beginPath();
    ctx.arc(0, 0, WORLD.coreRadius + i * 38, 0, TAU);
    ctx.stroke();
  }
  ctx.strokeStyle = "rgba(198, 255, 154, 0.07)";
  for (let i = 0; i < 10; i += 1) {
    const angle = (TAU * i) / 10 + state.waveTimer * 0.1;
    ctx.beginPath();
    ctx.moveTo(Math.cos(angle) * 58, Math.sin(angle) * 58);
    ctx.lineTo(Math.cos(angle) * WORLD.arenaRadius, Math.sin(angle) * WORLD.arenaRadius);
    ctx.stroke();
  }
  ctx.restore();
}

function drawCore() {
  ctx.save();
  ctx.translate(WORLD.centerX, WORLD.centerY);
  const pulse = 1 + Math.sin(state.waveTimer * 2.1) * 0.04 + state.clearFlash * 0.18;
  ctx.scale(pulse, pulse);
  const gradient = ctx.createRadialGradient(0, 0, 6, 0, 0, WORLD.coreRadius * 1.8);
  gradient.addColorStop(0, "rgba(244, 255, 142, 0.95)");
  gradient.addColorStop(0.36, "rgba(198, 255, 154, 0.62)");
  gradient.addColorStop(1, "rgba(142, 242, 255, 0)");
  ctx.fillStyle = gradient;
  ctx.beginPath();
  ctx.arc(0, 0, WORLD.coreRadius * 1.6, 0, TAU);
  ctx.fill();
  ctx.strokeStyle = "rgba(142, 242, 255, 0.5)";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.arc(0, 0, WORLD.coreRadius, 0, TAU);
  ctx.stroke();
  ctx.strokeStyle = "rgba(198, 255, 154, 0.38)";
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.arc(0, 0, WORLD.coreRadius - 10, 0, TAU);
  ctx.stroke();
  ctx.restore();
}

function drawPlayer() {
  const p = state.player;
  ctx.save();
  ctx.translate(p.x, p.y);
  ctx.rotate(p.angle + Math.PI / 2);
  const glow = state.dashActive > 0 ? "#c6ff9a" : "#8ef2ff";
  ctx.shadowColor = glow;
  ctx.shadowBlur = 22;
  ctx.fillStyle = "rgba(8, 16, 28, 0.95)";
  ctx.beginPath();
  ctx.moveTo(0, -18);
  ctx.lineTo(14, 14);
  ctx.lineTo(0, 8);
  ctx.lineTo(-14, 14);
  ctx.closePath();
  ctx.fill();
  ctx.strokeStyle = glow;
  ctx.lineWidth = 2;
  ctx.stroke();
  ctx.fillStyle = glow;
  ctx.beginPath();
  ctx.arc(0, 2, 4, 0, TAU);
  ctx.fill();
  if (state.invulnerable > 0) {
    ctx.strokeStyle = "rgba(255,255,255,0.55)";
    ctx.lineWidth = 1.4;
    ctx.beginPath();
    ctx.arc(0, 0, 22 + Math.sin(state.waveTimer * 12) * 2, 0, TAU);
    ctx.stroke();
  }
  ctx.restore();
}

function drawEnemy(enemy) {
  ctx.save();
  ctx.translate(enemy.x, enemy.y);
  const pulse = enemy.kind === "brute" ? 1 + Math.sin(state.waveTimer * 3 + enemy.x * 0.01) * 0.08 : 1;
  ctx.scale(pulse, pulse);
  ctx.shadowColor = enemy.hue;
  ctx.shadowBlur = 18;
  ctx.fillStyle = "rgba(9, 14, 24, 0.95)";
  ctx.beginPath();
  const sides = enemy.kind === "brute" ? 8 : 6;
  for (let i = 0; i < sides; i += 1) {
    const a = (TAU * i) / sides + (enemy.kind === "brute" ? state.waveTimer * 0.25 : 0);
    const r = i % 2 === 0 ? enemy.radius : enemy.radius * 0.72;
    const x = Math.cos(a) * r;
    const y = Math.sin(a) * r;
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  }
  ctx.closePath();
  ctx.fill();
  ctx.strokeStyle = enemy.hue;
  ctx.lineWidth = 2;
  ctx.stroke();
  ctx.fillStyle = enemy.hue;
  ctx.beginPath();
  ctx.arc(0, 0, 3.5, 0, TAU);
  ctx.fill();
  ctx.restore();
}

function drawShard(shard) {
  ctx.save();
  ctx.translate(shard.x, shard.y);
  ctx.rotate(state.waveTimer * 2 + shard.x * 0.01);
  ctx.shadowColor = shard.hue;
  ctx.shadowBlur = 14;
  ctx.fillStyle = shard.hue;
  ctx.beginPath();
  ctx.moveTo(0, -shard.radius);
  ctx.lineTo(shard.radius * 0.9, 0);
  ctx.lineTo(0, shard.radius);
  ctx.lineTo(-shard.radius * 0.9, 0);
  ctx.closePath();
  ctx.fill();
  ctx.restore();
}

function drawBullet(bullet) {
  ctx.save();
  const trail = bullet.trail.slice(-4);
  trail.forEach((segment, index) => {
    const alpha = (index + 1) / trail.length;
    ctx.strokeStyle = `rgba(142, 242, 255, ${0.15 + alpha * 0.35})`;
    ctx.beginPath();
    ctx.moveTo(segment.x, segment.y);
    ctx.lineTo(bullet.x, bullet.y);
    ctx.stroke();
  });
  ctx.shadowColor = "#8ef2ff";
  ctx.shadowBlur = 14;
  ctx.fillStyle = "#f4ff8e";
  ctx.beginPath();
  ctx.arc(bullet.x, bullet.y, 3.5, 0, TAU);
  ctx.fill();
  ctx.restore();
}

function drawBurst(burst) {
  ctx.save();
  ctx.globalAlpha = Math.max(0, burst.life / 0.45);
  if (burst.pulse) {
    ctx.strokeStyle = burst.color;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(burst.x, burst.y, burst.size * (1 - burst.life / 0.28), 0, TAU);
    ctx.stroke();
  } else {
    ctx.fillStyle = burst.color;
    ctx.beginPath();
    ctx.arc(burst.x, burst.y, burst.size, 0, TAU);
    ctx.fill();
  }
  ctx.restore();
}

function drawPulse() {
  if (state.pulseActive <= 0) {
    return;
  }
  ctx.save();
  const radius = currentConfig().pulseRadius * state.pulseRadiusMul * (1 - state.pulseActive / 0.24);
  ctx.globalAlpha = Math.max(0, state.pulseActive / 0.24);
  ctx.strokeStyle = "#c6ff9a";
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.arc(state.player.x, state.player.y, radius, 0, TAU);
  ctx.stroke();
  ctx.strokeStyle = "#8ef2ff";
  ctx.beginPath();
  ctx.arc(state.player.x, state.player.y, radius * 0.78, 0, TAU);
  ctx.stroke();
  ctx.restore();
}

function drawBanner() {
  if (state.phaseBanner.life <= 0) {
    return;
  }
  const alpha = Math.min(1, state.phaseBanner.life);
  ctx.save();
  ctx.translate(WORLD.centerX, WORLD.centerY - 120);
  ctx.globalAlpha = alpha;
  ctx.fillStyle = "rgba(6, 12, 22, 0.82)";
  ctx.strokeStyle = "rgba(142, 242, 255, 0.4)";
  ctx.lineWidth = 1;
  const width = Math.min(420, 180 + state.phaseBanner.text.length * 9);
  ctx.beginPath();
  ctx.roundRect(-width / 2, -18, width, 36, 16);
  ctx.fill();
  ctx.stroke();
  ctx.fillStyle = "#f6fbff";
  ctx.font = "700 16px Avenir Next, sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(state.phaseBanner.text, 0, 0);
  ctx.restore();
}

function render() {
  ctx.clearRect(0, 0, WORLD.width, WORLD.height);
  drawBackground();
  drawCore();
  state.shards.forEach(drawShard);
  state.bullets.forEach(drawBullet);
  state.enemies.forEach(drawEnemy);
  drawPulse();
  state.bursts.forEach(drawBurst);
  drawPlayer();
  drawBanner();
}

function init() {
  resizeCanvas();
  spawnStars();
  syncModeButtons();
  syncRunButtons();
  updateOverlayForMenu();
  updateHud();
  bindEvents();
  requestAnimationFrame(loop);
}

init();
