---
last_updated: 2026-04-24
status: active
owner: core
---

# Two-Week PR Breakdown / 两周 PR 拆解

## Goal / 目标

Translate the two-week execution plan into a review-friendly PR sequence with bounded scopes, candidate files, verification commands, and risk expectations.

This breakdown is intended to keep the current sprint incremental.

It should help contributors answer:

- what should be grouped together
- what should stay out of scope for each PR
- how each PR should be verified
- what kind of regression risk is expected

## PR A: Permission And Safety Guardrails / PR A：权限与安全护栏

### Goal / 目标

Establish a first explicit `allow / confirm / deny` decision model and expose it clearly through the CLI-facing path.

### In Scope / 范围内

- define stable decision classes for at least file writes, command execution, git-facing actions, and network-shaped actions
- make policy outputs structured enough for CLI summaries and tests
- surface decision reasons clearly instead of only returning implicit approval state
- add regression tests for representative allow, confirm, and deny cases

### Out Of Scope / 范围外

- a full sandbox or OS-level isolation layer
- provider-specific policy trees for every runtime
- broad workflow-engine changes

### Candidate Files / 候选文件

- `app/agent/policies.py`
- `app/agent/intent_clarifier.py`
- `app/cli/main.py`
- `tests/test_*`

### Verification / 验证

- `python3 -m unittest discover -s tests`
- targeted policy and CLI tests covering allow, confirm, and deny outputs

### Risk Level / 风险等级

Medium.

This PR affects execution gating and user-facing messaging, so regressions are noticeable even if the code change is not large.

## PR B: Context Compression Foundations / PR B：上下文压缩基础

### Goal / 目标

Add bounded context shaping so planning and acceptance can reuse a more stable context budget.

### In Scope / 范围内

- introduce a first budget-aware context rule
- summarize oversized files and long sections into bounded slices
- compress git diffs, test outputs, and candidate file lists
- share at least one reusable compression path between planning and acceptance

### Out Of Scope / 范围外

- advanced semantic retrieval
- vector memory or long-term memory layers
- model-specific token accounting for every provider

### Candidate Files / 候选文件

- `app/agent/context_builder.py`
- `app/agent/context_selector.py`
- `app/acceptance/context_builder.py`
- `tests/test_*`

### Verification / 验证

- `python3 -m unittest discover -s tests`
- targeted context-builder and acceptance-context tests for budgeted output behavior

### Risk Level / 风险等级

Medium.

This PR changes what information the harness passes forward, so the main risk is reduced context quality or accidental omission.

## PR C: Workflow And Rule Wiring / PR C：工作流与规则接线

### Goal / 目标

Make selected `specs/workflows` and `specs/rules` assets visibly influence runtime behavior.

### In Scope / 范围内

- let workflow assets shape more clarification, planning, or verification behavior
- let rule assets shape more critic or verifier judgments
- reduce hard-coded task branching where assets can carry the intended behavior
- add tests proving that asset content changes produce behavior changes

### Out Of Scope / 范围外

- a full declarative workflow engine
- multi-agent orchestration
- broad migration of every task path into `specs/`

### Candidate Files / 候选文件

- `app/agent/planner.py`
- `app/agent/verification_gates.py`
- `app/agents/critic_agent.py`
- `app/agents/verifier_agent.py`
- `app/core/spec_loader.py`
- `specs/workflows/`
- `specs/rules/`
- `tests/test_*`

### Verification / 验证

- `python3 -m unittest discover -s tests`
- targeted planner, verifier, and critic tests showing workflow or rule-driven behavior differences

### Risk Level / 风险等级

Medium to high.

This PR touches execution meaning rather than only plumbing, so behavior drift is possible if tests are not specific enough.

## PR D: Structural Guardrails And Release Acceptance Tightening / PR D：结构护栏与发布验收收口

### Goal / 目标

Catch architecture drift earlier and clarify the project’s completion expectations for ordinary versus provider-facing changes.

### In Scope / 范围内

- extend import-boundary checks where current rules are too coarse
- add first-pass file-size or growth guardrails for risky modules
- tighten release acceptance documentation and script expectations
- normalize artifact naming or output-path expectations where helpful
- improve failure categorization so acceptance outcomes are easier to interpret

### Out Of Scope / 范围外

- a full static-analysis platform
- complete repository-wide complexity scoring
- provider-specific release pipelines beyond the current acceptance path

### Candidate Files / 候选文件

- `scripts/check_architecture.py`
- `scripts/release_acceptance.sh`
- `app/acceptance/report_runner.py`
- `app/acceptance/report_validator.py`
- `docs/plans/current-sprint.md`
- `docs/plans/release-notes.md`
- `tests/test_*`

### Verification / 验证

- `python3 -m unittest discover -s tests`
- `bash scripts/agent_verify.sh`
- targeted release-acceptance tests when provider-facing behavior changes

### Risk Level / 风险等级

Low to medium.

Most changes are guardrails and reporting improvements, but they can still break CI or confuse contributors if the failure messages are not clear.

## Sequence / 顺序

1. `PR A` first, because execution boundaries should be clearer before deeper behavior changes.
2. `PR B` second, because bounded context helps stabilize later workflow-driven behavior.
3. `PR C` third, because asset-driven wiring benefits from clearer control and context inputs.
4. `PR D` last, because guardrail tightening and acceptance cleanup are easier to finalize once the earlier behavior changes settle.

## Suggested Done Signals / 建议完成信号

- each PR can be reviewed without needing the entire two-week plan in one diff
- each PR has at least one targeted regression test area, not only full-suite verification
- contributor-facing docs stay aligned with the actual execution flow
