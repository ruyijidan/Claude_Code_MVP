---
last_updated: 2026-04-27
status: active
owner: core
---

# Harness Code Reading Path / Harness 读代码路径

## Purpose / 目的

This guide gives learners a deliberate reading order through the codebase.

The goal is not to read every file.

The goal is to trace one harness run from:

`user request`

to:

`verification and replay`

## Fast Path / 快速路径

If you only have 30 minutes, read these files in order:

1. [`app/cli/main.py`](../../app/cli/main.py)
2. [`app/agent/intent_clarifier.py`](../../app/agent/intent_clarifier.py)
3. [`app/agent/context_builder.py`](../../app/agent/context_builder.py)
4. [`app/agent/planner.py`](../../app/agent/planner.py)
5. [`app/agent/loop.py`](../../app/agent/loop.py)
6. [`app/agent/policies.py`](../../app/agent/policies.py)
7. [`app/runtime/local_runtime.py`](../../app/runtime/local_runtime.py)
8. [`app/agent/verification_gates.py`](../../app/agent/verification_gates.py)
9. [`app/superpowers/repair_policy.py`](../../app/superpowers/repair_policy.py)
10. [`app/evals/replay.py`](../../app/evals/replay.py)

That path is enough to understand the control loop.

## Reading By Layer / 按层阅读

### 1. Entry Layer / 第一层：入口层

Read:

- [`app/cli/main.py`](../../app/cli/main.py)

Questions:

- how does a request enter the system?
- what gets resolved before execution starts?
- where does provider selection happen?

What to notice:

- the CLI is a control surface, not the whole product
- risk and runtime decisions happen around the task, not inside output formatting

### 2. Interaction Control / 第二层：交互控制

Read:

- [`app/agent/intent_clarifier.py`](../../app/agent/intent_clarifier.py)

Questions:

- how does the harness treat short follow-up inputs?
- when does it continue automatically?
- when does it stop for clarification?

What to notice:

- continuation is a harness rule, not just model improvisation

### 3. Context Assembly / 第三层：上下文构造

Read:

- [`app/agent/context_builder.py`](../../app/agent/context_builder.py)
- [`app/agent/context_selector.py`](../../app/agent/context_selector.py)
- [`app/core/context_compressor.py`](../../app/core/context_compressor.py)

Questions:

- where does repo awareness come from?
- how are docs, tests, git state, and candidate files selected?
- how does the project keep context bounded?

What to notice:

- context quality matters more than dumping more files

### 4. Planning Layer / 第四层：规划层

Read:

- [`app/agent/planner.py`](../../app/agent/planner.py)
- [`specs/workflows`](../../specs/workflows)

Questions:

- how does the project infer task shape?
- where do workflow assets start influencing behavior?

What to notice:

- the planner is intentionally lightweight
- the workflow layer is present, but not yet a full orchestration engine

### 5. Policy Layer / 第五层：策略层

Read:

- [`app/agent/policies.py`](../../app/agent/policies.py)
- [`specs/rules`](../../specs/rules)

Questions:

- what is classified as safe, confirm-required, or denied?
- which parts are hard policy and which parts are reusable rule assets?

What to notice:

- policy sits before runtime
- rules and permissions are related, but not the same thing

### 6. Runtime Layer / 第六层：运行时层

Read:

- [`app/runtime/adapter_factory.py`](../../app/runtime/adapter_factory.py)
- [`app/runtime/local_runtime.py`](../../app/runtime/local_runtime.py)
- [`app/runtime/cli_adapter.py`](../../app/runtime/cli_adapter.py)
- [`app/runtime/api_adapter.py`](../../app/runtime/api_adapter.py)
- [`app/runtime/git_tool.py`](../../app/runtime/git_tool.py)

Questions:

- how does execution stay backend-agnostic?
- where do git-facing features live?
- how does the harness switch between local, CLI-backed, and API-backed paths?

What to notice:

- runtime abstraction is one of the strongest signals that this is a harness, not a demo script

### 7. Verification And Repair / 第七层：验证与修复

Read:

- [`app/agent/completion_contracts.py`](../../app/agent/completion_contracts.py)
- [`app/agent/verification_gates.py`](../../app/agent/verification_gates.py)
- [`app/superpowers/failure_classifier.py`](../../app/superpowers/failure_classifier.py)
- [`app/superpowers/repair_policy.py`](../../app/superpowers/repair_policy.py)
- [`app/superpowers/self_repair.py`](../../app/superpowers/self_repair.py)

Questions:

- how does the harness decide whether a task is really done?
- which failures are retryable?
- where does the loop stop instead of trying again forever?

What to notice:

- completion, verification, and repair are separate concerns

### 8. Replay And Evaluation / 第八层：回放与评估

Read:

- [`app/evals/replay.py`](../../app/evals/replay.py)
- [`app/core/memory_store.py`](../../app/core/memory_store.py)

Questions:

- what evidence is stored after a run?
- how can later runs use recent trajectories?

What to notice:

- replay makes continuation and inspection much more reliable

## Reading With A Concrete Prompt / 带着一个真实任务去读

Use a sample task like:

- `fix failing tests`
- `add a tool router and tests`
- `investigate intermittent tool routing failures`

Then trace:

1. where the prompt first appears
2. where it gets normalized
3. where task type is inferred
4. where risk is classified
5. where execution backend is chosen
6. where verification result is interpreted
7. where replay is written

This is the fastest way to stop reading files in isolation and start seeing the system as a loop.

## Best Companion Docs / 最佳搭配文档

Read this alongside:

1. [`../../ARCHITECTURE.md`](../../ARCHITECTURE.md)
2. [`../architecture/harness-explained.md`](../architecture/harness-explained.md)
3. [`./harness-capability-matrix.md`](./harness-capability-matrix.md)
4. [`./from-zero-to-your-own-harness.md`](./from-zero-to-your-own-harness.md)
