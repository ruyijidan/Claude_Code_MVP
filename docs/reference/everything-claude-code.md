---
last_updated: 2026-04-10
status: active
owner: core
---

# Everything Claude Code Reference

## 参考仓库

- GitHub: `https://github.com/affaan-m/everything-claude-code`

## 一句话总结

`everything-claude-code` 不是单一工具，而是一个把 skills、rules、hooks、memory、MCP、agents、commands 全部打包在一起的 Agent Harness 增强系统。

## 它到底是什么

如果用一句话定位：

它更像一个“通用 Harness 增强包”，而不是一个单独的 coding agent。

从其 README 和目录结构来看，核心特点包括：

- `skills`
- `rules`
- `hooks`
- `memory / contexts`
- `agents`
- `commands`
- `mcp-configs`
- `schemas`

这意味着它不是只在某一个层面优化，而是在多个层面同时强化 Agent Harness。

## 和 Superpowers / gstack 的区别

如果放在同一个坐标系里看：

- Superpowers：更像工程工作流强化器
- gstack：更像组织角色系统
- everything-claude-code：更像全家桶式 Harness 增强层

也就是说，ECC 更关注：

给现有 Agent 平台装上一整套通用增强能力，而不是只强调某一个 workflow 或角色体系。

## 最值得关注的点

### 1. Skills 组织方式

ECC 对 skills 的组织非常完整。

这给我们的启发是：

- 技能不只是 prompt
- 技能可以和 hooks / rules / commands / MCP 联动
- 技能层可以成为 Harness 的正式扩展面

### 2. Hooks 体系

ECC 很强调 hooks。

这点对我们很重要，因为我们当前已经有：

- permission pipeline
- env loading
- verify
- replay
- repair

但这些能力还没有统一成 hook / middleware 插槽。

### 3. Rules + Commands + Agents 的分层组织

ECC 把系统资产分成：

- `rules/`
- `commands/`
- `agents/`
- `contexts/`
- `schemas/`

这说明它不是只把能力堆在 README 里，而是做了明确的工程资产分层。

### 4. MCP 配置作为正式子系统

ECC 里有 `mcp-configs/`，说明它把外部工具接入视为基础能力，而不是补充功能。

这对我们非常有启发，因为我们当前还没有真正把 MCP 层做成正式子系统。

## 和 `Claude_Code_MVP` 的关系

如果用一句话描述两者关系：

`everything-claude-code` 更像一个“给别的 Agent 平台加能力”的增强包；
`Claude_Code_MVP` 更像一个“自己实现运行时骨架”的最小 Harness 内核。

这两条路线并不冲突，反而互补。

## 它对我们最可用的借鉴点

如果只挑最值得借的 4 个点，我会选：

### 1. `skills/` 层

我们未来很适合引入自己的技能目录和技能资产组织方式。

### 2. hooks / middleware 插槽

把系统级行为统一挂到可扩展插槽，而不是分散在多个入口。

### 3. command / agent / context / schema 分层

让“工程资产”有稳定位置，而不是把所有能力写死在 loop 或 CLI 里。

### 4. `mcp-configs/` 作为正式目录

这可以成为我们未来外部信息接入和工具接入层的自然落点。

## 当前我们明显缺少的对应层

如果用 ECC 来照我们当前项目，最明显的缺口是：

### 1. 缺统一的 skills 层

- 没有 `skills/`
- 没有技能发现与组织方式
- 没有技能和 workflow 的正式耦合层

### 2. 缺 hooks / middleware 框架

- 系统能力还没有统一成标准插槽

### 3. 缺 commands / agent assets 层

- 目前有 CLI，但还没有成体系的 command assets / agent assets

### 4. 缺 MCP 作为正式子系统

- 目前还没有 `mcp-configs/` 或正式 MCP 子系统

## 对我们的启发

ECC 提醒我们，一个成熟 Harness 项目不只是“代码能跑”，还要有：

- 可复用的技能资产
- 可安装的增强层
- 可组合的 commands / hooks / rules / schemas
- 更清晰的外部工具接入组织方式

这对我们后续从 MVP 继续往上长，很重要。

## 现在不要急着全量照搬的部分

虽然 ECC 很强，但当前阶段并不适合我们直接照搬整套：

- 不要一开始就做太重的全家桶增强包
- 不要在基础控制层还不够厚时就铺太多 agent assets
- 不要为了“目录齐全”而过早引入过多跨平台兼容层

当前更合理的顺序还是：

- 先把内核骨架做厚
- 再逐步把 skills / hooks / commands / MCP 这些层抽出来

## 对本项目的结论

ECC 最值得我们学的，不是某个单点能力，而是：

一个成熟 Harness 项目最终会拥有一整套可复用、可安装、可扩展的工程资产。

`Claude_Code_MVP` 现在还在内核骨架阶段；
而 ECC 展示的是未来“增强层生态化”可能长成什么样。

## 推荐搭配阅读

建议这样看：

1. [`../../README.md`](../../README.md)
2. [`../../ARCHITECTURE.md`](../../ARCHITECTURE.md)
3. [`../architecture/harness-explained.md`](../architecture/harness-explained.md)
4. [`deer-flow.md`](./deer-flow.md)
5. 本文档

这样能先理解本项目，再用 ECC 作为“增强层导向”的参考物来观察差距。
