---
last_updated: 2026-04-27
status: active
owner: core
---

# Harness Capability Matrix / Harness 能力矩阵

## Purpose / 目的

This document separates:

- what `Claude_Code_MVP` already implements
- what exists in a first but still-lightweight form
- what is still future work

Use it when writing docs, teaching the project, or deciding whether a behavior belongs in:

- current implementation
- near-term extension
- longer-term roadmap

## Reading Rule / 阅读规则

When describing the repository:

- say `implemented` when the behavior is materially present and test-backed
- say `partial` when the boundary exists but the behavior is still intentionally thin
- say `planned` when the idea appears in docs or roadmap but is not yet a meaningful control point in code

This keeps the project honest and makes teaching clearer.

## Capability Matrix / 能力矩阵

| Capability | Status | Current repository shape | Notes |
|---|---|---|---|
| CLI entrypoint | implemented | [`app/cli/main.py`](../../app/cli/main.py) | Stable terminal-first control surface |
| Repo-aware context assembly | implemented | [`app/agent/context_builder.py`](../../app/agent/context_builder.py) | Includes repo docs, git summary, and candidate files |
| Scoped context selection | implemented | [`app/agent/context_selector.py`](../../app/agent/context_selector.py) | Task-shaped context narrowing is present |
| Context compression | partial | [`app/core/context_compressor.py`](../../app/core/context_compressor.py) | Useful first pass exists, but not a rich retrieval system |
| Intent clarification | implemented | [`app/agent/intent_clarifier.py`](../../app/agent/intent_clarifier.py) | Short continuation handling and ambiguity stopping exist |
| Task planning | implemented | [`app/agent/planner.py`](../../app/agent/planner.py) | Lightweight task-shape inference is present |
| Workflow assets | partial | [`specs/workflows`](../../specs/workflows) | Assets shape planning and verification, but not a full phase engine |
| Rule assets | partial | [`specs/rules`](../../specs/rules) | Assets influence critic behavior, but not a full rule engine |
| Template assets | partial | [`specs/templates`](../../specs/templates) | Template boundary exists, but runtime usage is still limited |
| Permission model | implemented | [`app/agent/policies.py`](../../app/agent/policies.py) | Stable `allow / confirm / deny` model exists |
| Runtime abstraction | implemented | [`app/runtime`](../../app/runtime) | Local, CLI-backed, and API-backed runtime paths exist |
| Git-aware workflow support | implemented | [`app/runtime/git_tool.py`](../../app/runtime/git_tool.py) | Structured git-facing helper exists |
| Verification gates | implemented | [`app/agent/verification_gates.py`](../../app/agent/verification_gates.py) | Verification criteria are explicit and test-backed |
| Completion contracts | implemented | [`app/agent/completion_contracts.py`](../../app/agent/completion_contracts.py) | Task completion is not left to model prose alone |
| Failure classification | implemented | [`app/superpowers/failure_classifier.py`](../../app/superpowers/failure_classifier.py) | Classification feeds repair policy |
| Repair policy | implemented | [`app/superpowers/repair_policy.py`](../../app/superpowers/repair_policy.py) | Stop conditions and retry shaping exist |
| Self-repair loop | partial | [`app/superpowers/self_repair.py`](../../app/superpowers/self_repair.py) | Useful but still intentionally lightweight |
| Replay storage | implemented | [`app/evals/replay.py`](../../app/evals/replay.py) | Run evidence is persisted |
| Continuation from recent runs | implemented | replay plus clarifier path | Recent-task continuation is supported |
| Release acceptance path | implemented | [`scripts/release_acceptance.sh`](../../scripts/release_acceptance.sh) | Fast and opt-in live checks are separated |
| Live provider acceptance | partial | tests plus acceptance flow | Exists, but relies on external credentials and provider health |
| Application legibility beyond files | planned | roadmap only | Browser, DOM, preview, logs, metrics are still future work |
| Rich memory and retrieval | planned | roadmap only | Replay exists, richer memory does not |
| Tool registry and schema layer | planned | roadmap only | No unified registry yet |
| Multi-agent orchestration | planned | roadmap only | Repository is still single-loop first |
| Middleware or hook pipeline | planned | roadmap only | Useful concept, not a current code path |

## What To Say In Articles / 文章里应该怎么说

When teaching this project, the most accurate summary is:

`Claude_Code_MVP` already has a real coding-harness control loop, plus a first wave of explicit context, permission, verification, repair, and replay controls.

It does not yet have:

- a rich browser-style application legibility layer
- a strong memory and retrieval system
- multi-agent orchestration
- a full workflow or rule engine

That makes it a strong harness MVP and a good teaching base, not a finished agent platform.

## Recommended Pairing / 推荐搭配阅读

Read this together with:

1. [`../../ARCHITECTURE.md`](../../ARCHITECTURE.md)
2. [`../architecture/overview.md`](../architecture/overview.md)
3. [`../guides/how-to-implement-a-harness.md`](./how-to-implement-a-harness.md)
4. [`../../docs/plans/current-sprint.md`](../../docs/plans/current-sprint.md)
