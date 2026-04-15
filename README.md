# Claude Code MVP

[English Version](./README.en.md)

仓库地址：
- GitHub: `https://github.com/ruyijidan/Claude_Code_MVP`
- Git remote: `git@github.com:ruyijidan/Claude_Code_MVP.git`

外部参考：
- `claude-code-book`: `https://github.com/lintsinghua/claude-code-book/tree/main`
  说明：这是一个面向 Claude Code / Agent Harness 架构的中文深度分析仓库。它不是本项目依赖，但对理解本项目的设计方向、权限管线、对话循环、上下文系统和 Harness 心智模型很有帮助。
- `claw-code`: `https://github.com/ultraworkers/claw-code/tree/main`
  说明：这是一个面向 CLI Agent Harness 的开源实现参考。它不是本项目依赖，但对理解产品化 CLI 结构、文档分层、仓库表达方式和 runtime surface 的组织很有帮助。
- `hermes-agent`: `https://github.com/nousresearch/hermes-agent`
  说明：这是一个更完整、更产品化的 Agent Harness 参考。它不是本项目依赖，但适合用来理解 skills、memory、toolsets、MCP、多入口产品形态等后续演进方向。项目内整理说明见 [`docs/reference/hermes-agent.md`](./docs/reference/hermes-agent.md)。
- `DeerFlow 2.0`
  说明：这是一个从 Deep Research 框架演进为 Super Agent Harness 的代表性参考。它不是本项目依赖，但非常适合用来理解 skills、sandbox、middleware、sub-agent、long-horizon agent，以及我们当前和更完整 Harness 之间的差距。项目内整理说明见 [`docs/reference/deer-flow.md`](./docs/reference/deer-flow.md)。
- `everything-claude-code`
  说明：这是一个把 skills、hooks、rules、commands、memory、MCP 等增强层资产打包在一起的 Harness 增强系统。它不是本项目依赖，但非常适合用来理解未来如何把工程资产组织成可安装、可组合、可扩展的增强层。项目内整理说明见 [`docs/reference/everything-claude-code.md`](./docs/reference/everything-claude-code.md)。
- `Claude Code 源码工程分析`
  说明：这是对 Claude Code 工业级实现的一类工程视角总结，适合用来理解上下文压缩、权限系统、记忆体系、流式执行、多 Agent 隔离，以及我们当前项目的短板。项目内整理说明见 [`docs/reference/claude-code-source-leak.md`](./docs/reference/claude-code-source-leak.md)。
- `得物 Spec Coding 实战`
  说明：这是一个非常有代表性的 Claude Code + Spec Coding 一线实战复盘。它不是本项目依赖，但对理解规则层、示范层、视觉层、MCP 和 AI 失效模式非常有帮助。项目内整理说明见 [`docs/reference/dewu-spec-coding.md`](./docs/reference/dewu-spec-coding.md)。

一个面向终端开发工作流的 Claude Code MVP 仓库。

这版项目的目标不再是“多 Agent 研究骨架”，而是收敛成一个更接近真实 coding agent 的最小产品形态：

`CLI -> Repo Context -> Plan -> Execute -> Verify -> Repair -> Replay`

深入理解项目结构与 Harness 分层，优先阅读 [`ARCHITECTURE.md`](./ARCHITECTURE.md)。

文档分工可以这样理解：

- [`README.md`](./README.md)：首页压缩版，适合第一次快速理解项目
- [`ARCHITECTURE.md`](./ARCHITECTURE.md)：结构化架构版，适合理解系统怎么工作
- [`docs/architecture/harness-explained.md`](./docs/architecture/harness-explained.md)：中文讲透版，适合完整理解 Harness 视角
- [`ROADMAP.md`](./ROADMAP.md)：按 P0 / P1 / P2 整理的工程化短板与演进路线

外部参考可以这样快速对照：

- 想看工业级 Harness 缺了哪些厚度：[`docs/reference/claude-code-source-leak.md`](./docs/reference/claude-code-source-leak.md)
- 想看 skills / sandbox / middleware / sub-agent：[`docs/reference/deer-flow.md`](./docs/reference/deer-flow.md)
- 想看产品化 Harness 长什么样：[`docs/reference/hermes-agent.md`](./docs/reference/hermes-agent.md)
- 想看 Spec Coding 在真实项目里怎么落地：[`docs/reference/dewu-spec-coding.md`](./docs/reference/dewu-spec-coding.md)
- 想看完整能力映射表：[`docs/reference/README.md`](./docs/reference/README.md)

## 如果用 Claude Code 来开发，最推荐怎么组合

如果先给一句最短建议：

- `Claude Code`：当执行器
- `Superpowers`：当工程流程层
- `gstack`：当高层决策 / 角色评审层
- `DeerFlow`：当未来平台化时的运行时蓝图
- `everything-claude-code`：当增强资产仓库参考

### 最推荐的落地顺序

对于个人或小团队，最稳的组合是：

- 先用 `Claude Code + Superpowers`
- 做 Web 产品时再叠 `gstack`
- 做平台化时参考 `DeerFlow`
- 做团队资产沉淀时参考 `everything-claude-code`

### 每个东西分别怎么用

#### 1. Claude Code：执行器

最适合干这些事：

- 读代码
- 改代码
- 跑命令
- 跑测试
- 修 bug
- 做 refactor

把它当成真正动手的 coding agent，而不是全流程方法论本身。

#### 2. Superpowers：流程层

最适合补 Claude Code 的短板：

- brainstorming
- writing plans
- TDD
- task decomposition
- code review
- finish branch

它最适合用来让 Agent 少跳步骤、实现更规整、流程更有工程纪律。

#### 3. gstack：决策层

最适合在“写之前”和“交付前”介入。

它更擅长：

- 产品视角 review
- 工程视角 review
- 设计视角 review
- QA / browse
- ship / retro

如果你做的是 Web 应用、管理后台、SaaS 产品，它会特别有价值。

#### 4. DeerFlow：平台化蓝图

它不太适合直接拿来替代 Claude Code 写代码，更适合回答：

如果以后要把自己的 agent 系统做成平台，架构应该往哪长？

最值得借的是：

- skills
- middleware
- sandbox
- sub-agent
- long-horizon runtime

#### 5. everything-claude-code：增强资产仓库

它更像一个“全家桶式 Harness 增强包”。

最值得借的是：

- `skills/`
- `hooks/`
- `commands/`
- `mcp-configs/`
- `schemas/`

它适合拿来参考“未来如何把工程资产组织成可安装、可复用、可扩展的增强层”。

### 最推荐的实际工作流

#### 小需求

例如：

- 改文案
- 修显隐逻辑
- 改一个接口字段
- 修一个小 bug

建议：

- 直接用 Claude Code
- 必要时加 Superpowers 的轻量 plan

#### 中等需求

例如：

- 一个 CRUD 页面
- 一个标准模块
- 一次中型 refactor

建议：

1. Superpowers 做 brainstorming + planning
2. Claude Code 执行
3. Claude Code 跑测试
4. gstack `/review`
5. 如果是 Web，再 `/qa`

#### 大需求

例如：

- 复杂功能模块
- 核心流程重构
- 多页面 / 多接口 / 多角色协作

建议：

1. gstack 做高层评审
2. Superpowers 做详细执行 plan
3. Claude Code 按 plan 实现
4. Superpowers 保证测试 / review / finish
5. gstack 做 `/review` + `/qa` + `/ship`

### 如果只能先选一个增强层

- 更关注执行纪律、测试、计划、review：先选 `Superpowers`
- 更关注产品 / 设计 / 工程 / QA 多视角与浏览器验证：先选 `gstack`

### 对本项目最实用的结论

结合 `Claude_Code_MVP` 当前阶段，最合理的顺序是：

- 先借 `Superpowers` 的 workflow discipline
- 再借 `gstack` 的 role-based review / qa
- 用 `DeerFlow` 作为 skills / middleware / sandbox / sub-agent 的架构参考
- 用 `everything-claude-code` 作为 skills / hooks / rules / commands 的资产组织参考

一句话总结：

**Claude Code 负责执行，Superpowers 负责流程，gstack 负责判断，DeerFlow 负责未来蓝图，ECC 负责资产组织。**

## 现在这个项目是什么

它是一个 Claude Code 风格的 MVP 内核，强调：

- `CLI first`
- `single coding loop`
- `repo-aware context`
- `runtime / repair / replay` 可复用

它不是完整的 Claude Code 产品，也不是完整 infra 平台。目前更准确的定位是：

一个可以继续向真实 coding agent 演进的本地 MVP。

## 什么是 Harness，项目里怎么对应

可以把 Harness 理解成：**Agent 的运行环境，而不只是模型本身。**

它主要解决 5 件事：

- 任务从哪里进入系统
- 上下文如何组织
- 工具和执行器如何调用
- 哪些边界不能越过
- 做完后如何验证、修复、记录

在这个项目里，可以直接对应成下面这条链：

`用户请求`
-> [`app/cli/main.py`](./app/cli/main.py)
-> `Permission Pipeline`
-> [`app/agent/loop.py`](./app/agent/loop.py)
-> [`app/runtime`](./app/runtime)
-> `Verify`
-> [`app/superpowers/self_repair.py`](./app/superpowers/self_repair.py)
-> [`app/evals/replay.py`](./app/evals/replay.py)

如果按 Harness Engineering 的三层来理解，这个项目目前是这样的：

### 1. 信息层

让 Agent 看得懂项目。

对应文件：

- [`AGENTS.md`](./AGENTS.md)
- [`docs/architecture/overview.md`](./docs/architecture/overview.md)
- [`docs/architecture/boundaries.md`](./docs/architecture/boundaries.md)
- [`docs/conventions/README.md`](./docs/conventions/README.md)
- [`docs/plans/current-sprint.md`](./docs/plans/current-sprint.md)

这一层解决的是：**知识放在哪里，Agent 去哪里找。**

### 2. 约束层

让 Agent 不得不按规则来。

对应文件：

- [`app/agent/policies.py`](./app/agent/policies.py)
- [`scripts/check_architecture.py`](./scripts/check_architecture.py)
- [`scripts/agent_verify.sh`](./scripts/agent_verify.sh)
- [` .github/workflows/harness-checks.yml `](./.github/workflows/harness-checks.yml)

这一层解决的是：**什么能做，什么不能做，做错了如何被拦住。**

### 3. 自动化层

让 Agent 自己形成闭环。

对应文件：

- [`app/agent/loop.py`](./app/agent/loop.py)
- [`app/runtime/adapter_factory.py`](./app/runtime/adapter_factory.py)
- [`app/superpowers/self_repair.py`](./app/superpowers/self_repair.py)
- [`app/evals/replay.py`](./app/evals/replay.py)

这一层解决的是：**执行、验证、修复、留痕。**

一句话总结：

**这个项目不是一个“会写代码的 prompt 壳”，而是一个最小 Agent Harness。**
它已经具备 `入口 + runtime + policy + verify + repair + replay` 这些骨架，只是更高级的能力还在继续补。

## Harness 文档入口

如果你想从 Harness Engineering 的角度理解这个项目，优先看这些文件：

- [`README.md`](./README.md)
- [`ARCHITECTURE.md`](./ARCHITECTURE.md)
- [`AGENTS.md`](./AGENTS.md)
- [`docs/architecture/harness-explained.md`](./docs/architecture/harness-explained.md)
- [`docs/architecture/overview.md`](./docs/architecture/overview.md)
- [`docs/architecture/boundaries.md`](./docs/architecture/boundaries.md)
- [`docs/conventions/README.md`](./docs/conventions/README.md)
- [`docs/plans/current-sprint.md`](./docs/plans/current-sprint.md)

建议这样分工理解：

- [`README.md`](./README.md)：项目定位、快速启动、当前能力边界
- [`AGENTS.md`](./AGENTS.md)：Agent 导航入口和仓库工作规则
- [`ARCHITECTURE.md`](./ARCHITECTURE.md)：执行链路、Harness 分层和系统如何工作
- [`docs/architecture/harness-explained.md`](./docs/architecture/harness-explained.md)：一篇中文讲透版的 Harness 对照解读
- [`docs/`](./docs)：更细的架构规范、约束和计划信息

如果你想补 Claude Code / Agent Harness 的外部心智模型，推荐同时参考：

- `claude-code-book`: `https://github.com/lintsinghua/claude-code-book/tree/main`
- `claw-code`: `https://github.com/ultraworkers/claw-code/tree/main`

## 已有能力

### 1. CLI 入口

命令行入口在 [`app/cli/main.py`](./app/cli/main.py)。

安装后可以这样调用：

```bash
cc "fix failing tests"
cc "implement tool router" --repo /path/to/repo
cc "investigate intermittent failures" --json
```

支持的核心参数：

- `--repo`
- `--provider`
- `--task-type`
- `--json`
- `--auto-approve`
- `--dangerously-skip-confirmation`

### 2. 单代理主循环

主执行链路在 [`app/agent/loop.py`](./app/agent/loop.py)。

当前流程是：

1. 收集仓库上下文
2. 推断任务类型
3. 生成轻量计划
4. 执行代码修改
5. 跑测试并验证
6. 失败时进入 repair loop
7. 写入 replay 轨迹

### 3. Repo-aware Context

上下文构建在 [`app/agent/context_builder.py`](./app/agent/context_builder.py)。

当前会收集：

- 仓库路径
- 用户 prompt
- git 状态摘要
- 候选文件列表
- 是否存在 `tests/`

这一步是后续接真实模型前最关键的基础层之一。

### 4. Runtime / Repair / Replay

这几块保留并延续了原 starter repo 中最有价值的部分：

- runtime 工厂：[`app/runtime/adapter_factory.py`](./app/runtime/adapter_factory.py)
- 本地执行器：[`app/runtime/local_runtime.py`](./app/runtime/local_runtime.py)
- 文件/命令基础能力：[`app/runtime/ecc_adapter.py`](./app/runtime/ecc_adapter.py)
- git 摘要工具：[`app/runtime/git_tool.py`](./app/runtime/git_tool.py)
- repair：[`app/superpowers/self_repair.py`](./app/superpowers/self_repair.py)
- replay：[`app/evals/replay.py`](./app/evals/replay.py)

## 当前 provider 状态

目前 runtime provider 支持这些名字：

- `local`
- `claude_code`
- `codex_cli`

当前状态是：

- `local`：本地单循环执行路径
- `claude_code`：委托给本机 `claude` CLI
- `codex_cli`：委托给本机 `codex` CLI

也就是说，`claude_code` 和 `codex_cli` 已经有真实外部 CLI 委托路径。
是否能稳定运行，取决于本机的登录状态、API key、配置目录权限和网络环境。

## 任务类型

当前保留了少量 task contract，用于约束输出和 repair 行为：

- `implement_feature`
- `fix_bug`
- `write_tests`
- `investigate_issue`

这些定义位于 [`specs/tasks`](./specs/tasks)。

这里的 spec 已经降级为“约束层”，而不是整个产品的主入口。

## 快速开始

### 环境要求

- Python 3.10+

### Provider 配置（Anthropic 兼容）

项目现在会自动从仓库根目录的 [`.env`](./.env) 读取 provider 配置。
当前支持 `export KEY=value` 这种 shell 风格写法。

当前本地配置示例：

```bash
export ANTHROPIC_BASE_URL="https://llm-api.zego.cloud"
export ANTHROPIC_AUTH_TOKEN="<your-token>"
export ANTHROPIC_MODEL="glm-5"
```

说明：

- `ANTHROPIC_BASE_URL`：Anthropic 兼容服务地址
- `ANTHROPIC_AUTH_TOKEN`：认证令牌
- `ANTHROPIC_MODEL`：默认模型名

如果你要走 `claude_code` provider，可以直接用项目命令验证：

```bash
cd /data/ji/code/Claude_Code_MVP
python3 -m app.cli.main   --repo .   --provider claude_code   --delegate-to-provider   --auto-approve   --json   "Reply with exactly MODEL_OK"
```

预期：返回 `returncode: 0`，并且输出里包含 `MODEL_OK`。

### 开发运行

```bash
cd /data/ji/code/Claude_Code_MVP
python3 -m app.cli.main "fix failing tests" --repo .
python3 -m app.cli.main "implement tool router" --repo . --json
```

### 安装 CLI

```bash
cd /data/ji/code/Claude_Code_MVP
pip install -e .
cc "fix failing tests" --repo .
```

### 运行测试

```bash
cd /data/ji/code/Claude_Code_MVP
python3 -m unittest discover -s tests
```

### 快速验收

```bash
cd /data/ji/code/Claude_Code_MVP

python3 -m unittest discover -s tests

python3 -m app.cli.main --repo . --show-status
python3 -m app.cli.main --repo . --show-review
python3 -m app.cli.main --repo . --show-permissions

bash scripts/agent_verify.sh

python3 -m app.cli.main --repo . "summarize the current harness architecture"
```

### 验收检查

首次运行后，请确认下面几项都正常：

1. `python3 -m unittest discover -s tests`
   预期：测试执行完成，最后输出 `OK`

2. `python3 -m app.cli.main --repo . --show-status`
   预期：能输出当前分支和工作区状态

3. `python3 -m app.cli.main --repo . --show-review`
   预期：能输出 changed files、diff stats 和 review summary

4. `python3 -m app.cli.main --repo . --show-permissions`
   预期：能输出当前 permission mode、risk level、decision 和推荐 flag

5. `bash scripts/agent_verify.sh`
   预期：能创建临时 worktree，完成架构检查和测试，并在结束时自动清理

6. `python3 -m app.cli.main --repo . "summarize the current harness architecture"`
   预期：本地 loop 能返回结果，而不是直接报错退出

### 通过标准

当下面条件都满足时，可以认为本地 MVP 已成功跑通：

- 单元测试通过
- CLI 的 `--show-*` 命令可正常输出
- `scripts/agent_verify.sh` 可完整执行
- 本地 `local_loop` 可返回结果

### Worktree 验证

Harness 风格的本地验证脚本：

```bash
cd /data/ji/code/Claude_Code_MVP
bash scripts/agent_verify.sh
bash scripts/agent_verify.sh main
```

这个脚本会：

- 创建临时 git worktree
- 安装项目
- 运行架构边界检查
- 运行测试
- 自动清理临时 worktree

## 项目结构

```text
app/
├── agent/
│   ├── context_builder.py
│   ├── loop.py
│   ├── planner.py
│   └── policies.py
├── cli/
│   └── main.py
├── evals/
├── runtime/
├── superpowers/
└── tools/
```

关键目录说明：

- [`app/cli`](./app/cli)：终端入口
- [`app/agent`](./app/agent)：单代理主循环、上下文和策略
- [`app/runtime`](./app/runtime)：本地执行器与 provider 抽象
- [`app/superpowers`](./app/superpowers)：repair / retry
- [`app/evals`](./app/evals)：replay / scoring
- [`specs`](./specs)：保留的任务契约
- [`docs`](./docs)：Agent 可读的架构、规范和计划信息

## 与旧结构的关系

项目仍然保留了部分旧模块，例如：

- [`app/graph/executor.py`](./app/graph/executor.py)
- [`app/agents`](./app/agents)

但它们现在更偏兼容层和内部复用层，而不是产品主入口。

新的主入口是：

- [`app/cli/main.py`](./app/cli/main.py)
- [`app/agent/loop.py`](./app/agent/loop.py)

## 已验证内容

当前已验证：

- `python3 -m unittest discover -s tests`
- CLI 基础调用可运行
- 本地任务闭环可跑通

## 下一步建议

### P0

- 补 import / layer guardrails
- 增加危险命令确认与路径约束

### P1

- 让 context builder 更智能地筛相关文件
- 把 planner 从规则式升级成真实模型驱动
- 增强 verifier 的边界检查和约束检查

### P2

- 增加 session memory
- 增加 API / daemon 模式
- 增加 trajectory viewer / dashboard
