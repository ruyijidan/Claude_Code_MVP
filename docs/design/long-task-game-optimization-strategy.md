---
title: Long-Task Game Optimization Strategy / 长任务小游戏优化策略
version: 1.0.0
created: 2026-05-08
purpose: Define how autonomous long-task game sessions should converge toward a better final game instead of merely consuming time
tags: [process, game-dev, autonomy, optimization]
---

# Long-Task Game Optimization Strategy / 长任务小游戏优化策略

## Goal / 目标

The goal of a long-task game session is to improve one game continuously until the work converges on the best result achievable within the time budget.

长任务小游戏的目标，不是“跑满时间”，而是在一次持续执行里不断优化同一个游戏，让最终成果尽可能接近该时间预算内的最优解。

## Core Principle / 核心原则

Each iteration must make the game better in a way a user can observe.

每一轮迭代都必须带来用户可见的改进。

If a change does not improve playability, clarity, polish, or progression, it is not a useful change for the long-task loop.

如果一个改动没有提升可玩性、清晰度、完成度或推进感，它就不是长任务循环中的有效改动。

## Iteration Loop / 迭代循环

### 1. Observe / 观察

- Inspect the current artifact state
- Identify the highest-friction experience problems
- Pick the next change that will unlock the most visible improvement

### 2. Change / 修改

- Keep the next change narrow enough to finish quickly
- Prefer changes that improve the main game loop over decorative additions
- Avoid restarting the design unless the current direction is clearly wrong

### 3. Verify / 验证

- Check the game locally after each meaningful change
- Keep file:// compatibility intact
- Confirm the change does not break restart, progression, or results behavior

### 4. Record / 记录

- Capture what changed
- Capture what improved
- Capture what still feels weak

### 5. Repeat / 重复

- Use the next iteration to remove the biggest remaining weakness
- Keep the same game direction unless evidence says to pivot

## Optimization Order / 优化顺序

When time is limited, prioritize work in this order:

1. Core playability
2. Progression loop
3. Restart and results flow
4. Feedback quality
5. Visual polish
6. Score/leaderboard/streak depth
7. Nice-to-have embellishments

This order keeps the session focused on compounding value instead of scattered polish.

## Convergence Rules / 收敛规则

- Keep the same game identity through the session
- Improve the weakest user-facing part first
- Prefer fewer changes with stronger impact
- Remove features that create noise without improving the experience
- When the game feels good, shift from expansion to refinement

## Stop Conditions / 停止条件

Stop the session when one of these is true:

- The game is clearly better than the starting point and further changes would mostly be cosmetic
- The remaining improvements are too small for the time left
- A change would require a direction reset instead of a refinement

## What Success Looks Like / 成功标准

- The final game feels more complete than the starting build
- The main loop is stronger than at the beginning
- Restart and results behavior are reliable
- The best improvements were chosen because they helped the game converge, not because they filled time

## Anti-Patterns / 反模式

- Repeating the same kind of change just to spend time
- Expanding scope by adding unrelated modes or features
- Treating long duration as the success criterion
- Restarting from scratch when the current build only needs refinement
- Making changes that are hard to perceive in the game itself

