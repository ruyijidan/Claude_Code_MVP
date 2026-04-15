---
last_updated: 2026-04-10
status: active
owner: core
---

# Runtime And Git Workflow

## Runtime Rules

- `LocalRuntimeAdapter` is the default stable path.
- Provider adapters may delegate to external CLIs, but must report provider availability and execution details.
- Local loop failures should be reported clearly to the user, including actionable hints.

## Git Workflow Rules

- Use `GitTool` as the single place for git status, diff, review, and commit summary helpers.
- CLI should present git information; runtime should gather it.
- Commit suggestions are advisory, not authoritative.

## Safety Rules

- Prefer preview modes and summaries before write-heavy actions.
- If future commit/stage support is added, default to preview or explicit approval.
