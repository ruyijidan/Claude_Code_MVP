---
last_updated: 2026-04-15
status: active
owner: core
---

# How To Add A Rule / 如何新增规则

## Purpose / 目的

This guide explains how to add a new reusable rule asset without immediately turning it into a heavy policy engine.

## When To Add One / 何时新增

Add a rule when a behavior expectation repeats across tasks and should no longer stay implicit.

Good candidates:

- keep changes narrow
- verify before declaring success
- clarify ambiguity before making assumptions
- avoid broad cleanup unless required

Do not add a rule for a single one-off preference.

## Step 1: Add The Rule Asset / 第一步：新增规则资产

Create a file under `specs/rules/`.

A first-version rule should stay small.

Recommended fields:

- `name`
- `intent`
- `applies_to`
- `checks`
- `failure_message`

## Step 2: Pick One Control Point / 第二步：选择一个控制点

Do not connect a new rule to every part of the system at once.

Choose one place first:

- critic
- verification gates
- completion contracts
- future workflow selector

The current repository already uses `critic` as a safe first integration point.

## Step 3: Add A Narrow Interpretation / 第三步：增加窄解释

Do not build a general-purpose rule engine before the project needs one.

A good first interpretation is:

- one obvious failure signal
- one clear emitted issue
- one test that proves the rule is wired correctly

## Step 4: Add Tests / 第四步：补测试

At minimum, add:

- one direct unit test for the rule integration point
- one regression check if the rule affects loop behavior

## Step 5: Update Pattern Docs If The Rule Changes Project Thinking / 第五步：当规则改变项目认知时更新模式文档

If the rule represents a broader architectural concept, update:

- `docs/patterns/`
- `docs/guides/`
- `docs/plans/` if it is part of a tracked implementation wave

## Design Rules / 设计规则

- Prefer a narrow rule with a clear failure message.
- Avoid building a mini language too early.
- Connect rules to one control point first, then expand later if useful.
- Keep behavior stable enough that contributors can predict what the rule will do.
