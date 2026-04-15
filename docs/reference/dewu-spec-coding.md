---
last_updated: 2026-04-10
status: active
owner: core
---

# Dewu Spec Coding Reference

## 文章来源

文章标题：

- `AI编程能力边界探索：基于 Claude Code 的 Spec Coding 项目实战｜得物技术`

这篇文章不是本项目的实现文档，而是一份非常值得参考的外部实战复盘。

## 一句话总结

这篇文章最重要的结论不是“Claude Code 很强”，而是：

AI Coding 的关键不在模型多强，而在于你有没有先把执行空间变成一个足够清晰、足够受约束、足够可验证的确定性空间。

## 文章核心观点

### 1. Spec Coding 的价值不是“写文档”，而是先消除不确定性

文章里把工作流拆成：

- proposal
- design
- specs
- tasks

真正的价值是：

- 先讲清楚 Why
- 先讲清楚 What
- 先讲清楚 How
- 先讲清楚 Done

这样 AI 执行时就不需要自己补目标。

### 2. 规范不能只有约束，还要有示范和视觉锚点

文章把规范体系分成三层：

- 约束层：rules
- 示范层：模板代码 / code-design
- 视觉层：HTML 设计稿 / UI 参考

这点非常关键。

AI 不只需要知道“不能做什么”，还需要知道“好结果长什么样”。

### 3. MCP 的价值是消除信息孤岛

文章里重点提到了两类断层：

- 接口文档断层
- PRD / 设计文档断层

一旦把这些信息通过工具直连进来，AI 的执行输入会完整很多，返工率会明显下降。

### 4. AI 更像“顶级执行者”，不是自带业务常识的专家

文章对 AI 的定位很准确：

- 极度服从
- 无限耐心
- 没有内部业务常识

所以真正重要的不是“让 AI 更努力”，而是让环境更清晰。

### 5. AI 的失效是结构性的

文章把失效模式归成三类：

- 规范真空
- 信息孤岛
- 任务目标模糊

这个框架很适合拿来审视任何 Agent Harness 项目。

## 和 `Claude_Code_MVP` 的关系

如果把这篇文章映射到本项目，可以这样理解：

这篇文章讲的是如何让 AI 在一个被定义好的空间里可靠执行；
而 `Claude_Code_MVP` 正在做的是这个空间的运行时骨架。

## 本项目已经做到的部分

`Claude_Code_MVP` 当前已经有这些基础骨架：

- CLI 入口
- runtime abstraction
- permission pipeline
- verify / repair / replay
- worktree 验证
- `.env` provider 配置
- Harness 架构文档

也就是说，我们已经有：

- 入口
- 执行器
- 控制器
- 验证回路
- 留痕系统

这和文章强调的方向是对齐的。

## 本项目还缺的部分

如果对照这篇文章，当前最明显的缺口不是模型，而是下面三层：

### 1. 示范层

文章里的 `.claude/code-design/` 很强，而我们现在还没有真正成型的模板 / pattern 库。

### 2. 外部信息接入层

文章里有 MCP 直连接口文档和飞书文档；
我们现在的信息层主要还是 repo 内知识，外部上下文接入还很弱。

### 3. 按复杂度分层的工作流

文章已经把需求颗粒度区分成：

- 小需求：直接对话
- 中需求：rules / skills 模板化
- 大需求：spec / SDD

而我们现在主要还是单一 loop，没有把这些模式区分成产品能力。

## 对我们的启发

如果只挑最值得吸收的 4 个点，我会选：

### 1. 从“规则”升级到“规则 + 模板 + 视觉锚点”

仅有约束还不够，后续需要让 AI 看到标准产出样子。

### 2. 把失效模式写进 Harness 设计

可以把文章总结的三类失败模式直接映射进我们的路线：

- 规范真空 -> 补 conventions / patterns
- 信息孤岛 -> 补 MCP / external context
- 目标模糊 -> 强化 plan / spec / proposal

### 3. 让开发者角色上移

这篇文章和 Harness Engineering 一样，都在强调：

开发者不会消失，但重心会从“写代码”转向“定义边界、搭建环境、维护确定性空间”。

### 4. 工作流要按任务颗粒度分层

未来的 Harness 不应该只有一种模式，而应该能支持：

- quick edit mode
- template mode
- spec mode

## 对本项目的结论

这篇文章不是在推翻我们现在的方向，反而是在验证：

`Claude_Code_MVP` 走 Harness 这条路是对的。

但它也提醒我们，下一阶段最该补的不是“更多 Agent”，而是：

- 规范体系更细
- 模板体系更强
- 外部信息接入更完整
- 工作流按复杂度分层

## 推荐搭配阅读

建议这样看：

1. [`README.md`](../../README.md)
2. [`ARCHITECTURE.md`](../../ARCHITECTURE.md)
3. [`../architecture/harness-explained.md`](../architecture/harness-explained.md)
4. 本文档

这样能先理解本项目，再理解这篇实战文章为什么对我们有参考价值。
