---
last_updated: 2026-04-20
status: active
owner: core
---

# Testing Conventions / 测试约定

## Expectations / 期望

- New user-visible CLI behavior should have a test when practical.
- Runtime helpers should be covered by focused unit tests.
- Prefer deterministic tests over end-to-end external CLI execution during normal development.
- Live provider validation is required for final acceptance when the feature depends on real LLM execution paths.

## Test Layers / 测试分层

This repository now treats testing as three layers instead of one.

### 1. Unit Tests / 单元测试

Purpose:

- verify local logic
- verify asset loading
- verify planner, policy, guardrail, and CLI control behavior

Properties:

- fast
- deterministic
- no live network access
- safe to run on every edit

Typical command:

```bash
python3 -m unittest discover -s tests
```

### 2. Mocked Integration Tests / 伪集成测试

Purpose:

- verify runtime adapter wiring
- verify delegated provider command construction
- verify API request construction without live provider dependency

Properties:

- may patch external command execution or HTTP calls
- still deterministic
- still safe for normal CI and local iteration

Typical examples:

- `tests/test_provider_delegation.py`
- `tests/test_cli_main.py`

### 3. Live Acceptance Tests / 真实验收测试

Purpose:

- verify real provider availability
- verify auth configuration actually works
- verify the harness can complete a minimal real request against a live LLM path

Properties:

- slower than unit tests
- requires network and valid credentials
- may be flaky because of remote systems, latency, or provider incidents
- should not run by default in ordinary local loops or standard CI

These tests are part of final acceptance for real execution paths, not part of the default fast feedback loop.

## Patterns / 模式

- Patch external command execution in tests instead of invoking real long-running tools.
- Use temporary directories for repository simulations.
- Assert developer-facing output, not just internal return values.
- Keep live acceptance tests separate from the default fast suite and gate them behind explicit environment flags.

## Live Acceptance Policy / Live 验收策略

When a feature depends on real LLM execution, final acceptance should include at least one live validation path.

Recommended rules:

- Keep the prompt minimal and deterministic, for example `Reply with exactly MODEL_OK`.
- Validate transport success and a small expected output surface.
- Skip the test cleanly when required credentials or binaries are missing.
- Run live tests explicitly, not implicitly.

The repository currently uses:

- `CC_RUN_LIVE_PROVIDER_TESTS=1` to enable live provider acceptance tests
- optional provider selectors such as `CC_LIVE_API_PROVIDER` and `CC_LIVE_CLI_PROVIDER`

Example commands:

```bash
CC_RUN_LIVE_PROVIDER_TESTS=1 \
CC_LIVE_API_PROVIDER=glm5 \
ANTHROPIC_BASE_URL="https://example.test" \
ANTHROPIC_AUTH_TOKEN="secret" \
ANTHROPIC_MODEL="glm-5" \
python3 -m unittest tests.test_live_provider_integration
```

```bash
CC_RUN_LIVE_PROVIDER_TESTS=1 \
CC_LIVE_CLI_PROVIDER=claude_code \
python3 -m unittest tests.test_live_provider_integration
```

For a fuller release-style acceptance run, use:

```bash
bash scripts/release_acceptance.sh
```

To include a long unattended live task, set:

```bash
CC_RUN_LIVE_PROVIDER_TESTS=1 \
CC_RUN_LIVE_ACCEPTANCE_TASK=1 \
CC_LIVE_CLI_PROVIDER=claude_code \
CC_ACCEPTANCE_PROVIDER=claude_code \
CC_ACCEPTANCE_TIMEOUT_SECONDS=600 \
bash scripts/release_acceptance.sh
```

This acceptance script runs the fast suite first, then optional live provider checks, and finally an isolated long-running provider task that should complete without manual intervention.

If you want to keep the temporary acceptance workspace and generated artifacts after the run, add:

```bash
CC_ACCEPTANCE_KEEP_ARTIFACTS=1
```

The long acceptance task uses a dedicated template:

- `specs/templates/acceptance-task-template.md`

The acceptance JSON contract is documented in:

- `docs/design/acceptance-report.md`

and should leave both:

- `.claude-code/acceptance/final_acceptance_report.md`
- `.claude-code/acceptance/final_acceptance_report.json`

## Minimum Bar / 最低要求

When adding a new feature, at least one of the following should exist:

- a CLI behavior test
- a runtime/tool unit test
- an agent loop or integration-oriented test

For features that materially change live provider behavior, final acceptance should also include a live provider validation step before calling the work complete.
