---
last_updated: 2026-04-15
status: active
owner: core
---

# How To Add A Workflow

## Purpose

This guide explains how to add a new workflow asset to `Claude_Code_MVP` without immediately turning it into a large code refactor.

## When To Add One

Add a workflow when a task shape has enough repetition that it should no longer stay implicit in planner logic or prompt wording.

Good candidates:

- repeated bugfix flow
- repeated review flow
- repeated investigation flow
- repeated spec-driven implementation flow

Do not add a new workflow for one-off wording differences.

## Step 1: Create The Workflow Asset

Add a file under `specs/workflows/`.

Example:

- `specs/workflows/review-change.yaml`

Keep the first version small and structured. Prefer these fields:

- `name`
- `goal`
- `entry_signals`
- `required_context`
- `steps`
- `verification`
- `stop_conditions`

## Step 2: Reuse Existing Harness Control Points

A workflow should connect to existing control layers instead of inventing its own loop.

Current control points to reuse:

- scoped context from `context_builder` and `context_selector`
- completion contracts
- verification gates
- failure classifier
- repair policy

The goal is to express a task shape, not bypass the harness.

## Step 3: Check Whether A New Template Or Rule Is Also Needed

Sometimes a workflow asset is enough.

Sometimes it should be paired with:

- a template in `specs/templates/`
- a rule in `specs/rules/`

Examples:

- a review workflow may want a review summary template
- a refactor workflow may want a simplicity or surgical-changes rule

## Step 4: Add Or Extend Tests

At minimum, cover one of these:

- planner or selector integration
- workflow-specific completion expectations
- workflow-specific repair or stop behavior

Do not leave a workflow asset completely disconnected from tests.

## Step 5: Update Docs When The Workflow Changes Project Shape

If the new workflow affects how collaborators should think about the harness, update:

- `docs/patterns/` for long-lived architectural meaning
- `docs/guides/` for contributor instructions
- `docs/plans/` if the work is part of a tracked implementation wave

## Design Rules

- Prefer stable structures over verbose prose.
- Keep workflow names aligned with task names when possible.
- Reuse existing harness checks before inventing new ones.
- Keep the first version narrow and concrete.

## Recommended First Question

Before adding a new workflow, ask:

“Is this a genuinely different execution shape, or just a different example of an existing one?”

If it is not a different execution shape, improve the existing workflow instead.
