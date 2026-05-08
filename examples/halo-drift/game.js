// Long-task browser mini-game baseline for autonomous reruns.
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const overlay = document.getElementById("overlay");
const overlayTag = document.getElementById("overlayTag");
const overlayTitle = document.getElementById("overlayTitle");
const overlayText = document.getElementById("overlayText");
const startButton = document.getElementById("startButton");
const scoreLabel = document.getElementById("score");
const healthLabel = document.getElementById("health");
const phaseLabel = document.getElementById("phase");
const timeLabel = document.getElementById("time");
const upgradesLabel = document.getElementById("upgrades");
const chargeLabel = document.getElementById("charge");
const bestBadge = document.getElementById("bestBadge");
const modeButtons = Array.from(document.querySelectorAll(".mode-button"));
const runButtons = Array.from(document.querySelectorAll(".run-button"));
const touchButtons = Array.from(document.querySelectorAll(".touch-button"));
const upgradeSelect = document.getElementById("upgradeSelect");
const upgradeGrid = document.getElementById("upgradeGrid");

const STORAGE_KEY = "haloDrift.bestScore";
const TAU = Math.PI * 2;
const CENTER = { x: 0, y: 0 };
const TRACKS = [112, 168, 224, 280];
const MODE_CONFIG = {
  calm: {
    name: "CALM",
    spawnRate: 1.02,
    hazardRate: 0.72,
    motesPerPhase: 5,
    pulseCooldown: 1.25,
    rotationSpeed: 2.1,
    driftFactor: 0.65,
  },
  standard: {
    name: "STANDARD",
    spawnRate: 0.9,
    hazardRate: 0.92,
    motesPerPhase: 6,
    pulseCooldown: 1.55,
    rotationSpeed: 2.45,
    driftFactor: 0.82,
  },
  storm: {
    name: "STORM",
    spawnRate: 0.78,
    hazardRate: 1.16,
    motesPerPhase: 7,
    pulseCooldown: 1.85,
    rotationSpeed: 2.85,
    driftFactor: 1,
  },
};

const RUN_CONFIG = {
  classic: {
    name: "CLASSIC",
    phaseCap: 5,
    chargeScale: 1,
    spawnScale: 1,
    hazardScale: 1,
    draftBetweenPhases: false,
  },
  marathon: {
    name: "MARATHON",
    phaseCap: Infinity,
    chargeScale: 1.1,
    spawnScale: 0.94,
    hazardScale: 1.08,
    draftBetweenPhases: true,
  },
};

const UPGRADE_POOL = [
  {
    id: "magnet",
    tag: "ORBIT",
    name: "CORE MAGNET",
    description: "收集窗口更宽，靠近回声时更容易吸入。"
      + " 适合长局里稳住节奏。",
    apply(game) {
      game.collectAngleThreshold += 0.04;
      game.collectRadiusThreshold += 10;
    },
  },
  {
    id: "thrust",
    tag: "MOVE",
    name: "THRUST TUNE",
    description: "旋转响应更快，换轨更顺滑。"
      + " 让你在高压阶段更灵活。",
    apply(game) {
      game.rotationSpeedMul += 0.12;
    },
  },
  {
    id: "pulse",
    tag: "BURST",
    name: "PULSE LATTICE",
    description: "脉冲范围扩大，清理危机时更从容。"
      + " 代价是要把握好冷却。",
    apply(game) {
      game.pulseAngleThreshold += 0.08;
      game.pulseRadiusThreshold += 18;
      game.pulseCooldownMul *= 0.92;
    },
  },
  {
    id: "armor",
    tag: "SURVIVE",
    name: "HULL PLATING",
    description: "获得 1 点最大生命，并立即回复 1 点生命。"
      + " 适合顶住后半程。",
    apply(game) {
      game.maxHealth += 1;
      game.health = Math.min(game.maxHealth, game.health + 1);
    },
  },
  {
    id: "signal",
    tag: "SCORE",
    name: "SIGNAL BOOST",
    description: "得分倍率提升，连击收益变高。"
      + " 让长局更有追分空间。",
    apply(game) {
      game.scoreMul += 0.18;
      game.comboWindowMul += 0.15;
    },
  },
  {
    id: "drift",
    tag: "STABLE",
    name: "DRIFT BRAKE",
    description: "虚空噪点的漂移稍微放缓，便于应对更长的局面。",
    apply(game) {
      game.hazardDriftMul *= 0.9;
    },
  },
];

const state = {
  mode: "menu",
  difficulty: "standard",
  runMode: "marathon",
  bestScore: readBestScore(),
  lastTime: 0,
  accumulator: 0,
  score: 0,
  elapsedMs: 0,
  health: 3,
  phase: 1,
  charge: 0,
  chargeTarget: 6,
  combo: 1,
  comboTimer: 0,
  pulseCooldown: 0,
  pulseActive: 0,
  pauseFlash: 0,
  shake: 0,
  victoryPulse: 0,
  rotation: -0.35,
  ringIndex: 1,
  rotLeft: false,
  rotRight: false,
  moveIn: false,
  moveOut: false,
  motes: [],
  hazards: [],
  pulses: [],
  stars: [],
  scoreBursts: [],
  phaseBanner: { text: "", life: 0 },
  upgradeDraft: [],
  upgrades: [],
  collectAngleThreshold: 0.28,
  collectRadiusThreshold: 22,
  hazardAngleThreshold: 0.24,
  hazardRadiusThreshold: 26,
  pulseAngleThreshold: 0.6,
  pulseRadiusThreshold: 78,
  pulseCooldownMul: 1,
  rotationSpeedMul: 1,
  scoreMul: 1,
  comboWindowMul: 1,
  hazardDriftMul: 1,
  maxHealth: 3,
};

const player = {
  angle: 0,
  ringIndex: 1,
  pulseAngle: 0,
};

const world = {
  centerX: 0,
  centerY: 0,
  minRadius: 104,
  ringGap: 56,
  coreRadius: 56,
  outerRadius: 320,
};

function currentRunConfig() {
  return RUN_CONFIG[state.runMode] || RUN_CONFIG.classic;
}

function getPhaseCap() {
  return currentRunConfig().phaseCap;
}

function getChargeTarget() {
  const runConfig = currentRunConfig();
  const base = currentConfig().motesPerPhase + state.phase - 1;
  return Math.max(4, Math.round(base * runConfig.chargeScale));
}

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
    // Ignore storage failures in privacy modes.
  }
}

function resizeCanvas() {
  const frame = canvas.parentElement;
  const width = frame.clientWidth;
  const aspect = 1200 / 760;
  const height = Math.max(520, Math.round(width / aspect));
  const dpr = Math.max(1, window.devicePixelRatio || 1);
  canvas.style.height = `${height}px`;
  canvas.width = Math.floor(width * dpr);
  canvas.height = Math.floor(height * dpr);
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  CENTER.x = width / 2;
  CENTER.y = height / 2;
  world.centerX = CENTER.x;
  world.centerY = CENTER.y;
  world.outerRadius = Math.min(width, height) * 0.44;
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

function currentConfig() {
  return MODE_CONFIG[state.difficulty];
}

function resetGame() {
  const config = currentConfig();
  state.mode = "playing";
  state.lastTime = performance.now();
  state.accumulator = 0;
  state.score = 0;
  state.elapsedMs = 0;
  state.maxHealth = config.lives;
  state.health = state.maxHealth;
  state.phase = 1;
  state.charge = 0;
  state.chargeTarget = getChargeTarget();
  state.combo = 1;
  state.comboTimer = 0;
  state.pulseCooldown = 0.25 * state.pulseCooldownMul;
  state.pulseActive = 0;
  state.pauseFlash = 0;
  state.shake = 0;
  state.victoryPulse = 0;
  state.rotation = -0.35;
  state.ringIndex = 1;
  state.rotLeft = false;
  state.rotRight = false;
  state.moveIn = false;
  state.moveOut = false;
  state.motes = [];
  state.hazards = [];
  state.pulses = [];
  state.scoreBursts = [];
  state.phaseBanner = { text: "", life: 0 };
  state.upgradeDraft = [];
  state.upgrades = [];
  player.angle = state.rotation;
  player.ringIndex = state.ringIndex;
  player.pulseAngle = 0;
  spawnOpeningFormation();
  hideOverlay();
  upgradeSelect.classList.add("hidden");
  startButton.hidden = false;
  resultsScreen.classList.add("hidden");
  updateHud();
}

function spawnOpeningFormation() {
  const config = currentConfig();
  for (let i = 0; i < 5; i += 1) {
    spawnMote(0.12 * i, 0.3 + i * 0.08, true);
  }
  for (let i = 0; i < 2; i += 1) {
    spawnHazard(0.2 * i, 0.18 + i * 0.04, true);
  }
  state.pulseCooldown = config.pulseCooldown * 0.7 * state.pulseCooldownMul;
}

function hideOverlay() {
  overlay.classList.add("hidden");
}

function showOverlay(tag, title, text, buttonText) {
  overlay.classList.remove("hidden");
  overlayTag.textContent = tag;
  overlayTitle.textContent = title;
  overlayText.textContent = text;
  startButton.textContent = buttonText;
  startButton.hidden = false;
  upgradeSelect.classList.add("hidden");
  upgradeGrid.innerHTML = "";
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

function openUpgradeDraft() {
  state.mode = "draft";
  state.upgradeDraft = pickUpgradeChoices();
  overlay.classList.remove("hidden");
  overlayTag.textContent = "UPGRADE";
  overlayTitle.textContent = "选择一个永久升级";
  overlayText.textContent = `第 ${state.phase} 阶段完成。挑一个升级，让这次长局更能跑下去。也可以按 1 / 2 / 3 直接选择。`;
  startButton.hidden = true;
  upgradeSelect.classList.remove("hidden");
  renderUpgradeChoices(state.upgradeDraft);
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
  state.mode = "playing";
  state.lastTime = performance.now();
  hideOverlay();
  startButton.hidden = false;
  state.combo = Math.min(8, state.combo + 1);
  state.comboTimer = 1.5 * state.comboWindowMul;
  spawnOpeningFormation();
  updateHud();
  updateStatusStrip();
}

function pickUpgradeChoices() {
  const available = UPGRADE_POOL.filter((upgrade) => !state.upgrades.some((owned) => owned.id === upgrade.id));
  const pool = available.length > 0 ? available : UPGRADE_POOL;
  const picks = [];
  const used = new Set();
  while (picks.length < Math.min(3, pool.length)) {
    const upgrade = pool[Math.floor(Math.random() * pool.length)];
    if (used.has(upgrade.id)) {
      continue;
    }
    used.add(upgrade.id);
    picks.push(upgrade);
  }
  return picks;
}

function startGame() {
  resetGame();
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
  showOverlay(
    victory ? "COMPLETE" : "RUN ENDED",
    victory ? "长任务同步完成" : "长任务还没跑满",
    victory
      ? "你成功点亮了整座核心塔。可以重新选择难度，再跑一轮更快的轨道。"
      : "核心保护层耗尽了。换个难度再试一次，或者继续追求更高分。",
    "重新开始"
  );
}

function setDifficulty(mode) {
  if (!MODE_CONFIG[mode] || state.difficulty === mode) {
    return;
  }
  state.difficulty = mode;
  syncModeButtons();
  if (state.mode === "menu") {
    updateOverlayForDifficulty();
  }
}

function setRunMode(mode) {
  if (!RUN_CONFIG[mode] || state.runMode === mode) {
    return;
  }
  state.runMode = mode;
  syncRunButtons();
  if (state.mode === "menu") {
    updateOverlayForDifficulty();
  }
}

function updateOverlayForDifficulty() {
  const config = currentConfig();
  const runConfig = currentRunConfig();
  const runText = runConfig.name === "MARATHON"
    ? "马拉松模式会持续推进，并在每个阶段后给你一次永久升级选择，适合 30 分钟长任务验证。"
    : "经典模式会在 5 个阶段后直接结算。";
  showOverlay(
    "READY",
    "校准环轨，进入长任务漂移",
    `当前难度 ${config.name} · ${runConfig.name}。${runText} 用方向键沿轨旋转，用上下键切换轨道，Space 释放脉冲，1/2/3 选择升级。`,
    "开始游戏"
  );
}

function ringRadius(index) {
  return world.minRadius + world.ringGap * index;
}

function activeRadius() {
  return ringRadius(state.ringIndex);
}

function polarToPoint(radius, angle) {
  return {
    x: CENTER.x + Math.cos(angle) * radius,
    y: CENTER.y + Math.sin(angle) * radius,
  };
}

function wrapAngle(angle) {
  let normalized = angle % TAU;
  if (normalized < 0) {
    normalized += TAU;
  }
  return normalized;
}

function shortestAngleDistance(a, b) {
  let diff = wrapAngle(a) - wrapAngle(b);
  if (diff > Math.PI) {
    diff -= TAU;
  } else if (diff < -Math.PI) {
    diff += TAU;
  }
  return diff;
}

function spawnStarfield() {
  if (state.stars.length > 70) {
    return;
  }
  while (state.stars.length < 70) {
    state.stars.push({
      x: Math.random(),
      y: Math.random(),
      size: 0.8 + Math.random() * 2.2,
      speed: 0.02 + Math.random() * 0.08,
      twinkle: Math.random() * TAU,
    });
  }
}

function spawnMote(spawnDelay = 0, progress = 0, seeded = false) {
  const radius = ringRadius(Math.floor(Math.random() * 4)) + (Math.random() - 0.5) * 16;
  const direction = Math.random() > 0.5 ? 1 : -1;
  state.motes.push({
    radius,
    angle: Math.random() * TAU,
    angularVelocity: direction * (0.55 + Math.random() * 0.75) * currentConfig().driftFactor * state.hazardDriftMul,
    radialVelocity: (Math.random() - 0.5) * 16 * currentConfig().driftFactor * state.hazardDriftMul,
    spin: Math.random() * TAU,
    life: seeded ? 8 + progress : 7.5,
    value: 12 + Math.floor(progress * 2),
  });
}

function spawnHazard(progress = 0, bias = 0, seeded = false) {
  const config = currentConfig();
  const runConfig = currentRunConfig();
  const outer = world.outerRadius + 24 + Math.random() * 40;
  state.hazards.push({
    radius: seeded ? ringRadius(3) + 40 + bias * 12 : outer,
    angle: Math.random() * TAU,
    angularVelocity: (Math.random() > 0.5 ? 1 : -1) * (0.35 + Math.random() * 0.65) * config.driftFactor * state.hazardDriftMul,
    radialVelocity: (-42 - progress * 8 - Math.random() * 26) * runConfig.hazardScale,
    life: 10,
    damage: 1,
    size: 15 + progress * 1.6 + Math.random() * 10,
  });
}

function addBurst(x, y, color, count) {
  for (let i = 0; i < count; i += 1) {
    const angle = (TAU * i) / count + Math.random() * 0.2;
    const speed = 60 + Math.random() * 160;
    state.scoreBursts.push({
      x,
      y,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      life: 0.45 + Math.random() * 0.5,
      color,
    });
  }
}

function addPulse(radius) {
  state.pulses.push({
    radius,
    life: 0.45,
  });
}

function updateControls(delta) {
  const config = currentConfig();
  const rotationDelta = config.rotationSpeed * state.rotationSpeedMul * delta;
  if (state.rotLeft) {
    state.rotation -= rotationDelta;
  }
  if (state.rotRight) {
    state.rotation += rotationDelta;
  }
  if (state.moveIn) {
    state.ringIndex = Math.max(0, state.ringIndex - 1);
    state.moveIn = false;
  }
  if (state.moveOut) {
    state.ringIndex = Math.min(TRACKS.length - 1, state.ringIndex + 1);
    state.moveOut = false;
  }
  player.angle = wrapAngle(state.rotation);
  player.ringIndex = state.ringIndex;
}

function updateCombat(delta) {
  if (state.pulseCooldown > 0) {
    state.pulseCooldown = Math.max(0, state.pulseCooldown - delta);
  }
  if (state.comboTimer > 0) {
    state.comboTimer = Math.max(0, state.comboTimer - delta);
    if (state.comboTimer === 0) {
      state.combo = 1;
    }
  }
  if (state.phaseBanner.life > 0) {
    state.phaseBanner.life = Math.max(0, state.phaseBanner.life - delta);
  }
  if (state.pulseActive > 0) {
    state.pulseActive = Math.max(0, state.pulseActive - delta);
  }
  if (state.shake > 0) {
    state.shake = Math.max(0, state.shake - delta * 2.2);
  }
  if (state.victoryPulse > 0) {
    state.victoryPulse = Math.max(0, state.victoryPulse - delta);
  }
}

function updateSpawns(delta) {
  const config = currentConfig();
  const runConfig = currentRunConfig();
  state.accumulator += delta;

  const moteGap = Math.max(0.28, (config.spawnRate - state.phase * 0.05) * runConfig.spawnScale);
  const hazardGap = Math.max(0.42, (config.hazardRate - state.phase * 0.03) * runConfig.hazardScale);

  if (state.accumulator >= moteGap) {
    state.accumulator = 0;
    spawnMote(0, state.phase / 5);
  }

  if (Math.random() < delta * hazardGap * 0.85) {
    spawnHazard(state.phase / 2);
  }
}

function updateEntities(delta) {
  const config = currentConfig();
  state.motes.forEach((mote) => {
    mote.radius += mote.radialVelocity * delta;
    mote.angle += mote.angularVelocity * delta;
    mote.life -= delta;
    mote.spin += delta * 2;
    mote.radius += Math.sin(mote.spin) * delta * 3 * config.driftFactor;
  });

  state.hazards.forEach((hazard) => {
    hazard.radius += hazard.radialVelocity * delta;
    hazard.angle += hazard.angularVelocity * delta;
    hazard.life -= delta;
  });

  state.pulses.forEach((pulse) => {
    pulse.life -= delta;
    pulse.radius += delta * 340;
  });

  state.scoreBursts.forEach((burst) => {
    burst.life -= delta;
    burst.x += burst.vx * delta;
    burst.y += burst.vy * delta;
    burst.vx *= Math.pow(0.1, delta);
    burst.vy *= Math.pow(0.1, delta);
  });

  state.motes = state.motes.filter((mote) => mote.life > 0 && mote.radius > 50 && mote.radius < world.outerRadius + 50);
  state.hazards = state.hazards.filter((hazard) => hazard.life > 0 && hazard.radius > 42);
  state.pulses = state.pulses.filter((pulse) => pulse.life > 0);
  state.scoreBursts = state.scoreBursts.filter((burst) => burst.life > 0);
}

function hitWindow(entityRadius, entityAngle, radius, angle, angleThreshold, radiusThreshold) {
  return Math.abs(entityRadius - radius) <= radiusThreshold && Math.abs(shortestAngleDistance(entityAngle, angle)) <= angleThreshold;
}

function collectMotes() {
  const radius = activeRadius();
  const angle = player.angle;
  const collected = [];
  state.motes = state.motes.filter((mote) => {
    if (hitWindow(mote.radius, mote.angle, radius, angle, state.collectAngleThreshold, state.collectRadiusThreshold)) {
      collected.push(mote);
      return false;
    }
    return true;
  });

  if (collected.length) {
    let gained = 0;
    collected.forEach((mote) => {
      gained += mote.value;
      addBurst(...Object.values(polarToPoint(mote.radius, mote.angle)), "#c6ff9a", 10);
    });
    state.score += Math.round(gained * state.combo * state.scoreMul);
    state.charge += collected.length;
    state.combo = Math.min(8, state.combo + 1);
    state.comboTimer = 2.5 * state.comboWindowMul;
    if (state.score > state.bestScore) {
      state.bestScore = state.score;
      saveBestScore(state.bestScore);
    }
    if (state.charge >= state.chargeTarget) {
      advancePhase();
    }
  }
}

function checkHazards() {
  const radius = activeRadius();
  const angle = player.angle;
  let hit = false;
  state.hazards = state.hazards.filter((hazard) => {
    if (hitWindow(hazard.radius, hazard.angle, radius, angle, state.hazardAngleThreshold, state.hazardRadiusThreshold)) {
      hit = true;
      return false;
    }
    return true;
  });

  if (hit) {
    state.health -= 1;
    state.combo = 1;
    state.comboTimer = 0;
    state.shake = 1;
    addBurst(...Object.values(polarToPoint(radius, angle)), "#ff7f9b", 18);
    state.phaseBanner = { text: "护盾受损", life: 1.15 };
    if (state.health <= 0) {
      endGame(false);
    }
  }
}

function triggerPulse() {
  if (state.mode !== "playing" || state.pulseCooldown > 0) {
    return;
  }
  const radius = activeRadius();
  const angle = player.angle;
  state.pulseCooldown = currentConfig().pulseCooldown * state.pulseCooldownMul;
  state.pulseActive = 0.4;
  addPulse(radius);
  const removedMotes = [];
  state.motes = state.motes.filter((mote) => {
    if (hitWindow(mote.radius, mote.angle, radius, angle, state.pulseAngleThreshold, state.pulseRadiusThreshold)) {
      removedMotes.push(mote);
      return false;
    }
    return true;
  });
  const removedHazards = [];
  state.hazards = state.hazards.filter((hazard) => {
    if (hitWindow(hazard.radius, hazard.angle, radius, angle, state.pulseAngleThreshold + 0.08, state.pulseRadiusThreshold + 10)) {
      removedHazards.push(hazard);
      return false;
    }
    return true;
  });
  if (removedMotes.length || removedHazards.length) {
    state.score += Math.round((removedMotes.length * 4 + removedHazards.length * 9) * state.scoreMul);
    if (state.score > state.bestScore) {
      state.bestScore = state.score;
      saveBestScore(state.bestScore);
    }
    addBurst(...Object.values(polarToPoint(radius, angle)), "#8ef2ff", 24);
  }
  updateHud();
}

function advancePhase() {
  state.phase += 1;
  state.charge = 0;
  state.chargeTarget = getChargeTarget();
  state.motes = [];
  state.hazards = [];
  state.score += Math.round((150 + state.phase * 35) * state.scoreMul);
  state.phaseBanner = {
    text: state.phase > getPhaseCap() ? "核心完成" : state.runMode === "marathon" && state.phase % 3 === 0 ? `阶段 ${state.phase} 进入浪涌` : `阶段 ${state.phase} 同步`,
    life: 1.7,
  };
  state.victoryPulse = 1.1;
  addBurst(CENTER.x, CENTER.y, "#8ef2ff", 36);
  if (state.runMode === "marathon" && state.phase % 3 === 0) {
    for (let i = 0; i < 3; i += 1) {
      spawnHazard(state.phase / 2, 0.2 * i, true);
    }
    for (let i = 0; i < 2; i += 1) {
      spawnMote(0, state.phase / 2, true);
    }
  }
  if (state.phase > getPhaseCap()) {
    endGame(true);
  } else {
    state.combo = Math.min(6, state.combo + 1);
    state.comboTimer = 2;
    if (currentRunConfig().draftBetweenPhases) {
      openUpgradeDraft();
      return;
    }
  }
  if (state.score > state.bestScore) {
    state.bestScore = state.score;
    saveBestScore(state.bestScore);
  }
}

function updateHud() {
  scoreLabel.textContent = String(state.score);
  healthLabel.textContent = String(state.health);
  phaseLabel.textContent = state.runMode === "marathon" ? `${state.phase} / ∞` : String(state.phase);
  const totalSeconds = Math.floor(state.elapsedMs / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = String(totalSeconds % 60).padStart(2, "0");
  timeLabel.textContent = `${minutes}:${seconds}`;
  upgradesLabel.textContent = String(state.upgrades.length);
  chargeLabel.textContent = `${state.charge} / ${state.chargeTarget}`;
  bestBadge.textContent = `BEST ${state.bestScore}`;
}

function update(delta) {
  if (state.mode !== "playing") {
    return;
  }
  state.elapsedMs += delta * 1000;
  updateControls(delta);
  updateCombat(delta);
  updateSpawns(delta);
  updateEntities(delta);
  collectMotes();
  checkHazards();
  spawnStarfield();
  updateHud();
  if (state.score > state.bestScore) {
    state.bestScore = state.score;
    saveBestScore(state.bestScore);
  }
}

function drawGrid() {
  const fade = 1 - Math.min(1, Math.abs(Math.sin(state.rotation * 0.4)) * 0.3);
  ctx.save();
  ctx.translate(CENTER.x, CENTER.y);
  ctx.strokeStyle = `rgba(142, 242, 255, ${0.12 * fade})`;
  ctx.lineWidth = 1;
  for (let i = 0; i < TRACKS.length; i += 1) {
    ctx.beginPath();
    ctx.arc(0, 0, ringRadius(i), 0, TAU);
    ctx.stroke();
  }
  ctx.strokeStyle = `rgba(198, 255, 154, ${0.11 * fade})`;
  for (let i = 0; i < 12; i += 1) {
    const angle = (TAU * i) / 12 + state.rotation * 0.08;
    ctx.beginPath();
    ctx.moveTo(Math.cos(angle) * 52, Math.sin(angle) * 52);
    ctx.lineTo(Math.cos(angle) * (world.outerRadius + 18), Math.sin(angle) * (world.outerRadius + 18));
    ctx.stroke();
  }
  ctx.restore();
}

function drawStarfield() {
  state.stars.forEach((star, index) => {
    const twinkle = 0.45 + 0.55 * Math.sin(state.rotation + star.twinkle + index * 0.2);
    const x = star.x * canvas.clientWidth;
    const y = star.y * canvas.clientHeight;
    ctx.fillStyle = `rgba(255, 255, 255, ${0.25 + twinkle * 0.55})`;
    ctx.beginPath();
    ctx.arc(x, y, star.size * (0.7 + twinkle * 0.6), 0, TAU);
    ctx.fill();
  });
}

function drawCore() {
  ctx.save();
  ctx.translate(CENTER.x, CENTER.y);
  const pulse = 1 + Math.sin(state.victoryPulse * 8 + state.rotation * 2) * 0.06;
  const glow = ctx.createRadialGradient(0, 0, 10, 0, 0, 96 * pulse);
  glow.addColorStop(0, "rgba(255, 255, 255, 0.9)");
  glow.addColorStop(0.35, "rgba(142, 242, 255, 0.55)");
  glow.addColorStop(1, "rgba(142, 242, 255, 0)");
  ctx.fillStyle = glow;
  ctx.beginPath();
  ctx.arc(0, 0, 94 * pulse, 0, TAU);
  ctx.fill();

  ctx.strokeStyle = "rgba(255, 255, 255, 0.32)";
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.arc(0, 0, 58, 0, TAU);
  ctx.stroke();

  ctx.fillStyle = "rgba(7, 14, 26, 0.96)";
  ctx.beginPath();
  ctx.arc(0, 0, 42, 0, TAU);
  ctx.fill();

  ctx.strokeStyle = "rgba(198, 255, 154, 0.45)";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.arc(0, 0, 22, 0, TAU);
  ctx.stroke();

  ctx.restore();
}

function drawMote(mote) {
  const point = polarToPoint(mote.radius, mote.angle);
  ctx.save();
  ctx.translate(point.x, point.y);
  ctx.rotate(mote.spin);
  const grad = ctx.createRadialGradient(0, 0, 2, 0, 0, 16);
  grad.addColorStop(0, "rgba(255, 255, 255, 0.96)");
  grad.addColorStop(0.4, "rgba(198, 255, 154, 0.94)");
  grad.addColorStop(1, "rgba(198, 255, 154, 0)");
  ctx.fillStyle = grad;
  ctx.beginPath();
  ctx.arc(0, 0, 14, 0, TAU);
  ctx.fill();
  ctx.strokeStyle = "rgba(255, 255, 255, 0.44)";
  ctx.lineWidth = 1;
  ctx.strokeRect(-4, -4, 8, 8);
  ctx.restore();
}

function drawHazard(hazard) {
  const point = polarToPoint(hazard.radius, hazard.angle);
  ctx.save();
  ctx.translate(point.x, point.y);
  ctx.rotate(hazard.angle + state.rotation * 0.1);
  const size = hazard.size;
  const grad = ctx.createRadialGradient(0, 0, 2, 0, 0, size * 1.3);
  grad.addColorStop(0, "rgba(255, 255, 255, 0.88)");
  grad.addColorStop(0.25, "rgba(255, 127, 155, 0.82)");
  grad.addColorStop(1, "rgba(255, 127, 155, 0)");
  ctx.fillStyle = grad;
  ctx.beginPath();
  ctx.moveTo(0, -size);
  for (let i = 0; i < 6; i += 1) {
    const angle = (TAU * i) / 6;
    const radius = size + (i % 2 === 0 ? 10 : -4);
    ctx.lineTo(Math.cos(angle) * radius, Math.sin(angle) * radius);
  }
  ctx.closePath();
  ctx.fill();
  ctx.strokeStyle = "rgba(255, 255, 255, 0.2)";
  ctx.lineWidth = 1.4;
  ctx.stroke();
  ctx.restore();
}

function drawPulse(pulse) {
  ctx.save();
  ctx.translate(CENTER.x, CENTER.y);
  ctx.strokeStyle = `rgba(142, 242, 255, ${pulse.life * 1.4})`;
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.arc(0, 0, pulse.radius, 0, TAU);
  ctx.stroke();
  ctx.restore();
}

function drawPlayer() {
  const point = polarToPoint(activeRadius(), player.angle);
  ctx.save();
  ctx.translate(point.x, point.y);
  ctx.rotate(player.angle + Math.PI / 2);
  const pulseScale = state.pulseActive > 0 ? 1.18 : 1;
  ctx.fillStyle = "rgba(255, 255, 255, 0.95)";
  ctx.beginPath();
  ctx.moveTo(0, -18 * pulseScale);
  ctx.lineTo(14 * pulseScale, 14 * pulseScale);
  ctx.lineTo(0, 9 * pulseScale);
  ctx.lineTo(-14 * pulseScale, 14 * pulseScale);
  ctx.closePath();
  ctx.fill();
  ctx.fillStyle = "rgba(142, 242, 255, 0.92)";
  ctx.fillRect(-4, -2, 8, 16);
  ctx.fillStyle = "rgba(198, 255, 154, 0.88)";
  ctx.fillRect(-10, 11, 5, 11);
  ctx.fillRect(5, 11, 5, 11);
  ctx.restore();
}

function drawScoreBursts() {
  state.scoreBursts.forEach((burst) => {
    ctx.globalAlpha = Math.max(0, burst.life);
    ctx.fillStyle = burst.color;
    ctx.beginPath();
    ctx.arc(burst.x, burst.y, 2.4, 0, TAU);
    ctx.fill();
  });
  ctx.globalAlpha = 1;
}

function drawRoundedRect(x, y, width, height, radius) {
  const r = Math.min(radius, width / 2, height / 2);
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + width, y, x + width, y + height, r);
  ctx.arcTo(x + width, y + height, x, y + height, r);
  ctx.arcTo(x, y + height, x, y, r);
  ctx.arcTo(x, y, x + width, y, r);
  ctx.closePath();
}

function drawPhaseBanner() {
  if (state.phaseBanner.life <= 0) {
    return;
  }
  const alpha = Math.min(1, state.phaseBanner.life);
  ctx.save();
  ctx.translate(CENTER.x, 58);
  ctx.fillStyle = `rgba(7, 14, 26, ${0.68 * alpha})`;
  ctx.strokeStyle = `rgba(142, 242, 255, ${0.18 * alpha})`;
  ctx.lineWidth = 1;
  drawRoundedRect(-132, -20, 264, 40, 20);
  ctx.fill();
  ctx.stroke();
  ctx.fillStyle = `rgba(245, 251, 255, ${alpha})`;
  ctx.font = "700 20px " + getComputedStyle(document.documentElement).getPropertyValue("--body-font");
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(state.phaseBanner.text, 0, 0);
  ctx.restore();
}

function drawHudOverlay() {
  ctx.save();
  ctx.fillStyle = "rgba(255, 255, 255, 0.7)";
  ctx.font = "600 17px " + getComputedStyle(document.documentElement).getPropertyValue("--body-font");
  ctx.textAlign = "left";
  ctx.fillText(`COMBO x${state.combo}`, 26, canvas.clientHeight - 34);
  ctx.fillText(
    state.pulseCooldown > 0 ? `PULSE ${state.pulseCooldown.toFixed(1)}s` : "PULSE READY",
    canvas.clientWidth - 180,
    canvas.clientHeight - 34
  );
  ctx.restore();
}

function drawPauseOverlay() {
  if (state.mode !== "paused") {
    return;
  }
  ctx.save();
  ctx.fillStyle = "rgba(3, 7, 18, 0.55)";
  ctx.fillRect(0, 0, canvas.clientWidth, canvas.clientHeight);
  ctx.fillStyle = "rgba(245, 251, 255, 0.96)";
  ctx.textAlign = "center";
  ctx.font = "700 42px " + getComputedStyle(document.documentElement).getPropertyValue("--display-font");
  ctx.fillText("PAUSED", CENTER.x, CENTER.y - 6);
  ctx.font = "600 18px " + getComputedStyle(document.documentElement).getPropertyValue("--body-font");
  ctx.fillStyle = "rgba(159, 180, 206, 0.96)";
  ctx.fillText("按 P 继续，或 Space 释放脉冲", CENTER.x, CENTER.y + 34);
  ctx.restore();
}

function render() {
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  ctx.clearRect(0, 0, width, height);
  ctx.save();
  if (state.shake > 0) {
    ctx.translate((Math.random() - 0.5) * 10 * state.shake, (Math.random() - 0.5) * 10 * state.shake);
  }
  drawGrid();
  drawStarfield();
  drawCore();
  state.pulses.forEach(drawPulse);
  state.motes.forEach(drawMote);
  state.hazards.forEach(drawHazard);
  drawScoreBursts();
  drawPlayer();
  drawPhaseBanner();
  drawHudOverlay();
  drawPauseOverlay();
  ctx.restore();
}

function loop(timestamp) {
  if (state.lastTime === 0) {
    state.lastTime = timestamp;
  }
  const delta = Math.min(0.033, (timestamp - state.lastTime) / 1000);
  state.lastTime = timestamp;
  if (state.mode === "playing") {
    update(delta);
  } else if (state.mode === "paused") {
    updateCombat(delta);
    updateEntities(delta * 0.3);
    updateHud();
  }
  render();
  requestAnimationFrame(loop);
}

function togglePause() {
  if (state.mode === "playing") {
    state.mode = "paused";
    overlay.classList.remove("hidden");
    overlayTag.textContent = "PAUSED";
    overlayTitle.textContent = "轨道已暂停";
    overlayText.textContent = "再次按 P 或点击继续按钮，返回当前环轨。";
    startButton.textContent = "继续游戏";
  } else if (state.mode === "paused") {
    state.mode = "playing";
    hideOverlay();
  }
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
    state.rotLeft = true;
    event.preventDefault();
  } else if (key === "arrowright" || key === "d") {
    state.rotRight = true;
    event.preventDefault();
  } else if (key === "arrowup" || key === "w") {
    state.moveIn = true;
    event.preventDefault();
  } else if (key === "arrowdown" || key === "s") {
    state.moveOut = true;
    event.preventDefault();
  } else if (key === " " || key === "spacebar") {
    event.preventDefault();
    if (state.mode === "menu") {
      startGame();
    } else if (state.mode === "paused") {
      togglePause();
    } else if (state.mode === "results") {
      startGame();
    } else {
      triggerPulse();
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
    state.rotLeft = false;
  } else if (key === "arrowright" || key === "d") {
    state.rotRight = false;
  }
}

function handleTouchAction(action) {
  if (action === "left") {
    state.rotLeft = true;
    setTimeout(() => {
      state.rotLeft = false;
    }, 90);
    return;
  }
  if (action === "right") {
    state.rotRight = true;
    setTimeout(() => {
      state.rotRight = false;
    }, 90);
    return;
  }
  if (action === "in") {
    state.moveIn = true;
    if (state.mode !== "playing" && state.mode !== "paused") {
      startGame();
    }
    return;
  }
  if (action === "out") {
    state.moveOut = true;
    if (state.mode !== "playing" && state.mode !== "paused") {
      startGame();
    }
    return;
  }
  if (action === "pulse") {
    if (state.mode === "menu") {
      startGame();
      return;
    }
    if (state.mode === "results") {
      startGame();
      return;
    }
    if (state.mode === "paused") {
      togglePause();
      return;
    }
    triggerPulse();
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
      return;
    }
    startGame();
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

  canvas.addEventListener("pointerdown", (event) => {
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    if (x < rect.width * 0.35) {
      state.rotLeft = true;
      setTimeout(() => {
        state.rotLeft = false;
      }, 90);
    } else if (x > rect.width * 0.65) {
      state.rotRight = true;
      setTimeout(() => {
        state.rotRight = false;
      }, 90);
    } else if (state.mode === "menu" || state.mode === "results") {
      startGame();
    } else if (state.mode === "paused") {
      togglePause();
    } else {
      triggerPulse();
    }
  });

  canvas.addEventListener("wheel", (event) => {
    if (state.mode !== "playing") {
      return;
    }
    if (event.deltaY < 0) {
      state.moveIn = true;
    } else {
      state.moveOut = true;
    }
  }, { passive: true });
}

function initialise() {
  resizeCanvas();
  syncModeButtons();
  syncRunButtons();
  state.bestScore = readBestScore();
  updateHud();
  updateOverlayForDifficulty();
  bindEvents();
  requestAnimationFrame(loop);
}

initialise();
