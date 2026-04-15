---
last_updated: 2026-04-15
status: active
owner: core
---

# 12 Harness Patterns Reference

## 文章来源

文章：

- `Claude Code中的12个 Harness 模式`
- 链接：https://www.hubwiz.com/blog/12-harness-patterns-in-claude-code/

这不是本项目的实现文档，而是一份很适合拿来做 Harness 设计清单的外部参考。

## 一句话总结

这篇文章最重要的结论是：

Claude Code 一类系统真正的工程价值，不在“模型会不会写代码”，而在模型外面有没有一套稳定的 Harness 控制层。

## 文章在讲什么

文章把 Claude Code 风格的 Harness 总结成 12 个常见模式，核心覆盖四类问题：

- 上下文和记忆怎么组织
- 工作流怎么分阶段和编排
- 工具和权限怎么做隔离
- 失败之后怎么恢复

它更适合拿来回答：

- 一个 Agent Harness 应该包含哪些控制层
- 哪些能力该留在模型里
- 哪些能力应该产品化成系统模块

而不是回答：

- 某个模式具体应该如何编码实现

## 这篇文章最值得吸收的地方

如果只提炼最关键的 4 个观点，我会总结成这些：

### 1. 上下文必须是作用域化的

不是把整个仓库都塞进 prompt，而是只把和当前任务最相关的部分组织进去。

### 2. 成功标准不能只靠模型主观判断

需要有显式的验证门、完成定义和失败信号。

### 3. 工具与权限必须有外部控制层

不能假设模型自己会一直“有分寸”。

### 4. 失败恢复是正常路径，不是异常分支

repair loop 不是附加项，而是 Harness 的一部分。

## 和 `Claude_Code_MVP` 的对照

如果拿这 12 个 pattern 对照当前仓库，可以分成三类看：

- 已经有了第一版实现
- 已经有雏形，但还比较轻
- 还明显缺失

## 一、已经有了第一版实现的

### 1. Persistent Instruction Files

对应本项目：

- [`../../AGENTS.md`](../../AGENTS.md)
- [`../../ARCHITECTURE.md`](../../ARCHITECTURE.md)
- [`../architecture/harness-explained.md`](../architecture/harness-explained.md)
- [`../architecture/interaction-harness.md`](../architecture/interaction-harness.md)
- `docs/conventions/*`

说明：

项目已经明确把“长期稳定规则”沉淀为文档层，而不是只靠会话 prompt。

### 2. Scoped Context Assembly

对应本项目：

- [`../../app/agent/context_builder.py`](../../app/agent/context_builder.py)
- [`../../app/agent/context_selector.py`](../../app/agent/context_selector.py)

说明：

PR2 完成后，项目已经不再只有简单文件抽样，而是开始用结构化方式产出：

- `always_include_docs`
- `likely_relevant_files`
- `test_targets`
- `architecture_constraints`

这已经是作用域上下文组装的第一版。

### 3. Explore -> Plan -> Execute

对应本项目：

- [`../../app/agent/context_builder.py`](../../app/agent/context_builder.py)
- [`../../app/agent/planner.py`](../../app/agent/planner.py)
- [`../../app/agent/loop.py`](../../app/agent/loop.py)

说明：

虽然现在还是轻量单 loop，但已经有明确的：

- 先构造上下文
- 再推断任务类型
- 再进入执行与验证

### 4. Verification Gates

对应本项目：

- [`../../app/agent/completion_contracts.py`](../../app/agent/completion_contracts.py)
- [`../../app/agent/verification_gates.py`](../../app/agent/verification_gates.py)

说明：

PR1 完成后，系统已经有了：

- `completion_check`
- `gate_results`
- `gate_failures`

也就是说，“成功”开始从模型判断转为 Harness 判断。

### 5. Tool Adapter Layer

对应本项目：

- [`../../app/runtime/adapter_factory.py`](../../app/runtime/adapter_factory.py)
- [`../../app/runtime/ecc_adapter.py`](../../app/runtime/ecc_adapter.py)
- [`../../app/runtime/cli_adapter.py`](../../app/runtime/cli_adapter.py)
- [`../../app/runtime/local_runtime.py`](../../app/runtime/local_runtime.py)

说明：

当前 runtime/provider 已经明确走适配层，而不是把不同执行后端硬写进 loop。

### 6. Least-Privilege / Permission Gate

对应本项目：

- [`../../app/agent/policies.py`](../../app/agent/policies.py)

说明：

虽然还不是特别厚的权限系统，但已经有：

- 风险等级
- 是否批准
- 是否需要确认
- 推荐重试 flag

### 7. Self-Healing Loop

对应本项目：

- [`../../app/superpowers/failure_classifier.py`](../../app/superpowers/failure_classifier.py)
- [`../../app/superpowers/repair_policy.py`](../../app/superpowers/repair_policy.py)
- [`../../app/superpowers/self_repair.py`](../../app/superpowers/self_repair.py)

说明：

PR3 完成后，repair 已经从“轻量重试”升级成：

- failure classification
- repair decision
- bounded retry
- repair attempt history

### 8. Replay / Traceability

对应本项目：

- [`../../app/evals/replay.py`](../../app/evals/replay.py)
- [`../../app/core/memory_store.py`](../../app/core/memory_store.py)

说明：

虽然文章不一定把 replay 单列为独立 pattern，但从 Harness 视角看，traceability 是这套系统的重要补充控制面。

## 二、已经有雏形，但还比较轻的

### 9. Layered Memory

对应本项目：

- `memory_store`
- `replay`

说明：

当前更多是轨迹存储与回放，还不是成熟的长期记忆系统。

缺的主要是：

- 工作记忆
- 摘要记忆
- 长期项目记忆
- checkpoint 恢复

### 10. Progressive Context Compression

对应本项目：

- `context selector` 是前置筛选

说明：

现在已经有“选哪些上下文”，但还没有“长任务过程中如何逐步压缩上下文”的系统。

### 11. Explicit Stage Machine

对应本项目：

- `loop` 已经越来越像显式流程控制

说明：

但它还没有真正抽成：

- phase enum
- phase transition
- phase-specific permission / gate

所以它更像“增强版顺序 loop”，还不是完整状态机。

## 三、还明显缺失的

### 12. Parallel / Multi-Agent Workflow

说明：

当前项目明确还是单代理优先，没有真正的 sub-agent orchestration、上下文隔离和并行执行控制。

### 13. Dreaming / Background Memory Consolidation

说明：

文章提到的后台记忆整合、摘要合并、历史压缩，这类能力当前还没有。

### 14. Headless Batch / Productized Unattended Mode

说明：

虽然项目已经有 CLI 和 verify 脚本，但还没有真正产品化的无头批处理运行面。

## 对本项目的直接结论

如果按这篇文章的 12 个 pattern 来看，`Claude_Code_MVP` 现在已经覆盖了最关键的第一波控制点：

- instruction layer
- context selection
- verification gates
- permission pipeline
- repair policy
- replay / trace

这意味着项目已经不再只是：

`prompt -> model -> output`

而是明显进入了：

`request -> context -> policy -> execute -> verify -> repair -> replay`

也就是说：

**它已经是一个 Harness MVP，而不是 prompt wrapper。**

## 还最值得继续补的地方

如果继续沿着这篇文章的思路推进，后面最值得补的 4 个方向是：

### 1. 把 loop 继续抽成 phase-aware state machine

这样可以把：

- permission
- verify
- stop condition

进一步和阶段绑定。

### 2. 把 memory 从 replay 雏形升级成分层记忆系统

### 3. 把上下文选择继续推进到压缩与预算管理

### 4. 引入更明确的多 agent / worktree isolation 模式

## 推荐搭配阅读

建议这样看：

1. [`../../README.md`](../../README.md)
2. [`../../ARCHITECTURE.md`](../../ARCHITECTURE.md)
3. [`../architecture/harness-explained.md`](../architecture/harness-explained.md)
4. [`claude-code-source-leak.md`](./claude-code-source-leak.md)
5. 本文档

这样能先理解本项目当前做到了哪一步，再用这篇 “12 patterns” 文章来检查还有哪些控制层没有被产品化。
