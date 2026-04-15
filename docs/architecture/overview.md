---
last_updated: 2026-04-10
status: active
owner: core
---

# Architecture Overview

## System Goal
Claude Code MVP is a harness-oriented coding agent that helps developers inspect repositories, plan work, apply code changes, verify results, and review the resulting patch.

## Primary Flow

1. CLI receives a developer request
2. Context builder gathers repo and git context
3. Planner infers a task type and builds a lightweight plan
4. Runtime-backed loop applies changes
5. Verifier runs tests
6. Repair logic retries when needed
7. Replay persists a trajectory
8. Git review and commit summary help the developer inspect the result

## Main Packages

- `app/cli`
  Terminal-first user entrypoint.
- `app/agent`
  The single-agent loop, planning, policies, and repo context construction.
- `app/runtime`
  Execution adapters, git tooling, provider abstraction, and filesystem/shell primitives.
- `app/superpowers`
  Retry and self-repair support.
- `app/evals`
  Replay and scoring support.
- `app/core`
  Shared models, spec loading, schema validation, and memory store utilities.
- `specs`
  Constraint-oriented task and agent definitions retained from the original starter.

## Harness Perspective

This repository intentionally separates:

- information layer: `AGENTS.md`, `docs/`, `README`
- execution layer: `app/agent`, `app/runtime`
- feedback layer: tests, replay, git review, repair

That separation is the current foundation for evolving the project toward a stronger harness engineering model.

For a fuller Chinese walkthrough of how this repository maps to harness concepts, read [`harness-explained.md`](./harness-explained.md).

## External Architectural Reference

This project also uses the following repository as a conceptual reference for Claude Code style harness thinking:

- `claude-code-book`: `https://github.com/lintsinghua/claude-code-book/tree/main`
- `claw-code`: `https://github.com/ultraworkers/claw-code/tree/main`

These are reading/reference resources, not code dependencies.
