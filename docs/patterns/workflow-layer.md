---
last_updated: 2026-04-15
status: active
owner: core
---

# Workflow Layer / 工作流层

## Purpose / 目的

The workflow layer is where repeatable task shapes become explicit project assets instead of staying implicit inside the agent loop.

## Why It Exists / 为什么存在

`Claude_Code_MVP` already has a working harness loop:

`Context -> Plan -> Execute -> Verify -> Repair`

That loop is a strong control skeleton, but by itself it does not yet explain how different task types should vary in:

- required context
- expected steps
- verification requirements
- stop conditions

The workflow layer fills that gap.

## What Belongs Here / 这里应该放什么

Workflow assets should describe:

- when a workflow applies
- what context it needs
- what major steps it should follow
- what verification signals define success
- what conditions should stop repair or escalation

These assets are not implementation code. They are structured execution contracts that the harness can interpret over time.

## Current Repository Mapping / 当前仓库映射

Today, the project already has the raw ingredients:

- task inference in [`app/agent/planner.py`](../../app/agent/planner.py)
- scoped context in [`app/agent/context_selector.py`](../../app/agent/context_selector.py)
- completion checks in [`app/agent/completion_contracts.py`](../../app/agent/completion_contracts.py)
- verification gates in [`app/agent/verification_gates.py`](../../app/agent/verification_gates.py)
- repair policy in [`app/superpowers/repair_policy.py`](../../app/superpowers/repair_policy.py)

The new `specs/workflows/` directory is the missing expression layer that can tie these pieces together.

## First-Version Shape / 第一版形态

The first workflow assets should stay simple.

Each workflow can define:

- `goal`
- `entry_signals`
- `required_context`
- `steps`
- `verification`
- `stop_conditions`

That is enough to move the project from “one generic loop” toward “multiple explicit harness workflows” without introducing a heavy workflow engine too early.

## Why This Matters / 为什么重要

Without a workflow layer, the project risks putting too much responsibility back into:

- planner heuristics
- agent behavior
- ad hoc prompt interpretation

With a workflow layer, the project gains:

- more explicit task boundaries
- more reusable task behavior
- cleaner future evolution toward phase-aware state machines

## Near-Term Direction / 近期方向

The first practical use of this layer is likely:

- use planner output to select a workflow asset
- use workflow verification fields to strengthen completion and gates
- use workflow stop conditions to inform repair policy

That keeps the harness architecture aligned with the repo’s current MVP scope while making future growth much cleaner.

## Current Status / 当前状态

The repository has now moved beyond a purely descriptive workflow layer.

Today the workflow assets already influence runtime behavior in three places:

- planner output now selects a workflow asset and uses workflow steps to build the visible plan
- verification gates and completion contracts now consume workflow verification expectations
- repair policy now accepts workflow stop conditions as part of its decision interface

This means `specs/workflows/` is no longer just a documentation shelf. It is the beginning of a real behavior-shaping asset layer.

The current implementation is still intentionally lightweight:

- workflow assets do not yet drive a full phase machine
- workflow stop conditions are not yet a rich rule engine
- workflow selection is still simple task-type mapping

But the architectural boundary is now established, which is the most important first step.
