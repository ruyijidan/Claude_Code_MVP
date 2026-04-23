---
last_updated: 2026-04-23
status: active
owner: core
---

# Current Sprint / 当前冲刺

## Goal / 目标
Move Claude Code MVP from a runnable coding loop into a clearer harness-oriented project with stronger information and constraint layers.

## Related Plans / 相关计划

- `docs/plans/harness-hardening-pr-plan.md`: first implementation wave for completion contracts, verification gates, scoped context selection, and repair policy hardening

## Status Snapshot / 状态快照

Before this sprint, the repository was primarily a runnable single-loop coding harness with early documentation and runtime abstractions.

At that stage, the core flow already existed, but several control concerns were still relatively implicit:

- task completion was not yet strongly defined outside the model
- verification existed, but gate behavior was still light
- repo context selection was still closer to generic sampling than scoped assembly
- repair behavior was lighter and less policy-driven

After the first hardening wave and the follow-on asset work, the repository now looks more like an explicit harness system:

- `completion contracts` and `verification gates` are in place
- `scoped context selection` is in place
- `failure classification` and `repair policy` are in place
- workflow, template, and rule assets now exist under `specs/`
- workflow assets already shape plan and verification behavior
- rule assets have started to shape critic behavior
- pre-execution `intent clarification` now exists as an explicit CLI control point
- continuation-aware clarification now distinguishes between a single recent task and multiple ambiguous recent tasks
- ambiguous continuation prompts now return actionable continuation candidate labels that can be selected on the next CLI run
- release acceptance now has a single scripted entrypoint plus optional live provider checks
- API-backed providers can now run local acceptance reporting through `app/acceptance` and `app/models`
- live `glm5` acceptance now has transient timeout retry handling so unattended final acceptance is less fragile
- release acceptance now keeps fast unit verification isolated from opt-in live provider flags
- acceptance artifact creation prompts can reference new output paths without being blocked by repo-target clarification
- isolated live acceptance reports now have explicit prompt guidance to rely on git snapshots instead of flagging missing `.git` metadata as a release issue

In practical terms, the project has moved from:

- a runnable coding loop with harness intent

to:

- a clearer harness-oriented project with explicit control points around context, completion, verification, and repair

The repository also gained two concrete product-facing additions after the hardening wave:

- a dedicated `glm5` delegated provider path through an Anthropic-compatible API adapter
- a browser-playable web game demo under `examples/web-game`

So the current state is no longer just “MVP that can run”.
It is now:

- a harness learning base with a hardened first control plane
- an emerging asset-driven harness with reusable workflow/template/rule boundaries
- a project that can delegate through both CLI-backed providers and a configured `GLM-5` compatible endpoint
- a project with an explicit release acceptance path for provider-facing changes
- a project with a first working local acceptance path for API-backed providers such as `glm5`

## Delivery Board / 交付看板

### Completed / 已完成

- First hardening wave is complete:
  - `completion contracts`
  - `verification gates`
  - `scoped context selection`
  - `failure classification`
  - `repair policy`
- `specs/workflows/`, `specs/templates/`, and `specs/rules/` now exist as reusable harness assets
- Workflow assets already shape planning and verification behavior in a lightweight way
- Rule assets have started to shape critic behavior
- Worktree-based verification already exists through `scripts/agent_verify.sh`
- `intent clarifier` is now wired into the CLI before execution
- `scripts/release_acceptance.sh` now exists as a single release acceptance entrypoint
- live provider acceptance expectations are now documented and backed by opt-in tests
- `glm5` local acceptance runs can now generate validated markdown and JSON acceptance artifacts
- short continuation inputs now stop for clarification when more than one recent task is a plausible continuation target
- continuation clarification now surfaces bounded candidate choices and supports label-based selection such as `recent_task_1`
- transient `glm5` gateway timeout failures can now be retried automatically during local acceptance reporting
- release acceptance fast checks now unset live-test flags before unit discovery so 600-second preflight remains deterministic
- delegated live acceptance can now create required `.claude-code/acceptance` artifacts from a fresh isolated workspace

### In Progress / 进行中

- Continue turning workflow, template, and rule assets into behavior-shaping harness inputs
- Improve application legibility foundations so the harness can inspect more than repository files
- Keep final acceptance expectations explicit for live provider paths instead of relying only on mocked tests

### Not Started / 未开始

- Add context compression and token-budget-aware context shaping
- Add stronger permission and safety control layers with clearer allow / deny boundaries
- Add a more unified tool registry and schema abstraction layer
- Add stronger memory and retrieval strategy beyond replay storage
- Add richer workflow execution behavior beyond simple task-to-workflow mapping
- Add browser, preview, log, and metric reading capabilities
- Add multi-agent isolation and orchestration patterns
- Add API / daemon, dashboard, and cost / cache platform capabilities

### Doc Debt / 文档待修正

- `worktree-based verification script` should no longer be listed as upcoming work because it is already implemented
- Sprint planning docs should distinguish between:
  - completed first-wave hardening work
  - active second-wave asset-shaping work
  - longer-term roadmap items

## Next / 下一步

- Add application legibility foundations
- Add stronger import and file-size guardrails
- Add context compression foundations
- Add thicker permission and safety guardrails
- Continue turning workflow, template, and rule assets into behavior-shaping harness inputs
- Keep live provider acceptance as an explicit release check for provider-facing changes
- continue hardening unattended live acceptance reliability for API-backed providers without hiding real blocking failures

## Acceptance Notes / 验收备注

For ordinary development, fast local verification remains the default:

- `python3 -m unittest discover -s tests`
- `bash scripts/agent_verify.sh`

For changes that affect real provider execution paths, release acceptance should also include:

- `tests/test_live_provider_integration.py`
- `scripts/release_acceptance.sh`

This live layer should stay explicit and opt-in rather than being mixed into the default fast suite.

## Later / 稍后

- Add browser and preview tooling
- Add log and metric readers
- Add memory and retrieval layers beyond replay
- Add workflow mode layering such as `quick edit`, `template`, and `spec mode`
- Add tool registry and schema standardization
- Add multi-agent isolation patterns
- Add API / daemon, dashboard, and cost / cache platform capabilities
- Add cleanup automation and doc-gardening tasks
