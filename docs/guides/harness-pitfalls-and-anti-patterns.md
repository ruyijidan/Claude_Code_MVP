---
last_updated: 2026-04-27
status: active
owner: core
---

# Harness Pitfalls And Anti-Patterns / Harness 常见踩坑与反模式

## Purpose / 目的

This guide collects the most common ways people build something that looks like a harness but behaves like a fragile prompt wrapper.

Use it when:

- preparing teaching material
- reviewing architecture changes
- deciding whether a new feature belongs in the harness or only in prompt wording

## Pitfall 1: Prompt-As-System / 踩坑一：把 Prompt 当系统

Symptoms:

- every behavior change means editing a bigger prompt
- risk policy lives only in instructions
- task completion is judged by model prose alone

Why it hurts:

- behavior becomes hard to test
- rules drift across providers
- the system gets harder to reason about after every change

Better direction:

- move stable controls into code and assets
- keep prompt wording as one input to the harness, not the whole harness

## Pitfall 2: Overloaded CLI / 踩坑二：CLI 过度膨胀

Symptoms:

- the CLI starts owning planning logic, git rules, and workflow special cases
- every feature adds another branch to one large entrypoint

Why it hurts:

- the control surface becomes the hidden implementation core
- extension work gets noisy and brittle

Better direction:

- keep CLI responsible for intake, routing, and reporting
- move execution meaning into agent, runtime, and asset layers

## Pitfall 3: Context Flooding / 踩坑三：上下文洪水

Symptoms:

- the harness pastes large file dumps instead of selecting relevant evidence
- repo awareness is measured by volume, not precision

Why it hurts:

- slower runs
- noisier planning
- weaker repeatability

Better direction:

- gather bounded context
- compress large inputs
- bias toward task-relevant files and docs

## Pitfall 4: Policy After Execution / 踩坑四：先执行再判断策略

Symptoms:

- the model can directly trigger risky commands
- file writes happen before explicit permission classification

Why it hurts:

- safety becomes accidental
- runtime behavior differs across providers and prompts

Better direction:

- classify risk before runtime action
- make `allow / confirm / deny` explicit and testable

## Pitfall 5: Verification As An Afterthought / 踩坑五：把验证当收尾补丁

Symptoms:

- tasks are considered done because code changed
- verification commands are inconsistent or missing
- repair has no strong signal to work from

Why it hurts:

- "looks done" replaces "is done"
- failures surface late and ambiguously

Better direction:

- define completion contracts and verification gates early

## Pitfall 6: Retry Without Failure Typing / 踩坑六：不分类失败就重试

Symptoms:

- every failure loops back into "try again"
- there is no distinction between timeout, auth failure, and bad implementation

Why it hurts:

- the harness becomes noisy and wasteful
- deterministic failures take longer to surface

Better direction:

- classify failures
- retry only when the next step is obvious and bounded

## Pitfall 7: No Asset Layer / 踩坑七：没有资产层

Symptoms:

- every repeated task shape lives inside ad hoc prompt wording
- workflow or rule knowledge cannot be reviewed separately from loop code

Why it hurts:

- the project becomes harder to extend
- contributors have no stable place to add reusable behavior

Better direction:

- keep workflows, rules, and templates as explicit repo assets where practical

## Pitfall 8: No Replay / 踩坑八：没有 Replay

Symptoms:

- the team cannot inspect what happened after a run
- short follow-up inputs are hard to interpret safely

Why it hurts:

- continuation gets weaker
- debugging becomes guesswork

Better direction:

- persist enough run evidence to support inspection and continuation

## Pitfall 9: Teaching The Final Form First / 踩坑九：一上来就教最终形态

Symptoms:

- beginner material starts with browsers, memory, subagents, and dashboards
- learners cannot identify the minimum useful control loop

Why it hurts:

- the system feels magical instead of buildable
- readers copy product thickness without understanding the core

Better direction:

- teach the thin loop first
- add advanced layers only after entry, policy, runtime, verification, and replay are understood

## How This Repository Avoids Some Of These / 本仓库目前是怎么规避一部分问题的

`Claude_Code_MVP` already does a few important things right:

- it keeps CLI, runtime, policy, verification, and replay separated
- it has a real permission model instead of only descriptive guidance
- it persists replay evidence
- it has started an explicit asset layer

It also still has honest limits:

- workflow and rule assets are still early
- browser-style application legibility is not here yet
- memory beyond replay is still future work

That combination is exactly why the repository is useful as a teaching base.

## Best Companion Docs / 最佳搭配文档

Read this after:

1. [`./from-zero-to-your-own-harness.md`](./from-zero-to-your-own-harness.md)
2. [`./harness-capability-matrix.md`](./harness-capability-matrix.md)
3. [`./how-to-implement-a-harness.md`](./how-to-implement-a-harness.md)
