---
last_updated: 2026-04-15
status: active
owner: core
---

# Harness Hardening PR Plan / Harness 加固 PR 计划

## Goal / 目标

Capture the first implementation wave for turning more implicit agent behavior into explicit harness control.

This plan organizes the work into three small-to-medium PRs so the project can improve stability without taking on a risky one-shot refactor.

## Why This Plan Exists / 为什么有这份计划

The current repository already has a clear harness direction:

- information layer through `AGENTS.md` and `docs/`
- constraint layer through policies, architecture checks, and CI
- automation layer through the coding loop, runtime adapters, verify, and replay

The next step is not to make the model logic more elaborate. The next step is to externalize four control concerns into harness modules:

- scoped context selection
- completion definition
- verification gates
- failure classification and repair policy

## Wave Summary / 阶段总结

Status: completed on 2026-04-15

The first hardening wave is now complete.

This wave moved the repository from a lighter implicit loop toward a more explicit harness shape in three ways:

- success is now defined outside the model through completion contracts and verification gates
- repo context is now selected more deliberately through a scoped context selector
- repair is now policy-driven through failure classification, repair decisions, and recorded repair attempts

After this wave, the single-agent loop has stronger control points around:

- what context is shown to the agent
- what counts as task completion
- what verification signals can block success
- what failure types allow repair and when repair must stop

Concrete harness gains from this wave:

- structured `completion_check` and `gate_results` in loop state and replay artifacts
- structured scoped context fields alongside backward-compatible `candidate_files`
- structured `failure_signals`, `repair_decision`, and `repair_attempts` in loop state and replay artifacts
- broader unit and integration coverage for completion, context selection, and repair policy behavior

This means the project now has an end-to-end first version of all three planned control additions:

- completion and verification control
- context selection control
- repair policy control

The next major improvements are no longer about introducing these control points for the first time. They are about tightening them, broadening coverage, and making them more phase-aware.

## Follow-On Direction / 后续方向

After the first hardening wave, the repository began a second kind of improvement:

- adding workflow assets under `specs/workflows/`
- adding reusable templates under `specs/templates/`
- adding reusable rules under `specs/rules/`
- connecting those assets to planner, verification, repair, and critic behavior

This is a different kind of change from PR1-PR3.

PR1-PR3 made the harness control plane thicker.
The follow-on work makes that control plane easier to adjust by moving more execution meaning into explicit repo assets.

At a high level, the direction is:

- workflow assets shape plans
- workflow verification shapes gates and completion checks
- workflow stop conditions shape repair interfaces
- rule assets shape critic behavior

This follow-on direction is intentionally incremental.
It is not yet a full workflow engine, but it creates the asset boundaries needed to grow toward one.

## PR 1: Completion Contracts And Verification Gates / PR 1：完成契约与验证门

Status: completed on 2026-04-14

### Goal / 目标

Define what "done" means outside the model and add a minimal gate system that can block bad outcomes before they are treated as successful runs.

### Files To Add / 新增文件

- `app/agent/completion_contracts.py`
- `app/agent/verification_gates.py`

### Files To Update / 更新文件

- `app/agent/loop.py`
- `app/agent/planner.py`

### Scope / 范围

- Add structured completion checks for:
  - `fix_bug`
  - `write_tests`
  - `implement_feature`
- Add a minimal gate runner for post-execute checks
- Make the loop consume gate results and completion checks before final success is recorded
- Keep planner responsibility focused on task inference and lightweight plan creation

### Suggested Interfaces / 建议接口

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

### First-Version Checks / 第一版检查项

- tests passed
- no architecture violation detected
- task completion contract passed

### Acceptance Criteria / 验收标准

- The loop produces a structured completion result
- The loop records gate results in final state
- A task cannot be treated as successful if its completion contract fails
- Existing behavior remains compatible for simple local-loop runs

### Delivered / 已交付

- Added `app/agent/completion_contracts.py`
- Added `app/agent/verification_gates.py`
- Wired post-execute gate evaluation into `app/agent/loop.py`
- Extended critic and evaluator handling for gate-driven failures
- Persisted completion and gate results in replay artifacts
- Added unit coverage for completion contracts, verification gates, evaluator scoring, and graph execution integration

### Risk Level / 风险等级

Low. This PR adds harness control without changing runtime providers or CLI behavior in a large way.

## PR 2: Scoped Context Selector / PR 2：作用域上下文选择器

Status: completed on 2026-04-15

### Goal / 目标

Replace generic file sampling with a task-scoped context selection path so the model receives more relevant repo context and less accidental noise.

### Files To Add / 新增文件

- `app/agent/context_selector.py`

### Files To Update / 更新文件

- `app/agent/context_builder.py`
- `app/agent/loop.py`

### Scope / 范围

- Split raw signal collection from context selection strategy
- Preserve git summary and repo facts
- Select a bounded set of relevant docs, files, and test targets
- Return structured context sections instead of only `candidate_files`

### Suggested Output Shape / 建议输出形态

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

### First-Version Signals / 第一版信号

- always include:
  - `AGENTS.md`
  - `ARCHITECTURE.md`
  - `docs/architecture/boundaries.md`
- prompt keyword to path matching
- current git summary
- `tests/` presence and probable test targets

### Acceptance Criteria / 验收标准

- The loop receives structured scoped context
- Context selection remains bounded and deterministic
- Relevant architecture docs are consistently included
- Existing repo-summary functionality is preserved

### Delivered / 已交付

- Added `app/agent/context_selector.py`
- Refactored `app/agent/context_builder.py` to combine raw repo signals with selector output
- Preserved `candidate_files` compatibility while adding structured scoped context fields
- Added unit coverage for context selection and context builder integration
- Verified that the full test suite still passes after the scoped context upgrade

### Risk Level / 风险等级

Low to medium. This PR changes what context the agent sees, but keeps the runtime and outer control flow stable.

## PR 3: Failure Classifier And Repair Policy / PR 3：失败分类器与修复策略

Status: completed on 2026-04-15

### Goal / 目标

Turn repair from a lightweight retry helper into a small recovery system that classifies failures, chooses a repair policy, and knows when to stop.

### Files To Add / 新增文件

- `app/superpowers/failure_classifier.py`
- `app/superpowers/repair_policy.py`

### Files To Update / 更新文件

- `app/superpowers/self_repair.py`
- `app/agent/loop.py`

### Scope / 范围

- Classify common failure signals before repair
- Separate repair decision logic from repair execution
- Add explicit stop conditions to prevent unproductive loops
- Keep first-version repair behavior intentionally small and deterministic

### Suggested Interfaces / 建议接口

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

### First-Version Failure Types / 第一版失败类型

- `missing_tests`
- `test_failure`
- `architecture_violation`
- `no_effect_change`

### First-Version Policy Direction / 第一版策略方向

- `missing_tests`: allow repair
- `test_failure`: allow bounded repair attempts
- `architecture_violation`: stop by default
- `no_effect_change`: retry once, then stop

### Acceptance Criteria / 验收标准

- The loop classifies failures before attempting repair
- Repair decisions are recorded in state and replay data
- The loop has explicit stop conditions for repeated low-value retries
- `self_repair.py` becomes an execution helper rather than a mixed strategy module

### Delivered / 已交付

- Added `app/superpowers/failure_classifier.py`
- Added `app/superpowers/repair_policy.py`
- Refactored `app/superpowers/self_repair.py` into an execution helper driven by `RepairDecision`
- Updated `app/agent/loop.py` to classify failures before repair and record repair attempts
- Persisted failure signals, repair decisions, and repair attempt history in replay artifacts
- Added unit coverage for failure classification, repair policy decisions, and repair-driven graph execution

### Risk Level / 风险等级

Medium. This PR changes loop behavior and failure handling, but still stays inside the local harness architecture.

## Recommended Order / 推荐顺序

1. PR 1 defines completion and gating
2. PR 2 improves the quality of model input
3. PR 3 improves bounded recovery behavior

This order reduces risk because the project first defines success, then improves context, then expands automated recovery.

## Out Of Scope For This Wave / 本阶段范围外

- large multi-agent orchestration changes
- heavy long-term memory systems
- major CLI redesign
- provider-specific prompt tuning as a primary solution
- broad workflow-engine refactors

Those can come later. This wave is focused on making the current single-agent harness more explicit, more testable, and easier to evolve across future model upgrades.
