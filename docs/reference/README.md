---
last_updated: 2026-04-10
status: active
owner: core
---

# Reference

这个目录用于存放两类内容：

- 外部参考资料的项目内整理说明
- 与本项目架构方向相关的对照笔记

这些文档不是本项目依赖，也不是源码真相来源，而是帮助理解方向、能力边界和演进路径的阅读材料。

## 当前参考导航

### 1. Harness 心智模型

如果你想先理解“什么是 Claude Code / Agent Harness”，优先看：

- `claude-code-book`
  外部仓库：`https://github.com/lintsinghua/claude-code-book/tree/main`
  适合：理解对话循环、权限管线、上下文系统、Harness 心智模型

### 2. 产品形态与成熟 Harness 参考

如果你想理解“当 Harness 长成产品后会是什么样”，重点看：

- [`hermes-agent.md`](./hermes-agent.md)
  对应外部仓库：`https://github.com/nousresearch/hermes-agent`
  适合：skills、memory、toolsets、MCP、多入口产品形态

- [`deer-flow.md`](./deer-flow.md)
  对应外部仓库：`https://github.com/bytedance/deer-flow`
  适合：理解 skills、sandbox、middleware、sub-agent、long-horizon agent 运行时，以及我们当前与更完整 Harness 之间的差距

- [`everything-claude-code.md`](./everything-claude-code.md)
  对应外部仓库：`https://github.com/affaan-m/everything-claude-code`
  适合：理解 skills、hooks、rules、commands、MCP、schemas 等“增强层资产”如何被组织成一个可安装的 Harness 增强系统

- [`claude-code-source-leak.md`](./claude-code-source-leak.md)
  对应主题：Claude Code 工业级源码工程分析
  适合：理解上下文压缩、权限厚度、记忆体系、流式执行、多 Agent 隔离、成本控制，以及本项目当前短板

- `claw-code`
  外部仓库：`https://github.com/ultraworkers/claw-code/tree/main`
  适合：CLI 产品表面、文档分层、仓库表达方式

### 3. Spec Coding 实战方法论

如果你想理解“团队在真实项目里怎么把 AI Coding 工程化”，重点看：

- [`dewu-spec-coding.md`](./dewu-spec-coding.md)
  对应文章：`AI编程能力边界探索：基于 Claude Code 的 Spec Coding 项目实战｜得物技术`
  适合：理解规则层、示范层、视觉层、MCP、AI 失效模式、按需求颗粒度选择工作流

## 推荐阅读顺序

建议按这个顺序阅读：

1. 先看 [`../../README.md`](../../README.md)
   先理解 `Claude_Code_MVP` 自己是什么
2. 再看 [`../../ARCHITECTURE.md`](../../ARCHITECTURE.md)
   理解本项目的 Harness 骨架
3. 再看 [`../architecture/harness-explained.md`](../architecture/harness-explained.md)
   用中文完整理解 Harness 视角
4. 最后回到这个目录，看外部参考
   把外部项目和文章当成“下一阶段参考物”，而不是当前实现说明

## 当前已整理文档

- [`hermes-agent.md`](./hermes-agent.md)
- [`deer-flow.md`](./deer-flow.md)
- [`everything-claude-code.md`](./everything-claude-code.md)
- [`claude-code-source-leak.md`](./claude-code-source-leak.md)
- [`dewu-spec-coding.md`](./dewu-spec-coding.md)

## 能力映射表

下面这张表可以直接用来对照：

- 某篇外部参考主要在讲什么
- 它对应我们当前的哪类短板
- 它最接近 `ROADMAP` 里的哪一段

| 参考 | 主要价值 | 对应我们的短板 | 对应路线图 |
|---|---|---|---|
| `claude-code-book` | Harness 心智模型、对话循环、权限、上下文系统 | 角色与流程认知层不足 | `P0` 控制层、`P1` 工作流分层 |
| [`hermes-agent.md`](./hermes-agent.md) | 更完整的产品化 Harness 形态 | memory、skills、toolsets、多入口产品面 | `P1` 记忆系统、模板层、外部信息接入 |
| [`deer-flow.md`](./deer-flow.md) | skills、sandbox、middleware、sub-agent、long-horizon | skills 缺失、middleware 缺失、sandbox 缺失、state 偏轻 | `P1` 模板/skills、`P2` 多 Agent、`P2` application legibility |
| [`claude-code-source-leak.md`](./claude-code-source-leak.md) | 工业级 Harness 厚度 | 上下文压缩、记忆、流式执行、安全厚度、缓存成本 | `P0` 上下文压缩、权限系统、工具 schema；`P2` 流式执行、成本体系 |
| [`dewu-spec-coding.md`](./dewu-spec-coding.md) | Spec Coding 实战、规则层/示范层/视觉层、MCP | 模板层不足、外部信息断层、工作流颗粒度单一 | `P1` 工作流分层、模板层、外部信息接入 |

## 读完以后怎么用

如果你是按“下一步该补什么”来读，可以按这个路径：

1. 想补基础控制层：
   先看 [`claude-code-source-leak.md`](./claude-code-source-leak.md)
2. 想补模板、Spec、外部上下文：
   先看 [`dewu-spec-coding.md`](./dewu-spec-coding.md)
3. 想补 skills / middleware / sandbox：
   先看 [`deer-flow.md`](./deer-flow.md)
4. 想看成熟产品形态长什么样：
   先看 [`hermes-agent.md`](./hermes-agent.md)
