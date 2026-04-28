---
last_updated: 2026-04-27
status: active
owner: core
---

# How To Implement A Harness / 如何实现 Harness

## Purpose / 目的

This guide teaches the implementation path behind `Claude_Code_MVP`.

It is for readers who already understand the high-level idea:

`CLI -> Repo Context -> Plan -> Execute -> Verify -> Repair -> Replay`

and now want to know how to build that shape in code.

## The Short Version / 最短版本

A coding-agent harness is not a bigger prompt. It is a control system around model execution.

The minimum useful harness has seven parts:

1. Entry: accept a user request
2. Context: collect bounded repository context
3. Plan: choose a task shape and next steps
4. Policy: decide what is allowed before execution
5. Runtime: perform file, shell, provider, and git actions through adapters
6. Verification and repair: check the result and retry only when rules allow it
7. Replay: record what happened so the run can be inspected later

If any of these parts are missing, the project can still be an agent demo, but it is not yet a durable harness.

## Implementation Map / 实现地图

In this repository, the current mapping is:

| Harness concern | Current implementation |
|---|---|
| Entry | [`app/cli/main.py`](../../app/cli/main.py) |
| Intent clarification | [`app/agent/intent_clarifier.py`](../../app/agent/intent_clarifier.py) |
| Repo context | [`app/agent/context_builder.py`](../../app/agent/context_builder.py), [`app/agent/context_selector.py`](../../app/agent/context_selector.py) |
| Planning | [`app/agent/planner.py`](../../app/agent/planner.py), [`specs/workflows`](../../specs/workflows) |
| Policy | [`app/agent/policies.py`](../../app/agent/policies.py), [`specs/rules`](../../specs/rules) |
| Loop | [`app/agent/loop.py`](../../app/agent/loop.py) |
| Runtime | [`app/runtime`](../../app/runtime) |
| Git workflow | [`app/runtime/git_tool.py`](../../app/runtime/git_tool.py) |
| Verification | [`app/agent/verification_gates.py`](../../app/agent/verification_gates.py), [`scripts/agent_verify.sh`](../../scripts/agent_verify.sh) |
| Completion | [`app/agent/completion_contracts.py`](../../app/agent/completion_contracts.py) |
| Repair | [`app/superpowers/self_repair.py`](../../app/superpowers/self_repair.py), [`app/superpowers/repair_policy.py`](../../app/superpowers/repair_policy.py) |
| Replay | [`app/evals/replay.py`](../../app/evals/replay.py), [`app/core/memory_store.py`](../../app/core/memory_store.py) |

This table is the best starting point for reading the codebase because it follows the runtime order, not package names.

## Step 1: Build A Thin Entry Point / 第一步：做薄入口

Start with a CLI or API endpoint that does only control-surface work.

It should:

- accept the user prompt
- resolve the repository path
- load configuration
- select the provider or runtime mode
- call policy checks before execution
- print structured status, review, and permission summaries

It should not:

- contain task-specific implementation logic
- run ad hoc git commands directly
- bypass the runtime layer for special cases

In this repo, `app/cli/main.py` is intentionally the control surface, not the whole harness.

Success check:

- a new operation can be added without turning the CLI into a large branch tree
- CLI tests can assert visible behavior without needing a real provider

## Step 2: Normalize Intent Before Execution / 第二步：执行前先规范化意图

Real users do not always send complete tasks.

They often type:

- `继续`
- `好`
- `先做 PR1`
- `文档也补上`

A harness should decide whether that input is:

- a new task
- a continuation of one recent task
- an ambiguous continuation that needs clarification
- a risky operation that needs confirmation

This belongs before the main execution loop.

In this repo, `intent_clarifier` is the first version of that control point. It keeps short continuation inputs from being interpreted purely by model guesswork.

Success check:

- short inputs continue only when there is one clear target
- ambiguous inputs produce actionable choices
- high-risk or missing-target requests stop before execution

## Step 3: Build Bounded Repo Context / 第三步：构造有边界的仓库上下文

The context builder should not dump the whole repository into the model.

It should collect compact signals:

- current repo path
- user prompt
- git status summary
- diff summary
- candidate files
- relevant docs
- test layout
- previous replay summaries when continuation matters

Then the selector or compressor should trim this into a task-sized context.

The design principle is:

`context should be enough to act, not enough to drown`.

Success check:

- large files and diffs are summarized or bounded
- context assembly is deterministic enough to test
- important project docs are easy to discover through `AGENTS.md` and `docs/`

## Step 4: Separate Planning From Execution / 第四步：把计划和执行分开

Planning should answer:

- what kind of task is this?
- which workflow asset applies?
- what visible steps should the harness report?
- what context and verification signals matter?

Execution should answer:

- what files or commands need to change?
- what runtime backend should do the work?
- what verification should run after the change?

In this repo, the planner maps prompts into task shapes such as:

- `fix_bug`
- `implement_feature`
- `write_tests`
- `investigate_issue`

Workflow assets under `specs/workflows/` then give those task shapes a more explicit structure.

Success check:

- adding a new repeated task shape starts with a workflow asset, not a large loop rewrite
- generated plans are short, visible, and tied to verification expectations

## Step 5: Put Policy In Front Of Tools / 第五步：让策略挡在工具前面

A harness must know the difference between safe inspection and risky mutation.

Policy should classify:

- operation type
- command risk
- file-write risk
- network-shaped behavior
- git-facing behavior
- whether to allow, confirm, or deny

The important part is that this classification happens before the runtime executes the action.

In this repo, `policies.py` provides the current permission model, and rule assets under `specs/rules/` provide reusable behavioral expectations.

Success check:

- policy output is structured
- tests can assert `allow / confirm / deny`
- risky behavior has a visible reason, not just a hidden boolean

## Step 6: Hide Execution Behind Runtime Adapters / 第六步：用 Runtime Adapter 隔离执行

Do not let the agent loop know every backend detail.

The loop should express intent:

- run local commands
- apply a patch
- delegate to a provider CLI
- read git state
- run tests

Runtime adapters should decide how that work is performed.

In this repo, the runtime layer supports:

- local execution
- delegated `claude` CLI execution
- delegated `codex` CLI execution
- API-backed provider paths

The point is not provider variety by itself. The point is keeping the harness loop stable when execution backends change.

Success check:

- adding a provider does not rewrite the main agent loop
- provider-specific auth and invocation details stay inside runtime/model adapters
- git-facing workflow features use `GitTool`

## Step 7: Define Completion Before Declaring Success / 第七步：先定义完成，再宣布成功

An agent should not finish just because it produced text or edited files.

Completion contracts should define what "done" means for a task type:

- expected files changed
- expected tests added or updated
- expected verification command
- expected docs update when behavior changes
- expected artifact creation for acceptance/reporting tasks

In this repo, completion checks and verification gates are separated so the harness can ask two different questions:

- Did the task produce the expected shape?
- Did verification pass strongly enough for this workflow?

Success check:

- a task can fail completion even when the model says it is done
- verification requirements can vary by workflow
- failure output is specific enough to drive repair

## Step 8: Repair With Stop Conditions / 第八步：带停止条件地修复

Repair is useful only when it is bounded.

A good repair loop should know:

- what failed
- whether the failure is retryable
- which next action is allowed
- when to stop instead of looping forever

In this repo, failure classification and repair policy are separate so the harness can avoid treating every failure as "try again harder".

Success check:

- retryable provider or timeout failures can be retried
- deterministic product/test failures are surfaced clearly
- stop conditions are explicit and testable

## Step 9: Persist Replay Evidence / 第九步：保存可回放证据

Replay turns an agent run from a black box into an inspectable trajectory.

A useful replay record should include:

- original prompt
- selected provider or runtime mode
- inferred task type
- plan summary
- key actions
- verification result
- final status

This lets future runs answer:

- what happened last time?
- is a short input continuing a recent task?
- which failures were transient?
- what evidence supports the final claim?

Success check:

- replay data can be read without re-running the task
- continuation logic can inspect recent runs
- acceptance or release reports can cite concrete run evidence

## Minimal Vertical Slice / 最小纵向切片

If you are implementing a new harness from scratch, build this slice first:

1. CLI accepts `--repo` and a prompt
2. Context builder returns repo path, git status, and candidate files
3. Planner emits one task type and three visible steps
4. Policy classifies the operation as `allow`, `confirm`, or `deny`
5. Runtime can run one safe command and read git status
6. Verification runs one deterministic test command
7. Replay writes one JSON record

Do not start with multi-agent orchestration, dashboards, browser automation, or a complex rule engine. Those become useful after the first control loop is reliable.

## What To Test First / 优先测试什么

Prioritize tests for control points, not model prose.

Good first tests:

- short continuation prompt becomes clarification when multiple recent tasks exist
- missing target path stops before execution
- network-shaped command requires confirmation
- workflow asset changes generated plan or verification expectations
- verification gate fails when required checks are absent
- repair policy stops on non-retryable failures
- replay record includes enough data for later inspection

These tests prove the harness is doing real work outside the model.

## Common Mistakes / 常见错误

- putting task-specific branches directly in the CLI
- treating prompts as the only source of policy
- letting the model decide whether a risky command should run
- dumping too much context and calling it repository awareness
- declaring success without verification evidence
- retrying failures without classification or stop conditions
- adding workflow YAML that no code or test consumes
- building a provider integration before the local control loop is testable

## Reading Path / 推荐阅读顺序

To understand this repository as an implementation example, read:

1. [`../../ARCHITECTURE.md`](../../ARCHITECTURE.md)
2. [`../architecture/harness-explained.md`](../architecture/harness-explained.md)
3. [`../architecture/interaction-harness.md`](../architecture/interaction-harness.md)
4. [`../patterns/workflow-layer.md`](../patterns/workflow-layer.md)
5. [`../patterns/asset-layer.md`](../patterns/asset-layer.md)
6. [`./how-to-add-a-workflow.md`](./how-to-add-a-workflow.md)
7. [`./how-to-add-a-rule.md`](./how-to-add-a-rule.md)

Then follow the implementation map at the top of this guide through the code.
