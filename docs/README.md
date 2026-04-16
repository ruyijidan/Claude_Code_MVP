---
last_updated: 2026-04-16
status: active
owner: core
---

# Docs Map / 文档地图

`docs/` is organized by intent, not by chronology.

If you only want one rule for navigating this directory:

- `architecture`: understand how the system is shaped
- `conventions`: understand project rules
- `patterns`: understand reusable harness concepts
- `guides`: understand how to extend the repo
- `plans`: understand what is being built next
- `reference`: understand external comparisons and reading notes

## Fast Start / 快速开始

If you are new to the repository, read in this order:

1. [`../README.md`](../README.md)
2. [`../ARCHITECTURE.md`](../ARCHITECTURE.md)
3. [`architecture/overview.md`](./architecture/overview.md)
4. [`architecture/harness-explained.md`](./architecture/harness-explained.md)
5. [`conventions/README.md`](./conventions/README.md)
6. [`plans/current-sprint.md`](./plans/current-sprint.md)

## Directory Map / 目录地图

### Architecture / 架构

Core system shape and layer boundaries.

- [`architecture/overview.md`](./architecture/overview.md)
- [`architecture/boundaries.md`](./architecture/boundaries.md)
- [`architecture/harness-explained.md`](./architecture/harness-explained.md)
- [`architecture/interaction-harness.md`](./architecture/interaction-harness.md)

Use this directory when the question is:

- how does the system work?
- where does this responsibility belong?
- what does a harness layer mean here?

### Conventions / 约定

Project rules and day-to-day engineering expectations.

- [`conventions/README.md`](./conventions/README.md)
- [`conventions/testing.md`](./conventions/testing.md)
- [`conventions/runtime-and-git.md`](./conventions/runtime-and-git.md)
- [`conventions/docs.md`](./conventions/docs.md)

Use this directory when the question is:

- what is the expected coding style?
- how should tests be added?
- how should runtime and git behavior work?

### Patterns / 模式

Stable reusable harness ideas that sit above raw architecture details.

- [`patterns/workflow-layer.md`](./patterns/workflow-layer.md)
- [`patterns/asset-layer.md`](./patterns/asset-layer.md)

Use this directory when the question is:

- what reusable pattern are we following?
- how should workflow assets or rule assets be modeled?

### Guides / 指南

Contributor playbooks for adding or extending assets.

- [`guides/how-to-add-a-workflow.md`](./guides/how-to-add-a-workflow.md)
- [`guides/how-to-add-a-rule.md`](./guides/how-to-add-a-rule.md)

Use this directory when the question is:

- how do I add something safely?
- where should a new workflow or rule go?

### Plans / 计划

Execution roadmap and current implementation focus.

- [`plans/current-sprint.md`](./plans/current-sprint.md)
- [`plans/harness-hardening-pr-plan.md`](./plans/harness-hardening-pr-plan.md)

Use this directory when the question is:

- what is in flight?
- what already shipped?
- what is the next hardening step?

### Reference / 参考

External reading notes and comparison material.

- [`reference/README.md`](./reference/README.md)
- [`reference/12-harness-patterns.md`](./reference/12-harness-patterns.md)
- grouped reading notes for harness basics, product/runtime shape, reverse engineering, and spec coding

Use this directory when the question is:

- what outside project or article should I compare against?
- where did a certain harness idea come from?

### Design / 设计

Lightweight templates for future feature/design writeups.

- [`design/template.md`](./design/template.md)

Use this directory when the question is:

- where is the draft design template?

## Recommended Reading Paths / 推荐阅读路径

### Understand The Current Harness / 理解当前 Harness

1. [`../ARCHITECTURE.md`](../ARCHITECTURE.md)
2. [`architecture/overview.md`](./architecture/overview.md)
3. [`architecture/boundaries.md`](./architecture/boundaries.md)
4. [`architecture/interaction-harness.md`](./architecture/interaction-harness.md)

### Extend The Workflow System / 扩展工作流系统

1. [`patterns/workflow-layer.md`](./patterns/workflow-layer.md)
2. [`guides/how-to-add-a-workflow.md`](./guides/how-to-add-a-workflow.md)
3. [`../specs/workflows`](../specs/workflows)

### Extend The Rule System / 扩展规则系统

1. [`patterns/asset-layer.md`](./patterns/asset-layer.md)
2. [`guides/how-to-add-a-rule.md`](./guides/how-to-add-a-rule.md)
3. [`../specs/rules`](../specs/rules)

### Compare With External Harnesses / 对照外部 Harness

1. [`reference/README.md`](./reference/README.md)
2. [`reference/12-harness-patterns.md`](./reference/12-harness-patterns.md)

## Notes / 说明

- `docs/` explains the repository.
- `specs/` contains structured assets that the code can consume.
- `logs/` contains execution evidence, not durable documentation.
