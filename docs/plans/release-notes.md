---
last_updated: 2026-04-21
status: active
owner: core
---

# Release Notes / 发布说明

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
