const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const overlay = document.getElementById("overlay");
const overlayTitle = document.getElementById("overlayTitle");
const overlayText = document.getElementById("overlayText");
const startButton = document.getElementById("startButton");
const scoreLabel = document.getElementById("score");
const livesLabel = document.getElementById("lives");
const levelLabel = document.getElementById("level");
const touchControl = document.getElementById("touchControl");

const state = {
  running: false,
  lastTime: 0,
  spawnTimer: 0,
  starTimer: 0,
  score: 0,
  lives: 3,
  level: 1,
  moveLeft: false,
  moveRight: false,
  ship: {
    x: canvas.width / 2,
    y: canvas.height - 72,
    width: 42,
    height: 54,
    speed: 320,
  },
  meteors: [],
  stars: [],
};

function resetGame() {
  state.running = false;
  state.lastTime = 0;
  state.spawnTimer = 0;
  state.starTimer = 0;
  state.score = 0;
  state.lives = 3;
  state.level = 1;
  state.moveLeft = false;
  state.moveRight = false;
  state.ship.x = canvas.width / 2;
  state.meteors = [];
  state.stars = [];
  touchControl.value = 50;
  syncHud();
}

function syncHud() {
  scoreLabel.textContent = String(state.score);
  livesLabel.textContent = String(state.lives);
  levelLabel.textContent = String(state.level);
}

function showOverlay(title, text, buttonText) {
  overlay.classList.remove("hidden");
  overlayTitle.textContent = title;
  overlayText.textContent = text;
  startButton.textContent = buttonText;
}

function hideOverlay() {
  overlay.classList.add("hidden");
}

function startGame() {
  resetGame();
  state.running = true;
  hideOverlay();
  requestAnimationFrame(loop);
}

function levelSpeedBoost() {
  return 1 + (state.level - 1) * 0.18;
}

function spawnMeteor() {
  const width = 24 + Math.random() * 28;
  state.meteors.push({
    x: 22 + Math.random() * (canvas.width - 44),
    y: -40,
    width,
    height: width,
    speed: (180 + Math.random() * 160) * levelSpeedBoost(),
    spin: Math.random() * Math.PI,
  });
}

function spawnStar() {
  state.stars.push({
    x: 28 + Math.random() * (canvas.width - 56),
    y: -20,
    radius: 11,
    speed: 150 + Math.random() * 80,
    pulse: 0,
  });
}

function clampShip() {
  state.ship.x = Math.max(28, Math.min(canvas.width - 28, state.ship.x));
}

function update(delta) {
  const direction = Number(state.moveRight) - Number(state.moveLeft);
  state.ship.x += direction * state.ship.speed * delta;
  clampShip();

  state.spawnTimer += delta;
  state.starTimer += delta;

  const meteorInterval = Math.max(0.28, 1 - state.level * 0.06);
  const starInterval = Math.max(1.4, 3.1 - state.level * 0.1);

  if (state.spawnTimer >= meteorInterval) {
    state.spawnTimer = 0;
    spawnMeteor();
  }

  if (state.starTimer >= starInterval) {
    state.starTimer = 0;
    spawnStar();
  }

  for (const meteor of state.meteors) {
    meteor.y += meteor.speed * delta;
    meteor.spin += delta * 2;
  }

  for (const star of state.stars) {
    star.y += star.speed * delta;
    star.pulse += delta * 8;
  }

  state.meteors = state.meteors.filter((meteor) => {
    if (meteor.y - meteor.height > canvas.height + 10) {
      state.score += 1;
      maybeLevelUp();
      syncHud();
      return false;
    }
    return true;
  });

  state.stars = state.stars.filter((star) => star.y - star.radius <= canvas.height + 12);

  handleCollisions();
}

function maybeLevelUp() {
  const nextLevel = 1 + Math.floor(state.score / 12);
  if (nextLevel !== state.level) {
    state.level = nextLevel;
  }
}

function rectHit(a, b) {
  return (
    a.x - a.width / 2 < b.x + b.width / 2 &&
    a.x + a.width / 2 > b.x - b.width / 2 &&
    a.y - a.height / 2 < b.y + b.height / 2 &&
    a.y + a.height / 2 > b.y - b.height / 2
  );
}

function circleRectHit(circle, rect) {
  const closestX = Math.max(rect.x - rect.width / 2, Math.min(circle.x, rect.x + rect.width / 2));
  const closestY = Math.max(rect.y - rect.height / 2, Math.min(circle.y, rect.y + rect.height / 2));
  const dx = circle.x - closestX;
  const dy = circle.y - closestY;
  return dx * dx + dy * dy <= circle.radius * circle.radius;
}

function handleCollisions() {
  const shipRect = {
    x: state.ship.x,
    y: state.ship.y,
    width: state.ship.width,
    height: state.ship.height,
  };

  state.meteors = state.meteors.filter((meteor) => {
    const meteorRect = {
      x: meteor.x,
      y: meteor.y,
      width: meteor.width,
      height: meteor.height,
    };
    if (rectHit(shipRect, meteorRect)) {
      state.lives -= 1;
      syncHud();
      if (state.lives <= 0) {
        endGame();
      }
      return false;
    }
    return true;
  });

  state.stars = state.stars.filter((star) => {
    if (circleRectHit(star, shipRect)) {
      state.score += 5;
      maybeLevelUp();
      syncHud();
      return false;
    }
    return true;
  });
}

function drawBackground() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "rgba(255,255,255,0.12)";
  for (let i = 0; i < 60; i += 1) {
    const x = (i * 47) % canvas.width;
    const y = (i * 97 + state.score * 2) % canvas.height;
    ctx.beginPath();
    ctx.arc(x, y, i % 3 === 0 ? 1.8 : 1, 0, Math.PI * 2);
    ctx.fill();
  }
}

function drawShip() {
  ctx.save();
  ctx.translate(state.ship.x, state.ship.y);

  ctx.fillStyle = "#7dd3fc";
  ctx.beginPath();
  ctx.moveTo(0, -28);
  ctx.lineTo(18, 22);
  ctx.lineTo(0, 12);
  ctx.lineTo(-18, 22);
  ctx.closePath();
  ctx.fill();

  ctx.fillStyle = "#f8fafc";
  ctx.fillRect(-6, -2, 12, 18);

  ctx.fillStyle = "#fb7185";
  ctx.fillRect(-12, 18, 8, 14);
  ctx.fillRect(4, 18, 8, 14);

  ctx.restore();
}

function drawMeteor(meteor) {
  ctx.save();
  ctx.translate(meteor.x, meteor.y);
  ctx.rotate(meteor.spin);
  ctx.fillStyle = "#fb7185";
  ctx.beginPath();
  ctx.moveTo(0, -meteor.height / 2);
  for (let i = 0; i < 7; i += 1) {
    const angle = (Math.PI * 2 * i) / 7;
    const radius = meteor.width / 2 + (i % 2 === 0 ? 6 : -4);
    ctx.lineTo(Math.cos(angle) * radius, Math.sin(angle) * radius);
  }
  ctx.closePath();
  ctx.fill();
  ctx.restore();
}

function drawStar(star) {
  const pulse = 1 + Math.sin(star.pulse) * 0.08;
  ctx.save();
  ctx.translate(star.x, star.y);
  ctx.scale(pulse, pulse);
  ctx.fillStyle = "#fcd34d";
  ctx.beginPath();
  for (let i = 0; i < 10; i += 1) {
    const angle = -Math.PI / 2 + (Math.PI * i) / 5;
    const radius = i % 2 === 0 ? star.radius : star.radius * 0.45;
    const x = Math.cos(angle) * radius;
    const y = Math.sin(angle) * radius;
    if (i === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  }
  ctx.closePath();
  ctx.fill();
  ctx.restore();
}

function draw() {
  drawBackground();
  for (const meteor of state.meteors) {
    drawMeteor(meteor);
  }
  for (const star of state.stars) {
    drawStar(star);
  }
  drawShip();
}

function endGame() {
  state.running = false;
  showOverlay(
    "任务结束，飞船已返航",
    `本次得分 ${state.score}，达到了第 ${state.level} 级。按按钮或者空格再来一局。`,
    "重新开始"
  );
}

function loop(timestamp) {
  if (!state.running) {
    return;
  }
  if (!state.lastTime) {
    state.lastTime = timestamp;
  }
  const delta = Math.min(0.032, (timestamp - state.lastTime) / 1000);
  state.lastTime = timestamp;
  update(delta);
  draw();
  if (state.running) {
    requestAnimationFrame(loop);
  }
}

window.addEventListener("keydown", (event) => {
  if (event.key === "ArrowLeft" || event.key.toLowerCase() === "a") {
    state.moveLeft = true;
  }
  if (event.key === "ArrowRight" || event.key.toLowerCase() === "d") {
    state.moveRight = true;
  }
  if (event.code === "Space" && !state.running) {
    startGame();
  }
});

window.addEventListener("keyup", (event) => {
  if (event.key === "ArrowLeft" || event.key.toLowerCase() === "a") {
    state.moveLeft = false;
  }
  if (event.key === "ArrowRight" || event.key.toLowerCase() === "d") {
    state.moveRight = false;
  }
});

touchControl.addEventListener("input", () => {
  const minX = 28;
  const maxX = canvas.width - 28;
  const ratio = Number(touchControl.value) / 100;
  state.ship.x = minX + (maxX - minX) * ratio;
  clampShip();
});

startButton.addEventListener("click", startGame);
draw();
