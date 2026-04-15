# Claude Code MVP

[中文说明](./README.md)

Repository:
- GitHub: `https://github.com/ruyijidan/Claude_Code_MVP`
- Git remote: `git@github.com:ruyijidan/Claude_Code_MVP.git`

External reference:
- `claude-code-book`: `https://github.com/lintsinghua/claude-code-book/tree/main`
  This is a Chinese deep-dive repository focused on Claude Code and Agent Harness architecture. It is not a dependency of this project, but it is highly relevant for understanding the design direction, permission pipeline, conversation loop, context system, and harness mental model behind this repository.
- `claw-code`: `https://github.com/ultraworkers/claw-code/tree/main`
  This is a useful open-source reference for a CLI-oriented agent harness product shape. It is not a dependency of this project, but it is valuable for understanding runtime surface design, documentation layering, and repository presentation.
- `hermes-agent`: `https://github.com/nousresearch/hermes-agent`
  This is a more complete and product-like agent harness reference. It is not a dependency of this project, but it is useful for understanding future directions such as skills, memory, toolsets, MCP, and multi-entry product surfaces. Project-specific notes are captured in [`docs/reference/hermes-agent.md`](./docs/reference/hermes-agent.md).
- `DeerFlow 2.0`: `https://github.com/bytedance/deer-flow`
  This is a strong reference for a super-agent harness runtime with skills, sandboxing, middleware, sub-agents, context engineering, and long-term memory. It is not a dependency of this project, but it is very useful for understanding how a minimal harness might evolve into a more complete runtime. Project-specific notes are captured in [`docs/reference/deer-flow.md`](./docs/reference/deer-flow.md).
- `everything-claude-code`: `https://github.com/affaan-m/everything-claude-code`
  This is a harness enhancement system that packages skills, hooks, rules, commands, memory, and MCP-related assets together. It is not a dependency of this project, but it is a very good reference for how future agent assets can be organized into reusable enhancement layers. Project-specific notes are captured in [`docs/reference/everything-claude-code.md`](./docs/reference/everything-claude-code.md).
- `Claude Code source-engineering analysis`
  This is an engineering-oriented synthesis of industrial Claude Code implementation patterns, especially around context compression, permission systems, memory, streaming execution, and multi-agent isolation. It is useful as a reference for understanding the current gaps in this project. Project-specific notes are captured in [`docs/reference/claude-code-source-leak.md`](./docs/reference/claude-code-source-leak.md).
- `Dewu Spec Coding practice`
  This is a practical field report on Claude Code plus Spec Coding in a real project. It is especially useful for understanding rules, template layers, visual anchoring, MCP usage, and recurring AI failure modes. Project-specific notes are captured in [`docs/reference/dewu-spec-coding.md`](./docs/reference/dewu-spec-coding.md).

A terminal-first Claude Code style MVP repository.

This project is no longer positioned as a multi-agent research starter. It is being reshaped into a more practical coding-agent MVP with the following loop:

`CLI -> Repo Context -> Plan -> Execute -> Verify -> Repair -> Replay`

For the clearest explanation of the system shape and harness layers, start with [`ARCHITECTURE.md`](./ARCHITECTURE.md).

## If You Are Developing With Claude Code

The most practical setup is not to treat every tool as a competitor, but to use them in layers:

- `Claude Code`: the execution engine
- `Superpowers`: the engineering workflow layer
- `gstack`: the high-level decision and role-review layer
- `DeerFlow`: the runtime blueprint for future platformization
- `everything-claude-code`: the reference for organizing reusable enhancement assets

### Recommended adoption order

- Start with `Claude Code + Superpowers`
- Add `gstack` when you are building web products and need richer review / QA / browser flows
- Use `DeerFlow` as an architectural reference when you want to grow toward a fuller harness runtime
- Use `everything-claude-code` as a reference when you want to organize skills, hooks, rules, commands, and MCP-style assets

### 1. Claude Code: execution engine

Claude Code is best treated as the agent that actually does the work:

- reading code
- editing code
- running commands
- running tests
- fixing bugs
- implementing scoped features

It is strongest when the task is concrete and execution-ready.

### 2. Superpowers: workflow layer

Superpowers is most useful for adding engineering discipline around Claude Code:

- brainstorming before implementation
- explicit planning
- stronger task decomposition
- TDD-first execution habits
- code review
- branch finishing

The main value is not a single skill. The value is that the workflow itself becomes more structured and repeatable.

### 3. gstack: decision layer

gstack is most useful when the problem needs different evaluation perspectives:

- product / value review
- engineering / architecture review
- design review
- code review
- QA
- ship / release thinking

It is especially useful for web products, SaaS tools, admin panels, and projects where browser-based QA matters.

### 4. DeerFlow: platform blueprint

DeerFlow is not the first thing to install if your goal is simply to ship code with Claude Code.
It is more useful as a blueprint for what a larger harness runtime could become:

- skills
- middleware
- sandbox
- sub-agents
- long-term memory
- richer runtime state

Use it when thinking about future architecture, not as the first step for everyday coding.

### 5. everything-claude-code: enhancement-asset reference

Everything Claude Code is best thought of as a packaging and organization reference for reusable harness assets:

- `skills/`
- `hooks/`
- `rules/`
- `commands/`
- `mcp-configs/`
- `schemas/`

It is useful when you want to grow from "a repo that runs" into "a repo with reusable agent assets."

### Suggested workflows by task size

#### Small tasks

Examples:

- copy changes
- visibility logic fixes
- CSS spacing tweaks
- single-field API updates
- small bug fixes

Recommended path:

- use Claude Code directly
- optionally add a lightweight Superpowers planning step

#### Medium tasks

Examples:

- a CRUD page
- a standard business module
- a moderate refactor

Recommended path:

1. Use Superpowers for brainstorming and planning.
2. Let Claude Code implement the plan.
3. Let Claude Code run tests and fix the results.
4. Use gstack `/review`.
5. For web products, also use gstack `/qa`.

#### Large tasks

Examples:

- a complex feature module
- a core workflow refactor
- a multi-page or multi-interface delivery

Recommended path:

1. Use gstack for high-level reviews such as `/plan-ceo-review`, `/plan-eng-review`, and `/plan-design-review`.
2. Use Superpowers for the detailed execution plan.
3. Let Claude Code implement against that plan.
4. Use Superpowers to reinforce testing, review, and branch-finishing discipline.
5. Use gstack for `/review`, `/qa`, and `/ship`.

### If you only adopt one enhancement layer

- Choose `Superpowers` first if you care most about execution discipline, testing, planning, and review.
- Choose `gstack` first if you care most about product / design / engineering / QA perspective switching and browser validation.

### Practical recommendation for this project

- Borrow workflow discipline from `Superpowers`
- Borrow role-based review and QA from `gstack`
- Use `DeerFlow` as the reference for skills, middleware, sandbox, and sub-agent architecture
- Use `everything-claude-code` as the reference for skills, hooks, rules, commands, and asset organization

In one line:

**Claude Code handles execution, Superpowers handles workflow, gstack handles judgment, DeerFlow provides the future runtime blueprint, and ECC provides the asset-organization reference.**

## What This Project Is

This repository is a local Claude Code MVP kernel focused on:

- `CLI first`
- `single coding loop`
- `repo-aware context`
- reusable `runtime / repair / replay`

It is not a full Claude Code product and not a full infra platform yet. The best description right now is:

A practical local MVP that can evolve into a real coding agent.

## What Harness Means Here

You can think of a harness as: **the operating environment around the agent, not just the model itself.**

It answers five core questions:

- where tasks enter the system
- how context is organized
- how tools and runtimes are invoked
- which boundaries must not be crossed
- how work is verified, repaired, and recorded

In this project, that maps to the following chain:

`user request`
-> [`app/cli/main.py`](./app/cli/main.py)
-> `Permission Pipeline`
-> [`app/agent/loop.py`](./app/agent/loop.py)
-> [`app/runtime`](./app/runtime)
-> `Verify`
-> [`app/superpowers/self_repair.py`](./app/superpowers/self_repair.py)
-> [`app/evals/replay.py`](./app/evals/replay.py)

Using the three-layer Harness Engineering view, the project currently looks like this:

### 1. Information Layer

This makes the project legible to the agent.

Key files:

- [`AGENTS.md`](./AGENTS.md)
- [`docs/architecture/overview.md`](./docs/architecture/overview.md)
- [`docs/architecture/boundaries.md`](./docs/architecture/boundaries.md)
- [`docs/conventions/README.md`](./docs/conventions/README.md)
- [`docs/plans/current-sprint.md`](./docs/plans/current-sprint.md)

This layer answers: **where knowledge lives and where the agent should look.**

### 2. Constraint Layer

This forces the agent to operate within rules.

Key files:

- [`app/agent/policies.py`](./app/agent/policies.py)
- [`scripts/check_architecture.py`](./scripts/check_architecture.py)
- [`scripts/agent_verify.sh`](./scripts/agent_verify.sh)
- [` .github/workflows/harness-checks.yml `](./.github/workflows/harness-checks.yml)

This layer answers: **what is allowed, what is blocked, and how mistakes are caught.**

### 3. Automation Layer

This lets the agent complete a closed loop.

Key files:

- [`app/agent/loop.py`](./app/agent/loop.py)
- [`app/runtime/adapter_factory.py`](./app/runtime/adapter_factory.py)
- [`app/superpowers/self_repair.py`](./app/superpowers/self_repair.py)
- [`app/evals/replay.py`](./app/evals/replay.py)

This layer answers: **how execution, verification, repair, and replay fit together.**

In one sentence:

**This project is not just a prompt wrapper that writes code. It is a minimal agent harness.**
It already has the backbone of `entrypoint + runtime + policy + verify + repair + replay`, even though more advanced harness features are still ahead.

## Harness Reading Order

If you want to understand this project as a harness engineering codebase, start here:

- [`README.md`](./README.md)
- [`ARCHITECTURE.md`](./ARCHITECTURE.md)
- [`AGENTS.md`](./AGENTS.md)
- [`docs/architecture/overview.md`](./docs/architecture/overview.md)
- [`docs/architecture/boundaries.md`](./docs/architecture/boundaries.md)
- [`docs/conventions/README.md`](./docs/conventions/README.md)
- [`docs/plans/current-sprint.md`](./docs/plans/current-sprint.md)

Use the docs with this split of responsibilities:

- [`README.md`](./README.md): product positioning, quick start, and current capability boundaries
- [`AGENTS.md`](./AGENTS.md): agent navigation and repository working rules
- [`ARCHITECTURE.md`](./ARCHITECTURE.md): execution flow, harness layers, and how the system works
- [`docs/`](./docs): more detailed architecture constraints, conventions, and plans

For external architectural reading, also see:

- `claude-code-book`: `https://github.com/lintsinghua/claude-code-book/tree/main`
- `claw-code`: `https://github.com/ultraworkers/claw-code/tree/main`

## Current Capabilities

### 1. CLI entrypoint

The CLI lives in [`app/cli/main.py`](./app/cli/main.py).

Example usage:

```bash
cc "fix failing tests"
cc "implement tool router" --repo /path/to/repo
cc "investigate intermittent failures" --json
```

Key flags:

- `--repo`
- `--provider`
- `--task-type`
- `--json`
- `--auto-approve`
- `--dangerously-skip-confirmation`

### 2. Single-agent loop

The main execution loop is in [`app/agent/loop.py`](./app/agent/loop.py).

Current flow:

1. collect repository context
2. infer task type
3. build a lightweight plan
4. apply code changes
5. run tests and verify outputs
6. enter repair loop if needed
7. persist replay artifacts

### 3. Repo-aware context

Context building lives in [`app/agent/context_builder.py`](./app/agent/context_builder.py).

It currently collects:

- repository path
- user prompt
- git status summary
- candidate files
- whether a `tests/` directory exists

This is one of the most important foundations before wiring in a real model.

### 4. Runtime / Repair / Replay

The most valuable parts of the old starter repo are preserved:

- runtime factory: [`app/runtime/adapter_factory.py`](./app/runtime/adapter_factory.py)
- local runtime: [`app/runtime/local_runtime.py`](./app/runtime/local_runtime.py)
- command/file primitives: [`app/runtime/ecc_adapter.py`](./app/runtime/ecc_adapter.py)
- git summary tool: [`app/runtime/git_tool.py`](./app/runtime/git_tool.py)
- repair: [`app/superpowers/self_repair.py`](./app/superpowers/self_repair.py)
- replay: [`app/evals/replay.py`](./app/evals/replay.py)

## Provider Status

The runtime factory currently accepts:

- `local`
- `claude_code`
- `codex_cli`

Current status:

- `local`: local single-loop execution
- `claude_code`: delegates to the local `claude` CLI
- `codex_cli`: delegates to the local `codex` CLI

So `claude_code` and `codex_cli` now have real delegated CLI paths.
Whether they run reliably depends on local login state, API keys, config-directory permissions, and network access.

## Task Types

A small set of task contracts is still kept for output and repair constraints:

- `implement_feature`
- `fix_bug`
- `write_tests`
- `investigate_issue`

They live in [`specs/tasks`](./specs/tasks).

Specs are now treated as a constraint layer rather than the main product entrypoint.

## Quick Start

### Requirements

- Python 3.10+

### Provider Configuration (Anthropic-Compatible)

The project now auto-loads provider settings from the repository root [`.env`](./.env) file.
It supports shell-style `export KEY=value` lines.

Example local configuration:

```bash
export ANTHROPIC_BASE_URL="https://llm-api.zego.cloud"
export ANTHROPIC_AUTH_TOKEN="<your-token>"
export ANTHROPIC_MODEL="glm-5"
```

Notes:

- `ANTHROPIC_BASE_URL`: Anthropic-compatible endpoint
- `ANTHROPIC_AUTH_TOKEN`: auth token
- `ANTHROPIC_MODEL`: default model name

To validate the `claude_code` provider through the project:

```bash
cd /data/ji/code/Claude_Code_MVP
python3 -m app.cli.main   --repo .   --provider claude_code   --delegate-to-provider   --auto-approve   --json   "Reply with exactly MODEL_OK"
```

Expected result: `returncode: 0` and `MODEL_OK` in the output.

### Run in development

```bash
cd /data/ji/code/Claude_Code_MVP
python3 -m app.cli.main "fix failing tests" --repo .
python3 -m app.cli.main "implement tool router" --repo . --json
```

### Install the CLI

```bash
cd /data/ji/code/Claude_Code_MVP
pip install -e .
cc "fix failing tests" --repo .
```

### Run tests

```bash
cd /data/ji/code/Claude_Code_MVP
python3 -m unittest discover -s tests
```

### Quick Start

```bash
cd /data/ji/code/Claude_Code_MVP

python3 -m unittest discover -s tests

python3 -m app.cli.main --repo . --show-status
python3 -m app.cli.main --repo . --show-review
python3 -m app.cli.main --repo . --show-permissions

bash scripts/agent_verify.sh

python3 -m app.cli.main --repo . "summarize the current harness architecture"
```

### Acceptance Check

After the first run, confirm the following items work as expected:

1. `python3 -m unittest discover -s tests`
   Expected: the test suite finishes and ends with `OK`

2. `python3 -m app.cli.main --repo . --show-status`
   Expected: prints the current branch and working tree status

3. `python3 -m app.cli.main --repo . --show-review`
   Expected: prints changed files, diff stats, and a short review summary

4. `python3 -m app.cli.main --repo . --show-permissions`
   Expected: prints the current permission mode, risk level, decision, and suggested flags

5. `bash scripts/agent_verify.sh`
   Expected: creates a temporary worktree, runs architecture checks and tests, and cleans up automatically

6. `python3 -m app.cli.main --repo . "summarize the current harness architecture"`
   Expected: the local loop returns a result instead of exiting with an error

### Success Criteria

The local MVP can be considered successfully running when all of the following are true:

- Unit tests pass
- The CLI `--show-*` commands produce valid output
- `scripts/agent_verify.sh` completes successfully
- The local `local_loop` returns a result

### Worktree Verification

A harness-style local verification script is available:

```bash
cd /data/ji/code/Claude_Code_MVP
bash scripts/agent_verify.sh
bash scripts/agent_verify.sh main
```

The script will:

- create a temporary git worktree
- install the project
- run architecture boundary checks
- run the test suite
- clean up the worktree automatically

## Structure

```text
app/
├── agent/
│   ├── context_builder.py
│   ├── loop.py
│   ├── planner.py
│   └── policies.py
├── cli/
│   └── main.py
├── evals/
├── runtime/
├── superpowers/
└── tools/
```

Key directories:

- [`app/cli`](./app/cli): terminal entrypoint
- [`app/agent`](./app/agent): single-agent loop, context, and policies
- [`app/runtime`](./app/runtime): local runtime and provider abstraction
- [`app/superpowers`](./app/superpowers): retry / repair
- [`app/evals`](./app/evals): replay / scoring
- [`specs`](./specs): retained task contracts
- [`docs`](./docs): agent-readable architecture, conventions, and plans

## Relationship To The Older Structure

The project still keeps some older modules, such as:

- [`app/graph/executor.py`](./app/graph/executor.py)
- [`app/agents`](./app/agents)

But those are now closer to compatibility and internal reuse layers than the primary product interface.

The new primary entrypoints are:

- [`app/cli/main.py`](./app/cli/main.py)
- [`app/agent/loop.py`](./app/agent/loop.py)

## Verified So Far

Currently validated:

- `python3 -m unittest discover -s tests`
- basic CLI invocation works
- the local coding loop runs end to end

## Recommended Next Steps

### P0

- add stronger import and layer guardrails
- add dangerous command confirmation and path boundaries

### P1

- make context selection smarter
- upgrade planning from rule-based heuristics to model-driven planning
- strengthen verifier boundary checks and contract checks

### P2

- add session memory
- add API / daemon mode
- add a trajectory viewer / dashboard
