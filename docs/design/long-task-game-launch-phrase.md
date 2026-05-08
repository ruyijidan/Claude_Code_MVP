---
last_updated: 2026-05-07
status: active
owner: core
---

# Long Task Game Launch Phrase / 长任务小游戏发起口令

## Short Prompt / 短口令

```text
Run a long-task browser mini-game session for about 30 minutes.
Follow docs/design/long-task-game-execution.md.
Do not ask for step-by-step approval.
Stay autonomous.
Improve the game in visible, user-facing layers.
Verify locally before reporting completion.
Do not claim the 30-minute target was met unless the run really sustained it
or the session log proves it.
Create a session log using docs/design/long-task-game-session-log-template.md.
Success criteria:
- produce a visibly improved standalone browser game under examples/halo-drift
- keep the game playable from file:// without external dependencies
- add or strengthen a visible progression loop, restart flow, and results flow
- verify the main JavaScript file locally before finishing
Return only the final artifact path, key changes, and verification results.
```

## Notes / 备注

- Use this when you want the default unattended long-task flow.
- For script-driven runs, pair this with `scripts/start_long_task_game_session.sh`.
- Use the longer task template if you want extra detail or if the task needs
  explicit fallback instructions.
