# Claude Code MVP

[中文说明](./README.md)

`Claude_Code_MVP` is a learning-oriented project for understanding Claude Code style agent harness design in a terminal-first coding workflow.

It is built around a minimal but complete execution loop:

`CLI -> Repo Context -> Plan -> Execute -> Verify -> Repair -> Replay`

This repository is not just a demo that asks a model to write code, and it is not yet a large productized agent platform either. It is better understood as a small, concrete starting point for learning what a harness is, how a harness works, and how to engineer one step by step.

## What Is a Harness?

If you remember only one line:

**The agent is the executor. The harness is the operating environment.**

A harness is not the model itself. It is the system around the model that makes the agent actually usable. The real questions it answers are:

- Where do tasks enter the system?
- How is context organized?
- How are tools and runtimes invoked?
- Which actions are allowed, and which must be blocked?
- How are results verified?
- How are failures repaired?
- How are runs recorded, replayed, and reviewed?

That is why a harness is not mainly about “producing an answer.” It is about turning an agent run into a full engineering loop:

`Request -> Context -> Plan -> Execute -> Verify -> Repair -> Replay`

That is also the core difference between a simple AI demo and an agent harness.

A typical demo looks like:

`prompt -> model -> output`

A harness looks more like:

`prompt -> environment -> policy -> execution -> verification -> recovery -> trace`

## What This Project Actually Does

The goal of this project is not to clone the full Claude Code product. The goal is to implement the most important pieces of a Claude Code style harness first, and make them available as a minimal, runnable, understandable foundation for learning and iteration.

Today, the project focuses on four things:

- providing a `CLI first` entry point for a coding agent
- turning repo-aware context, planning, execution, verification, and repair into a single-agent closed loop
- separating runtime, policy, verification, and replay into clear layers
- turning docs, guardrail scripts, tests, and reference notes into a reusable engineering skeleton

At the code level, it already contains the most important layers of a harness MVP:

- entry layer: [`app/cli/main.py`](./app/cli/main.py)
- execution layer: [`app/agent/loop.py`](./app/agent/loop.py), [`app/agent/context_builder.py`](./app/agent/context_builder.py), [`app/agent/planner.py`](./app/agent/planner.py)
- runtime layer: [`app/runtime`](./app/runtime)
- constraint layer: [`app/agent/policies.py`](./app/agent/policies.py), [`scripts/check_architecture.py`](./scripts/check_architecture.py)
- verification and repair layer: [`scripts/agent_verify.sh`](./scripts/agent_verify.sh), [`app/superpowers/self_repair.py`](./app/superpowers/self_repair.py), [`app/evals/replay.py`](./app/evals/replay.py)

In other words, this repository is not mainly trying to teach “how to call a model.” It is trying to show:

**what the surrounding harness needs to look like if a coding agent is going to be genuinely usable.**

## How To Learn Harness Design Through This Project

The best way to learn a harness is not to memorize definitions first. It is to read ideas and implementations side by side inside a small working codebase.

### Step 1: Build the right mental model

Start with these documents in order:

1. [`README.md`](./README.md): build the high-level picture
2. [`ARCHITECTURE.md`](./ARCHITECTURE.md): understand the execution path and layering
3. [`docs/architecture/harness-explained.md`](./docs/architecture/harness-explained.md): read the deeper Chinese explanation

The goal of this pass is not to memorize APIs. It is to answer three questions:

- What is the difference between a harness and a prompt wrapper?
- Why do policy, verification, and replay matter?
- Why is “just calling a model” not enough for an agent project?

### Step 2: Read the code by layer, not file-by-file at random

A good reading path is:

1. entry layer: [`app/cli/main.py`](./app/cli/main.py)
2. context and planning: [`app/agent/context_builder.py`](./app/agent/context_builder.py), [`app/agent/planner.py`](./app/agent/planner.py)
3. main loop: [`app/agent/loop.py`](./app/agent/loop.py)
4. runtime: [`app/runtime/adapter_factory.py`](./app/runtime/adapter_factory.py), [`app/runtime/local_runtime.py`](./app/runtime/local_runtime.py), [`app/runtime/cli_adapter.py`](./app/runtime/cli_adapter.py)
5. constraints and verification: [`app/agent/policies.py`](./app/agent/policies.py), [`scripts/check_architecture.py`](./scripts/check_architecture.py), [`scripts/agent_verify.sh`](./scripts/agent_verify.sh)
6. repair and traceability: [`app/superpowers/self_repair.py`](./app/superpowers/self_repair.py), [`app/evals/replay.py`](./app/evals/replay.py)

Reading the repo this way makes it much easier to map code back to the core harness questions:

- How does a request enter?
- How is context constructed?
- How is work constrained?
- How is execution abstracted?
- How are outcomes verified?
- How are failures repaired?

### Step 3: Run it and watch the loop in practice

Install:

```bash
cd /data/ji/code/Claude_Code_MVP
pip install -e .
```

Minimal run:

```bash
cd /data/ji/code/Claude_Code_MVP
cc "fix failing tests" --repo .
```

You can also use the module entrypoint directly:

```bash
cd /data/ji/code/Claude_Code_MVP
python3 -m app.cli.main "implement tool router" --repo . --json
```

Run verification:

```bash
cd /data/ji/code/Claude_Code_MVP
python3 -m unittest discover -s tests
python3 -m app.cli.main --repo . --show-status
python3 -m app.cli.main --repo . --show-permissions
bash scripts/agent_verify.sh
```

Once you have actually run these commands, the code becomes much easier to understand. The harness stops being an abstract idea and starts to look like a real system made of entrypoints, rules, execution, verification, and recovery.

### Step 4: Treat it as a reference sample, not a final answer

`Claude_Code_MVP` is a harness MVP, not a full industrial implementation. It is especially useful for learning:

- which layers a minimal harness should have
- how those layers should be decoupled
- how docs, scripts, and tests together form a control surface

What it is not yet:

- a full multi-agent platform
- a long-term memory system
- a productized UI or dashboard
- a full industrial isolation and permission system

The most useful way to learn from it is:

- first use it to understand the skeleton
- then use external references to understand fuller forms
- then return to this repo and ask what the next missing layer should be

## Learning Notes: How To Actually Get Good At Harness Thinking

It is easy to read a few conceptual articles and feel like you understand harnesses. The harder part is turning those concepts into an engineering loop.

In practice, the following approach tends to work better.

### 1. Do not define a harness as “more agents”

Many people initially equate harness design with role systems, multi-agent orchestration, or a pile of fancy tools.

But the more fundamental questions are:

- Is there a control surface for task entry?
- Is there policy before execution?
- Is there verification after execution?
- Can the system recover from failure?
- Is there traceability for what happened?

Understanding these base layers matters much more than jumping straight into multi-agent design.

### 2. Separate the documentation layer, constraint layer, and automation layer

The real sign that you understand a harness is not that you can repeat a definition. It is that you can separate which part of the system solves which class of problem:

- the documentation layer answers where the agent should find knowledge
- the constraint layer answers what the agent is allowed to do
- the automation layer answers how the agent closes the loop reliably

If you do not separate these layers clearly, everything eventually collapses into the main loop.

### 3. Learn the minimal loop before the advanced capabilities

A better learning order is:

1. understand `CLI -> Context -> Plan -> Execute -> Verify -> Repair -> Replay`
2. then study provider abstraction, policy, and worktree verification
3. only then move to skills, memory, MCP, and sub-agents

That order makes the topic much less overwhelming.

### 4. Read code and run verification side by side

Harnesses are hard to understand from source alone because much of their value shows up in runtime behavior.

That is why it helps to read and run in parallel:

- `python3 -m unittest discover -s tests`
- `python3 -m app.cli.main --repo . --show-status`
- `python3 -m app.cli.main --repo . --show-permissions`
- `bash scripts/agent_verify.sh`

This makes several ideas click faster:

- why policy exists
- why verification matters
- why worktree checks belong inside a harness

### 5. Use external references to build intuition for fuller systems

This project is good for understanding the skeleton. These references help you imagine what a fuller harness can grow into:

- [`claude-code-book`](https://github.com/lintsinghua/claude-code-book/tree/main): a Chinese deep-dive into Claude Code and harness mental models
- [`claw-code`](https://github.com/ultraworkers/claw-code/tree/main): a useful reference for CLI product shape, repo presentation, and runtime surface design
- [`hermes-agent`](https://github.com/nousresearch/hermes-agent): a more complete, product-like harness reference for skills, memory, toolsets, MCP, and multi-entry surfaces
- [`DeerFlow 2.0`](https://github.com/bytedance/deer-flow): a strong reference for skills, sandboxing, middleware, sub-agents, and long-horizon runtime design
- [`everything-claude-code`](https://github.com/affaan-m/everything-claude-code): a reference for packaging skills, hooks, rules, commands, memory, and MCP assets into reusable enhancement layers
- `Claude Code source-engineering analysis`: an engineering-oriented synthesis for context compression, permissions, memory, streaming execution, and multi-agent isolation; see [`docs/reference/claude-code-source-leak.md`](./docs/reference/claude-code-source-leak.md)
- `Dewu Spec Coding practice`: a practical field report on rules, demonstration layers, MCP usage, and common AI failure modes; see [`docs/reference/dewu-spec-coding.md`](./docs/reference/dewu-spec-coding.md)
- [`docs/reference/README.md`](./docs/reference/README.md): the project’s own index of reference notes, reading order, and capability mapping

The goal is not to copy these projects wholesale. The better way to use them is to ask:

- Which layer does this add?
- Why does that layer exist?
- What would the smallest useful version of that layer look like in our own project?

## Suggested Reading Order

If you are learning harness design for the first time, this is a practical order:

1. [`README.md`](./README.md): understand what you are trying to learn
2. [`ARCHITECTURE.md`](./ARCHITECTURE.md): study the main system path
3. [`docs/architecture/harness-explained.md`](./docs/architecture/harness-explained.md): build a deeper mental model
4. [`AGENTS.md`](./AGENTS.md): understand repo navigation and working rules
5. [`docs/architecture/boundaries.md`](./docs/architecture/boundaries.md): understand why boundaries matter
6. [`docs/plans/current-sprint.md`](./docs/plans/current-sprint.md): understand what the project still needs next
7. [`docs/reference/README.md`](./docs/reference/README.md): expand into broader harness references

## What To Build Next: P0 / P1 / P2

If we describe “making a real harness” in three stages, the next steps for this project look like this.

### P0: Thicken the control and safety surfaces

This stage is not about more features. It is about making the system trustworthy:

- add explicit import / layer guardrails with clear rules and CI enforcement
- add dangerous command confirmation and path constraints, with finer risk classes and stable `--show-permissions` output
- add a structured verification summary (pass/fail, reason, risk level)
- make replay / trace explain what happened, why it failed, and what to do next

### P1: Make it feel like a real coding harness

This stage focuses on task understanding and workflow quality:

- smarter `context builder`: relevance ranking, git diff awareness, and test linkage
- upgrade `planner` from rule-only to model-assisted planning, with explicit test and risk plans
- upgrade `verifier`: not only tests, but completion, boundary, and constraint checks
- introduce lightweight templates / specs so task types influence execution paths
- add task-mode separation (quick edit vs. spec mode) so one loop does not handle everything

### P2: Platform depth and long-horizon capability

This stage is about industrial harness thickness:

- add session memory (short-term, working, long-term summaries)
- add API / daemon mode
- add a trajectory viewer / dashboard
- strengthen the skills / hooks / middleware asset layer
- add cost, cache, and isolation foundations

For more detailed breakdowns, see [`ROADMAP.md`](./ROADMAP.md) and [`docs/plans/current-sprint.md`](./docs/plans/current-sprint.md).

## Repository

- GitHub: [ruyijidan/Claude_Code_MVP](https://github.com/ruyijidan/Claude_Code_MVP)
- Git remote: `git@github.com:ruyijidan/Claude_Code_MVP.git`
