---
last_updated: 2026-04-24
status: active
owner: core
---

# Two-Week Execution Plan / 两周执行计划

## Goal / 目标

Turn the current sprint direction into a concrete two-week execution pass with clear workstreams, ownership-friendly slices, and visible acceptance criteria.

For a PR-oriented implementation sequence, see `docs/plans/two-week-pr-breakdown.md`.

This plan assumes the repository is already past the first hardening wave and is now strengthening the second-wave control plane:

- clearer permission and safety boundaries
- budget-aware context shaping
- more behavior driven by `specs/` assets
- stronger structural guardrails
- a tighter release acceptance definition of done

## Scope / 范围

This plan is intentionally narrow.

It is not trying to introduce:

- multi-agent orchestration
- a full workflow engine
- broad platform features such as dashboard or daemon APIs

It is trying to make the current harness more explicit, safer, and easier to evolve.

## Workstream 1: Permission And Safety Guardrails / 工作流 1：权限与安全护栏

### Goal / 目标

Make operation boundaries easier to understand, test, and enforce before execution starts.

### Target Outcomes / 目标结果

- define a first-version `allow / confirm / deny` decision model
- classify at least:
  - file writes
  - command execution
  - git-facing actions
  - network-shaped actions
- return structured decision summaries from the CLI-facing path
- keep decision reasons visible instead of silently blocking

### Candidate Files / 候选文件

- `app/agent/policies.py`
- `app/agent/intent_clarifier.py`
- `app/cli/main.py`
- `tests/`

### Acceptance Criteria / 验收标准

- policy decisions distinguish between safe, confirm-required, and blocked actions
- CLI output can expose the decision result and the reason in a stable shape
- regression tests cover at least one case in each decision class

## Workstream 2: Context Compression Foundations / 工作流 2：上下文压缩基础

### Goal / 目标

Reduce accidental context growth and make context assembly more predictable.

### Target Outcomes / 目标结果

- add a first token-budget-aware or size-budget-aware context policy
- summarize large files instead of always passing raw content
- compress git diffs, test outputs, and candidate file lists into bounded sections
- reuse the same shaping logic in both planning and acceptance flows where practical

### Candidate Files / 候选文件

- `app/agent/context_builder.py`
- `app/agent/context_selector.py`
- `app/acceptance/context_builder.py`
- `tests/`

### Acceptance Criteria / 验收标准

- context assembly is bounded by an explicit budget rule
- oversized inputs are summarized into stable sections
- planner and acceptance flows share at least one reusable compression path

## Workstream 3: Asset-Driven Behavior Wiring / 工作流 3：资产驱动行为接线

### Goal / 目标

Move `specs/` assets further from documentation into active behavior inputs.

### Target Outcomes / 目标结果

- let `specs/workflows` shape more clarification, planning, or verification behavior
- let `specs/rules` shape more critic or verifier judgments
- reduce hard-coded task branching where reusable assets can carry the meaning

### Candidate Files / 候选文件

- `app/agent/planner.py`
- `app/agent/verification_gates.py`
- `app/agents/critic_agent.py`
- `app/agents/verifier_agent.py`
- `app/core/spec_loader.py`
- `specs/workflows/`
- `specs/rules/`
- `tests/`

### Acceptance Criteria / 验收标准

- at least one workflow asset changes runtime behavior in a visible way
- at least one rule asset changes critic or verifier output in a visible way
- tests prove that behavior differs when the relevant asset content changes

## Workstream 4: Structural Guardrails / 工作流 4：结构护栏

### Goal / 目标

Catch architecture drift earlier and keep growth inside clearer repository boundaries.

### Target Outcomes / 目标结果

- extend import-boundary checks where current rules are too coarse
- add first-pass file-size or file-growth warnings for risky modules
- keep CI failures easy to interpret and actionable

### Candidate Files / 候选文件

- `scripts/check_architecture.py`
- `.github/workflows/`
- `tests/`

### Acceptance Criteria / 验收标准

- at least one new structural rule is enforced automatically
- failure messages explain what boundary was crossed and how to fix it
- existing allowed dependencies remain unaffected

## Workstream 5: Release Acceptance Tightening / 工作流 5：发布验收收口

### Goal / 目标

Make it clearer when ordinary verification is enough and when live provider acceptance is required.

### Target Outcomes / 目标结果

- distinguish ordinary changes from provider-facing changes more explicitly
- normalize acceptance artifact names and output paths
- clarify failure classes such as:
  - transient environment issue
  - setup or auth issue
  - real product-blocking issue
- keep live acceptance explicit instead of silently mixed into the fast default path

### Candidate Files / 候选文件

- `scripts/release_acceptance.sh`
- `app/acceptance/report_runner.py`
- `app/acceptance/report_validator.py`
- `docs/plans/current-sprint.md`
- `docs/plans/release-notes.md`
- `tests/`

### Acceptance Criteria / 验收标准

- contributors can tell from docs and script behavior whether live acceptance is expected
- artifact outputs are predictable and easier to review
- acceptance failures are easier to classify without reading raw logs first

## Suggested Sequence / 建议顺序

1. Start with permission and safety guardrails because they clarify execution boundaries for all later work.
2. Build context compression next because it improves both local planning and acceptance reliability.
3. Deepen asset-driven behavior once context and control signals are more stable.
4. Add structural guardrails in parallel or immediately after the first two workstreams.
5. Tighten release acceptance once the new control points have clearer definitions.

## Suggested Deliverable Shape / 建议交付形态

Keep this two-week pass split into small, reviewable changes instead of one large refactor.

Suggested grouping:

- PR A: permission and safety guardrails
- PR B: context compression foundations
- PR C: workflow and rule wiring
- PR D: structural guardrails and release acceptance tightening

## Done Signals / 完成信号

This plan should be considered successful when:

- permission decisions are more explicit and testable
- context assembly is more bounded and less noisy
- `specs/` assets visibly influence runtime behavior
- architecture drift is caught earlier by automated checks
- release acceptance expectations are clearer for both fast and live paths
