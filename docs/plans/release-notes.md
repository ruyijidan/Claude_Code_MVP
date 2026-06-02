---
last_updated: 2026-05-08
status: active
owner: core
---

# Release Notes / 发布说明

## 2026-06-02

### specs: 首次创建 product.md 和 tech.md（001-token-cli spec-merge）

- `specs/product.md`：新建，录入 Token CLI 产品能力（token-count + compare 子命令）
- `specs/tech.md`：新建，录入 Token CLI 技术模块（tiktoken cl100k_base、argparse 实现、测试覆盖）
- `specs/001-token-cli/spec-merge/specs-diff.md`：存档 G2 Gate 确认的 diff 原文

### test_dev.py: Remove stale docstring

- Removed "MUST fail until T005" note from module docstring (T005 has landed, all 9 tests pass)

### dev.py: Implement compare subcommand

- `scripts/dev.py`: `_cmd_compare` shows per-file token counts, absolute diff with sign, and percentage; handles missing files (non-zero exit + filename in stderr); handles baseline = 0 tokens edge case
- All 9 tests in `tests/test_dev.py` now pass

### test_dev.py: Add CompareTests (failing, awaiting T005)

- Added `CompareTests` class with 5 scenarios: basic diff+percentage, equal files → 0 diff, missing file → non-zero exit, too few args, too many args
- 3 tests fail until `compare` subcommand is implemented (expected red)
- 2 tests (wrong arg count) already pass via argparse enforcement

### dev.py: Implement token-count subcommand + cleanup import style

- `scripts/dev.py`: `_cmd_token_count` now counts tokens for one or more files using cl100k_base; prints per-file counts and a total row for multi-file input; exits non-zero with filename in stderr for missing files; reports 0 for empty files
- Added `import sys` at the top level (replaced inline `__import__("sys")` trick)
- All 4 tests in `tests/test_dev.py::TokenCountTests` now pass

### test_dev.py: Fix Relative Path Sensitivity In Missing-File Test

- `tests/test_dev.py` scenario 3: replaced literal `"missing.md"` with a uuid-based temp path so the test does not silently pass if a file named `missing.md` happens to exist in the working directory

### dev.py Dependency Declaration And Error Handling Fix / dev.py 依赖声明与错误处理修复

Included change set:

- `pyproject.toml`: declared `tiktoken>=0.7` in `[project.dependencies]` so the import in `scripts/dev.py` is properly tracked
- `scripts/dev.py`: wrapped `args.func(args)` in `main()` with `try/except NotImplementedError` so placeholder subcommands print a clean `argparse` error instead of a raw traceback

Highlights:

- removes an undeclared runtime dependency that would cause `ImportError` in fresh installs
- replaces the raw `NotImplementedError` traceback with a formatted `usage: dev.py: error: Not yet implemented: …` message

Verification:

- `python scripts/dev.py --help` still shows correct usage
- `python scripts/dev.py token-count somefile.txt` now prints a clean error line instead of a traceback

### Token-Count Acceptance Tests / token-count 验收测试

Included change set:

- `tests/test_dev.py`: four failing acceptance tests for the `token-count` subcommand covering single-file output, multi-file output with a total row, non-existent file error handling, and the empty-file edge case

Highlights:

- tests are intentionally red until T003 implements `_cmd_token_count`
- subprocess-based harness exercises real CLI argument parsing and exit-code semantics
- spec file at `specs/001-token-cli/spec.md` used as a real non-empty fixture

Verification:

- `python -m pytest tests/test_dev.py -v` → 4 FAILED (expected — implementation pending)

### Token CLI Skeleton / Token 计数 CLI 骨架

Included pending change set:

- `scripts/dev.py`: new CLI entry point with `token-count` and `compare` subcommand placeholders and a `count_tokens(path: str) -> int` helper using tiktoken cl100k_base encoding

Highlights:

- provides a unified `dev.py` CLI for token-related development utilities
- `count_tokens` helper is importable by other scripts in addition to being used by the CLI
- subcommands are registered and show correct `--help` output; implementations are placeholder stubs pending future tasks

Verification:

- `python scripts/dev.py --help`
- `python scripts/dev.py token-count --help`
- `python scripts/dev.py compare --help`

## 2026-05-15

### Local Codex Usage Inspector Script / 本地 Codex 用量检查脚本

Included pending change set:

- `scripts/show_codex_usage.py`: added a small local utility for reading `~/.codex/sessions/*.jsonl` logs and printing token usage plus 5-hour and weekly rate-limit status

Highlights:

- makes it easier to inspect local Codex token usage without opening raw session logs manually
- supports both a detailed latest-session view and an `--all` summary mode across local session files
- keeps the utility outside the harness runtime path so it stays a lightweight operator script

Verification:

- `python3 scripts/show_codex_usage.py --help`

### Teaching Path And Harness Lab Onboarding Flow / 教学路径与 Harness Lab 入门路径

Included pending change set:

- `docs/guides/harness-teaching-path.md`: added a dedicated teaching-order guide for onboarding, internal sharing, and concept-to-practice routing
- `docs/guides/README.md`: linked the new teaching path from the guides index
- `examples/harness-lab/README.md`: added a quick-start flow and related-reading links so the tiny practice target can be used directly in teaching

Highlights:

- turned the existing guide set into a clearer teaching path instead of leaving learners to infer reading order
- made `examples/harness-lab` easier to use as the first hands-on exercise after the conceptual reading material
- removed stale references to the deleted longform Feishu packaging path from the teaching route

Verification:

- manual link and content review across `docs/guides/README.md`, `docs/guides/harness-teaching-path.md`, and `examples/harness-lab/README.md`

### Harness Learning Docs Collapse Into A Single Publishable Core / Harness 学习文档收拢为单一可发布主集

Included pending change set:

- `docs/design/harness-blog-feishu-copyready.md`: finalized the unified Feishu-ready harness learning article and aligned it with the current project architecture and sprint status
- `docs/design/harness-blog-feishu-promotion-summary.md`: kept the short summary as the companion preview asset
- `docs/design/harness-feishu-distribution-kit.md`: kept the publishing and submission copy as the outward-facing distribution asset
- `docs/design/harness-docs-retention-plan.md`: added a local keep/delete plan for cleaning redundant harness-learning docs
- `docs/design/README.md`: rewrote the design-doc navigation around a smaller canonical harness learning set
- removed redundant local harness-learning drafts and split companion docs:
  - `docs/design/harness-blog-feishu-draft.md`
  - `docs/design/harness-blog-feishu-longform.md`
  - `docs/design/harness-blog-feishu-cover-note.md`
  - `docs/design/harness-feishu-topic-index.md`
  - `docs/design/harness-feishu-01-what-is-harness.md`
  - `docs/design/harness-feishu-02-how-to-build-a-minimal-harness.md`
  - `docs/design/harness-feishu-03-how-to-evaluate-a-harness-project.md`
  - `docs/design/harness-feishu-04-how-harness-looks-in-a-real-project.md`

Highlights:

- turned the harness learning material into one default article instead of a scattered local topic pack
- kept only the pieces that still have distinct jobs: unified article, short summary, and distribution copy
- aligned the unified article with the real repository state so first-pass daemon, retrieval, multi-agent, acceptance, registry, and artifact-reader work are not accidentally understated
- made the local documentation surface easier to maintain before code submission

Verification:

- manual doc review against `README.md`, `ARCHITECTURE.md`, and `docs/plans/current-sprint.md`
- manual formatting pass for Feishu-friendly code fences in `docs/design/harness-blog-feishu-copyready.md`

## 2026-05-08

### Starforge Relay Sets a New Browser-Game Baseline / 星炉中继建立新的浏览器小游戏基线

Included pending change set:

- `examples/starforge-relay/`: new browser mini-game with free movement, automatic firing, wave pressure, permanent module drafts, classic/marathon run modes, touch controls, and persistent best-score storage
- `tests/test_starforge_relay_game.py`: new regression coverage for asset presence and JavaScript parseability

Highlights:

- built a new game from scratch instead of continuing to patch the rough `examples/halo-drift` long-task demo
- shifted the interaction model toward a cleaner wave-defense loop with clearer HUD/session feedback and stronger module-based progression
- kept the artifact directly playable from `file://` and added a regression test so the new game path stays parseable

Verification:

- `node --check examples/starforge-relay/game.js`
- `python3 -m unittest tests.test_starforge_relay_game tests.test_task_templates tests.test_coder_agent_long_task_game tests.test_permission_pipeline tests.test_completion_contracts tests.test_verification_gates`
- full unit test discovery passed locally: `168 tests OK, 2 skipped`

### Long-Task Iteration Logs Now Report Did / Optimized / Artifact / Next / 长任务迭代日志现在输出做了什么、优化了什么、产物和下一轮

Included pending change set:

- `scripts/start_long_task_game_session.sh`: changed the per-iteration markdown block to surface a fixed four-part view of each round: what was done, what was optimized, what artifact changed, and what the next round should focus on

Highlights:

- made the long-task session logs easier to read without opening each iteration JSON file
- exposed a stable per-iteration narrative so session readers can see the concrete improvement path at a glance

Verification:

- `bash -n scripts/start_long_task_game_session.sh`

## 2026-05-08

### Long-Task Runner Now Enforces Real Per-Iteration Progress / 长任务执行器现已强制每轮真实推进

Included pending change set:

- `scripts/start_long_task_game_session.sh`: tightened the long-task loop so per-iteration progress is validated against target-path fingerprint changes, no-progress streaks are tracked, and fallback upgrades now have multiple visible improvement rungs instead of repeating the same patch
- `examples/halo-drift/index.html`, `examples/halo-drift/styles.css`, and `examples/halo-drift/game.js`: added a richer session summary strip plus stronger menu, upgrade, and results copy so the game visibly reflects long-session convergence instead of only counting time
- tests rerun locally after the update, including the existing harness and task-template coverage

Highlights:

- made the long-task runner treat empty or repeated iterations as real harness failures instead of successful-looking progress
- added a visible multi-field session summary strip so long runs can show stage, convergence, upgrades, best score, tempo, and focus in one place
- kept the long-task session flow aligned with actual content changes rather than letting repeated textual edits stand in for new progress
- the 30-minute verification now proves sustained progress, but the resulting `examples/halo-drift` artifact is still rough and should be treated as a harness-quality demo, not a polished game

Verification:

- `bash -n scripts/start_long_task_game_session.sh`
- `python3 -m unittest tests.test_task_templates tests.test_coder_agent_long_task_game tests.test_permission_pipeline tests.test_spec_loader tests.test_completion_contracts tests.test_verification_gates`
- `node --check examples/halo-drift/game.js`
- short local long-task run passed with `target progress valid: yes` on all three iterations

### Long-Task Game Session Runner Now Supports Verified 30-Minute Runs / 长任务小游戏会话执行器现已支持可验证的 30 分钟运行

Included pending change set:

- `scripts/start_long_task_game_session.sh`: added spinner feedback, temp-file-backed session logging, and iterative long-task execution for `long_task_game`
- `docs/design/long-task-game-*.md`: added the runbook, launch phrase, task template, and session log template for repeatable long-task game verification
- `specs/tasks/long_task_game.yaml` and `specs/workflows/long-task-game.yaml`: added a dedicated long-task game task/workflow pair targeting `examples/halo-drift`
- `app/core/task_templates.py`, `app/agents/coder_agent.py`, `app/agent/policies.py`, and `specs/rules/permission-rules.yaml`: routed the long-task game path to the browser mini-game workspace and allowed repo-managed example writes
- `examples/halo-drift/`: added the browser mini-game target used by the long-task verification session
- tests updated under `tests/test_task_templates.py`, `tests/test_coder_agent_long_task_game.py`, `tests/test_halo_drift_game.py`, and related spec/permission tests

Highlights:

- turned the long-task game workflow into a repeatable, scriptable verification path instead of a one-off manual run
- added visible terminal progress so long runs can be monitored while they are still executing
- fixed two real shell/runtime failure modes during verification: multiline command splitting and oversized argv/session payloads
- completed a full 30-minute verification session that sustained the target duration and returned to the intended `examples/halo-drift` artifact path

Verification:

- `bash -n scripts/start_long_task_game_session.sh`
- full unit test discovery passed locally: `166 tests OK, 2 skipped`
- final long-task session passed with `elapsed_seconds: 1801`, `requested_seconds: 1800`, `sustained_target_duration: yes`

## 2026-05-07

### Workflow Resolution Now Uses Workflow Asset Metadata / 工作流解析现在使用工作流资产元数据

Included pending change set:

- `app/core/models.py`: added optional `task_type` and `workflow_slug` metadata to workflow assets
- `app/core/spec_loader.py`: added bulk workflow loading and task-type workflow lookup helpers
- `app/agent/planner.py`: made prompt-to-task and task-to-workflow resolution prefer workflow metadata before heuristic fallback
- `app/agent/intent_clarifier.py`: reused the shared workflow lookup helper for clarification fields
- `app/agent/loop.py`: now loads the workflow catalog once and uses it for task/workflow resolution
- `specs/workflows/*.yaml`: added explicit `task_type` and `workflow_slug` metadata
- tests updated in `tests/test_spec_loader.py` and `tests/test_planner.py`

Highlights:

- moved the main task-to-workflow mapping out of hard-coded planner branching and into workflow asset metadata
- kept a small fallback mapping only for cases where workflow metadata is unavailable
- aligned intent clarification with the same shared workflow lookup path
- made the active loop load the workflow catalog once instead of encoding separate task/workflow resolution rules in multiple places

Verification:

- targeted spec loader, planner, CLI, and daemon tests passed locally
- full unit test discovery passed locally: `159 tests OK, 2 skipped`

Impact:

- workflow assets now carry enough metadata to drive both task inference and workflow file resolution
- the task-to-behavior path is now more spec-driven and less dependent on duplicated code constants

### Rule Assets Now Route Into Critic And Verifier / 规则资产现已接入 Critic 与 Verifier

Included pending change set:

- `app/core/models.py`: extended `RuleSpec` with explicit `enforced_by` ownership
- `app/agents/critic_agent.py`: filtered rule execution by `critic` ownership instead of applying every rule generically
- `app/agents/verifier_agent.py`: added rule-driven verifier judgments and structured `verifier_rule_hits`
- `app/agent/loop.py`: passed loaded rule assets into verifier execution
- `specs/rules/surgical-changes.yaml`: marked the existing surgical scope rule as critic-owned
- `specs/rules/application-artifact-signals.yaml`: added a first verifier-owned rule asset for blocking application artifact failure signals
- tests updated in `tests/test_spec_loader.py`, `tests/test_critic_agent.py`, and `tests/test_verifier_agent.py`

Highlights:

- moved rule assets from critic-only influence toward explicit multi-agent enforcement
- let verifier treat application artifact failure signals as rule-backed blocking evidence instead of relying only on hard-coded verifier logic
- kept rule ownership explicit so verifier-targeted rules do not accidentally alter critic behavior
- made both verifier and critic expose structured rule-hit reporting for downstream replay and debugging

Verification:

- targeted spec loader, critic, and verifier tests passed locally
- full unit test discovery passed locally: `157 tests OK, 2 skipped`

Impact:

- `specs/rules` now shape verifier and critic judgments through explicit ownership instead of only influencing critic summaries
- the harness took another concrete step toward the sprint goal of making repo assets control real runtime behavior

### Workflow Verification Gates Become Spec-Driven / 工作流验证门转为规范驱动

Included pending change set:

- `app/core/models.py`: added a structured `VerificationGateSpec` model on workflow assets
- `app/core/spec_loader.py`: added workflow gate loading from `verification_gates`
- `app/agent/verification_gates.py`: made workflow-defined gate specs drive runtime gate selection
- `app/agent/completion_contracts.py`: aligned completion-contract test-file requirements with structured workflow gate configuration
- `specs/workflows/*.yaml`: added explicit `verification_gates` entries for shipped workflow assets
- tests updated in `tests/test_spec_loader.py`, `tests/test_completion_contracts.py`, and `tests/test_verification_gates.py`

Highlights:

- moved workflow verification-gate selection from string matching toward explicit spec-backed gate declarations
- kept backward compatibility for workflows that still rely on legacy `verification` text entries
- made workflow assets visibly change runtime verification behavior instead of only plan text
- kept completion-contract requirements aligned with workflow gate configuration so the harness does not apply conflicting rules

Verification:

- targeted workflow, gate, completion-contract, and planner tests passed locally
- full unit test discovery passed locally: `155 tests OK, 2 skipped`

Impact:

- workflow assets now control post-execution gate selection through a structured runtime-facing field
- the project took a concrete step toward the current sprint goal of making `specs/` assets shape real harness behavior

## 2026-05-06

### Multi-Agent Orchestration And Local Daemon Service / 多代理编排与本地守护服务

Included pending change set:

- `app/agent/orchestrator.py`: added explicit agent isolation and transition recording across planner, coder, verifier, critic, and router stages
- `app/daemon/service.py` and `app/daemon/server.py`: added a minimal local daemon service and HTTP surface for run, status, and latest-trajectory queries
- loop and replay wiring updates in `app/agent/loop.py` and `app/evals/replay.py`
- agent reuse update in `app/agents/planner_agent.py`
- new orchestration and daemon tests under `tests/test_orchestrator.py`, `tests/test_daemon_service.py`, and `tests/test_daemon_server.py`

Highlights:

- made agent handoff explicit instead of leaving execution order implicit inside one local loop
- recorded agent-level allowed tools, declared I/O contracts, observed keys, and next-agent transitions in replay artifacts
- kept the orchestration layer minimal and synchronous while still surfacing isolation boundaries clearly
- added a small daemon service that can run a task, report latest run status, and return the latest stored trajectory over HTTP

Verification:

- targeted orchestration and daemon tests passed locally
- full unit test discovery passed locally: `153 tests OK, 2 skipped`
- architecture check passed locally with `python3 scripts/check_architecture.py`
- isolated worktree verification passed locally with `bash scripts/agent_verify.sh`

Impact:

- the harness now has a first explicit multi-agent control surface instead of a purely monolithic local loop
- replay artifacts are now more useful for studying stage boundaries and agent-level execution behavior
- the project now has a first reusable daemon-style entrypoint beyond the CLI without committing to a larger platform surface yet

## 2026-04-30

### Tool Registry, Workflow Execution, Legibility Readers, And Memory Retrieval / 工具注册表、工作流执行、可观测读层与记忆检索

Included pending change set:

- `app/core/tool_registry.py`: added a spec-backed tool registry with schema-validated input and output checks
- `app/runtime/artifact_readers.py`: added a registered artifact reader layer for preview, log, and metric inputs
- `app/agent/workflow_executor.py`: added structured workflow execution state instead of plan-only workflow shaping
- `app/core/memory_store.py`: added lightweight related-trajectory retrieval scoped to the active repository
- `specs/tools/` and `specs/readers/`: added tool and reader specs for the new registry layer
- loop, verifier, replay, CLI, and context wiring updates across `app/agent/loop.py`, `app/agents/verifier_agent.py`, `app/evals/replay.py`, `app/cli/main.py`, and `app/agent/context_builder.py`

Highlights:

- unified tool invocation behind spec-backed registry and schema validation instead of scattered direct calls
- upgraded workflow behavior from plan shaping only into explicit `workflow_execution` state with selected tools, readers, steps, and completion status
- moved browser preview, log, and metric collection into a reusable reader registry instead of hard-coded artifact scanning
- let verifier, critic, replay, and CLI consume structured application artifact verification results
- added repository-scoped related memory retrieval so new runs can reuse relevant recent trajectories in context assembly
- let `IntentClarifier` reuse strong related-memory hits for continuation fallback and target completion when the prompt is underspecified
- let the planner turn related-memory hits into bounded `memory_context_paths` so context assembly can prioritize narrower file slices

Verification:

- targeted registry, workflow, legibility, verifier, graph, CLI, and memory tests passed locally
- full unit test discovery passed locally: `149 tests OK, 2 skipped`
- architecture check passed locally with `python3 scripts/check_architecture.py`
- isolated worktree verification passed locally with `bash scripts/agent_verify.sh`

Impact:

- the harness now has a first reusable control plane for tools and application readers instead of one-off runtime wiring
- workflow assets now influence execution state and not only the generated plan text
- application legibility is now registered, typed, and replay-visible across preview, log, and metric surfaces
- memory moved from replay-only storage toward lightweight retrieval that can shape future task context
- retrieval now influences continuation choice, target completion, and plan-level context narrowing instead of staying as a passive context annotation

## 2026-04-28

### Harness Article Walkthrough Upgrade / Harness 文章实战增强

Included pending change set:

- `docs/guides/from-zero-to-your-own-harness.md`: expanded the main learning article with a harness evolution map and a repository-grounded request walkthrough

Highlights:

- added a stage-by-stage evolution diagram from prompt wrapper to workflow-aware harness
- added a concrete call-chain walkthrough that traces a request through CLI, clarification, context, planning, policy, runtime, verification, repair, and replay
- strengthened the article as a practical learning guide instead of only a conceptual overview

Verification:

- manual markdown link check for touched documentation passed locally
- architecture check passed locally with `python3 scripts/check_architecture.py`
- full unit test discovery passed locally: `126 tests OK, 2 skipped`

Impact:

- the main harness learning article is now closer to publishable long-form teaching material
- readers can connect the concepts directly to real repository files with less interpretation work

### Harness Learning Preparation Pack / Harness 学习准备包

Included pending change set:

- `docs/guides/harness-capability-matrix.md`: separates implemented, partial, and planned harness capabilities
- `docs/guides/harness-code-reading-path.md`: gives an execution-order code reading route through the repository
- `docs/guides/harness-pitfalls-and-anti-patterns.md`: collects common harness failure modes and teaching counterexamples
- `examples/harness-lab/`: tiny practice target for first-harness exercises
- navigation updates in `README.md`, `docs/guides/README.md`, `docs/README.md`, and `docs/architecture/README.md`

Highlights:

- clarified the boundary between current MVP behavior and future roadmap items
- added a learner-friendly path for tracing one request through entry, context, planning, runtime, verification, repair, and replay
- created a small practice target so readers can exercise harness behavior on something simpler than the full repository
- collected anti-pattern material for future articles and onboarding docs

Verification:

- manual markdown link check for touched documentation passed locally
- architecture check passed locally with `python3 scripts/check_architecture.py`
- full unit test discovery passed locally: `126 tests OK, 2 skipped`
- harness lab sample test discovery runs locally and currently shows one intentional failing regression in `test_divide_by_zero_raises_value_error`

Impact:

- the repository now has a stronger teaching substrate for future harness articles and onboarding
- readers can move between concept docs, code reading, practice, and anti-patterns without inventing their own study path

### Harness Learning Article / Harness 学习长文

Included pending change set:

- `docs/guides/from-zero-to-your-own-harness.md`: a long-form article that teaches harness learning from basics to implementation
- documentation navigation updates in `docs/guides/README.md`, `docs/README.md`, and `docs/architecture/README.md`

Highlights:

- explains what a harness solves compared with a prompt wrapper
- gives a staged learning path from mental model to asset layer to a first personal harness project
- maps repository modules to harness responsibilities so readers can study the current codebase with less guesswork
- complements the existing implementation guide with a more article-like onboarding path

Verification:

- manual markdown link check for touched documentation passed locally

Impact:

- the repository now has both a practical implementation guide and a more narrative learning article
- onboarding readers can move from concept to code with a clearer path

### Documentation Title Convention / 文档标题规范

Included pending change set:

- `docs/conventions/docs.md`: documented the bilingual-title rule for project documentation
- `docs/conventions/README.md` and `AGENTS.md`: surfaced the rule in contributor and agent-facing navigation

Highlights:

- every new or materially updated document should use an `English Title / 中文标题` heading
- section headings are encouraged to follow the same bilingual style when practical
- body content stays flexible as long as the structure is clear

Verification:

- manual review of touched documentation passed locally

Impact:

- documentation style is now a repository rule instead of a conversational preference
- future doc work has a clearer default, which should reduce formatting drift

### Harness Implementation Guide / Harness 实现指南

Included pending change set:

- `docs/guides/how-to-implement-a-harness.md`: new contributor guide that teaches the end-to-end harness implementation path
- documentation navigation updates in `ARCHITECTURE.md`, `docs/README.md`, and `docs/guides/README.md`
- sprint status update in `docs/plans/current-sprint.md`

Highlights:

- mapped harness concerns to concrete repository implementation files
- documented the minimum vertical slice for building a harness from scratch
- explained entry, intent clarification, context, planning, policy, runtime, verification, repair, and replay as separate control points
- added test-first guidance for proving harness behavior outside model prose

Verification:

- manual markdown link check for touched documentation passed locally
- architecture check passed locally with `python3 scripts/check_architecture.py`
- full unit test discovery passed locally: `126 tests OK, 2 skipped`

Impact:

- new contributors now have a direct path from "what is a harness?" to "how do I implement one?"
- the project documentation is better organized as a teaching base, not only an architecture reference

### Long Task Game Rerun Example / 长任务小游戏续跑示例

Included pending change set:

- `docs/design/long-task-game-rerun-2026-04-24.md`: design record for the second delegated game task rerun
- `examples/long-task-game-2026-04-24/`: new standalone browser mini-game "Starforge Relay", a dependency-free vanilla HTML/CSS/JS top-down arcade courier game

## 2026-04-24

### Permission Guardrails, Context Compression, And Acceptance Tightening / 权限护栏、上下文压缩与验收收口

Included pending change set:

- current working tree, focused on completing the first two-week execution pass across permission boundaries, context shaping, asset-driven behavior, and release guardrails

Highlights:

- added an explicit permission `action` model with stable `allow / confirm / deny` outputs across operation, command, and file-write decisions
- extended command classification so network-shaped commands such as `curl` and `wget` now require explicit approval by default
- improved CLI permission visibility with action-oriented summaries, clearer blocked-output details, and structured permission snapshots
- added shared context compression utilities and reused them in both repo planning context and acceptance context assembly
- added bounded prompt, path, file-content, and git-summary shaping so context assembly is shorter and more budget-aware
- made workflow assets shape planning more explicitly through bounded context and clarification steps
- made rule assets shape critic output more explicitly through structured rule-hit reporting and multi-rule loading
- extended architecture checks with file-size guardrails for high-risk control-surface modules
- tightened release acceptance messaging so fast-only and live-provider modes are surfaced more clearly
- added provider risk categorization in local acceptance reporting for transient environment issues, setup/auth issues, and product-blocking issues

Verification:

- full unit test discovery passed locally: `126 tests OK, 2 skipped`
- `bash scripts/agent_verify.sh` passed
- default `bash scripts/release_acceptance.sh` path passed

Impact:

- the harness now exposes permission decisions in a clearer control-plane shape instead of relying on mixed approval booleans alone
- context assembly is more compact and reusable across local planning and release acceptance flows
- `specs/` assets now have stronger visible influence on plan construction and critic output
- structural drift and provider-facing release expectations are easier to catch and interpret

## 2026-04-23

### Long Task Game Visible Upgrade / 长任务小游戏可见升级

Included pending change set:

- current working tree, focused on documenting the visible upgrade produced by the 600-second delegated game task

Highlights:

- added `examples/long-task-game`, a dependency-free browser game that opens directly from `index.html`
- upgraded the game with first-open visible systems: mission select, difficulty choices, modifiers, power-up legend, in-game status strip, power-up drops, and a detailed results screen
- documented the upgrade in [`docs/design/long-task-game-upgrade.md`](../design/long-task-game-upgrade.md)
- kept the existing `examples/web-game` demo untouched

Verification:

- `node --check examples/long-task-game/game.js` passed
- static checks confirmed local `./styles.css` and `./game.js` references, visible mission / power-up / results UI markers, and no external URLs

Impact:

- the repository now has a concrete product-facing artifact from a long delegated coding task
- the upgrade record distinguishes real visible product changes from hidden implementation polish

### Live Acceptance Fast-Test Isolation / Live 验收快速测试隔离

Included pending change set:

- current working tree after `62ab0dc`, focused on preparing the release flow for a 600-second unattended live acceptance run

Highlights:

- isolated default fast acceptance tests from `CC_RUN_LIVE_PROVIDER_TESTS` so release acceptance no longer runs live provider tests during the unit-test phase
- applied the same environment isolation inside `scripts/agent_verify.sh` so unit verification stays deterministic even when the caller has live-test flags set
- kept live provider checks in the dedicated `tests.test_live_provider_integration` phase where provider failures are easier to interpret

Verification:

- targeted script-structure tests should confirm both verification scripts unset the live-test flag for unit-test discovery

Impact:

- today’s 600-second acceptance run has a cleaner preflight path: fast checks remain fast, and live provider checks happen only in the intended live phase
- transient live provider failures are less likely to be misreported as ordinary unit-test failures

### Acceptance Artifact Path Clarification / 验收产物路径澄清

Included pending change set:

- current working tree after `5098fbc`, focused on unblocking the delegated 600-second acceptance task prompt

Highlights:

- allowed explicit artifact creation prompts to reference not-yet-existing output paths such as `.claude-code/acceptance/final_acceptance_report.md`
- kept missing existing repo targets protected, so requests like `write tests for missing_module.py` still stop for clarification
- added regression coverage for creation-oriented artifact paths

Verification:

- targeted intent clarifier, CLI, and script tests passed locally: `38 tests OK`

Impact:

- delegated live acceptance prompts can now reach the provider instead of being blocked by repo-target clarification before artifact creation begins

### Continuation Candidate Selection / 续跑候选选择

Included pending change set:

- current working tree, focused on making ambiguous short continuation prompts actionable instead of only blocking execution

Highlights:

- added structured continuation candidates to clarification results, including stable labels, task type hints, optional timestamps, original prompts, and summaries
- updated CLI clarification output to show candidate summaries, bounded choices, and a concrete rerun hint such as `cc recent_task_1 --repo ...`
- allowed label-based follow-up prompts such as `recent_task_1` to continue the selected recent task directly
- kept ambiguous continuation clarification focused on selecting a continuation target instead of also asking unrelated target and success-criteria questions

Verification:

- targeted continuation and CLI tests passed locally: `29 passed`

Impact:

- short prompts such as `继续` now produce a clearer recovery path when multiple recent tasks are available
- users can resolve ambiguity with a stable candidate label instead of rewriting the original task prompt

## 2026-04-22

### Acceptance Prompt Git Snapshot Guidance / 验收提示词 Git 快照指引

Included pending change set:

- current working tree after `2a3121a`, focused on reducing false-positive git-environment noise in isolated live acceptance workspaces

Highlights:

- updated the local acceptance prompt in [`app/acceptance/report_runner.py`](../../app/acceptance/report_runner.py) so `GIT_STATUS_SUMMARY` and `GIT_DIFF_STAT_SUMMARY` are treated as authoritative repository-state inputs
- clarified that isolated acceptance workspaces may intentionally omit `.git` metadata and that this alone should not be reported as a release risk when git summaries are already present
- added prompt regression coverage in [`tests/test_acceptance_report_runner.py`](../../tests/test_acceptance_report_runner.py)

Verification:

- targeted acceptance runner tests should confirm the new prompt guidance is present

Impact:

- real acceptance reports should be less likely to include environment-specific “missing .git” noise
- release reviewers should see repository-state conclusions derived from the supplied git snapshots rather than from isolation mechanics

### GLM5 Acceptance Retry Hardening / GLM5 验收重试加固

Included pending change set:

- current working tree after `599a7fa`, focused on making live `glm5` acceptance more resilient to transient gateway timeouts

Highlights:

- added retry classification in [`app/acceptance/report_runner.py`](../../app/acceptance/report_runner.py) for transient provider failures such as `502`, `503`, `504`, and timeout-shaped runtime errors
- added configurable retry controls through `CC_ACCEPTANCE_API_RETRIES` and `CC_ACCEPTANCE_API_RETRY_DELAY_SECONDS`
- kept non-retryable failures such as auth or validation errors as immediate hard failures so the acceptance result still reflects real release risk
- added regression coverage in [`tests/test_acceptance_report_runner.py`](../../tests/test_acceptance_report_runner.py) for retry-on-timeout behavior and retryability classification

Verification:

- full unit test discovery passed locally: `113 tests OK`
- default `bash scripts/release_acceptance.sh` path passed
- real unattended `glm5` acceptance completed successfully after the retry hardening, producing validated markdown and JSON artifacts

Impact:

- long-running live acceptance runs are less likely to fail due to one transient provider-side timeout
- release acceptance remains strict on real blocking issues while becoming more stable against flaky network edges
- the `glm5` release path is now closer to the intended unattended final acceptance workflow

## 2026-04-21

### Continuation Ambiguity Handling / 续轮歧义处理

Included pending change set:

- current working tree after `85799f3`, focused on safer continuation handling for short follow-up inputs

Highlights:

- extended `intent clarifier` to inspect multiple recent replay summaries instead of only the latest run
- added ambiguity detection for short continuation inputs such as `继续` so the harness now stops for clarification when multiple recent tasks are plausible
- kept the continuation path automatic when there is only one clear recent task candidate
- added replay-store helpers for reading multiple recent trajectory summaries
- ignored the local `bin/feishu-cli` helper binary so local tooling noise no longer pollutes release acceptance git status

Verification:

- relevant test suite passed locally, including full unit test discovery
- default `bash scripts/release_acceptance.sh` path passed before this follow-up commit

Impact:

- short continuation inputs are now safer and more predictable in multi-task repository sessions
- release acceptance conclusions are less likely to be skewed by local untracked helper binaries
- the interaction-harness path now better distinguishes between “continue automatically” and “stop because continuation is ambiguous”

## 2026-04-20

### Intent Clarification And Release Acceptance Flow / 意图澄清与发布验收流

Included commit:

- `efc81d9` `feat: add intent clarification and release acceptance flow`

Highlights:

- added a pre-execution `intent clarifier` that can normalize clear requests and block ambiguous ones with structured clarification output
- connected workflow-level `clarification_fields` so clarification requirements can be shaped by workflow assets
- added live provider acceptance test scaffolding under [`tests/test_live_provider_integration.py`](../../tests/test_live_provider_integration.py)
- added a unified release acceptance entrypoint via [`scripts/release_acceptance.sh`](../../scripts/release_acceptance.sh)
- added an unattended long-running live acceptance task path with a dedicated prompt template under [`specs/templates/acceptance-task-template.md`](../../specs/templates/acceptance-task-template.md)
- added an acceptance report contract plus example markdown and JSON artifacts under [`docs/design`](../../docs/design)
- added lightweight acceptance JSON validation, including `acceptance_status` enum checks

Verification:

- unit test suite passed: `96 tests OK`
- default release acceptance flow passed through [`scripts/release_acceptance.sh`](../../scripts/release_acceptance.sh)

Impact:

- the harness now has an explicit preflight clarification control point before execution
- provider-facing release validation is now documented and runnable from a single script entrypoint
- unattended acceptance runs can leave both human-readable and machine-readable artifacts for later review or automation

### GLM5 Local Acceptance Reporting / GLM5 本地验收报告

Included pending change set:

- current working tree after `04f53d3`, focused on API-backed acceptance execution and artifact reporting

Highlights:

- added a local `app/acceptance` runner and `app/models` client layer so `glm5` and other Anthropic-compatible API providers can generate acceptance artifacts without requiring a delegated CLI runtime
- moved acceptance report validation into a reusable Python module and kept shell-level release acceptance as the single entrypoint
- reduced acceptance prompt size through summarized context slices and added git snapshot fallbacks so isolated acceptance workspaces still carry useful repository state
- added an artifact-retention flag so long acceptance runs can keep their temporary workspace for later inspection
- confirmed a real unattended `glm5` acceptance run can now produce validated markdown and JSON acceptance artifacts

Verification:

- unit and integration suite passed locally: `107 tests OK`
- default `bash scripts/release_acceptance.sh` path passed
- real `glm5` release acceptance path produced validated artifacts and completed successfully

Impact:

- API-backed providers are no longer limited to single-shot live probes for acceptance use cases
- `glm5` can now participate in unattended release acceptance runs through a local harness-controlled execution path
- release acceptance artifacts can be validated and optionally retained for audit and debugging

## 2026-05-25

### Final Harness Learning Article Polish / Harness 学习主文终稿收尾

Included commit:

- pending local change set for the final Feishu-ready pass on the unified harness learning article

Highlights:

- finalized [`docs/design/harness-blog-feishu-copyready.md`](../design/harness-blog-feishu-copyready.md) as the single primary harness learning article
- removed remaining draft-style formatting such as fragmented one-line paragraphs and mixed glossary pacing
- kept the article front half project-agnostic and reserved `Claude_Code_MVP` references for the later sample-project mapping section
- aligned terminology toward Chinese-first narration with English kept mainly for code-adjacent flow chains and glossary annotations
- tightened the vibecoding-versus-harness comparison so it reads as one article section instead of a teaching outline

Verification:

- manual final-read pass completed against content richness, readability, and Feishu formatting expectations
- working tree review confirmed the intended doc-only scope: `docs/design/harness-blog-feishu-copyready.md`

Impact:

- the repository now has one final publishable harness learning article that can be uploaded to Feishu without depending on the removed companion drafts
- the main learning document now better matches the project's role as a harness learning base instead of a project-intro-only article

## 2026-05-11

### Sample App Removal And Starter Path Cleanup / sample_app 移除与起步路径清理

Included commit:

- pending local change set for removing `sample_app` and retargeting starter task artifacts

Highlights:

- removed the leftover `sample_app/` starter package from the repository
- retargeted starter task templates so generated calculator, string utility, and tool router artifacts now live under `app/`
- kept temporary workspace execution working by generating `app/__init__.py` for non-long-task starter flows
- updated permission rules, write-profile examples, and harness tests so they no longer depend on `sample_app`
- simplified the long-task launcher reminder so it only blocks unrelated-file edits instead of naming a removed directory

Verification:

- targeted migration suite passed: `python3 -m unittest tests.test_tool_router tests.test_context_selector tests.test_completion_contracts tests.test_permission_pipeline tests.test_runtime_command_guard tests.test_verification_gates tests.test_failure_classifier tests.test_critic_agent tests.test_graph_execution`
- full unit suite passed: `python3 -m unittest discover -s tests`

Impact:

- the repository no longer carries an orphaned starter package with half-stale references
- starter-flow examples and repair paths now point at the main `app/` tree instead of a separate sample namespace

## 2026-05-11

### Long-Task Session Reporting Tightening / 长任务会话报告收紧

Included commit:

- pending local change set for long-task session reporting and CLI permission-path test stability

Highlights:

- tightened the long-task session markdown block so each iteration now records `did`, `optimized`, `artifact`, and `next` fields
- threaded per-iteration focus text through the long-task launcher so follow-up guidance survives into the saved session report
- inferred a clearer artifact category from changed target files to make long runs easier to review at a glance
- stabilized the delegated `codex_cli` permission-denied JSON test by patching the runtime adapter instead of depending on ambient provider availability
- shortened one `halo-drift` marathon overlay sentence

Verification:

- shell syntax check passed: `bash -n scripts/start_long_task_game_session.sh`
- Python compile check passed: `python3 -m py_compile tests/test_cli_main.py`
- targeted unit suite passed: `python3 -m unittest tests.test_cli_main`

Impact:

- long-task replay notes now show clearer per-iteration intent and artifact focus instead of relying only on a summary blob
- the CLI test suite is less sensitive to local provider installation state when asserting permission-denied behavior

## 2026-04-16

### GLM5 Provider And Web Game Demo / GLM5 Provider 与网页小游戏 Demo

Included commits:

- `5320aec` `feat: support explicit auth source selection`
- `a4edc0d` `feat: add glm5 provider and web game demo`

Highlights:

- added a dedicated `glm5` provider backed by an Anthropic-compatible messages API adapter
- added proxy-bypass handling for private gateway targets such as `llm-api.zego.cloud`
- confirmed live delegated execution through `glm5` with a real `MODEL_OK` response
- added a zero-dependency browser game demo under [`examples/web-game`](../../examples/web-game)
- kept the existing `claude_code` and `codex_cli` paths separate from the new compatible API path

Verification:

- unit test suite passed: `61 tests OK`
- live `glm5` delegated provider check passed
- local static serving check for the web game returned `HTTP 200`

Impact:

- the harness can now execute coding-style delegated prompts through a configured `GLM-5` compatible endpoint
- the repository now includes a simple end-user-facing web artifact that can be opened directly in a browser or shared on a LAN
