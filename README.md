# Claude Code MVP

[English Version](./README.en.md)

`Claude_Code_MVP` 是一个面向终端开发工作流的 Claude Code 风格 Agent Harness 学习型项目。

它围绕一条最小但完整的执行闭环展开：

`CLI -> Repo Context -> Plan -> Execute -> Verify -> Repair -> Replay`

它不是一个单纯“让模型帮你写代码”的 demo，也不是一个已经产品化的大型 Agent 平台。它更像一个学习 Harness、理解 Harness、并逐步把 Harness 工程化的最小起点。

## 什么是 Harness

如果只记一句话：

**Agent 是执行者，Harness 是运行环境。**

Harness 不是模型本身，而是模型外面那套让 Agent 真正可用的工程系统。它要解决的不是“模型会不会生成代码”，而是：

- 任务从哪里进入系统
- 上下文如何被组织
- 工具和运行时如何被调用
- 哪些操作可以做，哪些操作必须拦住
- 结果如何验证
- 失败之后如何修复
- 过程如何记录、回放和复盘

所以 Harness 的重点，从来不只是“产出一个答案”，而是把一次 Agent 执行变成一个完整闭环：

`Request -> Context -> Plan -> Execute -> Verify -> Repair -> Replay`

这也是普通 AI demo 和 Agent Harness 的核心区别。

普通 demo 更像：

`prompt -> model -> output`

Harness 更像：

`prompt -> environment -> policy -> execution -> verification -> recovery -> trace`

## 本项目主要做什么

这个项目的目标不是直接复刻完整 Claude Code 产品，而是先把 Claude Code 风格 Harness 里最关键的骨架做出来，作为一个最小可运行、可理解、可继续演进的学习基座。

当前它主要在做四件事：

- 提供一个 `CLI first` 的 coding agent 入口
- 把 repo-aware context、规划、执行、验证、修复串成单代理闭环
- 把 runtime、policy、verify、replay 这些 Harness 核心部件拆成清晰层次
- 把文档、约束脚本、测试和参考资料沉淀成可持续迭代的工程骨架

同时，项目现在也开始补一层更靠上的可复用资产表达：

- `specs/workflows/`：结构化工作流资产
- `specs/templates/`：可复用输出模板
- `specs/rules/`：可复用行为规则
- `docs/patterns/`：稳定的架构模式说明
- `docs/guides/`：面向贡献者的操作手册

从代码结构上看，它已经具备一个 Harness MVP 最关键的几层：

- 入口层：[`app/cli/main.py`](./app/cli/main.py)
- 执行层：[`app/agent/loop.py`](./app/agent/loop.py)、[`app/agent/context_builder.py`](./app/agent/context_builder.py)、[`app/agent/planner.py`](./app/agent/planner.py)
- 运行时层：[`app/runtime`](./app/runtime)
- 约束层：[`app/agent/policies.py`](./app/agent/policies.py)、[`scripts/check_architecture.py`](./scripts/check_architecture.py)
- 验证与修复层：[`scripts/agent_verify.sh`](./scripts/agent_verify.sh)、[`app/superpowers/self_repair.py`](./app/superpowers/self_repair.py)、[`app/evals/replay.py`](./app/evals/replay.py)

换句话说，这个仓库真正想帮助你理解的不是“某个模型怎么调”，而是：

**一个 coding agent 想真正可用，外围的 Harness 应该长什么样。**

## 怎么通过本项目学习 Harness

学习 Harness 最好的方式，不是先记定义，而是边读边对照这个仓库里的实际实现。

### 第一步：先建立 Harness 心智模型

建议先按这个顺序读：

1. [`README.md`](./README.md)：先建立整体认知
2. [`ARCHITECTURE.md`](./ARCHITECTURE.md)：看执行链路和系统分层
3. [`docs/README.md`](./docs/README.md)：看文档总导航和阅读路径
4. [`docs/architecture/harness-explained.md`](./docs/architecture/harness-explained.md)：看中文深度解释

这一轮的目标不是记 API，而是先回答三个问题：

- Harness 和 prompt wrapper 到底差在哪
- 为什么要有 policy / verify / replay
- 为什么一个 agent 项目不能只有“模型调用”

### 第二步：按层读代码，而不是按文件散读

推荐按这条路径来读：

1. 入口层：[`app/cli/main.py`](./app/cli/main.py)
2. 上下文与规划：[`app/agent/context_builder.py`](./app/agent/context_builder.py)、[`app/agent/planner.py`](./app/agent/planner.py)
3. 主循环：[`app/agent/loop.py`](./app/agent/loop.py)
4. 运行时：[`app/runtime/adapter_factory.py`](./app/runtime/adapter_factory.py)、[`app/runtime/local_runtime.py`](./app/runtime/local_runtime.py)、[`app/runtime/cli_adapter.py`](./app/runtime/cli_adapter.py)
5. 约束与验证：[`app/agent/policies.py`](./app/agent/policies.py)、[`scripts/check_architecture.py`](./scripts/check_architecture.py)、[`scripts/agent_verify.sh`](./scripts/agent_verify.sh)
6. 修复与留痕：[`app/superpowers/self_repair.py`](./app/superpowers/self_repair.py)、[`app/evals/replay.py`](./app/evals/replay.py)

这样读，你会更容易把代码映射回 Harness 的核心问题：

- 请求怎么进来
- 上下文怎么被构造
- 任务怎么被约束
- 执行怎么被抽象
- 结果怎么被验证
- 失败怎么被修复

读完这些代码层之后，如果你想进一步理解“怎样把这些能力沉淀成更可复用的上层资产”，可以继续看：

1. [`specs/workflows`](./specs/workflows)
2. [`specs/templates`](./specs/templates)
3. [`specs/rules`](./specs/rules)
4. [`docs/patterns`](./docs/patterns)
5. [`docs/guides`](./docs/guides)

推荐优先看：

- [`docs/patterns/workflow-layer.md`](./docs/patterns/workflow-layer.md)
- [`docs/patterns/asset-layer.md`](./docs/patterns/asset-layer.md)
- [`docs/guides/how-to-add-a-workflow.md`](./docs/guides/how-to-add-a-workflow.md)
- [`docs/guides/how-to-add-a-rule.md`](./docs/guides/how-to-add-a-rule.md)

### 第三步：直接跑起来，看闭环怎么工作

安装：

```bash
cd /data/ji/code/Claude_Code_MVP
pip install -e .
```

最小运行：

```bash
cd /data/ji/code/Claude_Code_MVP
cc "fix failing tests" --repo .
```

也可以直接运行模块入口：

```bash
cd /data/ji/code/Claude_Code_MVP
python3 -m app.cli.main "implement tool router" --repo . --json
```

如果你要走外部 provider CLI，也可以显式指定认证来源：

```bash
cd /data/ji/code/Claude_Code_MVP
python3 -m app.cli.main "Reply with exactly MODEL_OK" --repo . --provider claude_code --delegate-to-provider --auto-approve
python3 -m app.cli.main "Reply with exactly MODEL_OK" --repo . --provider claude_code --auth-source cli --delegate-to-provider --auto-approve
python3 -m app.cli.main "Reply with exactly MODEL_OK" --repo . --provider claude_code --auth-source env --delegate-to-provider --auto-approve
```

认证模式说明：

- `auto`：默认模式。`claude_code` / `codex_cli` 优先走本机 CLI 登录态，不导入项目 `.env` 里的 `ANTHROPIC_*`
- `cli`：显式强制走本机 CLI 登录态
- `env`：显式启用项目 `.env` 里的 `ANTHROPIC_*` 配置

推荐默认使用 `auto`。只有在你明确要让项目 `.env` 驱动外部 provider 时，再切到 `env`。

跑验证：

```bash
cd /data/ji/code/Claude_Code_MVP
python3 -m unittest discover -s tests
python3 -m app.cli.main --repo . --show-status
python3 -m app.cli.main --repo . --show-permissions
bash scripts/agent_verify.sh
```

当你真正跑过这些命令，再回头看代码，就会更容易理解 Harness 不是抽象概念，而是“入口、规则、执行、验证、修复”一起工作的系统。

### 发布前验收 / Pre-Release Acceptance

日常开发阶段，仓库主要依赖本地单元测试和 mocked integration tests 来保持反馈快速稳定。

但如果改动影响了真实 provider 执行路径，例如：

- `claude_code`
- `codex_cli`
- `anthropic_api`
- `glm5`
- auth loading
- delegated execution
- live prompt transport

那么在把工作视为“最终完成”之前，建议额外跑一轮 live provider 验收。

推荐最小清单：

```bash
cd /data/ji/code/Claude_Code_MVP
python3 -m unittest discover -s tests
bash scripts/agent_verify.sh
```

如果你想把发布前验收统一成一个入口，可以直接运行：

```bash
cd /data/ji/code/Claude_Code_MVP
bash scripts/release_acceptance.sh
```

如果要验真实 API provider：

```bash
cd /data/ji/code/Claude_Code_MVP
CC_RUN_LIVE_PROVIDER_TESTS=1 \
CC_LIVE_API_PROVIDER=glm5 \
ANTHROPIC_BASE_URL="https://your-endpoint" \
ANTHROPIC_AUTH_TOKEN="your-token" \
ANTHROPIC_MODEL="glm-5" \
python3 -m unittest tests.test_live_provider_integration
```

如果要验真实 delegated CLI provider：

```bash
cd /data/ji/code/Claude_Code_MVP
CC_RUN_LIVE_PROVIDER_TESTS=1 \
CC_LIVE_CLI_PROVIDER=claude_code \
python3 -m unittest tests.test_live_provider_integration
```

live 验收测试默认不会进入普通 `unittest discover`。它们的作用不是替代日常快测，而是确认：

- 真实凭证和认证路径可用
- 真实 provider 可达
- 最小 prompt 可以跑通
- Harness 的真实执行入口没有偏离预期

更完整的测试分层说明见 [`docs/conventions/testing.md`](./docs/conventions/testing.md)。

如果要把最终验收提升到更接近真实交付的级别，还可以开启一个最多 10 分钟、无需人工干预的 live acceptance task。推荐用于：

- `claude_code`
- `codex_cli`
- 其他支持 delegated prompt execution 的真实 provider 路径

示例：

```bash
cd /data/ji/code/Claude_Code_MVP
CC_RUN_LIVE_PROVIDER_TESTS=1 \
CC_RUN_LIVE_ACCEPTANCE_TASK=1 \
CC_LIVE_CLI_PROVIDER=claude_code \
CC_ACCEPTANCE_PROVIDER=claude_code \
CC_ACCEPTANCE_TIMEOUT_SECONDS=600 \
bash scripts/release_acceptance.sh
```

这个脚本会：

- 先跑默认本地验收
- 再跑 live provider integration tests
- 最后在一个临时仓库副本中执行一个 autonomous acceptance task

长任务的默认目标是让 provider 在临时副本里生成：

- `.claude-code/acceptance/final_acceptance_report.md`
- `.claude-code/acceptance/final_acceptance_report.json`

这样可以做到：

- 全程无需人工干预
- 最长运行约 10 分钟
- 不污染当前工作区
- 能留下可检查的真实验收产物

默认长任务 prompt 已经抽到模板文件里：

- [`specs/templates/acceptance-task-template.md`](./specs/templates/acceptance-task-template.md)

所以后续如果要调整验收任务目标，优先改模板，而不是直接改脚本。

长任务生成的 JSON 报告现在也有一个最小固定契约，详见：

- [`docs/design/acceptance-report.md`](./docs/design/acceptance-report.md)

`release_acceptance.sh` 会在长任务结束后校验：

- JSON 可解析
- 必需字段存在
- `acceptance_status` 必须是 `READY`、`NEEDS_REVIEW`、或 `BLOCKED`

### 第四步：把它当成对照样本，而不是标准答案

`Claude_Code_MVP` 现在是 Harness MVP，不是完整工业级实现。它更适合用来学习：

- 最小骨架应该有哪些层
- 各层之间怎么解耦
- 文档、脚本、测试如何一起构成控制面

它暂时还不是：

- 完整的多 Agent 平台
- 带长期 memory 的系统
- 带 UI / dashboard 的产品化控制面
- 完整工业级隔离与权限系统

所以更合适的学习方式是：

- 先用它理解骨架
- 再用外部参考理解更完整形态
- 最后回到本项目思考下一步该补什么

## 学习经验：怎么才能真正掌握 Harness

如果只是看概念文章，很容易觉得自己“懂了”；但 Harness 真正难的地方，是把概念变成工程闭环。

结合这个项目，更有效的学习方式通常是下面这些。

### 1. 不要把 Harness 理解成“多加几个 Agent”

很多人一开始会把 Harness 理解成角色系统、多 Agent 编排，或者一堆很炫的 tools。

但更本质的东西其实是：

- 入口有没有控制面
- 执行前有没有约束判断
- 执行后有没有验证
- 失败后能不能恢复
- 整个过程有没有留痕

先把这些基础层看明白，比先研究多 Agent 更重要。

### 2. 一定要把“文档层、约束层、自动化层”分开理解

掌握 Harness 的关键，不是会背定义，而是能分清三类东西各自解决什么问题：

- 文档层解决“Agent 去哪里找知识”
- 约束层解决“Agent 什么能做、什么不能做”
- 自动化层解决“Agent 如何形成稳定闭环”

只有把这三层拆开，后面做扩展时才不会把所有逻辑都堆进主循环。

### 3. 先学最小闭环，再学复杂能力

学习顺序最好是：

1. 先看 `CLI -> Context -> Plan -> Execute -> Verify -> Repair -> Replay`
2. 再看 provider 抽象、policy、worktree verify
3. 最后再去看 skills、memory、MCP、sub-agent 这些更复杂的演进方向

这样不容易一上来就被大而全的系统吓住。

### 4. 一边看源码，一边亲手跑验证

Harness 这种东西只看代码很难真正吃透，因为很多关键价值体现在“执行时行为”里。

所以建议你边读边跑：

- `python3 -m unittest discover -s tests`
- `python3 -m app.cli.main --repo . --show-status`
- `python3 -m app.cli.main --repo . --show-permissions`
- `bash scripts/agent_verify.sh`

你会更直观地理解：

- policy 为什么存在
- verify 为什么重要
- worktree 检查为什么是 Harness 的一部分

### 5. 用外部参考补足“更完整形态”的想象力

这个项目适合帮你理解骨架；更完整的演进方向，可以结合这些参考一起看：

- [`claude-code-book`](https://github.com/lintsinghua/claude-code-book/tree/main)：这是一个面向 Claude Code / Agent Harness 架构的中文深度分析仓库。它不是本项目依赖，但对理解本项目的设计方向、权限管线、对话循环、上下文系统和 Harness 心智模型很有帮助。
- [`claw-code`](https://github.com/ultraworkers/claw-code/tree/main)：这是一个面向 CLI Agent Harness 的开源实现参考。它不是本项目依赖，但对理解产品化 CLI 结构、文档分层、仓库表达方式和 runtime surface 的组织很有帮助。
- [`hermes-agent`](https://github.com/nousresearch/hermes-agent)：这是一个更完整、更产品化的 Agent Harness 参考。它不是本项目依赖，但适合用来理解 skills、memory、toolsets、MCP、多入口产品形态等后续演进方向。项目内整理说明见 [`docs/reference/hermes-agent.md`](./docs/reference/hermes-agent.md)。
- [`DeerFlow 2.0`](https://github.com/bytedance/deer-flow)：这是一个从 Deep Research 框架演进为 Super Agent Harness 的代表性参考。它不是本项目依赖，但非常适合用来理解 skills、sandbox、middleware、sub-agent、long-horizon agent，以及我们当前和更完整 Harness 之间的差距。项目内整理说明见 [`docs/reference/deer-flow.md`](./docs/reference/deer-flow.md)。
- [`everything-claude-code`](https://github.com/affaan-m/everything-claude-code)：这是一个把 skills、hooks、rules、commands、memory、MCP 等增强层资产打包在一起的 Harness 增强系统。它不是本项目依赖，但非常适合用来理解未来如何把工程资产组织成可安装、可组合、可扩展的增强层。项目内整理说明见 [`docs/reference/everything-claude-code.md`](./docs/reference/everything-claude-code.md)。
- `Claude Code 源码工程分析`：这是对 Claude Code 工业级实现的一类工程视角总结，适合用来理解上下文压缩、权限系统、记忆体系、流式执行、多 Agent 隔离，以及我们当前项目的短板。项目内整理说明见 [`docs/reference/claude-code-source-leak.md`](./docs/reference/claude-code-source-leak.md)。
- `得物 Spec Coding 实战`：这是一个非常有代表性的 Claude Code + Spec Coding 一线实战复盘。它不是本项目依赖，但对理解规则层、示范层、视觉层、MCP 和 AI 失效模式非常有帮助。项目内整理说明见 [`docs/reference/dewu-spec-coding.md`](./docs/reference/dewu-spec-coding.md)。
- [`docs/reference/README.md`](./docs/reference/README.md)：如果你想看项目内整理好的总索引、阅读顺序和能力映射表，可以从这里继续展开。

最好的方法不是把外部项目照搬进来，而是带着问题去看：

- 它多了哪一层
- 它为什么需要这一层
- 这一层在我们当前项目里应该以什么最小形态出现

## 推荐阅读顺序

如果你是第一次系统学习 Harness，推荐顺序是：

1. [`README.md`](./README.md)：先知道要学什么
2. [`ARCHITECTURE.md`](./ARCHITECTURE.md)：看系统主链路
3. [`docs/architecture/harness-explained.md`](./docs/architecture/harness-explained.md)：建立中文心智模型
4. [`AGENTS.md`](./AGENTS.md)：理解仓库导航与规则入口
5. [`docs/architecture/boundaries.md`](./docs/architecture/boundaries.md)：理解边界为什么重要
6. [`docs/plans/current-sprint.md`](./docs/plans/current-sprint.md)：理解项目下一步要补什么
7. [`docs/reference/README.md`](./docs/reference/README.md)：扩展到更完整的 Harness 参考

## 当前状态：已经做到哪一步

如果只看当前仓库状态，而不是最早期目标，这个项目已经不只是“能跑起来的单 loop MVP”了。

第一波 harness hardening 已经完成，当前仓库已经具备：

- `completion contracts` 和 `verification gates`
- `scoped context selection`
- `failure classification` 和 `repair policy`
- `specs/workflows/`、`specs/templates/`、`specs/rules/` 这一层可复用资产边界
- `scripts/agent_verify.sh` 提供的 worktree-based verification

这意味着它现在更准确的定位是：

- 一个已经完成第一波控制面加固的 Harness MVP
- 一个开始进入 asset-driven harness 阶段的学习与演进基座

## 下一步：P0 / P1 / P2 应该补什么

如果把“做好 Harness”拆成三阶段，这个项目下一步的重点可以这样理解。

### P0：控制面与安全面先做厚

这一层不是追求更多能力，而是让系统更可控、更可信：

- 增加 `context compression` 与 token 预算感知，避免长任务上下文失控
- 补 `import / layer guardrails`，用明确层级规则 + CI 强制守卫
- 增加危险命令确认与路径约束，形成更细风险分级 + 稳定 `--show-permissions` 输出
- 增加结构化验证摘要（通过/失败/原因/风险级别）
- 让 replay / trace 能解释发生了什么、为什么失败、下一步怎么修
- 建立更统一的工具注册与 schema 抽象，降低后续扩展成本

### P1：让 Harness 更像真实可用的 coding agent

这一层要让 Harness 更懂任务、更懂上下文：

- 让 `context builder` 更智能：相关文件排序、git diff 感知、测试关联
- 把 `planner` 从规则式升级为模型辅助规划，带显式测试与风险计划
- 增强 `verifier`：不仅跑测试，还做完成度/边界/约束检查
- 引入轻量模板或 spec 层，让任务类型影响执行路径
- 做任务模式分层（quick edit vs. spec mode），避免单一 loop 解决所有任务

### P2：平台化与长周期能力

这一层是“从 MVP 走向工业级 Harness”的能力补齐：

- 增加 session memory（短期/工作/长期 + 摘要）
- 增加 API / daemon 模式
- 增加 trajectory viewer / dashboard
- 增加 application legibility：浏览器、DOM、截图、日志、指标读取
- 增强 skills / hooks / middleware 资产体系
- 增加成本、缓存、隔离等工业级能力

更细的拆解可以直接看 [`ROADMAP.md`](./ROADMAP.md) 和 [`docs/plans/current-sprint.md`](./docs/plans/current-sprint.md)。

## 仓库信息

- GitHub: [ruyijidan/Claude_Code_MVP](https://github.com/ruyijidan/Claude_Code_MVP)
- Git remote: `git@github.com:ruyijidan/Claude_Code_MVP.git`
