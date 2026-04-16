---
last_updated: 2026-04-16
status: active
owner: core
---

# Reference / 参考

This directory is for outside reading, comparison notes, and architecture cross-checks.

These files are:

- not implementation source of truth
- not runtime dependencies
- not commit-by-commit project history

They are here to answer:

- what external material is worth reading?
- what problem does each reference illuminate?
- how does each reference map back to `Claude_Code_MVP`?

## Quick Picks / 快速选择

If you only want the most useful starting points:

1. [`12-harness-patterns.md`](./12-harness-patterns.md)
   Best for: quick harness control-surface checklist.
2. [`dewu-spec-coding.md`](./dewu-spec-coding.md)
   Best for: turning AI coding into a constrained delivery workflow.
3. [`deer-flow.md`](./deer-flow.md)
   Best for: seeing how a thicker agent runtime grows around skills, sandbox, and sub-agents.

## Read By Goal / 按目标阅读

### Goal: Understand Harness Basics / 目标：理解 Harness 基础

Start here if you want the cleanest mental model of harness engineering.

- [`12-harness-patterns.md`](./12-harness-patterns.md)
- external: `claude-code-book`

Questions these help answer:

- what belongs in the harness instead of the model?
- what control points are essential?
- which parts of our repository already match common harness patterns?

### Goal: Understand Product-Shaped Harnesses / 目标：理解产品化 Harness

Start here if you want to see what a more complete harness platform looks like.

- [`hermes-agent.md`](./hermes-agent.md)
- [`deer-flow.md`](./deer-flow.md)
- [`everything-claude-code.md`](./everything-claude-code.md)
- external: `claw-code`

Questions these help answer:

- what comes after a coding-harness MVP?
- how do skills, toolsets, sandboxing, and multi-entrypoint products fit together?
- what does a thicker runtime or product surface look like?

### Goal: Understand Industrial-Strength Claude Code Style Systems / 目标：理解工业级 Claude Code 风格系统

Start here if you want to study more complete or reverse-engineered Claude Code style systems.

- [`claude-code-source-leak.md`](./claude-code-source-leak.md)
- external: `claude-code-book`

Questions these help answer:

- what are we still missing around context compression, memory, safety thickness, and cost controls?
- what usually gets productized beyond a compact harness MVP?

### Goal: Understand Spec Coding And Delivery Workflows / 目标：理解 Spec Coding 与交付工作流

Start here if you want to study how teams make AI coding more deterministic.

- [`dewu-spec-coding.md`](./dewu-spec-coding.md)

Questions these help answer:

- how should rules, templates, and examples work together?
- why are vague requirements and information gaps the real failure source?
- what should a layered delivery workflow look like?

## Reference Groups / 参考分组

### A. Harness Mental Models / Harness 心智模型

- [`12-harness-patterns.md`](./12-harness-patterns.md)

This group is best when you want a checklist or conceptual lens.

### B. Product And Runtime Shape / 产品与运行时形态

- [`hermes-agent.md`](./hermes-agent.md)
- [`deer-flow.md`](./deer-flow.md)
- [`everything-claude-code.md`](./everything-claude-code.md)

This group is best when you want to see how skills, sandboxing, memory, and richer runtime systems are organized.

### C. Claude Code Reverse Engineering And Deep Analysis / Claude Code 逆向与深度分析

- [`claude-code-source-leak.md`](./claude-code-source-leak.md)

This group is best when you want to compare our current harness thickness with a more industrial implementation style.

### D. Spec Coding And Team Workflow / Spec Coding 与团队工作流

- [`dewu-spec-coding.md`](./dewu-spec-coding.md)

This group is best when you want to think about task shaping, templates, examples, and deterministic execution spaces.

## Mapping To This Repository / 与本仓库的映射

| Reference | Best For | Most Relevant Gap In `Claude_Code_MVP` |
|---|---|---|
| [`12-harness-patterns.md`](./12-harness-patterns.md) | harness control surface checklist | context, gates, repair, permissions, memory roadmap |
| [`hermes-agent.md`](./hermes-agent.md) | product-shaped harness comparison | memory, skills, richer tool/runtime surfaces |
| [`deer-flow.md`](./deer-flow.md) | super-agent runtime evolution | skills, middleware, sandbox, sub-agent model |
| [`everything-claude-code.md`](./everything-claude-code.md) | extension asset organization | commands, hooks, MCP-style enhancement assets |
| [`claude-code-source-leak.md`](./claude-code-source-leak.md) | industrial-strength Claude Code style analysis | compression, safety thickness, memory, cost controls |
| [`dewu-spec-coding.md`](./dewu-spec-coding.md) | spec coding workflow | rule layer, template layer, external context, workflow tiers |

## Suggested Reading Paths / 推荐阅读路径

### Minimal Path / 最小阅读路径

1. [`../../README.md`](../../README.md)
2. [`../../ARCHITECTURE.md`](../../ARCHITECTURE.md)
3. [`../architecture/harness-explained.md`](../architecture/harness-explained.md)
4. [`12-harness-patterns.md`](./12-harness-patterns.md)

### Next-Step Product Path / 下一阶段产品路径

1. [`12-harness-patterns.md`](./12-harness-patterns.md)
2. [`hermes-agent.md`](./hermes-agent.md)
3. [`deer-flow.md`](./deer-flow.md)
4. [`claude-code-source-leak.md`](./claude-code-source-leak.md)

### Delivery Workflow Path / 交付工作流路径

1. [`12-harness-patterns.md`](./12-harness-patterns.md)
2. [`dewu-spec-coding.md`](./dewu-spec-coding.md)

## Notes / 说明

- `reference/` is for comparison and learning.
- `architecture/`, `conventions/`, and `patterns/` define this repository.
- `specs/` and `app/` are where behavior actually lives.
