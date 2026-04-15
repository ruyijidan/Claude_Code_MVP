---
last_updated: 2026-04-10
status: active
owner: core
---

# Architecture Boundaries

## Layer Intent

### `app/cli`
- Owns argument parsing and terminal output.
- Should not contain business logic beyond presentation orchestration.

### `app/agent`
- Owns planning, repo context construction, and loop orchestration.
- May call runtime, evals, and superpowers.

### `app/runtime`
- Owns command execution, file mutation, provider integration, and git-facing primitives.
- Must stay reusable and independent from CLI and agent planning logic.

### `app/superpowers`
- Owns retry and repair behavior.
- Must remain reusable by any future loop implementation.

### `app/evals`
- Owns replay and lightweight scoring.
- Should not become a dependency source for runtime internals.

### `app/core`
- Owns shared models, specs, schema validation, and memory storage helpers.
- Safe for other layers to depend on.

## Import Rules

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

## Why These Rules Exist

These rules keep the harness portable:

- runtime can be reused by multiple frontends
- agent logic stays independent from terminal presentation
- future middleware or daemon modes can reuse the same internals

## Enforcement

Boundary checks are implemented by:

- `scripts/check_architecture.py`
- CI workflow in `.github/workflows/harness-checks.yml`
