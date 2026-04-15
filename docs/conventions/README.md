---
last_updated: 2026-04-10
status: active
owner: core
---

# Conventions

This directory defines project rules that should be easy for both humans and agents to follow.

## Read Next

- Testing: `docs/conventions/testing.md`
- Runtime and Git workflow: `docs/conventions/runtime-and-git.md`
- Documentation hygiene: `docs/conventions/docs.md`
- Patterns: `docs/patterns/`
- Guides: `docs/guides/`

## Core Conventions

1. Prefer small, composable modules over large multi-purpose files.
2. Keep runtime abstractions reusable across different frontends.
3. Put git workflow logic in `GitTool`, not scattered shell calls.
4. Put execution logic in runtime or agent layers, not in CLI formatting code.
5. Add tests for new behavior when practical.
6. Favor explicit summaries and review output over opaque automation.
7. Put reusable execution assets in `specs/workflows`, `specs/templates`, and `specs/rules` instead of burying them in ad hoc prompts.
