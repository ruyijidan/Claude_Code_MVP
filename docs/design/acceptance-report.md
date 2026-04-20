---
last_updated: 2026-04-20
status: draft
owner: core
---

# Feature: Acceptance Report Contract / 功能：验收报告契约

## Status / 状态
Draft

## Goal / 目标
Define a small, stable JSON contract for unattended release acceptance artifacts so the final acceptance step can be consumed by both humans and automation. The first version should stay lightweight and only fix the minimum fields needed for release gating.

## Non-Goals / 非目标
- Do not introduce a full JSON Schema dependency.
- Do not version the report format yet.
- Do not turn the acceptance report into a large nested protocol.
- Do not require all historical acceptance artifacts to be migrated.

## Proposed Changes / 拟议变更
- Keep the markdown report as the human-readable artifact.
- Keep the JSON report as the automation-facing artifact.
- Require the JSON report to contain these top-level keys:
  - `system_summary`
  - `provider_risks`
  - `live_acceptance_configured`
  - `acceptance_status`
  - `evidence`
- Require `acceptance_status` to be one of:
  - `READY`
  - `NEEDS_REVIEW`
  - `BLOCKED`
- Add lightweight validation in `scripts/release_acceptance.sh` after the long live task finishes.

## Proposed Data Shape / 建议数据结构
Suggested first-version shape:

```json
{
  "system_summary": "short release-oriented summary",
  "provider_risks": [
    "risk one",
    "risk two"
  ],
  "live_acceptance_configured": true,
  "acceptance_status": "READY",
  "evidence": [
    "tests/test_live_provider_integration.py passed",
    "scripts/agent_verify.sh passed"
  ]
}
```

Expected field types:

- `system_summary`: string
- `provider_risks`: list of strings
- `live_acceptance_configured`: boolean
- `acceptance_status`: string enum
- `evidence`: list of strings

Example artifacts:

- [`acceptance-report-example.md`](./acceptance-report-example.md)
- [`acceptance-report-example.json`](./acceptance-report-example.json)

## Acceptance Criteria / 验收标准
- The acceptance JSON contract is documented in the repository.
- `scripts/release_acceptance.sh` validates that the JSON artifact is parseable.
- `scripts/release_acceptance.sh` validates required top-level keys.
- `scripts/release_acceptance.sh` rejects invalid `acceptance_status` values.
- The change does not add a heavy schema dependency.

## Verification Plan / 验证计划
- Add script-oriented tests to confirm the validation logic exists.
- Keep the default release acceptance path green when long live acceptance is not enabled.
- When long live acceptance is enabled, require both the markdown artifact and the validated JSON artifact.
