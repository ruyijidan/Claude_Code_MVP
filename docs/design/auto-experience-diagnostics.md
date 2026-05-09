---
title: Auto Experience Diagnostics / 自动体验诊断
version: 1.0.0
created: 2026-05-09
purpose: Define how long-task game runs can detect user-facing experience issues automatically instead of relying only on manual feedback
tags: [design, harness, diagnostics, game-dev, autonomy]
---

# Auto Experience Diagnostics / 自动体验诊断

## Goal / 目标

Long-task game runs should be able to notice when the game feels too short, too interruptive, too cramped, or too hard to read.

长任务小游戏执行不应该只记录“改了什么”，还要尽量自动发现游戏体验上的问题，比如一局太快结束、升级打断太频繁、界面太挤、画面太难读。

The harness should keep a lightweight diagnostic trail so each iteration can say what it improved and what still feels weak.

harness 应该保留轻量诊断轨迹，让每一轮迭代都能说明它改善了什么、还弱在哪里。

Actual gameplay feel takes priority over the diagnostics when they disagree.

如果诊断信号和实际游玩感受冲突，应以实际游玩感受为准。

## Scope of This Signal / 信号范围

These diagnostics are proxy signals for the current task and the current reviewer perspective.

这些诊断信号只是当前任务、当前执行者视角下的代理信号。

They are not a substitute for real customer research, live user testing, or product-market feedback.

它们不能替代真实客户调研、真实用户测试或产品市场反馈。

Use them to steer the long-task loop, not to claim that actual customers feel the same way.

它们的用途是指导长任务循环，而不是声称真实客户一定有同样的感受。

## What We Want To Detect / 我们要检测什么

### 1. Time-to-first-meaningful-play / 首次进入有效游玩所需时间

- How long it takes before the player is clearly in the main loop
- Whether the run spends too long on menus, overlays, or draft states

### 2. Wave Duration / 波次持续时间

- How long each wave lasts in practice
- Whether a wave ends before the player can learn or react

### 3. Upgrade Interruption Cost / 升级打断成本

- Whether an upgrade screen blocks the main loop too often
- Whether the player must click too many times just to continue

### 4. Visual Occlusion / 视觉遮挡

- Whether overlays cover the main action too aggressively
- Whether HUD elements overflow, wrap badly, or hide the arena

### 5. Input Friction / 输入摩擦

- Whether the player can keep moving without repeated modal confirmations
- Whether touch, keyboard, and pointer controls feel consistent

### 6. Visible Progress / 可见进步

- Whether a new iteration makes the game easier to read or play
- Whether the change affects the actual loop instead of only text labels

## Signals To Record / 需要记录的信号

The long-task session log should record a short list of gameplay signals for each iteration:

- `main_loop_entry_seconds`
- `first_wave_duration_seconds`
- `upgrade_interruptions`
- `overlay_visible_seconds`
- `ui_overflow_detected`
- `manual_clicks_required_to_continue`
- `player_visible_progress_delta`
- `summary`

These can start as approximate or heuristic values.

这些信号一开始可以是近似值或启发式值，不必一开始就做成很重的统计系统。

## Diagnostic Loop / 诊断循环

1. Observe current gameplay state
2. Record the weak signal with the highest user impact
3. Make one narrow visible fix
4. Re-run local verification
5. Compare the same signal again
6. Keep or discard the change based on whether the signal improved

## Recommended Heuristics / 推荐启发式

These heuristics are simple enough to use in a long-task runner without building a full analytics stack:

- If a wave ends in under a small threshold, treat it as too short
- If the player must click to continue every wave, treat it as interruptive
- If overlay text covers the playfield for too long, treat it as intrusive
- If canvas or HUD content wraps badly at mobile widths, treat it as layout friction
- If a change only touches labels without changing playability, treat it as weak progress

## How The Harness Should Use It / harness 应如何使用

The runner should include these diagnostics in each iteration summary:

- what was optimized
- which gameplay signal changed
- whether the change was visible
- whether the change reduced friction

If a run still looks bad after several iterations, the harness should pivot to the biggest remaining weakness instead of continuing to polish the same thing.

如果连续几轮后体验仍然不好，harness 应该切到最大短板，而不是继续在同一个地方抛光。

If a diagnostic signal says a change looks good but the game still feels bad in play, the harness should treat the iteration as incomplete and keep iterating.

如果诊断信号显示改动“看起来不错”，但实际玩起来仍然不好，harness 应该把这轮视为未完成，继续迭代。

## Example Per-Iteration Summary / 每轮摘要示例

```text
did: reduced wave interruption by removing a required mouse click
optimized: upgrade interruption cost
artifact: examples/starforge-relay/game.js
next: check whether the first wave now lasts long enough to feel playable
```

## Success Criteria / 成功标准

- Each iteration can name the experience problem it tackled
- The log shows whether the problem got better
- The final game feels better in practice for the current task context, not just in wording
- The final game feels better when actually played, even if a proxy metric still looks weak
- The harness can explain why a change was chosen without human prompting

## Anti-Patterns / 反模式

- Only logging file names without saying what got better
- Repeating the same type of fix while the main experience problem stays unsolved
- Treating text edits as progress when the game still feels bad
- Waiting for a human to point out obvious usability issues
