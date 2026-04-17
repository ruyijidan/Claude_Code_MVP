# Roadmap

## 概览

这份路线图把 `Claude_Code_MVP` 当前的短板，整理成可执行的工程演进顺序。

目标不是一步做成“完整 Claude Code”，而是按 Harness 的真实杠杆顺序推进：

- 先补基础闭环的缺口
- 再补让系统更像成熟 coding agent 的能力
- 最后再补工业级 Harness 的厚度

## 当前定位

当前项目已经具备：

- CLI-first 入口
- 单代理执行 loop
- runtime abstraction
- delegated provider path
- permission pipeline
- verify / repair / replay
- worktree 验证
- git-aware workflow
- `.env` provider 配置
- Harness 文档体系

并且，第一波 harness hardening 已经完成：

- `completion contracts` 和 `verification gates` 已落地
- `scoped context selection` 已落地
- `failure classification` 和 `repair policy` 已落地
- `specs/workflows/`、`specs/templates/`、`specs/rules/` 已建立起资产层边界
- workflow 资产已经开始以轻量方式影响 planning / verification / repair

当前更准确的定位是：

`Claude_Code_MVP` 已经是完成第一波控制面加固的 Harness MVP，但还不是工业级 Harness。

## P0 / P1 / P2 方向速览

为了和 README 的学习主线保持一致，这里先给一份简化版方向，细节仍以各阶段内容为准。

### P0：控制面与安全面先做厚

- 增加 `context compression` 与 token 预算感知
- 补 `import / layer guardrails`，用明确层级规则 + CI 强制守卫
- 增加危险命令确认与路径约束，形成更细风险分级 + 稳定 `--show-permissions` 输出
- 增加结构化验证摘要（通过/失败/原因/风险级别）
- 让 replay / trace 能解释发生了什么、为什么失败、下一步怎么修
- 建立统一 tool registry / schema abstraction

### P1：让 Harness 更像真实可用的 coding agent

- 让 `context builder` 更智能：相关文件排序、git diff 感知、测试关联
- 把 `planner` 从规则式升级为模型辅助规划，带显式测试与风险计划
- 增强 `verifier`：不仅跑测试，还做完成度/边界/约束检查
- 引入轻量模板或 spec 层，让任务类型影响执行路径
- 做任务模式分层（quick edit vs. spec mode），避免单一 loop 解决所有任务

### P2：平台化与长周期能力

- 增加 session memory（短期/工作/长期 + 摘要）
- 增加 API / daemon 模式
- 增加 trajectory viewer / dashboard
- 增强 skills / hooks / middleware 资产体系
- 增加成本、缓存、隔离等工业级能力

## Harness Patterns 覆盖情况（对照 12 模式）

下表用来快速判断本项目对典型 Harness 模式的覆盖程度：`已有` / `部分` / `缺失`。

| 模式 | 覆盖情况 | 当前对应 |
|---|---|---|
| 持久指令文件（CLAUDE.md） | 部分 | `AGENTS.md` 与文档层，但缺少强制注入的持久指令层 |
| 作用域上下文组装 | 部分 | 已有 scoped context selection，但尚缺目录级规则与更动态的组装策略 |
| 分层内存（三层设计） | 缺失 | 仅有 replay 轨迹，没有短/工/长期记忆体系 |
| 梦境整合（AutoDream） | 缺失 | 暂无后台内存整理/压缩流程 |
| 渐进式上下文压缩 | 缺失 | 已在 P0 规划中（上下文压缩体系） |
| 探索→计划→执行循环 | 部分 | 有 planning/loop，但缺少严格阶段权限门控 |
| 并行工作流 | 缺失 | 当前为单代理 loop |
| 验证门 | 部分 | 有 policy + worktree verify，但未形成统一“破坏性操作前门控” |
| 最小权限范围 | 部分 | 风险分级存在，但未形成阶段式最小权限工具集 |
| 工具适配器层 | 已有 | `app/runtime` 适配器与 provider 抽象 |
| 无头批处理模式 | 部分 | 有 CLI + CI 验证脚本，但缺少专用 batch 运行模式 |
| 自愈循环 | 部分 | 已有 failure classifier + repair policy + replay，但恢复策略仍不是更完整的阶段化恢复系统 |

## P0：必须补的 Harness 基础层

这些能力最影响后续所有功能的上限，优先级最高。

### 1. 上下文压缩体系

目标：

- 避免多轮任务上下文无限膨胀
- 让长任务能稳定继续执行

需要补的点：

- token 预算感知
- 轻量裁剪策略
- 自动摘要压缩
- 超限时的紧急压缩回退

### 2. 更厚的权限与安全体系

目标：

- 把当前 permission pipeline 从 MVP 级提升到更可依赖的 Harness 控制层

需要补的点：

- 更细的命令风险分类
- 更完整的 allow / deny 规则层级
- 更细的高危命令检查
- 拒绝 / 熔断策略

### 3. 工具注册与 Schema 抽象

目标：

- 让工具扩展不再依赖零散手写接线

需要补的点：

- 统一 tool registry
- 声明式工具 schema
- 统一 tool error shape
- 更低边际成本的工具扩展模式

## P0 里程碑拆解

下面这三项是当前最适合直接进入实施的 P0 milestone。

### P0-1：上下文压缩基础版

目标：

- 给当前 loop 增加最小可用的上下文治理能力
- 避免随着任务轮次增长而无限膨胀

最小可交付物：

- 在 context / loop 路径里引入 token 预算感知
- 对超长 git 输出、文件内容、工具结果做轻量裁剪
- 增加一个本地摘要压缩入口，用于长内容降维
- 在 replay 中记录压缩是否发生

验收标准：

- 长输出不会原样无限注入后续上下文
- 裁剪策略可预测、可复现
- 有测试覆盖压缩触发和压缩后输出 shape
- 不改变现有 CLI 的对外用法

依赖关系：

- 可独立开始
- 完成后会直接降低后续记忆层和多轮任务的不稳定性

### P0-2：权限系统加厚

目标：

- 把当前 permission pipeline 从“基础风险判断”提升到“更像真实 Harness 的控制层”

最小可交付物：

- 命令风险分类更细
- 增加 allow / deny 决策层级
- 为高危操作加入更清晰的拒绝原因与推荐动作
- 为 delegated provider 和本地 loop 分别定义更明确的风险边界

验收标准：

- `--show-permissions` 输出能体现更细的分类和解释
- 高危命令与低危 inspection 的决策明显分离
- 权限判断结果有稳定 JSON shape
- 对现有测试补充更多命令与模式覆盖

依赖关系：

- 可与 P0-1 并行
- 完成后会为后续工具扩展和多 provider 接线提供稳定边界

### P0-3：工具注册 / Schema 基础版

目标：

- 把当前零散 runtime / tool 能力收敛成更统一的工具抽象

最小可交付物：

- 建立基础 tool registry
- 给现有核心能力定义统一 schema
- 统一工具返回结构与错误结构
- 让 CLI / loop 不再直接依赖零散工具拼接

建议优先纳入的能力：

- shell / command
- file read / write
- git inspection
- test runner

验收标准：

- 新工具可通过统一注册入口挂载
- 核心工具具备一致的输入 / 输出结构
- 错误返回不再是随意字符串拼接
- 至少有一组测试验证 registry 和 schema 的基本行为

依赖关系：

- 最好在 P0-2 开始后推进
- 后续记忆、模板层、外部信息接入都会依赖这层稳定抽象

## P1：让系统更像成熟 coding agent 的能力

这些能力会让项目从“能跑的 Harness”走向“更实用的 Harness”。

### 1. 记忆系统

目标：

- 让系统不只是 replay，而是真正能跨任务、跨会话积累稳定信息

需要补的点：

- 短期记忆
- 工作记忆
- 长期记忆
- 摘要记忆
- checkpoint 恢复

### 2. 工作流按复杂度分层

目标：

- 不同颗粒度任务走不同模式，而不是所有事都走同一个 loop

建议模式：

- quick edit mode
- template mode
- spec mode

### 3. 示范层 / 模板层

目标：

- 不只是告诉 AI 不能做什么，还告诉 AI 好结果长什么样

需要补的点：

- patterns / templates / skills
- 常见任务模板
- 标准输出锚点

### 4. 外部信息接入层

目标：

- 让 Agent 不只看到 repo 内信息

需要补的点：

- 文档接入
- API / schema 接入
- PRD / 设计稿接入
- 更完整的外部上下文入口

## P2：往工业级 Harness 靠拢的能力

这些能力不是现在最急，但会决定项目能否从 MVP 继续长成完整平台。

### 1. 流式执行与投机执行

目标：

- 降低用户感知延迟
- 让系统从“顺序执行”升级成“边想边做”

需要补的点：

- 流式工具调用
- 提前执行
- 写操作 overlay / speculative execution

### 2. 多 Agent 隔离模式

目标：

- 在复杂任务中引入并发协作，但保持上下文和代码修改隔离

建议方向：

- fork 模式
- teammate 模式
- worktree 模式

### 3. Application Legibility

目标：

- 让 Agent 不只看见 repo，还能看见应用运行后的世界

需要补的点：

- 浏览器接入
- DOM 读取
- 页面截图
- 日志查询
- 指标查询

### 4. 成本与缓存体系

目标：

- 让系统在真实使用中更可持续

需要补的点：

- 静态 / 动态 prompt 分离
- prompt cache 策略
- 工具按需加载
- 小模型 / 大模型路由

## 推荐推进顺序

建议按这个顺序做：

1. 上下文压缩
2. 权限系统加厚
3. 工具注册 / schema
4. 记忆系统
5. 工作流分层
6. 模板 / skills
7. 外部信息接入
8. 流式执行
9. 多 Agent 隔离
10. application legibility
11. 成本与缓存体系

## 一句话总结

`Claude_Code_MVP` 下一阶段最该补的，不是“更多 Agent”，而是：

- 更强的上下文治理
- 更厚的控制层
- 更标准化的工具层
- 更完整的记忆与信息层

这些补齐之后，再往流式执行、多 Agent、工业级成本优化推进，才是最稳的顺序。
