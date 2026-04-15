---
last_updated: 2026-04-10
status: active
owner: core
---

# Harness Explained

## 一句话

`Claude_Code_MVP` 不是单纯的“AI 帮你写代码工具”，而是一个把 Agent 放进可读、可控、可验证环境里的最小 Harness。

## 1. Harness 到底是什么

Harness 不是模型本身，而是模型外面的这套工程系统。

它回答的是这些问题：

- 任务从哪里进来
- 上下文怎么组织
- 工具怎么调用
- 什么能做、什么不能做
- 做完怎么验证
- 失败怎么修
- 过程怎么记录

所以可以把它记成：

- Agent 是执行者
- Harness 是运行环境

## 2. 这个项目里，Harness 分成哪几层

### 入口层

用户请求从 CLI 进来。

入口文件：

- [`app/cli/main.py`](../../app/cli/main.py)

这一层负责：

- 收 prompt
- 选 provider
- 走权限判断
- 决定是本地 loop 还是委托外部 CLI

它就是这个 Harness 的控制台。

如果想理解“为什么系统会把 `好`、`ok`、`先做 PR1` 这种短输入补成更完整的内部任务，并在开始前回显下一步动作”，可以继续看：

- [`interaction-harness.md`](./interaction-harness.md)

### 执行层

真正干活的是单代理循环。

关键文件：

- [`app/agent/loop.py`](../../app/agent/loop.py)
- [`app/agent/planner.py`](../../app/agent/planner.py)
- [`app/agent/context_builder.py`](../../app/agent/context_builder.py)

这一层对应 Harness 的核心执行闭环：

`Context -> Plan -> Execute -> Verify -> Repair`

### 运行时层

这一层负责“真的去动手”。

关键文件：

- [`app/runtime/adapter_factory.py`](../../app/runtime/adapter_factory.py)
- [`app/runtime/ecc_adapter.py`](../../app/runtime/ecc_adapter.py)
- [`app/runtime/local_runtime.py`](../../app/runtime/local_runtime.py)
- [`app/runtime/cli_adapter.py`](../../app/runtime/cli_adapter.py)

这里就是 Harness 的 runtime/backends。

当前支持三种 provider：

- `local`
- `claude_code`
- `codex_cli`

它们现在分别代表：

- `local`：本地单循环
- `claude_code`：委托本机 `claude`
- `codex_cli`：委托本机 `codex`

### 约束层

Harness 不只是“能跑”，还要“别跑偏”。

关键文件：

- [`app/agent/policies.py`](../../app/agent/policies.py)
- [`scripts/check_architecture.py`](../../scripts/check_architecture.py)
- [`../../.github/workflows/harness-checks.yml`](../../.github/workflows/harness-checks.yml)

这层就是 Harness Engineering 里最关键的控制器。

它回答的是：

- 什么操作风险高
- 哪些命令要批准
- 哪些依赖边界不能越
- 哪些错误会直接阻断

### 验证层

Harness 要能自证，而不是只会产出。

关键位置：

- [`tests`](../../tests)
- [`scripts/agent_verify.sh`](../../scripts/agent_verify.sh)

`agent_verify.sh` 现在会：

- 建临时 worktree
- 同步当前工作区
- 安装项目
- 跑架构检查
- 跑测试

这就是 Harness 的 verify 环节。

### 恢复与记录层

Harness 不只要执行，还要会修、会记。

关键文件：

- [`app/superpowers/self_repair.py`](../../app/superpowers/self_repair.py)
- [`app/evals/replay.py`](../../app/evals/replay.py)
- [`logs`](../../logs)

这层对应：

- repair loop
- replay / trajectory
- postmortem 能力

## 3. 这个项目怎么对应 Harness 三层认知

最容易理解的方法就是按三层看。

### 信息层

让 Agent 看得懂项目。

现在项目里对应的是：

- [`AGENTS.md`](../../AGENTS.md)
- [`overview.md`](./overview.md)
- [`boundaries.md`](./boundaries.md)
- [`../conventions/README.md`](../conventions/README.md)
- [`../plans/current-sprint.md`](../plans/current-sprint.md)

这层解决的是：

Agent 去哪里找知识。

其中也包括一类很容易被忽略的知识：

- 当前轮输入是不是在续接上一轮任务
- 短输入应该如何被规范化成明确动作
- 启动回显什么时候该短、什么时候该详细

### 约束层

让 Agent 不得不按规则做。

现在对应的是：

- [`app/agent/policies.py`](../../app/agent/policies.py)
- [`scripts/check_architecture.py`](../../scripts/check_architecture.py)
- CI workflow
- git review / permission mode

这层解决的是：

Agent 什么能做，什么不能做。

### 自动化层

让 Agent 自己形成闭环。

现在对应的是：

- [`app/agent/loop.py`](../../app/agent/loop.py)
- [`app/superpowers/self_repair.py`](../../app/superpowers/self_repair.py)
- [`app/evals/replay.py`](../../app/evals/replay.py)
- [`scripts/agent_verify.sh`](../../scripts/agent_verify.sh)

这层解决的是：

Agent 做完后怎么自己验证、失败后怎么继续。

## 4. 这个项目最像 Harness 的地方

最像的不是“能调模型”，而是这些环节已经被串起来了：

- 有入口
- 有 runtime
- 有 policy
- 有 verify
- 有 repair
- 有 replay

也就是说，它已经不是：

`prompt -> 模型 -> 一段输出`

而是：

`prompt -> 环境判断 -> 执行 -> 验证 -> 修复 -> 留痕`

这就是 Harness 和普通 Agent demo 的本质区别。

## 5. 这个项目现在还缺什么

它已经是 Harness MVP，但还不是完整 Harness。

当前还缺的主要是：

- 上下文压缩
- 记忆系统
- hook / middleware 体系
- application legibility
- 浏览器
- DOM
- 日志
- 指标
- subagent 机制

所以更准确的定位是：

`Claude Code MVP` 内核版 Harness，而不是最终完整版。

## 6. 现在这个项目怎么用 Harness 视角去讲给别人

可以直接这样描述：

这个项目不是在做一个“会写代码的模型壳”，而是在做一个最小 Agent Harness。
它把开发请求接进来，用 CLI 作为入口，用 runtime 执行，用 policy 控边界，用 tests 和 worktree 做验证，用 repair 和 replay 做闭环。
它已经具备 Harness 的骨架：信息层、约束层、自动化层都在，只是高级能力还在继续补。

## 7. 最后一张最简图

可以把当前项目理解成这条链：

`用户请求`
-> [`app/cli/main.py`](../../app/cli/main.py)
-> `Permission Pipeline`
-> [`app/agent/loop.py`](../../app/agent/loop.py)
-> [`app/runtime`](../../app/runtime)
-> `Verify`
-> [`app/superpowers/self_repair.py`](../../app/superpowers/self_repair.py)
-> [`app/evals/replay.py`](../../app/evals/replay.py)

这条链本身，就是 Harness。
