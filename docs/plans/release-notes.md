---
last_updated: 2026-04-24
status: active
owner: core
---

# Release Notes / 发布说明

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
