# AGENTS.md

## Project Summary
Claude Code MVP is a terminal-first coding agent project. Its primary workflow is:

`CLI -> Repo Context -> Plan -> Execute -> Verify -> Repair -> Replay`

The codebase is optimized for harness engineering experiments, not for ad hoc prompt-only automation.

## Repository
- Git remote: `git@github.com:ruyijidan/Claude_Code_MVP.git`
- Canonical repo URL: [ruyijidan/Claude_Code_MVP](https://github.com/ruyijidan/Claude_Code_MVP)
- External harness reference: [claude-code-book](https://github.com/lintsinghua/claude-code-book/tree/main)
  Use this as a conceptual reference for Claude Code style harness design. It is not a runtime dependency and should not be treated as implementation source-of-truth for this repository.
- External CLI harness reference: [claw-code](https://github.com/ultraworkers/claw-code/tree/main)
  Use this as a reference for CLI product shape, repository surface, and documentation organization. It is not a runtime dependency and should not be treated as implementation source-of-truth for this repository.

## Quick Navigation
| If You Need To... | Read This |
|---|---|
| Understand how the system works end to end | `ARCHITECTURE.md` |
| Understand the harness mental model in Chinese | `docs/architecture/harness-explained.md` |
| Understand the system shape | `docs/architecture/overview.md` |
| Understand layer boundaries | `docs/architecture/boundaries.md` |
| Learn coding and review conventions | `docs/conventions/README.md` |
| Learn testing expectations | `docs/conventions/testing.md` |
| Learn runtime and git workflow rules | `docs/conventions/runtime-and-git.md` |
| See the current implementation roadmap | `docs/plans/current-sprint.md` |
| Understand the current product positioning | `README.md` |

`ARCHITECTURE.md` is the primary document for execution flow and Harness layer mapping. Use it before diving into individual subsystems.

## Hard Rules
These are expected to be enforced by scripts, tests, or CI:

1. `app/cli` must not be imported by lower layers.
2. `app/runtime` must not depend on `app/cli` or `app/agent`.
3. `app/agent` is allowed to orchestrate runtime, evals, and superpowers, but not CLI.
4. New behavior should include tests when practical.
5. Prefer structured output and summaries over silent side effects.
6. Use `GitTool` for git-facing workflow features instead of ad hoc git command logic in CLI code.

## Commit Prefixes
- `feat:` user-visible capability
- `fix:` correctness issue
- `refactor:` structural improvement
- `docs:` documentation only
- `test:` tests only
- `chore:` maintenance

## Working Style
- Keep prompts, plans, and outputs short and task-oriented.
- Prefer stable conventions over clever one-off implementations.
- Add new harness behavior as reusable infrastructure, not one-off CLI branching.
