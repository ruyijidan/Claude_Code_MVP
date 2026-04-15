# Architecture

Navigation:

- [`README.md`](./README.md): project positioning, quick start, and capability boundaries
- [`AGENTS.md`](./AGENTS.md): agent navigation and repository working rules
- [`docs/architecture/interaction-harness.md`](./docs/architecture/interaction-harness.md): interaction entry layer, intent normalization, and kickoff visibility
- [`docs/`](./docs): detailed architecture constraints, conventions, and plans

## Overview

`Claude_Code_MVP` is a minimal agent harness for terminal-first coding workflows.

Its core loop is:

`user request -> CLI -> permission pipeline -> agent loop -> runtime -> verify -> repair -> replay`

This repository is not just a prompt wrapper around a model. It is an execution environment that makes an agent:

- readable: the project has structured docs and entrypoints
- controllable: the project has policies and guardrails
- verifiable: the project can run tests and isolated verification
- observable: the project stores replay artifacts and git summaries

## Harness Layers

Harness Engineering is easiest to understand in three layers.

### 1. Information Layer

This layer tells the agent where knowledge lives and how to read the project.

Key files:

- [`AGENTS.md`](./AGENTS.md)
- [`docs/architecture/overview.md`](./docs/architecture/overview.md)
- [`docs/architecture/boundaries.md`](./docs/architecture/boundaries.md)
- [`docs/architecture/interaction-harness.md`](./docs/architecture/interaction-harness.md)
- [`docs/conventions/README.md`](./docs/conventions/README.md)
- [`docs/plans/current-sprint.md`](./docs/plans/current-sprint.md)

Responsibilities:

- explain repository purpose
- define architecture boundaries
- document interaction entry behavior and continuation rules
- document conventions and plans
- give the agent a stable navigation map

### 2. Constraint Layer

This layer forces the agent to operate inside explicit boundaries.

Key files:

- [`app/agent/policies.py`](./app/agent/policies.py)
- [`scripts/check_architecture.py`](./scripts/check_architecture.py)
- [`scripts/agent_verify.sh`](./scripts/agent_verify.sh)
- [` .github/workflows/harness-checks.yml `](./.github/workflows/harness-checks.yml)

Responsibilities:

- classify operation risk
- decide whether execution is allowed
- block architecture boundary violations
- verify code in an isolated worktree
- provide CI guardrails for repeated enforcement

### 3. Automation Layer

This layer closes the execution loop.

Key files:

- [`app/cli/main.py`](./app/cli/main.py)
- [`app/agent/loop.py`](./app/agent/loop.py)
- [`app/runtime/adapter_factory.py`](./app/runtime/adapter_factory.py)
- [`app/runtime`](./app/runtime)
- [`app/superpowers/self_repair.py`](./app/superpowers/self_repair.py)
- [`app/evals/replay.py`](./app/evals/replay.py)

Responsibilities:

- accept user intent
- collect repo context
- choose a task shape
- execute locally or delegate to provider CLIs
- verify outcomes
- repair when possible
- persist trajectories for replay

## Execution Flow

### 1. CLI Entry

Primary entrypoint:

- [`app/cli/main.py`](./app/cli/main.py)

The CLI is the control surface for the harness. It:

- reads the developer request
- resolves the repository path
- auto-loads local provider configuration from [`.env`](./.env)
- selects the runtime provider
- runs permission assessment
- either delegates to a provider CLI or enters the local loop

Representative modes:

- inspection mode: `--show-status`, `--show-review`, `--show-permissions`
- local loop mode: run the built-in coding loop
- delegated provider mode: send the request to `claude` or `codex`

### 2. Permission Pipeline

Policy decisions live in:

- [`app/agent/policies.py`](./app/agent/policies.py)

The permission pipeline is the first control point after request intake.

It currently evaluates operations such as:

- `inspect`
- `local_loop`
- `delegated_provider`

Outputs include:

- risk level
- whether the action is approved
- whether confirmation is required
- recommended retry flags

This is what makes the project a harness instead of a bare CLI wrapper: execution is classified before it happens.

### 3. Context and Planning

Key files:

- [`app/agent/context_builder.py`](./app/agent/context_builder.py)
- [`app/agent/planner.py`](./app/agent/planner.py)
- [`app/agent/loop.py`](./app/agent/loop.py)

The local loop first builds a repo-aware context. That context can include:

- repository path
- user prompt
- git summary
- candidate files
- test directory presence

The planner then infers a lightweight task shape such as:

- `fix_bug`
- `implement_feature`
- `write_tests`
- `investigate_issue`

This is deliberately lightweight. The project currently prefers a simple single-agent coding loop over a heavy multi-agent orchestration graph.

### 4. Runtime Abstraction

Key files:

- [`app/runtime/adapter_factory.py`](./app/runtime/adapter_factory.py)
- [`app/runtime/ecc_adapter.py`](./app/runtime/ecc_adapter.py)
- [`app/runtime/local_runtime.py`](./app/runtime/local_runtime.py)
- [`app/runtime/cli_adapter.py`](./app/runtime/cli_adapter.py)

The runtime layer decouples execution intent from execution backend.

Supported provider names:

- `local`
- `claude_code`
- `codex_cli`

Current meaning:

- `local`: local single-loop execution with repository file mutation and test execution
- `claude_code`: delegated execution through the local `claude` CLI
- `codex_cli`: delegated execution through the local `codex` CLI

This separation is important for harness design: the agent loop does not need to know which backend is used.

## Verification and Repair

### Verification

Verification happens in two forms.

Inline verification:

- run tests from the runtime layer
- inspect git state and review summaries

Isolated verification:

- [`scripts/agent_verify.sh`](./scripts/agent_verify.sh)

The worktree verification script:

- creates a temporary git worktree
- falls back to detached mode if the branch is already checked out
- syncs the current working tree into the verification workspace
- installs the project
- runs architecture checks
- runs the unit test suite
- cleans up automatically

### Repair

Repair logic lives in:

- [`app/superpowers/self_repair.py`](./app/superpowers/self_repair.py)

Repair is still lightweight, but it already reflects a harness mindset:

- do not stop at first failure when a deterministic retry or patch is possible
- use verification output to drive the next action

## Replay and Logs

Replay logic lives in:

- [`app/evals/replay.py`](./app/evals/replay.py)
- [`app/core/memory_store.py`](./app/core/memory_store.py)

Artifacts can be written to:

- repository-local `.claude-code/trajectories`
- fallback temp storage when repo-local writes are not possible
- [`logs`](./logs) for explicit test and verification logs

Replay matters because a harness is not only about execution. It is also about traceability:

- what happened
- which provider was used
- which path was selected
- whether verification passed

## Git-Aware UX

Git-facing utilities live in:

- [`app/runtime/git_tool.py`](./app/runtime/git_tool.py)

The current CLI can expose:

- status
- diff
- changed files
- review summary
- suggested commit summary
- post-run review and commit summary

This makes the project more than a coding sandbox. It turns the harness into a developer-facing workflow surface.

## Configuration Model

Local provider configuration is auto-loaded from:

- [`.env`](./.env)

The loader lives in:

- [`app/core/env_loader.py`](./app/core/env_loader.py)

At the moment the project supports shell-style `export KEY=value` entries for local configuration, including Anthropic-compatible settings such as:

- `ANTHROPIC_BASE_URL`
- `ANTHROPIC_AUTH_TOKEN`
- `ANTHROPIC_MODEL`

This makes the delegated provider path easier to run without manually exporting variables every time.

## Current Boundaries

This repository is a harness MVP, not a full production agent platform.

What it already has:

- CLI-first entrypoint
- single-agent coding loop
- runtime abstraction
- permission pipeline
- git-aware workflow helpers
- isolated verification script
- repair and replay primitives
- structured harness docs

What it does not yet fully have:

- context compression
- memory retrieval strategy
- middleware or hook pipeline
- browser or CDP-based application legibility
- logs and metrics query tools
- subagent orchestration
- full production-grade policy engine

## Design Position

The project deliberately sits between two extremes:

- it is more structured than a prompt demo
- it is simpler than a full agent platform like Deep Agents

That is the point.

`Claude_Code_MVP` is meant to make harness ideas concrete in a compact repository:

- small enough to understand end to end
- real enough to run, test, and evolve
- opinionated enough to teach harness engineering clearly

## Recommended Reading Order

For a fast architectural pass:

1. [`README.md`](./README.md)
2. [`AGENTS.md`](./AGENTS.md)
3. [`docs/architecture/overview.md`](./docs/architecture/overview.md)
4. [`app/cli/main.py`](./app/cli/main.py)
5. [`app/agent/loop.py`](./app/agent/loop.py)
6. [`app/agent/policies.py`](./app/agent/policies.py)
7. [`app/runtime`](./app/runtime)
8. [`scripts/agent_verify.sh`](./scripts/agent_verify.sh)
9. [`app/evals/replay.py`](./app/evals/replay.py)

## Backlinks

Use these entrypoints depending on what you want to understand next:

- Go back to [`README.md`](./README.md) for product framing, setup, and verification commands
- Go to [`AGENTS.md`](./AGENTS.md) for agent-facing navigation and working rules
- Go to [`docs/architecture/overview.md`](./docs/architecture/overview.md) for a narrower architecture summary
