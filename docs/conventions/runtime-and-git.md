---
last_updated: 2026-04-20
status: active
owner: core
---

# Runtime And Git Workflow / 运行时与 Git 工作流

## Runtime Rules / 运行时规则

- `LocalRuntimeAdapter` is the default stable path.
- Provider adapters may delegate to external CLIs, but must report provider availability and execution details.
- Local loop failures should be reported clearly to the user, including actionable hints.
- CLI auth and env-based auth are both supported, but they should be selected deliberately instead of implicitly mixed.

## Auth Source Rules / 认证来源规则

- The CLI supports `--auth-source auto|cli|env`.
- `auto` is the default.
- In `auto` mode, `claude_code` and `codex_cli` prefer the local CLI login/session and do not import `ANTHROPIC_*` keys from the project `.env`.
- In `cli` mode, the harness explicitly skips `ANTHROPIC_*` values from `.env` and relies on the local CLI login/session.
- In `env` mode, the harness explicitly loads `ANTHROPIC_*` values from `.env`.
- Use `env` mode only when you intentionally want project-local gateway/token settings to drive provider behavior.
- Do not assume that a valid local Claude CLI login and a project `.env` with `ANTHROPIC_*` values are interchangeable. They may point at different backends and can fail differently.

## Git Workflow Rules / Git 工作流规则

- Use `GitTool` as the single place for git status, diff, review, and commit summary helpers.
- CLI should present git information; runtime should gather it.
- Commit suggestions are advisory, not authoritative.
- Before creating a commit, record the completed change in project docs.
- Prefer updating `docs/plans/release-notes.md` with the commit-level summary.
- Also update `docs/plans/current-sprint.md` when the change affects current delivery status, acceptance expectations, or next-step planning.
- The preferred order is:
  - implement and verify
  - update project docs with the completed change
  - create the commit
- Install repository hooks with `bash scripts/install_git_hooks.sh`.
- The tracked pre-commit hook blocks commits that stage non-doc changes without also staging `docs/plans/release-notes.md`.

## Safety Rules / 安全规则

- Prefer preview modes and summaries before write-heavy actions.
- If future commit/stage support is added, default to preview or explicit approval.
