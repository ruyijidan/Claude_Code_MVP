---
last_updated: 2026-05-07
status: active
owner: core
---

# Long Task Game Execution Runbook / 长任务小游戏执行手册

## Purpose / 目的

This document defines the default execution pattern for long-running mini-game
tasks in this repository.

This is the source of truth for future long-task mini-game runs. If a request
conflicts with this runbook, follow this runbook unless the user explicitly
overrides it.

The goal is to keep future runs consistent:

- the task is executed as an unattended long task, not as a back-and-forth
  design session
- progress is judged by the artifact and verification results, not by interim
  preference checks
- the final output should be a playable local game artifact plus a concise
  verification record

This runbook applies to the old “600-second / 30-minute game task” style work
and any future reruns that want the same unattended flow.

## Default Rule / 默认规则

Do not steer the task interactively while it is running.

Instead:

1. pick the target artifact or create a fresh standalone artifact
2. let the task run continuously
3. make improvements inside the task only when they clearly improve the
   playable output or reduce risk
4. report the final artifact and verification at the end

If the task needs a decision that changes the product direction, pause once and
ask before continuing. Otherwise, keep the run autonomous.

## Hard Requirements / 硬性要求

Every long-task mini-game run must satisfy all of the following:

- run as an unattended task, not as a step-by-step design review
- keep the task focused on one artifact or one rerun target
- prefer visible product improvements over implementation-only churn
- verify the artifact locally before reporting completion
- report both the final state and the verification result
- avoid asking the user to choose between every small upgrade
- when the request specifies "30 minutes" or "600 seconds", the run must
  either be actually sustained for that duration or explicitly say it was not
- when a time target is requested, create a session log that records the
  requested duration, actual duration, artifact path, and verification result

If any requirement cannot be met, say so clearly before proceeding.

## Approved Task Shapes / 允许的任务形态

Use this runbook for:

- standalone browser mini-games under `examples/`
- long-running polish passes that keep upgrading the same game artifact
- reruns of a previously completed long-task game
- validation tasks that must spend meaningful provider time and still produce a
  concrete local artifact

Do not use this runbook for:

- short documentation edits
- code review only
- acceptance reporting without code changes
- ad hoc brainstorming sessions

## Recommended Workflow / 推荐流程

### 1. Identify the target / 确定目标

Decide whether the run is:

- a rerun of an existing game artifact
- a fresh standalone game
- a polish pass on an already playable game

Prefer reusing an existing playable artifact if the user explicitly says “the
previous long-task game” or “the old one”.

### 2. Keep the run autonomous / 保持自治执行

During the run:

- do not ask for incremental approval for every upgrade
- avoid converting the run into a manual feature request thread
- choose improvements that make the game more complete, more durable, or more
  clearly verifiable

The run should behave like a focused worker session, not a product workshop.

### 3. Improve in visible layers / 分层改进

Prefer upgrades in this order:

1. core loop clarity
2. survival or progression systems
3. restart / pause / results flows
4. controls and accessibility
5. visual polish
6. documentation and verification notes

This keeps the task moving toward a better playable artifact instead of getting
stuck on ornamental changes.

### 4. Verify locally / 本地验证

At minimum, verify:

- the game opens directly from `file://`
- local assets are self-contained
- the main JavaScript file passes syntax validation
- no unintended files were modified

If the task includes more than a quick polish pass, add a lightweight smoke
check for the relevant game controls or page structure.

Suggested minimum commands:

```bash
node --check examples/<game>/game.js
```

If the task changed the page structure or interaction model, add an additional
browser-level smoke check or a second syntax check for any touched script files.

### 5. Record the outcome / 记录结果

When the run finishes, record:

- artifact path
- short description of what changed
- verification commands
- verification result
- whether the run preserved the old artifact or replaced it

## Game-Specific Acceptance Checklist / 小游戏专用验收清单

Use this checklist for browser mini-games:

- `index.html` opens directly from the filesystem
- the game has a clear first screen or start state
- controls are visible and usable without reading source code
- a failure or win state exists
- the run has a replay path
- the artifact does not rely on external build steps
- the final README explains the controls and quick checks

If the task is explicitly a long-run upgrade pass, also require:

- a progression mechanic that keeps the game interesting across time
- at least one visible improvement that is obvious on first open
- a result that is clearly better than a placeholder or minimal prototype

## Execution Notes / 执行备注

- If the request says “30 minutes” or “600 seconds”, treat that as a hard
  runtime target, not just a stylistic hint.
- Do not claim the run satisfied the time target unless the session really ran
  that long or the external provider/session log proves it.
- If there is no session log, do not claim the time target was met.
- If a provider-backed long task is available, use that path instead of manual
  incremental editing.
- If the provider-backed path is unavailable, say so plainly and fall back to a
  local autonomous implementation only when that still matches the user’s goal.
- Keep the final report short and factual.
- For script-driven runs, start with `scripts/start_long_task_game_session.sh`
  so the run gets a session log, a timeout wrapper, and a verification record.

## Operator Prompt Template / 执行提示模板

Use this template when starting a future long-task mini-game run:

```text
Run a long-task browser mini-game session for about 30 minutes.
Follow the long-task game execution runbook.
Do not ask for step-by-step approval during the run.
Keep the work autonomous and focused on one game artifact.
Improve the game in visible, user-facing layers.
Verify locally before reporting completion.
Return only the final artifact path, the key changes, and verification results.
```

## Related Docs / 相关文档

- [`long-task-game-upgrade.md`](./long-task-game-upgrade.md)
- [`long-task-game-rerun-2026-04-24.md`](./long-task-game-rerun-2026-04-24.md)
- [`acceptance-report.md`](./acceptance-report.md)
- [`intent-clarifier.md`](./intent-clarifier.md)
