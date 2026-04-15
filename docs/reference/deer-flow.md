---
last_updated: 2026-04-10
status: active
owner: core
---

# DeerFlow 2.0 Reference

## 文章来源

主题：

- `DeerFlow 2.0：从 Deep Research 框架转向 Super Agent Harness`

参考仓库：

- GitHub: `https://github.com/bytedance/deer-flow`

这不是本项目的实现文档，而是一份外部架构参考说明。

## 一句话总结

DeerFlow 2.0 不再只是一个 Deep Research 工具，而是在做一个带 Skills、Sandbox、Sub-agent、Memory、Context Engineering 的 Super Agent Harness。

## 这篇文章最核心的观点

### 1. Harness 是 “batteries included” 的 Agent 运行时

文章把 Harness 定义成：

- 不只是框架
- 不只是抽象
- 而是把最佳实践内置进去的运行时

典型能力包括：

- planning
- compaction
- filesystem tools
- memory
- sub-agents
- starter prompts

### 2. Long-horizon Agent 的关键是持续运行与自主决策

文章强调，Long-horizon Agent 不再是“一次调用就结束”的模型接口，而是：

- 持续运行数分钟甚至数小时
- 在循环中不断自主决定下一步
- 更擅长产出高质量 first draft

### 3. Skills 是能力扩展单元

在 DeerFlow 2.0 里，Skill 是核心组织方式。

一个 Skill 通常由这些组成：

- `SKILL.md`
- 脚本
- 模板
- 辅助资源

并且按需加载，而不是一次性塞满上下文。

### 4. Sandbox 是一等公民

Agent 有自己的计算机、工作区、上传区和输出区。

这意味着它不只是“会调几个工具”，而是真正拥有长期执行环境。

### 5. 架构从固定多 Agent 图转向 Lead Agent + Middleware + Sub-agent

文章最有架构价值的地方在这里。

DeerFlow 2.0 不再把能力固化在多个角色节点和它们的边上，而是：

- 单一 Lead Agent
- 一条 Middleware 链
- 动态 Sub-agent

这使得扩展能力时，不需要改整张图，只需要补 Skill、Tool 或 Middleware。

## 和 `Claude_Code_MVP` 的关系

如果用一句话描述两者关系：

`Claude_Code_MVP` 更像一个聚焦 coding workflow 的 Harness MVP 内核；
DeerFlow 2.0 更像一个已经长出完整运行时厚度的通用 Super Agent Harness。

## DeerFlow 值得我们借的地方

### 1. Skills 体系

这是最值得借鉴的部分之一。

我们当前还没有真正的：

- `skills/`
- `SKILL.md`
- skill lazy loading
- 可插拔能力单元

而 DeerFlow 已经把能力扩展做成了第一层结构。

### 2. Middleware 体系

这对我们也非常重要。

DeerFlow 的每次 Agent 调用都经过中间件链，负责：

- 线程数据
- 上传文件
- 沙箱分配
- 摘要压缩
- 记忆更新
- 图像注入
- 子 Agent 限流
- 澄清拦截

这正是我们未来非常值得演进的一层。

### 3. 更完整的任务状态

DeerFlow 的状态不只是消息，还包括：

- sandbox
- thread_data
- title
- artifacts
- todos
- uploaded_files
- viewed_images

这给我们的启发是：

未来要把“消息状态”升级成“任务状态”。

### 4. Sandbox 一等公民

我们现在已经有 runtime 和 worktree verify，但还没有完整沙箱模型。

DeerFlow 在这方面提供了很好的参考：

- 本地 / Docker / K8s 多模式
- 统一虚拟路径
- 稳定的工作目录抽象

### 5. 动态 Sub-agent，而不是固定角色图

这点也非常重要。

DeerFlow 的方向说明：

如果未来要做多 Agent，最稳的路径不是先画很多固定角色节点，而是：

- 先有单 Lead Agent
- 再在需要时动态派出 Sub-agent

这和我们当前“单代理优先”的路线是兼容的。

## 哪些现在不要急着照搬

DeerFlow 很强，但并不是所有东西都适合我们现在马上照搬。

### 1. 不要一开始就做通用 Super Agent 平台

我们当前的定位还是 coding workflow Harness MVP，不是通用 super agent 平台。

### 2. 不要一开始就把能力做成过厚的多部署形态

例如：

- Local
- Docker
- Kubernetes

这些是后续可能的方向，但现在不是最急需的。

### 3. 不要过早做过多 Skill，而忽略底层控制层

如果没有稳定的：

- permission
- context management
- tool schema
- verify

Skill 只会把复杂性扩大。

## 我们当前最明显的差距

如果直接对照 DeerFlow 2.0，我们当前还明显缺这些层：

### 1. Skills 系统

- 没有 skill discovery
- 没有 `SKILL.md` 组织方式
- 没有按需加载的能力包

### 2. Middleware 层

- 没有统一中间件链
- 系统能力还分散在多个模块和入口里

### 3. 更完整的 ThreadState

- 当前状态模型仍然偏轻
- 还没有 artifacts / uploads / richer task state

### 4. 长期记忆

- 当前只有 replay / memory store 雏形
- 还没有跨会话长期记忆能力

### 5. Sandbox 一等公民

- 当前还没有完整的沙箱抽象

### 6. Long-horizon 工程厚度

- 当前更像“能跑任务”
- 还不像“能长期持续运行的 Agent”

## 对我们的启发

如果只挑最重要的 5 个点，我会选：

### 1. Skills 应该成为未来的重要扩展方向

不是把所有能力硬编码进 loop，而是逐步 skill 化。

### 2. Middleware 是必经之路

随着系统能力增加，不走 middleware 化，结构会越来越散。

### 3. 任务状态要逐步升级

未来应该从 prompt / repo context，演进到更完整的 task state。

### 4. 多 Agent 先走 Lead Agent + Sub-agent

这比一上来做固定复杂角色图更稳。

### 5. Sandbox 和外部执行环境值得进入路线图，但不用抢在最前面

它很重要，但应该排在 context、permission、tool schema 这些基础层之后。

## 对本项目的结论

DeerFlow 2.0 更像“下一阶段蓝图”。

它告诉我们：

- 一个 Harness 不只是 loop + tools
- 它最终会长成 skills + middleware + sandbox + memory + sub-agent + richer state 的系统

而 `Claude_Code_MVP` 当前最适合做的，是继续把内核骨架做厚，再逐步向这个方向演进。

## 推荐搭配阅读

建议这样看：

1. [`../../README.md`](../../README.md)
2. [`../../ARCHITECTURE.md`](../../ARCHITECTURE.md)
3. [`../architecture/harness-explained.md`](../architecture/harness-explained.md)
4. [`claude-code-source-leak.md`](./claude-code-source-leak.md)
5. 本文档

这样能先理解本项目，再用 DeerFlow 2.0 作为更完整 Harness 形态的参考。
