---
last_updated: 2026-04-15
status: active
owner: core
---

# Harness Hardening PR Plan

## Goal

Capture the first implementation wave for turning more implicit agent behavior into explicit harness control.

This plan organizes the work into three small-to-medium PRs so the project can improve stability without taking on a risky one-shot refactor.

## Why This Plan Exists

The current repository already has a clear harness direction:

- information layer through `AGENTS.md` and `docs/`
- constraint layer through policies, architecture checks, and CI
- automation layer through the coding loop, runtime adapters, verify, and replay

The next step is not to make the model logic more elaborate. The next step is to externalize four control concerns into harness modules:

- scoped context selection
- completion definition
- verification gates
- failure classification and repair policy

## PR 1: Completion Contracts And Verification Gates

Status: completed on 2026-04-14

### Goal

Define what "done" means outside the model and add a minimal gate system that can block bad outcomes before they are treated as successful runs.

### Files To Add

- `app/agent/completion_contracts.py`
- `app/agent/verification_gates.py`

### Files To Update

- `app/agent/loop.py`
- `app/agent/planner.py`

### Scope

- Add structured completion checks for:
  - `fix_bug`
  - `write_tests`
  - `implement_feature`
- Add a minimal gate runner for post-execute checks
- Make the loop consume gate results and completion checks before final success is recorded
- Keep planner responsibility focused on task inference and lightweight plan creation

### Suggested Interfaces

```python
@dataclass(slots=True)
class CompletionCheck:
    passed: bool
    reasons: list[str]
    required_checks: list[str]
```

```python
@dataclass(slots=True)
class GateResult:
    name: str
    passed: bool
    severity: str
    message: str
```

### First-Version Checks

- tests passed
- no architecture violation detected
- task completion contract passed

### Acceptance Criteria

- The loop produces a structured completion result
- The loop records gate results in final state
- A task cannot be treated as successful if its completion contract fails
- Existing behavior remains compatible for simple local-loop runs

### Delivered

- Added `app/agent/completion_contracts.py`
- Added `app/agent/verification_gates.py`
- Wired post-execute gate evaluation into `app/agent/loop.py`
- Extended critic and evaluator handling for gate-driven failures
- Persisted completion and gate results in replay artifacts
- Added unit coverage for completion contracts, verification gates, evaluator scoring, and graph execution integration

### Risk Level

Low. This PR adds harness control without changing runtime providers or CLI behavior in a large way.

## PR 2: Scoped Context Selector

Status: completed on 2026-04-15

### Goal

Replace generic file sampling with a task-scoped context selection path so the model receives more relevant repo context and less accidental noise.

### Files To Add

- `app/agent/context_selector.py`

### Files To Update

- `app/agent/context_builder.py`
- `app/agent/loop.py`

### Scope

- Split raw signal collection from context selection strategy
- Preserve git summary and repo facts
- Select a bounded set of relevant docs, files, and test targets
- Return structured context sections instead of only `candidate_files`

### Suggested Output Shape

```python
@dataclass(slots=True)
class ScopedContext:
    repo_path: str
    prompt: str
    git_summary: dict
    always_include_docs: list[str]
    likely_relevant_files: list[str]
    test_targets: list[str]
    architecture_constraints: list[str]
```

### First-Version Signals

- always include:
  - `AGENTS.md`
  - `ARCHITECTURE.md`
  - `docs/architecture/boundaries.md`
- prompt keyword to path matching
- current git summary
- `tests/` presence and probable test targets

### Acceptance Criteria

- The loop receives structured scoped context
- Context selection remains bounded and deterministic
- Relevant architecture docs are consistently included
- Existing repo-summary functionality is preserved

### Delivered

- Added `app/agent/context_selector.py`
- Refactored `app/agent/context_builder.py` to combine raw repo signals with selector output
- Preserved `candidate_files` compatibility while adding structured scoped context fields
- Added unit coverage for context selection and context builder integration
- Verified that the full test suite still passes after the scoped context upgrade

### Risk Level

Low to medium. This PR changes what context the agent sees, but keeps the runtime and outer control flow stable.

## PR 3: Failure Classifier And Repair Policy

### Goal

Turn repair from a lightweight retry helper into a small recovery system that classifies failures, chooses a repair policy, and knows when to stop.

### Files To Add

- `app/superpowers/failure_classifier.py`
- `app/superpowers/repair_policy.py`

### Files To Update

- `app/superpowers/self_repair.py`
- `app/agent/loop.py`

### Scope

- Classify common failure signals before repair
- Separate repair decision logic from repair execution
- Add explicit stop conditions to prevent unproductive loops
- Keep first-version repair behavior intentionally small and deterministic

### Suggested Interfaces

```python
@dataclass(slots=True)
class FailureSignal:
    kind: str
    message: str
    retryable: bool
```

```python
@dataclass(slots=True)
class RepairDecision:
    action: str
    retry_allowed: bool
    reason: str
```

### First-Version Failure Types

- `missing_tests`
- `test_failure`
- `architecture_violation`
- `no_effect_change`

### First-Version Policy Direction

- `missing_tests`: allow repair
- `test_failure`: allow bounded repair attempts
- `architecture_violation`: stop by default
- `no_effect_change`: retry once, then stop

### Acceptance Criteria

- The loop classifies failures before attempting repair
- Repair decisions are recorded in state and replay data
- The loop has explicit stop conditions for repeated low-value retries
- `self_repair.py` becomes an execution helper rather than a mixed strategy module

### Risk Level

Medium. This PR changes loop behavior and failure handling, but still stays inside the local harness architecture.

## Recommended Order

1. PR 1 defines completion and gating
2. PR 2 improves the quality of model input
3. PR 3 improves bounded recovery behavior

This order reduces risk because the project first defines success, then improves context, then expands automated recovery.

## Out Of Scope For This Wave

- large multi-agent orchestration changes
- heavy long-term memory systems
- major CLI redesign
- provider-specific prompt tuning as a primary solution
- broad workflow-engine refactors

Those can come later. This wave is focused on making the current single-agent harness more explicit, more testable, and easier to evolve across future model upgrades.
