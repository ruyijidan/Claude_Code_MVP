---
last_updated: 2026-04-20
status: draft
owner: core
---

# Feature: Intent Clarifier / 功能：意图澄清器

## Status / 状态
Draft

## Goal / 目标
Add a small pre-execution harness control point that decides whether a user request is clear enough to enter planning and execution. The first version should reduce avoidable mis-execution on ambiguous requests by making clarification behavior explicit, deterministic, and testable.

## Non-Goals / 非目标
- Do not build a general-purpose conversational agent or multi-turn dialogue manager.
- Do not rewrite every request into a long prompt.
- Do not depend on model-generated clarification in the first version.
- Do not merge memory, replay retrieval, or long-term personalization into this feature.
- Do not move planner responsibility for task-shape inference into the clarifier.

## Proposed Changes / 拟议变更
- Add a narrow `intent clarifier` module before planner execution.
- Let the clarifier inspect the raw request plus lightweight repo signals.
- Return one of three structured outcomes:
  - `ready`: request is clear enough to continue
  - `needs_clarification`: request is missing required constraints
  - `normalized`: request is clarified into a more explicit internal task string
- Keep the first implementation rule-driven and repo-aware instead of model-driven.
- Expose the result through CLI-visible structured output so the user can see why execution continues or stops.

## Placement In The Harness / 在 Harness 中的位置
The intended flow is:

`CLI -> permission pipeline -> intent clarifier -> context builder / planner -> execution loop`

This keeps the feature aligned with the interaction harness abstraction described in:

- [`docs/architecture/interaction-harness.md`](../architecture/interaction-harness.md)
- [`ARCHITECTURE.md`](../../ARCHITECTURE.md)

The clarifier is part of the interaction entry layer in this project's architecture, not part of runtime execution.

## Responsibilities / 职责
The first-version clarifier is responsible for:

- checking whether the request names a clear target, action, and success shape
- deciding when ambiguity crosses the clarification threshold
- producing a normalized internal task string when the request is already actionable but underspecified in wording
- emitting a small number of concrete clarification questions when required

The clarifier is not responsible for:

- building the full repo context bundle
- selecting runtime providers
- executing code changes
- running verification or repair

## First-Version Heuristics / 第一版启发式策略
The first version should remain intentionally small and deterministic.

Suggested signals:

- request contains a recognizable task verb such as `fix`, `add`, `refactor`, `investigate`, or `write tests`
- request points to a likely target such as a file, module, feature, command, provider, or test
- request includes a success indicator such as pass/fail expectation, scope boundary, or behavior constraint
- request can be weakly mapped to an existing workflow asset
- repo signals support the requested target instead of contradicting it

Suggested ambiguity triggers:

- action is present but target is missing
- target is present but expected outcome is missing
- multiple next steps are similarly plausible from short continuation input
- request refers to repo elements that cannot be found from lightweight inspection
- request implies broad changes without any explicit scope boundary

## Workflow Alignment / 与 Workflow 资产的对齐
The clarifier should stay compatible with the existing workflow asset direction under [`specs/workflows`](../../specs/workflows).

A small first mapping is enough:

- `fix_bug`: expects a failure symptom, failing behavior, or target module
- `implement_feature`: expects a feature boundary and a rough success condition
- `write_tests`: expects a target module, behavior, or test intent
- `investigate_issue`: expects an observed problem and a scope of investigation

The clarifier should not become a workflow engine. It should only use workflow expectations as a small source of required fields.

## Proposed Data Shape / 建议数据结构
Suggested first-version output shape:

```python
@dataclass(slots=True)
class ClarificationQuestion:
    key: str
    question: str
    reason: str


@dataclass(slots=True)
class IntentClarificationResult:
    status: str  # ready | needs_clarification | normalized
    normalized_prompt: str
    inferred_task_type: str | None = None
    missing_constraints: list[str] = field(default_factory=list)
    questions: list[ClarificationQuestion] = field(default_factory=list)
```

This result should be easy for:

- CLI display
- planner consumption
- JSON output
- unit testing

## CLI Implications / CLI 影响
The CLI should treat the clarifier as a preflight step.

Suggested first behavior:

- if result is `ready`, continue normally
- if result is `normalized`, continue using `normalized_prompt`
- if result is `needs_clarification`, print structured feedback and stop before execution

Optional flags can be considered later, such as:

- `--no-clarify`
- `--strict-clarify`

These flags are not required for the first design approval.

## Boundary With Planner / 与 Planner 的边界
The planner should remain responsible for task-shape inference and lightweight plan creation.

The clarifier may provide:

- a normalized prompt
- an optional task-type hint

The planner should not depend on the clarifier for all inference. It should treat clarification output as an upstream control signal, not as a replacement for planning logic.

## Acceptance Criteria / 验收标准
- Ambiguous requests can be blocked before execution with a structured clarification result.
- Clear requests can continue without changing existing simple local-loop behavior.
- Normalized requests can be consumed by planner without introducing a second planning system.
- The feature remains rule-driven and deterministic in its first version.
- Repo-aware mismatch cases can produce at least one useful clarification message.

## Verification Plan / 验证计划
- Add unit tests for direct clarifier behavior on:
  - clear actionable request
  - ambiguous request missing target
  - ambiguous request missing success criteria
  - short continuation request with multiple plausible meanings
  - repo mismatch request
- Add CLI integration checks to verify:
  - `needs_clarification` stops execution cleanly
  - `normalized` continues into existing flow
  - existing direct requests still behave as before

## Open Questions / 待确认问题
- Should short continuation inputs such as `好` and `继续` be handled by the same module in v1, or stay documented-only until a later interaction-harness pass?
- Should workflow assets declare required clarification fields explicitly in the future, or should the first version keep those expectations in code?
- When the clarifier finds a repo mismatch, should it stop immediately or allow execution with a warning in low-risk cases?
