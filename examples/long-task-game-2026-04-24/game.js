(function () {
  "use strict";

  var WIDTH = 1600;
  var HEIGHT = 900;
  var SECTOR_COUNT = 5;
  var STORAGE_KEY = "starforgeRelay.bestScore";
  var SOUND_KEY = "starforgeRelay.sound";
  var BASE_TARGETS = [10, 15, 21, 28, 36];
  var ARENA_MARGIN = 70;
  var RELAY_RADIUS = 105;
  var UPGRADE_POOL = [
    {
      id: "thrusters",
      name: "Vector Thrusters",
      short: "Speed+",
      description: "Increase top speed and acceleration for faster routes.",
      apply: function (game) {
        game.player.maxSpeed += 45;
        game.player.acceleration += 70;
      }
    },
    {
      id: "cargo",
      name: "Cargo Lattice",
      short: "Cargo+",
      description: "Expand cell storage capacity by two.",
      apply: function (game) {
        game.player.maxCargo += 2;
      }
    },
    {
      id: "pulse",
      name: "Pulse Cascade",
      short: "Pulse+",
      description: "Pulse reaches farther and refreshes faster.",
      apply: function (game) {
        game.player.pulseRadius += 40;
        game.player.pulseCooldown = Math.max(2.3, game.player.pulseCooldown - 0.35);
      }
    },
    {
      id: "hull",
      name: "Reactive Hull",
      short: "Hull+",
      description: "Gain more maximum integrity and restore part of it immediately.",
      apply: function (game) {
        game.player.maxHealth += 20;
        game.player.health = Math.min(game.player.maxHealth, game.player.health + 25);
      }
    },
    {
      id: "magnet",
      name: "Grav Magnet",
      short: "Magnet+",
      description: "Collect loose cells from a wider radius.",
      apply: function (game) {
        game.player.pickupRadius += 28;
      }
    },
    {
      id: "stabilizer",
      name: "Relay Stabilizer",
      short: "Chain+",
      description: "Longer delivery chains and stronger score multiplier.",
      apply: function (game) {
        game.player.chainWindow += 0.85;
        game.player.scoreBoost += 0.2;
      }
    }
  ];

  var canvas = document.getElementById("gameCanvas");
  var ctx = canvas.getContext("2d");
  var startScreen = document.getElementById("startScreen");
  var pauseOverlay = document.getElementById("pauseOverlay");
  var upgradeOverlay = document.getElementById("upgradeOverlay");
  var resultOverlay = document.getElementById("resultOverlay");
  var upgradeChoices = document.getElementById("upgradeChoices");
  var startButton = document.getElementById("startButton");
  var restartButton = document.getElementById("restartButton");
  var muteButton = document.getElementById("muteButton");

  var ui = {
    sectorValue: document.getElementById("sectorValue"),
    sectorStatus: document.getElementById("sectorStatus"),
    chargeFill: document.getElementById("chargeFill"),
    chargeText: document.getElementById("chargeText"),
    healthFill: document.getElementById("healthFill"),
    healthText: document.getElementById("healthText"),
    scoreValue: document.getElementById("scoreValue"),
    cargoValue: document.getElementById("cargoValue"),
    chainValue: document.getElementById("chainValue"),
    pulseValue: document.getElementById("pulseValue"),
    upgradeList: document.getElementById("upgradeList"),
    resultTag: document.getElementById("resultTag"),
    resultTitle: document.getElementById("resultTitle"),
    resultSubtitle: document.getElementById("resultSubtitle"),
    resultScore: document.getElementById("resultScore"),
    resultBest: document.getElementById("resultBest"),
    resultSector: document.getElementById("resultSector"),
    resultDeliveries: document.getElementById("resultDeliveries"),
    resultPulses: document.getElementById("resultPulses"),
    resultUpgrades: document.getElementById("resultUpgrades")
  };

  var keys = Object.create(null);
  var lastTime = 0;
  var rafId = 0;
  var starfield = createStarfield();
  var audioContext = null;

  var game = createGameState();
  syncMuteButton();
  syncHud();
  render(0);

  startButton.addEventListener("click", startRun);
  restartButton.addEventListener("click", function () {
    showOverlay(resultOverlay, false);
    showOverlay(startScreen, true);
    game.mode = "menu";
    resetRunState();
    render(0);
  });
  muteButton.addEventListener("click", toggleMute);

  window.addEventListener("keydown", function (event) {
    var key = event.key.toLowerCase();
    if (["arrowup", "arrowdown", "arrowleft", "arrowright", " ", "escape"].indexOf(key) >= 0) {
      event.preventDefault();
    }
    keys[key] = true;

    if (key === "m") {
      toggleMute();
      return;
    }
    if (key === "p" || key === "escape") {
      if (game.mode === "playing") {
        setPaused(true);
      } else if (game.mode === "paused") {
        setPaused(false);
      }
      return;
    }
    if (key === " " || key === "enter") {
      if (game.mode === "menu") {
        startRun();
      } else if (game.mode === "paused") {
        setPaused(false);
      } else if (game.mode === "results") {
        restartButton.click();
      } else if (game.mode === "playing") {
        activatePulse();
      }
    }
  });

  window.addEventListener("keyup", function (event) {
    keys[event.key.toLowerCase()] = false;
  });

  document.addEventListener("visibilitychange", function () {
    if (document.hidden && game.mode === "playing") {
      setPaused(true);
    }
  });

  function createGameState() {
    return {
      mode: "menu",
      sector: 1,
      score: 0,
      bestScore: readNumber(STORAGE_KEY),
      soundOn: readSound(),
      targetCharge: BASE_TARGETS[0],
      delivered: 0,
      deliveries: 0,
      pulseUses: 0,
      upgrades: [],
      upgradeDraft: [],
      particles: [],
      pickups: [],
      enemies: [],
      shockwaves: [],
      flashes: [],
      spawnTimer: 0,
      damageFlash: 0,
      combo: 1,
      comboTimer: 0,
      player: createPlayer(),
      elapsed: 0
    };
  }

  function createPlayer() {
    return {
      x: WIDTH * 0.5,
      y: HEIGHT * 0.75,
      vx: 0,
      vy: 0,
      radius: 20,
      maxSpeed: 320,
      acceleration: 820,
      drag: 0.9,
      health: 100,
      maxHealth: 100,
      invulnerable: 0,
      pulseCooldown: 3.6,
      pulseTimer: 0,
      pulseRadius: 130,
      pickupRadius: 52,
      cargo: 0,
      maxCargo: 4,
      chainWindow: 3.6,
      scoreBoost: 0
    };
  }

  function resetRunState() {
    game = createGameState();
    syncMuteButton();
    syncHud();
  }

  function startRun() {
    ensureAudio();
    game = createGameState();
    game.mode = "playing";
    hideAllOverlays();
    seedSector(game.sector);
    syncHud();
    lastTime = 0;
    queueFrame();
  }

  function seedSector(sector) {
    game.sector = sector;
    game.targetCharge = BASE_TARGETS[Math.min(sector - 1, BASE_TARGETS.length - 1)];
    game.delivered = 0;
    game.pickups = [];
    game.enemies = [];
    game.particles = [];
    game.shockwaves = [];
    game.flashes = [];
    game.spawnTimer = 1.1;
    spawnCluster(8 + sector * 2);
    for (var i = 0; i < sector + 1; i += 1) {
      spawnEnemy(true);
    }
    placePlayerNearBottom();
  }

  function placePlayerNearBottom() {
    game.player.x = WIDTH * 0.5;
    game.player.y = HEIGHT * 0.76;
    game.player.vx = 0;
    game.player.vy = 0;
    game.player.invulnerable = 1.25;
    game.player.cargo = 0;
    game.combo = 1;
    game.comboTimer = 0;
  }

  function frame(timestamp) {
    rafId = 0;
    if (game.mode === "menu") {
      render(0);
      return;
    }
    if (!lastTime) {
      lastTime = timestamp;
    }
    var dt = Math.min(0.033, (timestamp - lastTime) / 1000);
    lastTime = timestamp;

    if (game.mode === "playing") {
      update(dt);
    }
    render(dt);

    queueFrame();
  }

  function update(dt) {
    game.elapsed += dt;
    game.damageFlash = Math.max(0, game.damageFlash - dt * 2);
    if (game.player.invulnerable > 0) {
      game.player.invulnerable -= dt;
    }
    if (game.player.pulseTimer > 0) {
      game.player.pulseTimer -= dt;
    }
    if (game.comboTimer > 0) {
      game.comboTimer -= dt;
    } else {
      game.combo = 1;
    }

    handleMovement(dt);
    keepPlayerInBounds();
    updatePickups(dt);
    updateEnemies(dt);
    updateEffects(dt);
    handleRelayDeposit(dt);
    maybeSpawnEntities(dt);

    if (game.player.health <= 0) {
      finishRun(false);
      return;
    }
    if (game.delivered >= game.targetCharge) {
      if (game.sector >= SECTOR_COUNT) {
        finishRun(true);
      } else {
        openUpgradeDraft();
      }
    }
    syncHud();
  }

  function handleMovement(dt) {
    var ax = 0;
    var ay = 0;
    if (keys.arrowleft || keys.a) {
      ax -= 1;
    }
    if (keys.arrowright || keys.d) {
      ax += 1;
    }
    if (keys.arrowup || keys.w) {
      ay -= 1;
    }
    if (keys.arrowdown || keys.s) {
      ay += 1;
    }

    var length = Math.hypot(ax, ay) || 1;
    ax /= length;
    ay /= length;

    game.player.vx += ax * game.player.acceleration * dt;
    game.player.vy += ay * game.player.acceleration * dt;

    game.player.vx *= Math.pow(game.player.drag, dt * 60);
    game.player.vy *= Math.pow(game.player.drag, dt * 60);

    var speed = Math.hypot(game.player.vx, game.player.vy);
    if (speed > game.player.maxSpeed) {
      var scale = game.player.maxSpeed / speed;
      game.player.vx *= scale;
      game.player.vy *= scale;
    }

    game.player.x += game.player.vx * dt;
    game.player.y += game.player.vy * dt;

    if (keys[" "] && game.mode === "playing") {
      activatePulse();
    }
  }

  function keepPlayerInBounds() {
    game.player.x = clamp(game.player.x, ARENA_MARGIN, WIDTH - ARENA_MARGIN);
    game.player.y = clamp(game.player.y, ARENA_MARGIN, HEIGHT - ARENA_MARGIN);
  }

  function updatePickups(dt) {
    for (var i = game.pickups.length - 1; i >= 0; i -= 1) {
      var pickup = game.pickups[i];
      pickup.pulse += dt * (2 + pickup.seed);
      pickup.life -= dt;
      if (pickup.life <= 0) {
        game.pickups.splice(i, 1);
        continue;
      }
      var dx = game.player.x - pickup.x;
      var dy = game.player.y - pickup.y;
      var dist = Math.hypot(dx, dy) || 1;
      if (dist < game.player.pickupRadius + 80) {
        pickup.x += (dx / dist) * dt * 120;
        pickup.y += (dy / dist) * dt * 120;
      }
      if (dist < game.player.pickupRadius && game.player.cargo < game.player.maxCargo) {
        game.player.cargo += 1;
        game.pickups.splice(i, 1);
        spawnBurst(pickup.x, pickup.y, "#75e7ff", 8);
        playTone(620, 0.06, "triangle", 0.028);
      }
    }
  }

  function updateEnemies(dt) {
    for (var i = game.enemies.length - 1; i >= 0; i -= 1) {
      var enemy = game.enemies[i];
      enemy.flash = Math.max(0, enemy.flash - dt * 2.4);
      enemy.stun = Math.max(0, enemy.stun - dt);

      var tx = game.player.x;
      var ty = game.player.y;
      if (game.player.cargo === 0 && Math.random() < 0.25) {
        tx = WIDTH * 0.5;
        ty = HEIGHT * 0.5;
      }
      var dx = tx - enemy.x;
      var dy = ty - enemy.y;
      var dist = Math.hypot(dx, dy) || 1;
      var speed = enemy.speed * (enemy.stun > 0 ? 0.12 : 1);
      enemy.vx += (dx / dist) * speed * dt;
      enemy.vy += (dy / dist) * speed * dt;
      enemy.vx *= Math.pow(0.92, dt * 60);
      enemy.vy *= Math.pow(0.92, dt * 60);
      enemy.x += enemy.vx * dt;
      enemy.y += enemy.vy * dt;

      if (enemy.x < 40 || enemy.x > WIDTH - 40) {
        enemy.vx *= -0.7;
      }
      if (enemy.y < 40 || enemy.y > HEIGHT - 40) {
        enemy.vy *= -0.7;
      }

      var pdx = game.player.x - enemy.x;
      var pdy = game.player.y - enemy.y;
      var playerDist = Math.hypot(pdx, pdy) || 1;
      if (playerDist < enemy.radius + game.player.radius + 4) {
        if (game.player.invulnerable <= 0) {
          takeDamage(11 + enemy.tier * 2);
          enemy.stun = 0.5;
          enemy.vx -= (pdx / playerDist) * 260;
          enemy.vy -= (pdy / playerDist) * 260;
          if (game.player.cargo > 0) {
            scatterCargo();
          }
        }
      }
    }
  }

  function updateEffects(dt) {
    stepCollection(game.particles, dt, function (item) {
      item.x += item.vx * dt;
      item.y += item.vy * dt;
      item.vx *= Math.pow(0.94, dt * 60);
      item.vy *= Math.pow(0.94, dt * 60);
      item.life -= dt;
      return item.life > 0;
    });

    stepCollection(game.shockwaves, dt, function (wave) {
      wave.radius += wave.speed * dt;
      wave.life -= dt;
      return wave.life > 0;
    });

    stepCollection(game.flashes, dt, function (flash) {
      flash.life -= dt;
      return flash.life > 0;
    });
  }

  function handleRelayDeposit() {
    var dx = game.player.x - WIDTH * 0.5;
    var dy = game.player.y - HEIGHT * 0.5;
    var distance = Math.hypot(dx, dy);
    if (distance < RELAY_RADIUS && game.player.cargo > 0) {
      var deliveredNow = game.player.cargo;
      game.delivered += deliveredNow;
      game.deliveries += 1;
      game.combo = Math.min(6, game.combo + 1);
      game.comboTimer = game.player.chainWindow;
      var bonus = 100 * deliveredNow * game.combo * (1 + game.player.scoreBoost);
      game.score += Math.round(bonus + game.sector * 35);
      game.player.cargo = 0;
      spawnBurst(WIDTH * 0.5, HEIGHT * 0.5, "#ffcc66", 20);
      game.flashes.push({ life: 0.38, color: "255, 204, 102" });
      playTone(480 + deliveredNow * 40, 0.12, "sine", 0.045);
    }
  }

  function maybeSpawnEntities(dt) {
    game.spawnTimer -= dt;
    if (game.spawnTimer <= 0) {
      game.spawnTimer = Math.max(0.8, 2.6 - game.sector * 0.18);
      spawnEnemy(false);
      if (Math.random() < 0.8) {
        spawnCluster(2 + Math.floor(Math.random() * 4));
      }
    }
    if (game.pickups.length < 8 + game.sector) {
      spawnCluster(1 + Math.floor(Math.random() * 3));
    }
  }

  function spawnCluster(count) {
    for (var i = 0; i < count; i += 1) {
      var angle = Math.random() * Math.PI * 2;
      var radius = 180 + Math.random() * 380;
      var x = WIDTH * 0.5 + Math.cos(angle) * radius;
      var y = HEIGHT * 0.5 + Math.sin(angle) * radius;
      x = clamp(x, ARENA_MARGIN + 10, WIDTH - ARENA_MARGIN - 10);
      y = clamp(y, ARENA_MARGIN + 10, HEIGHT - ARENA_MARGIN - 10);
      if (Math.hypot(x - WIDTH * 0.5, y - HEIGHT * 0.5) < RELAY_RADIUS + 90) {
        y += RELAY_RADIUS + 60;
      }
      game.pickups.push({
        x: x,
        y: y,
        radius: 10 + Math.random() * 4,
        pulse: Math.random() * Math.PI * 2,
        life: 14 + Math.random() * 8,
        seed: Math.random() * 2
      });
    }
  }

  function spawnEnemy(initial) {
    var edge = Math.floor(Math.random() * 4);
    var x = WIDTH * 0.5;
    var y = HEIGHT * 0.5;
    if (edge === 0) {
      x = 30;
      y = 90 + Math.random() * (HEIGHT - 180);
    } else if (edge === 1) {
      x = WIDTH - 30;
      y = 90 + Math.random() * (HEIGHT - 180);
    } else if (edge === 2) {
      x = 90 + Math.random() * (WIDTH - 180);
      y = 30;
    } else {
      x = 90 + Math.random() * (WIDTH - 180);
      y = HEIGHT - 30;
    }

    game.enemies.push({
      x: x,
      y: y,
      vx: 0,
      vy: 0,
      radius: 18 + game.sector * 0.9,
      speed: (initial ? 80 : 95) + game.sector * 22 + Math.random() * 16,
      tier: game.sector,
      stun: initial ? 0.3 : 0,
      flash: 0
    });
  }

  function activatePulse() {
    if (game.mode !== "playing" || game.player.pulseTimer > 0) {
      return;
    }
    game.player.pulseTimer = game.player.pulseCooldown;
    game.pulseUses += 1;
    game.shockwaves.push({
      x: game.player.x,
      y: game.player.y,
      radius: game.player.radius,
      speed: 480,
      life: 0.4
    });
    for (var i = 0; i < game.enemies.length; i += 1) {
      var enemy = game.enemies[i];
      var dx = enemy.x - game.player.x;
      var dy = enemy.y - game.player.y;
      var dist = Math.hypot(dx, dy) || 1;
      if (dist < game.player.pulseRadius) {
        enemy.stun = 1.2;
        enemy.flash = 1;
        enemy.vx += (dx / dist) * 320;
        enemy.vy += (dy / dist) * 320;
        game.score += 18;
      }
    }
    for (var j = 0; j < game.pickups.length; j += 1) {
      var pickup = game.pickups[j];
      var px = game.player.x - pickup.x;
      var py = game.player.y - pickup.y;
      var pd = Math.hypot(px, py) || 1;
      if (pd < game.player.pulseRadius * 1.1) {
        pickup.x += (px / pd) * 36;
        pickup.y += (py / pd) * 36;
      }
    }
    spawnBurst(game.player.x, game.player.y, "#3ddbc4", 16);
    playTone(190, 0.18, "sawtooth", 0.04);
  }

  function takeDamage(amount) {
    game.player.health = Math.max(0, game.player.health - amount);
    game.player.invulnerable = 1.15;
    game.damageFlash = 1;
    game.combo = 1;
    game.comboTimer = 0;
    spawnBurst(game.player.x, game.player.y, "#ff8f8f", 18);
    playTone(140, 0.14, "square", 0.04);
  }

  function scatterCargo() {
    var lost = Math.min(2, game.player.cargo);
    game.player.cargo -= lost;
    for (var i = 0; i < lost; i += 1) {
      game.pickups.push({
        x: game.player.x + (Math.random() - 0.5) * 40,
        y: game.player.y + (Math.random() - 0.5) * 40,
        radius: 10,
        pulse: Math.random() * Math.PI * 2,
        life: 8,
        seed: Math.random() * 2
      });
    }
  }

  function openUpgradeDraft() {
    game.mode = "upgrade";
    game.upgradeDraft = pickUpgrades(3);
    showOverlay(upgradeOverlay, true);
    render(0);
    upgradeChoices.innerHTML = "";
    game.upgradeDraft.forEach(function (upgrade) {
      var button = document.createElement("button");
      button.type = "button";
      button.className = "upgrade-card";
      button.innerHTML = "<span class=\"feature-kicker\">" + upgrade.short + "</span><strong>" + upgrade.name + "</strong><p>" + upgrade.description + "</p>";
      button.addEventListener("click", function () {
        applyUpgrade(upgrade);
      });
      upgradeChoices.appendChild(button);
    });
  }

  function pickUpgrades(count) {
    var available = UPGRADE_POOL.filter(function (upgrade) {
      return !game.upgrades.some(function (owned) {
        return owned.id === upgrade.id;
      });
    });
    if (available.length <= count) {
      return available.slice();
    }
    shuffle(available);
    return available.slice(0, count);
  }

  function applyUpgrade(upgrade) {
    game.upgrades.push(upgrade);
    upgrade.apply(game);
    showOverlay(upgradeOverlay, false);
    game.mode = "playing";
    seedSector(game.sector + 1);
    syncHud();
    lastTime = performance.now();
    queueFrame();
  }

  function setPaused(paused) {
    if (paused && game.mode === "playing") {
      game.mode = "paused";
      showOverlay(pauseOverlay, true);
    } else if (!paused && game.mode === "paused") {
      game.mode = "playing";
      showOverlay(pauseOverlay, false);
      lastTime = performance.now();
      queueFrame();
    }
  }

  function finishRun(victory) {
    game.mode = "results";
    game.bestScore = Math.max(game.bestScore, game.score);
    try {
      localStorage.setItem(STORAGE_KEY, String(game.bestScore));
    } catch (error) {
      // Ignore storage failures.
    }
    ui.resultTag.textContent = victory ? "Relay Stabilized" : "Relay Lost";
    ui.resultTitle.textContent = victory ? "Starforge Reignited" : "Swarm Breach";
    ui.resultSubtitle.textContent = victory
      ? "All five sectors are online again. The yard is bright for one more cycle."
      : "Your courier frame collapsed before the relay could be fully restored.";
    ui.resultScore.textContent = formatNumber(game.score);
    ui.resultBest.textContent = formatNumber(game.bestScore);
    ui.resultSector.textContent = String(game.sector);
    ui.resultDeliveries.textContent = String(game.deliveries);
    ui.resultPulses.textContent = String(game.pulseUses);
    ui.resultUpgrades.textContent = String(game.upgrades.length);
    showOverlay(resultOverlay, true);
    syncHud();
    render(0);
  }

  function syncHud() {
    var chargeRatio = clamp(game.delivered / game.targetCharge, 0, 1);
    var healthRatio = clamp(game.player.health / game.player.maxHealth, 0, 1);
    ui.sectorValue.textContent = String(game.sector);
    ui.sectorStatus.textContent = "Target " + game.targetCharge;
    ui.chargeFill.style.width = (chargeRatio * 100).toFixed(1) + "%";
    ui.chargeText.textContent = "Relay charge " + game.delivered + " / " + game.targetCharge;
    ui.healthFill.style.width = (healthRatio * 100).toFixed(1) + "%";
    ui.healthText.textContent = "Hull " + Math.ceil(game.player.health) + " / " + game.player.maxHealth;
    ui.scoreValue.textContent = formatNumber(game.score);
    ui.cargoValue.textContent = game.player.cargo + " / " + game.player.maxCargo;
    ui.chainValue.textContent = "x" + game.combo;
    ui.pulseValue.textContent = game.player.pulseTimer > 0 ? game.player.pulseTimer.toFixed(1) + "s" : "Ready";
    ui.upgradeList.innerHTML = "";
    if (game.upgrades.length === 0) {
      ui.upgradeList.innerHTML = "<span class=\"badge subtle\">No upgrades yet</span>";
    } else {
      game.upgrades.forEach(function (upgrade) {
        var span = document.createElement("span");
        span.className = "badge";
        span.textContent = upgrade.short;
        ui.upgradeList.appendChild(span);
      });
    }
  }

  function render() {
    ctx.clearRect(0, 0, WIDTH, HEIGHT);
    renderBackground();
    renderArena();
    renderPickups();
    renderEnemies();
    renderRelay();
    renderPlayer();
    renderEffects();
    renderWorldHud();
  }

  function renderBackground() {
    var gradient = ctx.createLinearGradient(0, 0, 0, HEIGHT);
    gradient.addColorStop(0, "#133458");
    gradient.addColorStop(0.55, "#0c1a2c");
    gradient.addColorStop(1, "#09111c");
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, WIDTH, HEIGHT);

    ctx.save();
    starfield.forEach(function (star) {
      var twinkle = 0.45 + 0.55 * Math.sin(game.elapsed * star.speed + star.phase);
      ctx.globalAlpha = twinkle * star.alpha;
      ctx.fillStyle = star.color;
      ctx.fillRect(star.x, star.y, star.size, star.size);
    });
    ctx.restore();

    ctx.strokeStyle = "rgba(117, 231, 255, 0.08)";
    ctx.lineWidth = 1;
    for (var x = 0; x <= WIDTH; x += 120) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, HEIGHT);
      ctx.stroke();
    }
    for (var y = 0; y <= HEIGHT; y += 120) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(WIDTH, y);
      ctx.stroke();
    }
  }

  function renderArena() {
    ctx.save();
    ctx.strokeStyle = "rgba(117, 231, 255, 0.18)";
    ctx.lineWidth = 3;
    roundRectPath(ctx, 26, 26, WIDTH - 52, HEIGHT - 52, 36);
    ctx.stroke();

    ctx.fillStyle = "rgba(117, 231, 255, 0.03)";
    roundRectPath(ctx, 40, 40, WIDTH - 80, HEIGHT - 80, 30);
    ctx.fill();

    ctx.restore();
  }

  function renderRelay() {
    var pulse = 0.7 + Math.sin(game.elapsed * 3.2) * 0.12;
    var cx = WIDTH * 0.5;
    var cy = HEIGHT * 0.5;
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(game.elapsed * 0.18);

    ctx.strokeStyle = "rgba(255, 204, 102, 0.55)";
    ctx.lineWidth = 10;
    ctx.beginPath();
    ctx.arc(0, 0, RELAY_RADIUS + 10, 0, Math.PI * 2);
    ctx.stroke();

    ctx.strokeStyle = "rgba(117, 231, 255, 0.25)";
    ctx.lineWidth = 24;
    ctx.beginPath();
    ctx.arc(0, 0, RELAY_RADIUS - 24, 0, Math.PI * 2);
    ctx.stroke();

    ctx.fillStyle = "rgba(255, 204, 102, 0.12)";
    ctx.beginPath();
    ctx.arc(0, 0, 62 + pulse * 18, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = "#ffcc66";
    ctx.beginPath();
    ctx.arc(0, 0, 24 + pulse * 6, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  function renderPlayer() {
    ctx.save();
    ctx.translate(game.player.x, game.player.y);
    var angle = Math.atan2(game.player.vy || -1, game.player.vx || 0) + Math.PI / 2;
    ctx.rotate(angle);

    if (game.player.invulnerable > 0 && Math.floor(game.elapsed * 10) % 2 === 0) {
      ctx.globalAlpha = 0.5;
    }

    ctx.fillStyle = "#75e7ff";
    ctx.shadowColor = "rgba(117, 231, 255, 0.8)";
    ctx.shadowBlur = 24;
    ctx.beginPath();
    ctx.moveTo(0, -28);
    ctx.lineTo(18, 20);
    ctx.lineTo(0, 10);
    ctx.lineTo(-18, 20);
    ctx.closePath();
    ctx.fill();

    ctx.fillStyle = "#ffcc66";
    ctx.beginPath();
    ctx.arc(0, 4, 7, 0, Math.PI * 2);
    ctx.fill();

    ctx.restore();
  }

  function renderPickups() {
    game.pickups.forEach(function (pickup) {
      var glow = 0.75 + Math.sin(pickup.pulse * 2.5) * 0.25;
      ctx.save();
      ctx.translate(pickup.x, pickup.y);
      ctx.rotate(pickup.pulse);
      ctx.fillStyle = "rgba(117, 231, 255, 0.18)";
      ctx.beginPath();
      ctx.arc(0, 0, pickup.radius * 2.1, 0, Math.PI * 2);
      ctx.fill();

      ctx.strokeStyle = "rgba(255, 204, 102, " + (0.55 + glow * 0.25) + ")";
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(0, -pickup.radius * 1.5);
      ctx.lineTo(pickup.radius * 1.2, 0);
      ctx.lineTo(0, pickup.radius * 1.5);
      ctx.lineTo(-pickup.radius * 1.2, 0);
      ctx.closePath();
      ctx.stroke();
      ctx.restore();
    });
  }

  function renderEnemies() {
    game.enemies.forEach(function (enemy) {
      ctx.save();
      ctx.translate(enemy.x, enemy.y);
      ctx.rotate(game.elapsed * 0.7 + enemy.tier * 0.2);
      ctx.shadowColor = "rgba(255, 107, 107, 0.6)";
      ctx.shadowBlur = 18;
      ctx.fillStyle = enemy.flash > 0 ? "#ffe9a6" : "#ff6b6b";
      ctx.beginPath();
      for (var i = 0; i < 6; i += 1) {
        var angle = (Math.PI * 2 * i) / 6;
        var radius = i % 2 === 0 ? enemy.radius : enemy.radius * 0.55;
        var px = Math.cos(angle) * radius;
        var py = Math.sin(angle) * radius;
        if (i === 0) {
          ctx.moveTo(px, py);
        } else {
          ctx.lineTo(px, py);
        }
      }
      ctx.closePath();
      ctx.fill();
      ctx.restore();
    });
  }

  function renderEffects() {
    game.shockwaves.forEach(function (wave) {
      ctx.save();
      ctx.globalAlpha = wave.life * 1.4;
      ctx.strokeStyle = "rgba(61, 219, 196, 0.75)";
      ctx.lineWidth = 8;
      ctx.beginPath();
      ctx.arc(wave.x, wave.y, wave.radius, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();
    });

    game.particles.forEach(function (particle) {
      ctx.save();
      ctx.globalAlpha = particle.life;
      ctx.fillStyle = particle.color;
      ctx.beginPath();
      ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    });

    game.flashes.forEach(function (flash) {
      ctx.save();
      ctx.fillStyle = "rgba(" + flash.color + ", " + (flash.life * 0.25) + ")";
      ctx.fillRect(0, 0, WIDTH, HEIGHT);
      ctx.restore();
    });

    if (game.damageFlash > 0) {
      ctx.save();
      ctx.fillStyle = "rgba(255, 72, 72, " + (game.damageFlash * 0.16) + ")";
      ctx.fillRect(0, 0, WIDTH, HEIGHT);
      ctx.restore();
    }
  }

  function renderWorldHud() {
    ctx.save();
    ctx.fillStyle = "rgba(237, 248, 255, 0.9)";
    ctx.font = "700 30px Trebuchet MS, sans-serif";
    ctx.fillText("SECTOR " + game.sector, 70, 86);

    ctx.font = "500 20px Avenir Next, Segoe UI, sans-serif";
    ctx.fillStyle = "rgba(237, 248, 255, 0.7)";
    ctx.fillText("Deliver " + game.delivered + " / " + game.targetCharge + " cells", 70, 118);

    ctx.textAlign = "right";
    ctx.fillStyle = "rgba(255, 204, 102, 0.92)";
    ctx.fillText("Cargo " + game.player.cargo + " / " + game.player.maxCargo, WIDTH - 70, 86);
    ctx.fillStyle = "rgba(237, 248, 255, 0.7)";
    ctx.fillText("Chain x" + game.combo, WIDTH - 70, 118);
    ctx.restore();
  }

  function queueFrame() {
    if (rafId || (game.mode !== "playing" && game.mode !== "paused" && game.mode !== "upgrade")) {
      return;
    }
    rafId = requestAnimationFrame(frame);
  }

  function createStarfield() {
    var stars = [];
    for (var i = 0; i < 120; i += 1) {
      stars.push({
        x: Math.random() * WIDTH,
        y: Math.random() * HEIGHT,
        size: Math.random() * 2.6 + 0.8,
        alpha: Math.random() * 0.7 + 0.2,
        speed: Math.random() * 1.8 + 0.3,
        phase: Math.random() * Math.PI * 2,
        color: Math.random() > 0.82 ? "#ffcc66" : "#d7f6ff"
      });
    }
    return stars;
  }

  function spawnBurst(x, y, color, count) {
    for (var i = 0; i < count; i += 1) {
      var angle = Math.random() * Math.PI * 2;
      var speed = 60 + Math.random() * 220;
      game.particles.push({
        x: x,
        y: y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        radius: 2 + Math.random() * 4,
        color: color,
        life: 0.35 + Math.random() * 0.4
      });
    }
  }

  function hideAllOverlays() {
    [startScreen, pauseOverlay, upgradeOverlay, resultOverlay].forEach(function (overlay) {
      showOverlay(overlay, false);
    });
  }

  function showOverlay(node, visible) {
    node.classList.toggle("visible", visible);
  }

  function toggleMute() {
    game.soundOn = !game.soundOn;
    try {
      localStorage.setItem(SOUND_KEY, game.soundOn ? "on" : "off");
    } catch (error) {
      // Ignore storage failures.
    }
    syncMuteButton();
  }

  function syncMuteButton() {
    muteButton.textContent = game.soundOn ? "Sound: On" : "Sound: Off";
  }

  function ensureAudio() {
    if (!game.soundOn) {
      return;
    }
    if (!audioContext && window.AudioContext) {
      audioContext = new window.AudioContext();
    }
    if (audioContext && audioContext.state === "suspended") {
      audioContext.resume().catch(function () {
        // Ignore autoplay restrictions.
      });
    }
  }

  function playTone(frequency, duration, type, gainValue) {
    if (!game.soundOn || !window.AudioContext) {
      return;
    }
    ensureAudio();
    if (!audioContext) {
      return;
    }
    var osc = audioContext.createOscillator();
    var gain = audioContext.createGain();
    osc.type = type;
    osc.frequency.value = frequency;
    gain.gain.value = gainValue || 0.03;
    gain.gain.exponentialRampToValueAtTime(0.0001, audioContext.currentTime + duration);
    osc.connect(gain);
    gain.connect(audioContext.destination);
    osc.start();
    osc.stop(audioContext.currentTime + duration);
  }

  function stepCollection(items, dt, updater) {
    for (var i = items.length - 1; i >= 0; i -= 1) {
      if (!updater(items[i], dt)) {
        items.splice(i, 1);
      }
    }
  }

  function readNumber(key) {
    try {
      return Number(localStorage.getItem(key) || 0) || 0;
    } catch (error) {
      return 0;
    }
  }

  function readSound() {
    try {
      return localStorage.getItem(SOUND_KEY) !== "off";
    } catch (error) {
      return true;
    }
  }

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function shuffle(array) {
    for (var i = array.length - 1; i > 0; i -= 1) {
      var j = Math.floor(Math.random() * (i + 1));
      var temp = array[i];
      array[i] = array[j];
      array[j] = temp;
    }
    return array;
  }

  function formatNumber(value) {
    return Math.round(value).toLocaleString("en-US");
  }

  function roundRectPath(context, x, y, width, height, radius) {
    context.beginPath();
    context.moveTo(x + radius, y);
    context.arcTo(x + width, y, x + width, y + height, radius);
    context.arcTo(x + width, y + height, x, y + height, radius);
    context.arcTo(x, y + height, x, y, radius);
    context.arcTo(x, y, x + width, y, radius);
    context.closePath();
  }
})();
