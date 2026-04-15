---
last_updated: 2026-04-10
status: active
owner: core
---

# Hermes Agent Reference

## 仓库链接

- GitHub: `https://github.com/nousresearch/hermes-agent`

## 这份文档的用途

这不是本项目的实现文档，而是一份外部参考说明。

它的作用是回答两个问题：

- `hermes-agent` 值得我们看什么
- 它和 `Claude_Code_MVP` 当前处于什么关系

## 一句话定位

`hermes-agent` 更像一个更完整、更产品化的 Harness 平台；`Claude_Code_MVP` 更像一个更小、更聚焦 coding workflow 的 Harness MVP 内核。

## Hermes Agent 值得关注的点

基于其 GitHub 仓库首页和 README，可以重点关注这些能力：

- 既有终端入口，也有 messaging gateway
- 有更厚的 tools / toolsets 抽象
- 有 skills 系统
- 有 memory
- 有 MCP integration
- 有 cron / scheduled tasks
- 有更丰富的 terminal backends

这说明它不只是一个 coding CLI，而是一个更完整的 Agent Harness 产品面。

## 和本项目的差异

### 我们已经有的

`Claude_Code_MVP` 现在已经具备：

- CLI 入口
- 单代理 loop
- runtime abstraction
- permission pipeline
- verify / repair / replay
- worktree 验证
- `.env` provider 配置
- Harness 架构文档

### Hermes 更完整的

相较之下，`hermes-agent` 更接近成熟 Harness 平台，尤其体现在：

- messaging gateway
- richer tool and toolset system
- skills system
- persistent memory
- context compression
- MCP integration
- scheduling / cron tasks
- 多 backend 执行环境

## 对我们的启发

如果从工程演进角度看，`hermes-agent` 对我们最有参考价值的点有三类：

### 1. 技能与记忆

这部分对应我们未来还没补上的：

- memory system
- skills system
- context growth management

### 2. 更厚的工具与运行时抽象

这部分对应我们未来可能继续演进的：

- tool registry
- toolsets
- 多 execution backends
- richer runtime surface

### 3. 多入口产品形态

这部分对应我们从当前 CLI-first MVP 继续往上长之后可能出现的方向：

- 不只终端入口
- 也可能有 messaging / gateway / remote control 入口

## 对本项目的结论

如果要用一句话说明两者关系，可以这样说：

`Claude_Code_MVP` 适合讲清 Harness 的基本骨架；
`hermes-agent` 适合参考当 Harness 长成完整产品后会是什么样。

## 推荐阅读方式

阅读顺序建议是：

1. 先看 [`README.md`](../../README.md)，理解本项目定位
2. 再看 [`ARCHITECTURE.md`](../../ARCHITECTURE.md)，理解本项目骨架
3. 再把 `hermes-agent` 当作“下一阶段产品形态参考”去看

这样不会把本项目和外部参考混在一起。

## 说明

这份总结基于 `2026-04-10` 对 `https://github.com/nousresearch/hermes-agent` 的仓库首页与 README 的阅读。
它是架构参考说明，不是逐行源码分析，也不是兼容性承诺。
