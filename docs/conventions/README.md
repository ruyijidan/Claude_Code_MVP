---
last_updated: 2026-04-27
status: active
owner: core
---

# Conventions / 约定

This directory defines project rules that should be easy for both humans and agents to follow.

## Read Next / 接着阅读

- Docs map: `docs/README.md`
- Testing: `docs/conventions/testing.md`
- Runtime and Git workflow: `docs/conventions/runtime-and-git.md`
- Documentation hygiene: `docs/conventions/docs.md`
- Patterns: `docs/patterns/README.md`
- Guides: `docs/guides/README.md`

## Core Conventions / 核心约定

1. Prefer small, composable modules over large multi-purpose files.
2. Keep runtime abstractions reusable across different frontends.
3. Put git workflow logic in `GitTool`, not scattered shell calls.
4. Put execution logic in runtime or agent layers, not in CLI formatting code.
5. Add tests for new behavior when practical.
6. Favor explicit summaries and review output over opaque automation.
7. Put reusable execution assets in `specs/workflows`, `specs/templates`, and `specs/rules` instead of burying them in ad hoc prompts.
8. Before committing code, update project docs so the completed change and its verification state are recorded in the repository.
9. Keep repository git hooks installed so commit workflow checks run automatically before each commit.
10. New or materially updated documentation should use bilingual titles, with English and Chinese shown together in headings.
