---
last_updated: 2026-05-15
status: final
owner: core
---

# 从 AI Coding Demo 到 Harness Engineering / From AI Coding Demo To Harness Engineering

**副标题 / Subtitle**

如何理解、搭建并评估一个真正可用的 coding harness

## 文章摘要 / Article Summary

这两年，大家已经看过太多 AI 写代码的演示。

一个 prompt 发出去，模型回一段代码，或者直接改几个文件，看起来很惊艳。  
如果再往前走一步，模型还能读仓库、跑命令、补测试，甚至给你一个“我已经完成”的总结。

第一次看到这类系统时，很多人的直觉都是：

“这不就是未来的软件开发方式吗？”

这个直觉并没有错。  
但一旦你真的开始把它接进工程流程，问题几乎总会立刻出现。

比如：

- 用户只说一句“继续”，系统到底应该继续什么
- 一个任务应该看多少上下文，哪些文件才是相关的
- 哪些命令可以直接执行，哪些操作必须被拦住
- 改完代码以后，什么才算真正完成
- 测试失败以后，是该自动修复、自动重试，还是停下来
- 过了两天再回来看，能不能知道上一次到底做了什么

这些问题和“模型会不会写代码”其实已经不是一回事。  
它们问的是：

**你有没有把模型放进一个可控、可验证、可复盘的工程系统里。**

这个工程系统，就是 harness。

这篇文章想讲清楚四件事：

1. Harness 到底是什么，和普通 AI coding demo 有什么本质区别
2. 一个最小可用 harness 应该包含哪些部件
3. 第一版 harness 应该按什么顺序搭起来
4. 怎样判断一个项目是真正在做 harness，而不只是堆 prompt、工具和规则

为了让这些概念不只停留在定义层，文章后半部分也会用一个真实样本工程来对照这些控制点在代码里通常长什么样。

---

## 一句话定义 / One-Sentence Definition

如果只记一句话：

> **Agent 是执行者，Harness 是运行环境。**

模型负责生成、判断、推理。  
Harness 负责把一次 AI 执行变成一个工程闭环。

普通 AI coding demo 更像这样：

`prompt -> model -> output`

一个最小可用 harness 更像这样：

`request -> context -> plan -> policy -> runtime -> verify -> repair -> replay`

两者的本质差别，不在于是否“调用了模型”，而在于是否具备以下能力：

- 接收并解释任务
- 在执行前施加约束
- 在执行后进行验证
- 在失败时进行恢复或停止
- 在结束后留下可回看的证据

因此，harness 的价值不在于“让模型更聪明”，而在于“让系统更可控”。

---

## 为什么很多 AI Coding 项目会卡在 Demo 阶段 / Why Many AI Coding Projects Stall At The Demo Stage

很多项目的早期演化路径都很像：

1. 先有一个 prompt
2. 再补一些 repo 文件
3. 再接入 shell 工具或文件修改能力
4. 最后开始堆更多规则、模板和例外逻辑

表面上看，系统能力越来越多。  
但真正进入工程环境后，结果往往没有随着复杂度同步变好，反而更难预测、更难验证、也更难复盘。

这通常不是因为模型不够强，而是因为系统一直停留在 demo 思维里。

所谓 demo 思维，就是默认下面这些问题都还可以继续交给 prompt 解决：

- 意图澄清
- 上下文选择
- 权限边界
- 风险判断
- 完成定义
- 失败恢复
- 运行记录

这会带来几个很典型的问题。

### 1. 行为不可预测 / Unpredictable Behavior

同一句用户输入，在不同模型、不同 prompt 版本、不同上下文残留条件下，可能触发完全不同的动作。

例如用户只说一句“继续”。

如果没有 harness 层，这句话通常会再次被当作自然语言交给模型推断。  
但一个真正的 harness 会先判断：

- 这是在继续上一轮任务，还是新任务
- 最近是否存在多个可能的续轮候选
- 当前是否必须先停下来澄清

这类判断属于交互控制，不属于语言生成。

### 2. 边界不清晰 / Fuzzy Boundaries

如果没有显式 policy，系统就会默认“模型懂了就可以做”。

但真实工程里，核心问题之一恰恰是：

> **什么可以做，什么不可以做。**

例如：

- 哪些命令可以直接执行
- 哪些文件写入需要确认
- 哪些网络行为必须被拦截
- 哪些 git 相关动作应该统一收敛到专门封装中

没有 harness 接管这些边界，能力越强，风险越高。

### 3. 没有完成定义 / No Real Definition Of Done

很多 demo 默认“模型说完成了”就是完成。  
但工程里的完成至少意味着：

- 目标文件确实发生了预期变化
- 相关测试确实被添加或更新
- 验证命令确实执行过
- 失败时能明确区分实现失败、环境失败还是瞬时失败

因此，verification 和 completion contract 必须属于 harness，而不能只属于提示词。

### 4. 没有复盘能力 / No Real Replay

如果系统没有 replay，就很难回答这些问题：

- 上一轮到底做了什么
- 为什么这次会继续那个任务
- 是 provider 暂时超时，还是实现本身错误
- 这次结果到底如何产生

没有 replay，调试和复盘都会退化成猜测。

---

## Harness 真正要解决的是什么 / What Harness Actually Solves

harness 不是 prompt 的扩展，也不是模型调用的壳。  
它真正解决的是“控制闭环”。

一个最小可用 harness，至少要覆盖以下八个问题：

### 1. 任务从哪里进来 / Task Intake

第一版通常是 CLI。  
成熟后也可能是 API、daemon、IDE extension 或 chat entrypoint。

关键不是入口形式，而是是否存在稳定控制面。

### 2. 上下文如何组织 / Context Assembly

不是把整个仓库都塞进去，而是构造一个有边界的、与当前任务相关的上下文。

### 3. 用户意图如何被解释 / Intent Normalization

用户说的是 bugfix、feature、investigation，还是单纯在继续上一轮任务。

### 4. 哪些行为允许执行 / Policy

这就是 policy 层。  
它至少应该能表达：

- `allow`
- `confirm`
- `deny`

### 5. 实际执行如何发生 / Runtime

这就是 runtime 层。  
它应该把本地执行、CLI delegation、API provider 等路径抽象开。

### 6. 结果如何验证 / Verification

完成不应只依赖模型自述，而应依赖测试、架构检查、产物检查、git 摘要或 acceptance 流程。

### 7. 失败之后如何处理 / Repair

重试、修复还是停止，应该有清晰的失败分类和停止条件。

### 8. 过程如何留痕 / Replay

系统需要保留足够的运行证据，用于 continuation、postmortem 和调试。

总结来说，harness 的关注点不是“生成更多”，而是“控制更多”。

---

## 一个最小可用 Harness 应该包含什么 / What The Smallest Useful Harness Should Include

如果目标是实现第一版，而不是复刻最终产品，那么一个最小可用 harness 通常只需要七个部件：

### 1. Entry

一个稳定的任务入口。  
最常见的第一版就是 CLI。

### 2. Context

一个能够构造 repo-aware 上下文的模块。  
至少应该知道：

- 当前仓库在哪里
- 当前 git 状态是什么
- 哪些文件可能相关
- 哪些 docs 应优先读取

### 3. Planning

一个很轻的任务分类和步骤生成器。  
第一版通常只需要分清：

- fix bug
- implement feature
- write tests
- investigate issue

### 4. Policy

一个在 runtime 之前做风险分类的控制点。

### 5. Runtime

一个负责文件修改、命令调用、git 操作和 provider delegation 的抽象层。

### 6. Verification And Repair

至少有一条 deterministic check。  
例如：

- unit tests
- 架构检查脚本
- lint

并在失败时有最基础的 repair or stop 逻辑。

### 7. Replay

哪怕只是最简单的 JSON 记录，也应该把一次 run 的关键信息存下来。

如果这七个部件都在，系统就已经不是演示，而是一个真实的第一版 harness。

> **第一版 harness 的目标不是“惊艳”，而是“可信”。**

---

## 搭建一个 Harness，最值得先抓什么 / What To Focus On First When Building A Harness

如果读完之后想自己做第一版 harness，最容易踩坑的地方不是“少了某个高级能力”，而是顺序错了。

更稳妥的做法，通常不是一开始就追求复杂度，而是先把最关键的几个控制点长出来。

### 先把入口立住，不要先堆 prompt

先把控制面立住：

- 命令怎么进来
- repo 怎么指定
- 输出怎么展示
- runtime 怎么选择

### 再做一个有边界的 context builder

第一版只要能提供：

- repo root
- git status summary
- candidate files
- 关键 docs

就已经足够有用。

### 然后做一个很轻的 planner

第一版 planner 不需要复杂计划，只要能稳定区分几个 task shape。

### 把 policy 放到 runtime 前面

这是从 demo 走向 harness 的关键一步。  
至少应该在执行前判断：

- file write risk
- command risk
- network risk
- git-facing behavior

### 尽早把验证接进来

第一版就应该选一条最稳定的验证路径。  
例如：

- 单元测试
- 架构检查脚本
- lint

### 给系统留一层很薄的 replay

哪怕只是一个 JSON 文件，也值得先做。  
至少记录：

- 原始 prompt
- task type
- 关键步骤
- verification 结果
- final status

### 最后再考虑更厚的资产层

当行为开始重复时，再引入：

- workflows
- rules
- templates

不要在第一版还没跑通的时候，就先设计一层很重的 workflow engine。

---

## 从 Prompt Wrapper 到 Harness 的演进路径 / The Evolution Path From Prompt Wrapper To Harness

很多团队在做 AI coding 时最大的困难，不是“看不懂概念”，而是“跨度太大”。

一边是极简 demo，一边是看起来像完整产品的平台，中间缺少分阶段成长的路径。

更稳的理解方式，是把它看成一条逐步增加控制点的演进链：

```
Stage 0
prompt -> model -> output

Stage 1
CLI -> model -> output

Stage 2
CLI -> context -> model -> output

Stage 3
CLI -> context -> plan -> runtime -> verification

Stage 4
CLI -> context -> plan -> policy -> runtime -> verification -> replay

Stage 5
CLI -> context -> plan -> policy -> runtime -> verification -> repair -> replay

Stage 6
CLI -> context -> plan -> policy -> workflow assets -> runtime -> verification -> repair -> replay
```

这条演进链说明了两件事：

1. harness 的成长方式，是增加控制点，而不是无限堆 prompt
2. 第一版做到 Stage 4 或 Stage 5，就已经是很强的结果

大多数团队真正卡住的原因，不是做不到，而是一下子想做得太像最终产品。

---

## 什么样的第一版，已经值得继续往下做 / What Counts As A Strong First Version

第一版不需要一步到位，但至少应该让人看到：这个系统已经不只是演示，而是有了真实控制闭环。

一个很实用的判断标准是：

1. 一条 CLI 命令可以稳定接收 prompt 和 repo
2. harness 能构造有边界的仓库上下文
3. 能识别至少一种任务形状并执行到底
4. 风险行为在执行前被分类
5. 自动跑一条验证命令
6. run 结束后写出 replay 记录
7. 有 4 到 6 个 focused tests 保护核心控制点

如果这七条都满足，做出来的已经不是演示，而是一个值得继续迭代的第一版 harness。

---

## 最容易踩的坑 / Common Pitfalls

### 坑一：把 prompt 当系统

如果所有行为变化都只能靠改 prompt 完成，说明 harness 边界还没建立起来。

### 坑二：让 CLI 越长越胖

CLI 应该负责 intake、routing、reporting，而不是慢慢变成 planning、git 逻辑、workflow 分支的堆放地。

### 坑三：上下文越多越好

上下文越多，不代表效果越好。  
很多时候，更多的是噪音，而不是信息。

### 坑四：把验证留到很后面

如果第一版没有 deterministic verification，很容易一直停留在“看起来像完成”。

### 坑五：过早做厚重编排

还没有清楚主闭环时，就先做很厚的 workflow engine、复杂 agent graph，通常会让系统更难调。

### 坑六：没有 failure typing

没有 failure typing 的 retry，很容易把系统做成一个礼貌但混乱的循环器。

### 坑七：没有 replay

没有 replay，很多问题只能靠猜，很多 continuation 也会变得不可靠。

---

## 如何快速评估一个 Harness 项目 / How To Quickly Evaluate A Harness Project

如果你不是自己从零开始搭，而是在看一个现成项目值不值得学习，最有效的方式不是先看它“功能多不多”，而是先看它有没有形成真实控制闭环。

### 第一层：它是不是在做真实 Harness / Is It Doing Real Harness Work

优先看这八件事是否存在：

1. 有没有稳定入口
2. 有没有 bounded context
3. 有没有任务解释层
4. 有没有显式 policy
5. 有没有 runtime abstraction
6. 有没有 verification
7. 有没有 repair decision
8. 有没有 replay

如果这八项里缺掉一半以上，它大概率还更接近 demo，而不是工程系统。

### 第二层：它是不是“只是个 demo” / Is It More Than A Demo

更可靠的判断方式，是看它有没有下面这些特征：

- 完成不是靠模型自述，而是靠外部验证
- 风险边界不是藏在 prompt 里，而是被独立控制
- 失败以后不是只能重试，而是能区分修复、重试和停止
- 做完以后不是只剩聊天记录，而是有可回看的结构化证据

### 第三层：工程边界是不是健康 / Are The Boundaries Healthy

即使一个项目已经开始做 harness，也不代表它的结构就是健康的。  
更进一步要看：

- CLI 有没有慢慢长成巨石
- git 相关能力有没有统一收敛
- 验证逻辑有没有独立成层
- 风险行为有没有显式分类
- 资产层有没有开始承接重复行为

### 第四层：哪些是 MVP 必需，哪些是后续增强 / MVP Essentials Vs Later Enhancements

MVP 必需通常包括：

- 稳定入口
- bounded context
- 明确 planning
- 显式 policy
- deterministic verification
- replay

后续增强通常包括：

- workflow assets
- rule assets
- template assets
- memory retrieval
- daemon / API surface
- multi-agent orchestration
- dashboard / cost / cache platform

也就是说，一个项目没有多代理，不代表它不成熟；  
但如果它连 verification 和 replay 都没有，那它大概率还停留在 demo 阶段。

需要特别说明的是：  
在 `Claude_Code_MVP` 这样的样本工程里，`memory retrieval`、`daemon / API surface`、`multi-agent orchestration` 这些方向已经出现了第一版实现，但它们仍然更适合被理解为 **MVP 之后的增强层**，而不是学习第一版 harness 时必须先做厚的部分。

### 一个实用的评估问题清单 / A Practical Evaluation Checklist

如果只想快速判断一个项目值不值得深入看，可以直接问这几个问题：

1. 任务是怎么进入系统的？
2. 上下文是怎么被选择和裁剪的？
3. 风险行为是怎么被分类的？
4. 完成是怎么被证明的？
5. 失败以后系统怎么决定下一步？
6. 一轮运行结束后留下了什么证据？
7. 这些控制点是代码结构的一部分，还是只靠 prompt 维持？

---

## 一条适合快节奏阅读的学习路径 / A Fast-Paced Learning Path

如果你没有很多时间，也依然可以用比较低的成本建立对 harness 的基本理解。

### 10 分钟

- 先读这篇文章
- 建立 `Agent` 和 `Harness` 的区别
- 明白为什么很多 AI coding 项目会停留在 demo 阶段

### 30 分钟

- 回看文章里的七个部件和演进路径
- 形成“一个 harness 最少要包含什么”的整体印象

### 1 小时

- 选择一个真实工程，顺着 `Entry -> Context -> Plan -> Policy -> Runtime -> Verify -> Replay` 走一遍关键路径
- 看清哪些能力属于模型，哪些能力属于 harness

### 2 小时

- 找一个很小的练习目标
- 尝试自己搭出一条最薄的闭环
- 或者对照一个现有工程，把关键控制点和实现位置标出来

这条路径的目标，不是一次学完所有细节，而是用尽可能低的时间成本，先把 harness 的核心骨架看清楚。

---

## 用一个真实项目对照 Harness 的落地形态 / How Harness Looks In A Real Project

只讲概念，很容易让 harness 一直停留在“好像懂了”的状态。

真正有帮助的，通常不是再补更多定义，而是看一个真实项目怎么把这些控制点拆成工程结构。

这里用的样本，是 `Claude_Code_MVP`。  
它之所以值得看，不是因为它功能最全，而是因为它刚好处在一个比较适合学习的位置：

- 已经有完整闭环
- 还没有厚到把骨架完全遮住

### 一个适合阅读的简化项目树 / A Reader-Friendly Simplified Project Tree

```
Claude_Code_MVP/
  app/
    cli/
      main.py                  # 入口，参数解析，运行模式选择
    agent/
      loop.py                  # 主控制闭环
      intent_clarifier.py      # 短输入、续轮、模糊输入澄清
      planner.py               # 任务形状识别与轻量规划
      policies.py              # allow / confirm / deny 风险控制
      verification_gates.py    # 验证门
      completion_contracts.py  # 完成定义
    runtime/
      adapter_factory.py       # 本地 / provider 运行时选择
      local_runtime.py         # 本地执行
      git_tool.py              # git 相关统一封装
    superpowers/
      failure_classifier.py    # 失败分类
      repair_policy.py         # 重试 / 修复 / 停止决策
    evals/
      replay.py                # 运行留痕与回放
  specs/
    workflows/                 # 工作流资产
    rules/                     # 规则资产
    templates/                 # 模板资产
  examples/
    harness-lab/               # 小练习靶子
```

只看这棵树，其实已经能看出一个比较典型的 harness 形状：

- `cli/` 负责把请求接进来
- `agent/` 负责控制闭环
- `runtime/` 负责真正执行
- `superpowers/` 负责失败恢复
- `evals/` 负责回放和复盘
- `specs/` 负责逐步把行为从硬编码迁移到资产层

为了让结构更容易读，这里故意省略了几块已经在本工程里出现第一版实现、但不属于“先看骨架”主线的模块，例如：

- `app/acceptance/`：provider-facing acceptance 与报告生成
- `app/core/memory_store.py`：轻量 memory / retrieval 存储
- `app/agent/orchestrator.py`：第一版多代理编排
- `app/daemon/service.py`：第一版本地 daemon / API 控制面
- `app/core/tool_registry.py`、`app/runtime/artifact_readers.py`：更靠后的工具注册与产物可读层

### 1. Entry 是怎样接住请求的 / How Entry Receives A Request

入口层大致会做下面这些事：

```
def main():
    args = parse_cli_args()
    repo_path = resolve_repo(args.repo)

    adapter = build_runtime_adapter(args.provider)
    clarifier = IntentClarifier(...)
    permission_pipeline = PermissionPipeline(...)

    clarification = clarifier.clarify_with_context(args.prompt, repo_path)
    if clarification.status == "needs_clarification":
        return render_questions(clarification)

    loop = CodingAgentLoop(...)
    result = loop.run(
        prompt=clarification.normalized_prompt,
        repo_path=repo_path,
        task_type=clarification.inferred_task_type,
    )
    return render_result(result)
```

这段骨架背后的重点不是语法，而是顺序：

- 请求先进入稳定入口
- 再经过澄清和权限判断
- 最后才真正进入执行闭环

### 2. 澄清层是怎样拦住模糊输入的 / How Clarification Prevents Ambiguous Execution

澄清层的骨架大致像这样：

```
def clarify_with_context(prompt, repo_path, recent_runs):
    normalized_prompt = normalize(prompt)
    continuation_target = infer_continuation_target(normalized_prompt, recent_runs)
    inferred_task_type = infer_task_type(normalized_prompt, continuation_target)

    if short_continuation_but_no_clear_target(normalized_prompt, recent_runs):
        return needs_clarification("Which task should continue?")

    if target_is_missing(normalized_prompt, inferred_task_type):
        return needs_clarification("Which file, module, or behavior should change?")

    return ready(
        normalized_prompt=normalized_prompt,
        inferred_task_type=inferred_task_type,
    )
```

这个部件要解决的，不是语言能力，而是控制问题：

- 用户是不是只说了“继续”
- 这句话有没有明确续轮对象
- 这个任务到底是在修 bug、加 feature，还是在调查问题

### 3. Policy 是怎样把“能做什么”显式化的 / How Policy Makes Execution Boundaries Explicit

`policies.py` 展示的是 harness 的第二个核心能力：不要把权限边界藏在 prompt 里。

它的大致形状可以抽象成：

```
class PermissionPipeline:
    def assess(operation, policy_mode, provider_info):
        if operation == "inspect":
            return allow(low_risk=True)
        if operation == "local_loop":
            return allow(workspace_write=True)
        if operation == "delegated_provider":
            if provider_unavailable(provider_info):
                return deny("provider unavailable")
            if policy_mode == "dangerous":
                return allow("full bypass")
            if policy_mode == "auto":
                return allow("auto approved")
            return confirm("external execution requires approval")
        return deny("unknown operation")
```

这里只展示了非常小的一部分，但已经足够说明 harness 的关键差别：

- 权限判断是独立控制点
- 风险会被分类
- 系统会明确产出 `allow / confirm / deny`
- “是否执行”不应该依赖模型临场判断

### 4. Verification 是怎样把“模型说做完了”变成“系统证明做完了” / How Verification Turns Claims Into Evidence

验证层的大致逻辑可以被理解成：

```
def run_post_execute(state):
    completion_check = evaluate_completion_contract(state)
    gate_results = []

    gate_results.append(check_tests_passed(state))
    gate_results.append(check_changed_files_recorded(state))
    gate_results.append(check_completion_contract(completion_check))
    gate_results.append(check_no_architecture_violation(state))

    return {
        "completion_check": completion_check,
        "gate_results": gate_results,
        "gate_failures": [g for g in gate_results if not g.passed],
    }
```

这层的核心意义在于：

- 完成不是模型自述
- 完成要经过一组 deterministic gate
- “没通过”时要知道是哪道 gate 失败了

如果一个系统没有这层，它本质上仍然更像 demo，而不是工程系统。

### 5. Replay 为什么是闭环的一部分 / Why Replay Is Part Of The Loop

很多人第一次做 agent 时，会把 replay 当作“高级增强”。  
但真正从 harness 角度看，replay 不是锦上添花，而是闭环的一部分。

因为没有 replay，就很难回答下面这些问题：

- 上一轮到底做了什么
- 为什么这次会继续那个任务
- 上次失败是环境问题、实现问题，还是瞬时问题
- 这次结果到底是怎样产生的

从 harness 角度看，replay 的意义不是“记录日志”，而是：

**让 continuation、debug 和 postmortem 有证据可追。**

### 6. `specs/` 为什么重要 / Why The `specs/` Layer Matters

在这个样本里，`specs/` 的价值不是“文档放在这里”。  
更重要的是，它代表了一条工程演进方向：

- 先用代码把闭环搭起来
- 然后把稳定重复的行为抽成 workflow、rule、template
- 再让这些资产反过来驱动 planning、verification 和 critic / verifier 判断

这说明 harness 的工程化不只是“把代码写出来”，还包括：

**把行为逐步沉淀成可复用资产。**

---

## 为什么一个不过厚的样本工程更适合学习 / Why A Not-Too-Thick Sample Works Better

很多人会问：

“为什么不直接去研究一个更大的 agent 平台？”

答案很简单：  
在学习阶段，过厚的系统会遮住真正重要的骨架。

`Claude_Code_MVP` 适合作为学习样本，不是因为它功能最全，而是因为它的厚度刚好。

它已经有：

- CLI first 入口
- bounded context
- planning
- policy
- runtime abstraction
- verification
- repair
- replay
- 第一波 asset layer

但它也还没有：

- 很厚的长期 memory / retrieval 系统
- 丰富的 dashboard / cost / cache 平台层
- 完整产品化的 daemon / API 控制面
- 已经定型的重型多代理系统

更准确地说，这些方向在当前工程里已经出现了第一版入口，但还没有成长到会遮住学习主线的程度。

这反而很适合作为学习入口，因为它能清楚展示：

- 一个 harness 应该先长出什么
- 哪些是 MVP 必需
- 哪些是后续增强
- 为什么控制闭环比功能堆叠更重要

---

## 结尾 / Conclusion

从“AI 能帮我写代码”到“我能做一个 AI coding system”，中间真正要跨过去的，不是模型能力，而是工程控制能力。

这层工程控制能力，就是 harness。

如果要动手做第一版，最重要的不是模仿一个最终产品，而是先做出一个小而清楚的闭环：

- 有入口
- 有上下文
- 有计划
- 有策略
- 有运行时
- 有验证
- 有 replay

当这些东西都长出来之后，系统才真正从 demo 进入了工程。  
而这一步，往往比换一个更强的模型更重要。

如果用一句话概括整篇文章，我会这样说：

**真正值得学习的，不是某个单独模块，而是一个系统如何把入口、上下文、边界、执行、验证、修复和回放串成一个完整闭环。**
