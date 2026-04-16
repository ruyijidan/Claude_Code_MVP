---
last_updated: 2026-04-15
status: active
owner: core
---

# Current Sprint / 当前冲刺

## Goal / 目标
Move Claude Code MVP from a runnable coding loop into a clearer harness-oriented project with stronger information and constraint layers.

## Related Plans / 相关计划

- `docs/plans/harness-hardening-pr-plan.md`: first implementation wave for completion contracts, verification gates, scoped context selection, and repair policy hardening

## In Progress / 进行中

- Add `AGENTS.md` map-mode navigation
- Add architecture and convention docs
- Add architecture boundary checks
- Add CI harness guardrails baseline
- Complete harness hardening PR 1:
  - completion contracts
  - verification gates
- Complete harness hardening PR 2:
  - scoped context selector
- Complete harness hardening PR 3:
  - failure classifier
  - repair policy
- Finish the first harness hardening wave and record the stage summary in `docs/plans/harness-hardening-pr-plan.md`

## Next / 下一步

- Add worktree-based verification script
- Add application legibility foundations
- Add stronger import and file-size guardrails
- Continue turning workflow, template, and rule assets into behavior-shaping harness inputs

## Later / 稍后

- Add browser and preview tooling
- Add log and metric readers
- Add cleanup automation and doc-gardening tasks
