---
last_updated: 2026-05-08
status: active
owner: core
---

# Current Sprint / 当前冲刺

## Goal / 目标
Move Claude Code MVP from a runnable coding loop into a clearer harness-oriented project with stronger information and constraint layers.

## Related Plans / 相关计划

- `docs/plans/harness-hardening-pr-plan.md`: first implementation wave for completion contracts, verification gates, scoped context selection, and repair policy hardening
- `docs/plans/two-week-execution-plan.md`: near-term execution breakdown for permission guardrails, context compression, asset-driven behavior, structural checks, and acceptance tightening
- `docs/plans/two-week-pr-breakdown.md`: review-friendly PR grouping for the current two-week execution pass

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
- workflow assets now also carry explicit task-type and workflow-slug metadata used by planner resolution
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
- long-task runner verification now checks actual target-path fingerprint movement and tracks no-progress streaks so repeated empty iterations cannot masquerade as successful long-session iteration
- long-task game UI now exposes a richer session summary strip with stage, convergence, upgrades, best score, tempo, and focus so long-session convergence is visible during the run
- the latest 30-minute long-task result is intentionally recorded as a rough harness demo, not a polished game release
- `examples/starforge-relay` now provides a new browser-game baseline with a cleaner wave-defense loop, permanent module drafts, and touch support
- long-task session logs now surface a fixed per-iteration "did / optimized / artifact / next" summary so long runs are readable without opening each iteration JSON file
- application legibility now has a first registered reader layer for preview, log, and metric artifacts
- tool invocation now has a first unified spec-backed registry plus schema validation
- workflow behavior now records structured execution state instead of staying only at plan-shaping level
- repo context can now retrieve lightweight related trajectory summaries from local memory storage
- intent clarification can now reuse strong related-memory hits for continuation fallback and target completion
- planner context assembly can now prioritize bounded memory-derived file paths instead of relying only on fresh repo sampling
- multi-agent execution now records explicit planner, coder, verifier, critic, and router transitions with isolated stage views
- a first local daemon service now exposes run, status, and latest-trajectory queries outside the CLI entrypoint

In practical terms, the project has moved from:

- a runnable coding loop with harness intent

to:

- a clearer harness-oriented project with explicit control points around context, completion, verification, and repair

The repository also gained two concrete product-facing additions after the hardening wave:

- a dedicated `glm5` delegated provider path through an Anthropic-compatible API adapter
- a browser-playable web game demo under `examples/web-game`
- a higher-quality browser mini-game baseline under `examples/starforge-relay`

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
- operation, command, and file-write permissions now expose a stable `allow / confirm / deny` action model
- network-shaped commands now require explicit approval by default unless the active policy skips confirmation
- repo planning context and acceptance context now reuse shared compression helpers for prompt, path, file, and git shaping
- workflow assets now add explicit context and clarification steps to generated plans
- workflow assets now also select post-execution verification gates through structured `verification_gates` specs
- rule assets now produce structured critic and verifier rule-hit reporting and can declare explicit enforcement ownership
- architecture checks now include file-size guardrails for high-risk control-surface modules
- release acceptance reporting now classifies provider risks into transient environment, setup/auth, and product-blocking buckets
- the long-task game flow now has a repeatable launcher, session log template, and a verified 30-minute run against `examples/halo-drift`
- the long-task launcher now uses spinner feedback plus temp-file-backed session logging so long runs can continue without argv overflow or silent stalls
- `examples/starforge-relay` is now the active higher-quality browser-game candidate, while the earlier `examples/halo-drift` artifact remains labeled as rough demo output
- contributor-facing harness implementation guidance now exists under `docs/guides/how-to-implement-a-harness.md`
- documentation conventions now explicitly require bilingual English/Chinese titles for new or materially updated docs
- a new long-form learning article now connects harness basics to building a personal harness project
- the harness learning path now also includes a capability matrix, code-reading guide, anti-pattern guide, and a tiny practice lab under `examples/harness-lab`
- application legibility foundations now inspect browser preview, log, and metric artifacts through registered readers
- task execution now uses a unified tool registry with schema-validated tool I/O
- workflow execution now records selected tools, selected readers, and per-run workflow status in replay artifacts
- repo context now includes repository-scoped related memory hits from recent trajectories
- retrieval now shapes continuation resolution, target completion, and planner-side context narrowing
- multi-agent isolation and orchestration patterns now have a first explicit runtime implementation
- API / daemon capability now has a first local service and HTTP control surface

### In Progress / 进行中

- Keep final acceptance expectations explicit for live provider paths instead of relying only on mocked tests
- Keep the long-task browser mini-game workflow reproducible so future runs can be launched and verified from the documented runbook
- Keep the long-task runner focused on genuine per-iteration game improvement rather than repeated text-only edits
- Keep the current long-task game artifact labeled as rough demo output until a new design-first pass replaces it
- Continue iterating on `examples/starforge-relay` as the new browser-game baseline instead of extending the rough `halo-drift` artifact

### Not Started / 未开始

- Add dashboard and cost / cache platform capabilities

### Doc Debt / 文档待修正

- `worktree-based verification script` should no longer be listed as upcoming work because it is already implemented
- Sprint planning docs should distinguish between:
  - completed first-wave hardening work
  - active second-wave asset-shaping work
  - longer-term roadmap items

## Two-Week Focus / 未来两周重点

The next two weeks should consolidate the current transition from first-wave hardening into second-wave behavior shaping.

Priority order:

- first, make permission and safety boundaries more explicit
- second, make context shaping budget-aware and more compressive
- third, let `specs/` assets drive more runtime behavior instead of staying mostly descriptive
- fourth, reinforce structural guardrails so architecture drift is caught early
- fifth, tighten the release acceptance path into a clearer definition of done

### Week 1 / 第一周

- Land a first `allow / confirm / deny` permission model for file writes, command execution, git-facing actions, and network-shaped operations
- Return clearer structured CLI outputs for permission and safety decisions, with matching tests and user-facing failure messages
- Add first-pass context compression with budget-aware selection for large files, git diffs, test outputs, and candidate file lists
- Reuse the same compression foundations in both planning and acceptance flows
- Extend architecture checks with stronger import and file-size guardrails so risky growth is surfaced earlier in CI

### Week 2 / 第二周

- Deepen workflow wiring so `specs/workflows` influences clarification fields, planning shape, and verification gate selection
- Deepen rule wiring so `specs/rules` can more explicitly shape critic and verifier judgments
- Reduce hard-coded task-to-behavior branching where reusable workflow assets can carry the policy instead
- Tighten release acceptance expectations into a clearer standard for ordinary changes versus provider-facing changes
- Normalize acceptance artifact naming, output paths, and failure categorization so release outcomes are easier to interpret

### Definition Of Progress / 进展判定

- permission and safety checks should be clearer, more structured, and easier to test
- context assembly should become shorter, more stable, and more budget-aware
- at least part of the `specs/` layer should demonstrably change runtime behavior instead of only documenting intended behavior
- release acceptance should more clearly signal when a change is complete and when a live provider check is required

## Next / 下一步

- Continue turning workflow, template, and rule assets into behavior-shaping harness inputs
- Continue strengthening import and file-size guardrails
- Keep teaching material aligned with the real harness control loop as implementation evolves
- Keep live provider acceptance as an explicit release check for provider-facing changes
- Continue hardening unattended live acceptance reliability for API-backed providers without hiding real blocking failures

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
