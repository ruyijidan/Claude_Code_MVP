---
last_updated: 2026-04-10
status: active
owner: core
---

# Testing Conventions

## Expectations

- New user-visible CLI behavior should have a test when practical.
- Runtime helpers should be covered by focused unit tests.
- Avoid tests that depend on live network access.
- Prefer deterministic tests over end-to-end external CLI execution.

## Patterns

- Patch external command execution in tests instead of invoking real long-running tools.
- Use temporary directories for repository simulations.
- Assert developer-facing output, not just internal return values.

## Minimum Bar

When adding a new feature, at least one of the following should exist:

- a CLI behavior test
- a runtime/tool unit test
- an agent loop or integration-oriented test
