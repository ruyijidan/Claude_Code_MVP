---
last_updated: 2026-04-10
status: active
owner: core
---

# Architecture Boundaries / 架构边界

## Layer Intent / 分层意图

### `app/cli` / CLI 层
- Owns argument parsing and terminal output.
- Should not contain business logic beyond presentation orchestration.

### `app/agent` / Agent 层
- Owns planning, repo context construction, and loop orchestration.
- May call runtime, evals, and superpowers.

### `app/runtime` / Runtime 层
- Owns command execution, file mutation, provider integration, and git-facing primitives.
- Must stay reusable and independent from CLI and agent planning logic.

### `app/superpowers` / Superpowers 层
- Owns retry and repair behavior.
- Must remain reusable by any future loop implementation.

### `app/evals` / Evals 层
- Owns replay and lightweight scoring.
- Should not become a dependency source for runtime internals.

### `app/core` / Core 层
- Owns shared models, specs, schema validation, and memory storage helpers.
- Safe for other layers to depend on.

## Import Rules / 导入规则

The intended dependency direction is:

`app/core` -> reusable shared primitives

`app/runtime`, `app/evals`, `app/superpowers` -> may depend on `app/core`

`app/agent` -> may depend on `app/core`, `app/runtime`, `app/evals`, `app/superpowers`

`app/cli` -> may depend on all public entrypoints above

Forbidden patterns:

- `app/runtime` importing from `app/cli`
- `app/runtime` importing from `app/agent`
- `app/agent` importing from `app/cli`
- lower layers depending on CLI presentation concerns

## Why These Rules Exist / 为什么有这些规则

These rules keep the harness portable:

- runtime can be reused by multiple frontends
- agent logic stays independent from terminal presentation
- future middleware or daemon modes can reuse the same internals

## Enforcement / 执行方式

Boundary checks are implemented by:

- `scripts/check_architecture.py`
- CI workflow in `.github/workflows/harness-checks.yml`
