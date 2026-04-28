---
last_updated: 2026-04-28
status: active
owner: core
---

# From Zero To Your Own Harness / 从零到实现你自己的 Harness

## Why This Article Exists / 为什么写这篇

Many people first meet AI coding agents through demos.

The demo shape is usually:

- give a prompt
- wait for the model
- get a patch or an answer

That is useful, but it is not yet a harness.

A harness starts where the demo stops. It asks:

- how does the task enter the system?
- how much repo context should be exposed?
- which operations are allowed?
- how is execution verified?
- what happens after failure?
- how can the run be replayed later?

This article uses `Claude_Code_MVP` as the teaching example and aims to help you go from:

`I know what an agent is`

to:

`I can build and evolve my own harness project`

## One Sentence First / 先用一句话记住

An agent is the worker.

A harness is the engineering system that makes the worker readable, constrained, testable, and repeatable.

If you remember only one line, remember this:

`prompt -> model output` is not enough to become a harness.

You need a control loop around the model.

## Part 1: What A Harness Really Solves / 第一部分：Harness 真正在解决什么

Before we talk about code, it helps to see the real problem.

When people say "I want to build an AI coding tool", they often mean one of two very different things.

### Shape A: Prompt Wrapper / 形态 A：Prompt 包装器

This is the lightweight version:

- collect a prompt
- send it to a model
- show the answer

This shape is fine for experiments, but it breaks down quickly when you need:

- repository awareness
- file mutation
- shell execution
- permissions
- verification
- recovery
- auditability

### Shape B: Harness / 形态 B：Harness

This is the engineering version:

- accept a task
- gather bounded context
- classify risk
- choose a workflow
- execute through controlled tools
- verify results
- retry or stop
- persist evidence

That second shape is what this repository is building.

## Part 2: The Smallest Useful Harness / 第二部分：最小可用 Harness 长什么样

You do not need a giant system to start.

A minimum useful harness has these seven capabilities:

1. Entry
   A stable place where requests enter the system, usually CLI first.
2. Context
   A bounded repo-aware snapshot, not a raw dump of the entire codebase.
3. Planning
   A small task interpretation layer that chooses a task shape and next steps.
4. Policy
   A control point that decides whether an action is allowed, denied, or needs confirmation.
5. Runtime
   A tool-backed execution layer for files, shell, git, and provider delegation.
6. Verification and repair
   A mechanism to decide whether the result is really done and whether a failure should be retried.
7. Replay
   A saved trajectory of what happened for inspection and continuation.

If one of these is missing, your system may still be useful, but it will be much harder to trust and evolve.

## Part 3: Use This Repository As A Reference Skeleton / 第三部分：把本仓库当作参考骨架

`Claude_Code_MVP` is small enough to read end to end and real enough to teach engineering tradeoffs.

Its main loop is:

`CLI -> Repo Context -> Plan -> Execute -> Verify -> Repair -> Replay`

The most important code-to-concept mapping is:

| Harness concern | Repository mapping |
|---|---|
| entry | [`app/cli/main.py`](../../app/cli/main.py) |
| clarification | [`app/agent/intent_clarifier.py`](../../app/agent/intent_clarifier.py) |
| context | [`app/agent/context_builder.py`](../../app/agent/context_builder.py), [`app/agent/context_selector.py`](../../app/agent/context_selector.py) |
| planning | [`app/agent/planner.py`](../../app/agent/planner.py), [`specs/workflows`](../../specs/workflows) |
| permissions | [`app/agent/policies.py`](../../app/agent/policies.py) |
| execution loop | [`app/agent/loop.py`](../../app/agent/loop.py) |
| runtime | [`app/runtime`](../../app/runtime) |
| verification | [`app/agent/verification_gates.py`](../../app/agent/verification_gates.py), [`scripts/agent_verify.sh`](../../scripts/agent_verify.sh) |
| repair | [`app/superpowers`](../../app/superpowers) |
| replay | [`app/evals/replay.py`](../../app/evals/replay.py) |

This is the key mindset:

do not copy the repository file-for-file.

Copy the responsibilities and the separation of concerns.

## Part 4: The Small Evolution Map / 第四部分：最小 Harness 演进图

Most people learn faster when they can see how one stage grows into the next.

Here is a practical evolution path:

```text
Stage 0
prompt -> model -> output

Stage 1
CLI -> model -> output

Stage 2
CLI -> context -> model -> output

Stage 3
CLI -> context -> plan -> runtime -> verification

Stage 4
CLI -> context -> plan -> policy -> runtime -> verification -> replay

Stage 5
CLI -> context -> plan -> policy -> runtime -> verification -> repair -> replay

Stage 6
CLI -> context -> plan -> policy -> workflow assets -> runtime -> verification -> repair -> replay
```

This diagram helps in two ways:

- it shows that a harness grows by adding control points, not just by adding prompt complexity
- it keeps you from jumping straight from Stage 0 to a pretend final product

If you are building your first version, stopping around Stage 4 or Stage 5 is already a strong result.

## Part 5: Learn In Four Stages / 第五部分：用四个阶段学习

The smoothest path is not "read everything first".

It is better to learn in four stages.

### Stage 1: Learn The Mental Model / 阶段一：先学心智模型

At this stage, do not start coding yet.

You only need to answer:

- what is a harness?
- how is it different from an agent or a prompt wrapper?
- which control points must belong to the harness instead of the model?

Recommended reading:

1. [`../../ARCHITECTURE.md`](../../ARCHITECTURE.md)
2. [`../architecture/harness-explained.md`](../architecture/harness-explained.md)
3. [`../architecture/interaction-harness.md`](../architecture/interaction-harness.md)
4. [`../reference/12-harness-patterns.md`](../reference/12-harness-patterns.md)

Target outcome:

You should be able to explain the difference between "model capability" and "harness control".

### Stage 2: Learn The Project Skeleton / 阶段二：理解工程骨架

Now start reading the codebase in execution order.

Recommended reading:

1. [`app/cli/main.py`](../../app/cli/main.py)
2. [`app/agent/loop.py`](../../app/agent/loop.py)
3. [`app/agent/policies.py`](../../app/agent/policies.py)
4. [`app/runtime`](../../app/runtime)
5. [`app/evals/replay.py`](../../app/evals/replay.py)

Questions to keep in mind:

- what enters here?
- what gets normalized?
- what gets executed?
- what gets verified?
- where does failure go?

Target outcome:

You should be able to trace one task from user input to verification result.

### Stage 3: Learn The Asset Layer / 阶段三：理解资产层

The repo is not only code.

It is also teaching an important harness habit:

do not bury repeatable execution knowledge inside one giant loop.

That is why this repo has:

- [`specs/workflows`](../../specs/workflows)
- [`specs/rules`](../../specs/rules)
- [`specs/templates`](../../specs/templates)

Read these next:

1. [`../patterns/workflow-layer.md`](../patterns/workflow-layer.md)
2. [`../patterns/asset-layer.md`](../patterns/asset-layer.md)
3. [`./how-to-add-a-workflow.md`](./how-to-add-a-workflow.md)
4. [`./how-to-add-a-rule.md`](./how-to-add-a-rule.md)

Target outcome:

You should start seeing harness evolution as "add or refine assets and control points", not only "edit the loop again".

### Stage 4: Build Your Own Thin Version / 阶段四：自己做一个薄版本

Now build the smallest version yourself.

Your first version should not try to match a full product.

Build this:

1. A CLI that accepts repo path and prompt
2. A context builder that returns repo path, git summary, and candidate files
3. A planner that chooses one task type
4. A policy layer that returns `allow`, `confirm`, or `deny`
5. A runtime that can read files, run one safe command, and write a patch
6. A verifier that runs one deterministic check
7. A replay record written to JSON

That is enough to become a real harness project.

## Part 6: How To Implement Your Own Harness / 第六部分：怎么做出你自己的 Harness

Here is a practical implementation order.

### Step 1: Start With CLI, Not With The Model / 第一步：先做 CLI，不要先堆模型

A lot of teams begin with prompts and only later realize they have no stable entrypoint.

Start from the control surface:

- parse arguments
- locate the repository
- load environment
- select runtime mode
- print structured outcomes

If the entrypoint is vague, the rest of the harness will be vague too.

### Step 2: Bound Context Early / 第二步：尽早给上下文设边界

A common failure mode is to call a project "repo-aware" when it actually just pastes too many files.

Instead, collect:

- repo root
- changed files
- a small list of likely-relevant files
- architectural docs
- test hints

Then compress.

Context quality matters more than context size.

### Step 3: Separate Intent From Execution / 第三步：把意图和执行分开

Users often say:

- `继续`
- `帮我修一下`
- `先做 PR1`

These are not execution steps. They are interaction inputs.

Your harness should normalize them before acting.

That is why input clarification belongs near the entrypoint, not buried deep inside the model prompt.

### Step 4: Put Policy Before Runtime / 第四步：策略一定要在 Runtime 前面

Never let the model directly decide whether a risky command should run.

Your policy layer should classify:

- file writes
- command execution
- network-shaped behavior
- git-facing behavior

The model can suggest.

The harness should decide.

### Step 5: Add Verification Before Adding More Intelligence / 第五步：先补验证，再补更多智能

Verification is what turns an output into a delivery step.

Without verification, the harness has no strong notion of done.

Good early checks are:

- unit tests
- architecture checks
- lint or type checks
- git diff summaries

### Step 6: Add Repair With Clear Stop Conditions / 第六步：加修复，但要有停止条件

Repair does not mean "loop forever".

It means:

- classify failure
- retry only when the next step is obvious
- stop when the result is ambiguous or risky

This makes the harness feel disciplined instead of desperate.

### Step 7: Persist Replay Early / 第七步：尽早持久化 Replay

Replay is not a luxury feature.

It is how you debug the harness itself.

If you cannot inspect yesterday's run, continuation, auditing, and iteration all get weaker.

## Part 7: A Concrete Walkthrough In This Repository / 第七部分：在本仓库里走一遍真实调用链

The fastest way to make the idea feel real is to trace one request through the repository.

Use a prompt like:

- `fix failing tests`

Then read the system in this order:

1. [`app/cli/main.py`](../../app/cli/main.py)
   This is where the request enters, provider mode is resolved, and the harness decides which execution path to use.
2. [`app/agent/intent_clarifier.py`](../../app/agent/intent_clarifier.py)
   This is where short or ambiguous follow-up inputs can be normalized or stopped before they become execution.
3. [`app/agent/context_builder.py`](../../app/agent/context_builder.py)
   This is where repo docs, git state, and candidate files begin turning into bounded task context.
4. [`app/agent/planner.py`](../../app/agent/planner.py)
   This is where the harness infers whether the request looks like bugfix, feature work, tests, or investigation.
5. [`app/agent/policies.py`](../../app/agent/policies.py)
   This is where the harness classifies operations before runtime executes them.
6. [`app/agent/loop.py`](../../app/agent/loop.py)
   This is where the main control loop ties context, planning, execution, verification, and follow-up decisions together.
7. [`app/runtime/local_runtime.py`](../../app/runtime/local_runtime.py)
   This is where file and command work actually happens for the local path.
8. [`app/agent/verification_gates.py`](../../app/agent/verification_gates.py)
   This is where the harness decides whether the result is strong enough to count as verified.
9. [`app/superpowers/repair_policy.py`](../../app/superpowers/repair_policy.py)
   This is where failures are interpreted into retry, stop, or escalation behavior.
10. [`app/evals/replay.py`](../../app/evals/replay.py)
    This is where the run is preserved as evidence for later inspection or continuation.

If you want the shorter reading companion for this exact walkthrough, use:

- [`harness-code-reading-path.md`](./harness-code-reading-path.md)

This kind of tracing is what turns architecture from a static diagram into a working mental model.

## Part 8: A Practical First Project Layout / 第八部分：第一版工程目录怎么搭

When people hear "build a harness", they often imagine a huge codebase.

Do not start there.

A good first project layout can be very small:

```text
my-harness/
  README.md
  app/
    cli/
      main.py
    agent/
      loop.py
      planner.py
      context_builder.py
      policies.py
    runtime/
      local_runtime.py
      git_tool.py
    evals/
      replay.py
  tests/
    test_cli.py
    test_planner.py
    test_policies.py
    test_replay.py
  specs/
    workflows/
  logs/
```

This is enough for a real first version.

What matters is not matching this layout exactly.

What matters is that the responsibilities stay separated.

### What Each Part Owns / 每一层应该拥有什么职责

- `cli`: request intake, argument parsing, output formatting, provider selection
- `agent`: context, planning, task execution loop, permission decisions
- `runtime`: shell, file, git, backend-specific execution primitives
- `evals`: replay, scoring, or later trace inspection
- `tests`: proof that control points behave consistently
- `specs`: reusable workflows, rules, or templates once repetition appears

If your first version keeps those boundaries, you already have the beginnings of a maintainable harness.

## Part 9: Your First Definition Of Done / 第九部分：第一版的完成标准

One of the easiest traps is shipping a harness that feels impressive but has no clear standard of completion.

For a first personal project, a strong definition of done is:

1. a prompt can enter through one stable CLI command
2. the harness can collect bounded repo context
3. one task type can be planned and executed end to end
4. risky commands are classified before execution
5. one verification command runs automatically
6. replay evidence is written after the run
7. at least four to six focused tests protect the control loop

If you have all seven, your harness is not just a demo anymore.

## Part 10: Use The Tiny Practice Target / 第十部分：先用小练习靶子练手

Before building your own repo from scratch, it helps to practice on a tiny target.

This repository now includes:

- [`../../examples/harness-lab`](../../examples/harness-lab)

That lab is intentionally small and intentionally imperfect.

It starts with one failing regression and a couple of simple follow-up tasks.

The point is to give your harness a target where you can practice:

- selecting a small amount of context
- planning a bugfix task
- running a deterministic verification command
- writing a replay summary

Recommended sequence:

1. read [`../../examples/harness-lab/README.md`](../../examples/harness-lab/README.md)
2. run the lab tests
3. ask your harness to fix the failing regression
4. add the missing `safe_divide` behavior
5. write a short run summary or replay artifact

If your harness can complete that lab cleanly, it is ready for a larger repository.

## Part 11: What Most First Versions Get Wrong / 第十一部分：第一版最容易做错什么

These mistakes are extremely common.

### Mistake 1: Treating The Prompt As The Whole System / 错误一：把 Prompt 当成整个系统

If changing behavior always means rewriting a giant prompt, you are missing harness boundaries.

### Mistake 2: Making The CLI Too Smart / 错误二：让 CLI 变得过于臃肿

The CLI should route and report.

It should not become the hidden home for planning, git logic, and workflow-specific branches.

### Mistake 3: Dumping Too Much Context / 错误三：上下文越多越好

Too much context makes the system slower, noisier, and harder to test.

Bounded relevant context is a feature.

### Mistake 4: Verifying Too Late / 错误四：太晚才重视验证

If verification is added only after you already have a complex loop, it becomes much harder to reason about failure.

### Mistake 5: No Asset Layer / 错误五：没有资产层

If every reusable behavior stays hidden in code or prompts, your system becomes fragile to extend.

### Mistake 6: No Replay / 错误六：没有 Replay

Without replay, every debugging session becomes guesswork.

If you want the fuller anti-pattern set, continue with:

- [`./harness-pitfalls-and-anti-patterns.md`](./harness-pitfalls-and-anti-patterns.md)

## Part 12: A 30-Day Learning Roadmap / 第十二部分：30 天学习路线

If you want a realistic self-study plan, this is a good default.

### Days 1-3 / 第 1 到 3 天

- read the core architecture docs
- understand the difference between agent and harness
- write your own one-paragraph definition of a harness

### Days 4-7 / 第 4 到 7 天

- trace one request through this repository
- read the code in the order suggested by [`harness-code-reading-path.md`](./harness-code-reading-path.md)
- identify where policy, runtime, verification, and replay live

### Days 8-12 / 第 8 到 12 天

- study the capability matrix
- explicitly separate implemented behavior from roadmap ideas
- note which advanced features you do not need for a first build

### Days 13-17 / 第 13 到 17 天

- use [`../../examples/harness-lab`](../../examples/harness-lab) as practice
- fix the failing regression
- add one small behavior and its tests
- write a replay-style summary by hand if your harness does not support replay yet

### Days 18-24 / 第 18 到 24 天

- scaffold your own thin harness project
- keep only one task type and one verification command
- add a small permission model

### Days 25-30 / 第 25 到 30 天

- add replay persistence
- add one workflow or rule asset
- write a short postmortem: what belongs in prompt, code, runtime, and assets

By the end of that month, you should not only understand harness engineering.

You should have built one.

## Part 13: A Suggested Learning Roadmap / 第十三部分：推荐学习路线

If you want to genuinely learn harness engineering through this repository, use this sequence.

### Week 1 / 第一周

- understand the mental model
- read the architecture and interaction docs
- trace one real request through CLI, policy, loop, and runtime

### Week 2 / 第二周

- read workflow, rule, and template assets
- understand how verification and repair are wired
- study how replay enables continuation and post-run inspection

### Week 3 / 第三周

- build a tiny harness in your own repo
- keep only one task type
- keep only one verification command
- keep replay as JSON

### Week 4 / 第四周

- add one more workflow
- add one rule
- add one repair stop condition
- add one release-style verification script

This path is much more stable than trying to imitate a full product from day one.

## Part 14: How This Project Helps You Beyond The Article / 第十四部分：这个项目还能怎么继续帮你

This article is the overview.

The deeper implementation playbook is:

- [`how-to-implement-a-harness.md`](./how-to-implement-a-harness.md)

The best "what is already real versus still future work" guide is:

- [`harness-capability-matrix.md`](./harness-capability-matrix.md)

The best "how should I traverse the codebase" guide is:

- [`harness-code-reading-path.md`](./harness-code-reading-path.md)

The best practice target is:

- [`../../examples/harness-lab`](../../examples/harness-lab)

The best architecture docs are:

- [`../../ARCHITECTURE.md`](../../ARCHITECTURE.md)
- [`../architecture/overview.md`](../architecture/overview.md)
- [`../architecture/harness-explained.md`](../architecture/harness-explained.md)
- [`../architecture/interaction-harness.md`](../architecture/interaction-harness.md)

The best extension docs are:

- [`./how-to-add-a-workflow.md`](./how-to-add-a-workflow.md)
- [`./how-to-add-a-rule.md`](./how-to-add-a-rule.md)

If you treat those documents as a sequence instead of isolated notes, this repository becomes a compact harness curriculum.

## Final Takeaway / 最后带走的一句话

The real step up from "AI can help me code" to "I can build an AI coding system" is learning to design the control loop around the model.

That control loop is the harness.

And the best way to learn it is not by reading ten abstract frameworks.

It is by building one small, testable, opinionated harness of your own.
