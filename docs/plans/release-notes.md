---
last_updated: 2026-04-20
status: active
owner: core
---

# Release Notes / 发布说明

## 2026-04-20

### Continuation-Aware Intent Clarifier Flow / 续轮感知意图澄清流

Included commit:

- pending local commit for continuation-aware clarification and kickoff flow

Highlights:

- extended `intent clarifier` with `kickoff_message` and `continuation_target`
- taught the CLI to print a short kickoff summary before execution starts
- persisted replay request summaries so short continuation inputs can reuse the latest task context
- allowed inputs such as `继续` to resolve to the latest trajectory summary when the target is unambiguous
- kept continuation behavior covered by focused CLI and clarifier tests

Verification:

- `python3 -m unittest tests.test_intent_clarifier`
- `python3 -m unittest tests.test_cli_main`

Impact:

- short continuation input no longer always stops at clarification when recent replay context is sufficient
- execution-start behavior is now more visible and more consistent across clarified requests
- the interaction entry layer now has a clearer first engineering footprint in code

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
