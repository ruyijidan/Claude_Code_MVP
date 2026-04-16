---
last_updated: 2026-04-16
status: active
owner: core
---

# Architecture Docs / 架构文档

This directory answers one question:

**how is the harness structured?**

## Read Order / 阅读顺序

1. [`overview.md`](./overview.md)
2. [`boundaries.md`](./boundaries.md)
3. [`harness-explained.md`](./harness-explained.md)
4. [`interaction-harness.md`](./interaction-harness.md)

## File Roles / 文件角色

- [`overview.md`](./overview.md)
  System shape and main layers.
- [`boundaries.md`](./boundaries.md)
  Layer ownership and dependency constraints.
- [`harness-explained.md`](./harness-explained.md)
  Chinese mental-model walkthrough of the harness.
- [`interaction-harness.md`](./interaction-harness.md)
  Input normalization, turn continuation, and kickoff visibility.

## Use This Directory When / 适用场景

- you want to understand where a responsibility belongs
- you want to explain the harness to someone else
- you are deciding whether a new feature is architecture, pattern, or workflow asset
