---
last_updated: 2026-05-07
status: active
owner: core
---

# Long Task Game Task Template / 长任务小游戏任务模板

## When to Use / 何时使用

Use this template when starting a browser mini-game long task that should run
autonomously and follow the long-task game execution runbook.

## Copy-Paste Template / 可直接复制的模板

```text
Run a long-task browser mini-game session for about 30 minutes.

Follow docs/design/long-task-game-execution.md as the execution contract.

Requirements:
- do not ask for step-by-step approval during the run
- keep the task autonomous and focused on one game artifact
- improve the game in visible, user-facing layers
- verify locally before reporting completion
- report only the final artifact path, key changes, and verification results

If the provider-backed long-task path is available, use it.
If it is not available, say so plainly before falling back to a local
autonomous implementation.

Success criteria:
- produce a visibly improved standalone browser game under examples/halo-drift
- keep the game playable from file:// without external dependencies
- add or strengthen a visible progression loop, restart flow, and results flow
- verify the main JavaScript file locally before finishing
```

## Expected Output / 预期输出

The final response should include:

- the artifact path
- the most important changes made during the run
- the verification commands that were run
- the verification result
- whether the run preserved an existing artifact or created a new one
