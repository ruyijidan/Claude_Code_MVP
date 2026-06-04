---
last_updated: 2026-05-11
status: active
owner: core
---

# Harness Teaching Path / Harness 教学路径

## Purpose / 目的

This guide turns the current repository docs into a teaching pack.

Use it when you want to:

- onboard a new contributor
- prepare an internal harness sharing session
- choose the right article or guide for a learner
- move from concept learning into hands-on practice

## The Short Version / 最短路径

If you only need one recommended order, use this:

1. [`../../ARCHITECTURE.md`](../../ARCHITECTURE.md)
2. [`../architecture/harness-explained.md`](../architecture/harness-explained.md)
3. [`./how-to-implement-a-harness.md`](./how-to-implement-a-harness.md)
4. [`./from-zero-to-your-own-harness.md`](./from-zero-to-your-own-harness.md)
5. [`../../examples/harness-lab/README.md`](../../examples/harness-lab/README.md)
6. [`../../examples/harness-lab/TASKS.md`](../../examples/harness-lab/TASKS.md)

This path works for most first-time readers because it goes from concept to architecture to implementation to practice.

## Choose By Audience / 按受众选择

### For First-Time Learners / 面向第一次接触的人

Start here:

1. [`../architecture/harness-explained.md`](../architecture/harness-explained.md)
2. [`./from-zero-to-your-own-harness.md`](./from-zero-to-your-own-harness.md)
3. [`../../examples/harness-lab/README.md`](../../examples/harness-lab/README.md)

Goal:

- understand what a harness is
- understand why it is different from a prompt wrapper
- get a safe practice target quickly

### For Contributors Who Need The Code Map / 面向要读代码的人

Start here:

1. [`../../ARCHITECTURE.md`](../../ARCHITECTURE.md)
2. [`../architecture/overview.md`](../architecture/overview.md)
3. [`../architecture/boundaries.md`](../architecture/boundaries.md)
4. [`./harness-code-reading-path.md`](./harness-code-reading-path.md)
5. [`./how-to-implement-a-harness.md`](./how-to-implement-a-harness.md)

Goal:

- read the codebase in execution order
- understand layer boundaries before making changes

### For Internal Sharing Or Reading Clubs / 面向内部分享或读书会

Use this pack:

1. [`../design/harness-blog-feishu-copyready.md`](../design/harness-blog-feishu-copyready.md)
2. [`../design/harness-blog-feishu-promotion-summary.md`](../design/harness-blog-feishu-promotion-summary.md)
3. [`../../examples/harness-lab/README.md`](../../examples/harness-lab/README.md)

Suggested split:

- `copyready`: best default version for direct Feishu posting
- `promotion summary`: best for short previews, channel posts, or discussion openers
- `harness-lab`: best for turning the article into a small live exercise

## Choose By Goal / 按目标选择

### Goal: Learn The Mental Model / 目标：先学概念

Read:

1. [`../architecture/harness-explained.md`](../architecture/harness-explained.md)
2. [`../reference/12-harness-patterns.md`](../reference/12-harness-patterns.md)
3. [`../design/harness-blog-feishu-copyready.md`](../design/harness-blog-feishu-copyready.md)

### Goal: Learn The Implementation Path / 目标：学实现路径

Read:

1. [`../../ARCHITECTURE.md`](../../ARCHITECTURE.md)
2. [`./how-to-implement-a-harness.md`](./how-to-implement-a-harness.md)
3. [`./harness-capability-matrix.md`](./harness-capability-matrix.md)

### Goal: Practice On A Small Target / 目标：在小靶子上练手

Read and run:

1. [`../../examples/harness-lab/README.md`](../../examples/harness-lab/README.md)
2. [`../../examples/harness-lab/TASKS.md`](../../examples/harness-lab/TASKS.md)
3. `python3 -m unittest discover -s examples/harness-lab/tests`

## Teaching Pack Roles / 教学包分工

| Asset | Best use |
|---|---|
| [`../../ARCHITECTURE.md`](../../ARCHITECTURE.md) | the end-to-end control loop and runtime order |
| [`./how-to-implement-a-harness.md`](./how-to-implement-a-harness.md) | how to map harness ideas into code responsibilities |
| [`./from-zero-to-your-own-harness.md`](./from-zero-to-your-own-harness.md) | longer learner path from concept to first implementation |
| [`./harness-code-reading-path.md`](./harness-code-reading-path.md) | code-reading order |
| [`./harness-pitfalls-and-anti-patterns.md`](./harness-pitfalls-and-anti-patterns.md) | what mistakes to avoid |
| [`../design/harness-blog-feishu-copyready.md`](../design/harness-blog-feishu-copyready.md) | paste-ready external or cross-team article |
| [`../design/harness-blog-feishu-promotion-summary.md`](../design/harness-blog-feishu-promotion-summary.md) | short summary for promotion and discussion |
| [`../../examples/harness-lab`](../../examples/harness-lab) | hands-on learner practice target |

## Suggested Session Formats / 建议教学形式

### 30-Minute Intro / 30 分钟入门分享

Use:

1. `copyready` article as the main speaking outline
2. `ARCHITECTURE.md` for one control-loop slide
3. `examples/harness-lab` for one concrete exercise

### 60-Minute Workshop / 60 分钟工作坊

Use:

1. concept section from the `copyready` article
2. implementation map from `how-to-implement-a-harness.md`
3. live practice from `examples/harness-lab`
4. debrief using `harness-pitfalls-and-anti-patterns.md`

## Maintenance Notes / 维护说明

When the teaching material changes materially:

- keep bilingual headings
- update `last_updated`
- keep the audience split clear instead of creating many near-duplicate drafts
- prefer linking to durable guides from article drafts instead of repeating repository details in every article
