---
last_updated: 2026-05-15
status: draft
owner: core
---

# Claude Code 源码拆解：Anthropic 是怎么把编程 Agent 工程化出来的 / Claude Code Source Analysis: How Anthropic Engineered A Coding Agent

**副标题 / Subtitle**

从主循环、System Prompt、记忆系统到上下文压缩，拆解 Claude Code 最值得抄作业的工程设计

## 适用版本 / Suggested Use

这是一篇独立的源码分析型长文。

适合场景：

- 对 Claude Code 的工程实现方式做系统拆解
- 作为 Harness / Agent 工程的进阶阅读材料
- 面向已经有一定 Agent 开发经验的读者

---

## 文章摘要 / Article Summary

如果只把 Claude Code 理解成“一个能在终端里帮你写代码的 AI 工具”，其实低估了它。

真正值得研究的，不只是它能不能改文件、跑命令、管理 Git，而是：

**Anthropic 到底是怎么把一个编程 Agent 工程化出来的。**

一个真正可用的编程 Agent，要处理的事情远比想象中复杂：

- 怎样和大模型 API 稳定协作
- 怎样编排几十种工具调用
- 怎样给危险操作加上权限边界
- 怎样把 Prompt 设计成稳定控制面，而不是一段提示词
- 怎样让记忆跨会话保留，又不变成垃圾堆
- 怎样在长任务里管理上下文窗口，而不是越跑越失忆

Claude Code 的源码之所以值得拆，不是因为它有某一个“黑科技”，而是因为它把这些问题系统地做成了一套工程方案。

这篇文章会重点回答五个问题：

1. Claude Code 到底是什么，它和普通聊天机器人有什么区别
2. 它的整体架构是怎样组织起来的
3. 它为什么没有走经典 ReAct，而是用了更轻的 Tool-Use Loop
4. 它的 System Prompt、记忆系统和上下文压缩，分别解决了什么核心问题
5. 对所有做 Agent / Harness 的工程团队来说，Claude Code 源码里最值得抄的设计原则是什么

---

## 一、Claude Code 是什么 / What Claude Code Actually Is

在拆源码之前，先把最基本的问题讲清楚：Claude Code 到底是什么？

Claude Code 是 Anthropic 官方推出的编程 Agent 工具。

你可以把它理解成一个能直接在终端里干活的 AI 程序员。  
它不是一个聊天窗口，也不是一个代码补全插件，而是真正能：

- 读你的代码
- 改你的文件
- 跑你的命令
- 帮你管理 Git

从本质上说，Claude Code 就是一个 AI Agent。  
但 Agent 这个词现在被说得太泛了，很多人会把它和聊天机器人搞混，所以这件事必须先区分清楚。

### ChatBot、Copilot 和 Agent 的区别 / ChatBot, Copilot, And Agent

ChatBot 的交互模式是一次性的：

- 你问一句
- 它答一句

Copilot 的交互模式是局部预测：

- 你写一段代码
- 它补一个建议

Agent 的核心则是一个自主循环：

**感知 → 决策 → 行动**

你给它一个目标，比如“帮我修复这个 bug”，它会自己决定：

- 先读哪个文件
- 再跑什么命令
- 然后改哪一行代码
- 接着要不要跑测试

这个过程可能循环很多轮，直到任务完成。

也就是说，Claude Code 的关键不在于“它会不会写代码”，而在于：

**它能不能围绕一个目标持续自主行动。**

---

## 二、整体架构：它是怎么把这么多能力组织起来的 / The Overall Architecture

一个能自主编程的 Agent，要处理的事情非常多：

- 调大模型 API
- 执行几十种工具
- 管理权限
- 压缩上下文
- 维护记忆
- 支持多 Agent 协作

如果这些东西全部塞在一个文件里，代码会立刻变成一团乱麻。

Claude Code 的做法，是把系统拆成四层：

- 引擎层
- 工具层
- 服务层
- 安全与治理层

### 1. 引擎层 / Engine Layer

引擎层可以理解成 Agent 的大脑。

它最重要的设计原则是：

**不包含具体业务能力，只负责思考和调度。**

它不知道怎么读文件、怎么改代码、怎么搜索，这些全是工具层的事情。  
引擎层主要做三件事：

- 把用户输入、系统指令、历史消息拼起来发给大模型
- 当模型发起工具调用时，找到对应工具并执行
- 根据模型返回决定继续循环还是结束

这个设计的好处是：  
新增能力时，只需要新增一个工具，引擎层基本不用改。

### 2. 工具层 / Tool Layer

工具层是 Agent 的全部“能力”。

每个工具就是它的一项能力，比如：

- 执行 Shell 命令
- 读写文件
- 搜索代码
- 生成子 Agent

Claude Code 很值得学习的一点是：  
工具不是“随便实现一个函数就行”，而是遵循统一规范。

尤其重要的是，每个工具都必须显式声明几个安全属性：

- 是只读还是会修改内容
- 是否具有破坏性
- 能不能并发执行

这意味着每一把刀都不是裸奔的，而是从设计之初就带着刀鞘。

### 3. 服务层 / Service Layer

服务层是所有模块共享的基础设施。

这一层大致包括：

- 大模型 API 访问
- 上下文压缩
- 与外部工具服务器的通信协议

你可以把它理解成整栋楼的水、电、煤：

- 谁都离不开
- 但谁也不该自己重铺一遍

### 4. 安全与治理层 / Safety And Governance Layer

安全与治理层不是某个孤立模块，而像一张网罩在所有层上面。

它负责：

- 权限系统
- Hook 系统
- Shell 安全分析
- 高风险操作确认

这里最值得学的是：

**Claude Code 没有把“安全”当成附加功能，而是把它设计成横切所有层的基础约束。**

---

## 三、Agent 工作模式：为什么它没有用 ReAct / The Agent Loop: Why It Does Not Use ReAct

很多人谈 Agent 时，会默认联想到 ReAct。

ReAct 的核心循环是：

`Thought -> Action -> Observation`

也就是说，每一轮都要求模型先显式写出一段“思考”，再调用工具，再看工具结果，然后继续下一轮。

这个模式在早期模型时代很流行，因为它能强迫弱模型一步步推理。

但 Claude Code 没有这么做。

它采用的是一种更简洁的模式，可以叫做：

**Tool-Use Loop**

### Tool-Use Loop 的核心逻辑 / The Core Tool-Use Loop

它的逻辑非常简单，本质上就是一个 `while (true)`：

```ts
while (true) {
  const response = await streamAPI(messages)

  if (response.stopReason === "end_turn") {
    break
  }

  const toolResults = await executeToolCalls(response.toolUseRequests)
  messages = appendToolResults(messages, toolResults)
}
```

和 ReAct 最大的区别是：

**没有显式 Thought 步骤。**

模型会在内部完成推理，然后只返回两种结果之一：

- `tool_use`：我要调用工具
- `end_turn`：我说完了

### 为什么这样更适合强模型 / Why This Fits Strong Models Better

Claude Code 这样做有三个关键原因。

#### 1. 推理在模型内部完成

Claude 模型支持更强的内部推理能力。  
这意味着模型完全可以在内部想清楚下一步做什么，而不需要把每一步 Thought 都写出来。

这样做的好处是：

- 不浪费上下文 Token
- 不增加应用层解析复杂度

#### 2. API 原生支持 tool_use

Claude API 原生支持工具调用。  
模型可以直接返回结构化的 `tool_use` 响应，而不是在一段文本里写：

“Action: ReadFile(...)”

这意味着应用层不需要靠文本解析去猜模型意图，代码会简单很多。

#### 3. `end_turn` 是天然的终止信号

ReAct 常常还需要额外判断“模型是不是已经完成了”。  
而 Tool-Use Loop 直接用 API 提供的 `end_turn` 作为终止条件。

这在工程上更干净，也更稳定。

### Plan Mode 是怎么补足复杂任务规划的 / How Plan Mode Handles More Complex Tasks

Tool-Use Loop 并不意味着所有任务都直接“边想边做”。

对于复杂任务，Claude Code 还引入了 Plan Mode：

- 先规划
- 再执行

它的特别之处在于，Plan Mode 不是一套完全独立的新框架，而是通过两个工具实现的：

- `EnterPlanMode`
- `ExitPlanMode`

进入 Plan Mode 后，模型权限会被降成只读，只能探索和规划，不能改代码。  
等用户确认计划后，权限再恢复，正式进入执行阶段。

这里最值得学习的点是：

**“模式”在 Claude Code 里也被实现成“工具”。**

也就是说，Agent 的能力边界和工作模式，都被统一进了工具协议，而不是靠引擎层写很多特判逻辑。

---

## 四、System Prompt：为什么说它是 Claude Code 的灵魂 / Why The System Prompt Is The Soul Of Claude Code

System Prompt 定义了 Claude Code 的身份、边界、行为规范和工具使用方式。

但它不是一个静态文本文件。  
它更像一个动态组装出来的控制面。

### 1. 角色定义：它不是 assistant，而是 interactive agent

Claude Code 在开头就把自己定位成：

- 一个 interactive agent
- 一个帮助用户完成软件工程任务的系统

这不是措辞差异，而是行为差异。

如果模型把自己理解成 chatbot，它就更倾向于回答问题。  
如果模型把自己理解成 agent，它就更倾向于采取行动。

### 2. 行为准则：默认克制，而不是默认热心改造

Claude Code 的 Prompt 里有一组非常重要的行为约束：

- 不要修改你没有先读过的代码
- 不要在用户要求之外顺手重构
- 不要为了三行代码过早做抽象
- 某个方案失败后，先诊断，再决定是否换方案

这些规则解决的其实都是 Agent 开发里最常见的问题：

- 先猜后改
- 顺手重构
- 过度设计
- 失败后盲目重试

### 3. 操作安全：它不是“危险就别做”，而是“按可逆性和影响范围判断”

Claude Code 对操作风险的判断，不是简单粗暴地列一个黑名单。

它背后的核心判断维度其实是两个：

- 这个操作可逆吗
- 这个操作会影响别人吗

比如：

- 本地读写文件：通常可逆，影响范围小
- `git push`：不可逆，影响共享分支
- `reset --hard`：强破坏性

这种基于“可逆性 + blast radius”的判断，比简单的“危险 / 不危险”分法更细致，也更工程化。

### 4. 工具优先：优先用专用工具，不要什么都扔给 Bash

Claude Code 很明确地要求：

- 读文件用 Read 工具
- 改文件用 Edit / Write 工具
- 搜索内容用 Grep 工具
- 搜索文件用 Glob 工具

而不是一股脑用 Bash。

原因不只是“可用”，更关键是：

- 专用工具更容易被 UI 展示和审查
- 专用工具更容易挂权限检查
- 专用工具语义更清晰

换句话说，专用工具不仅提升体验，也提升安全。

### 5. 分割线与缓存：Prompt 本身也是工程对象

Claude Code 的 System Prompt 里有一个非常精妙的设计：

它会把所有用户都相同的静态部分，和因用户 / 项目而异的动态部分，用一条边界分开。

为什么这件事重要？

因为这样做能最大化利用 Prompt Cache：

- 静态前缀可以跨用户共享缓存
- 动态后缀只按需重新计算

这看起来像排版问题，实际上是实打实的成本优化。

这一点特别值得抄作业，因为它提醒我们：

**Prompt 不只是提示词，它也是工程对象。**

---

## 五、记忆系统：为什么它没有走“向量库万能论” / The Memory System: Why It Does Not Default To A Vector Database

每次启动 Claude Code，都是一个新会话。  
模型本身并不会记得上一次发生了什么。

但用户偏好、项目背景、行为反馈，显然又需要跨会话保留。

很多团队面对这个问题的第一反应是：

“上向量库。”

但 Claude Code 没有这么做。

原因很值得思考：

很多 Agent 需要记住的，并不是“相似文档片段”，而是结构化行为指令。

比如：

- 用户不喜欢冗长回复
- 集成测试必须用真实数据库
- 当前项目的认证模块重构是为了合规，不是技术债

这些东西更像“规则”或“画像”，而不是适合做相似度检索的自由文本。

### 1. 它先把记忆分类 / It First Classifies Memory

Claude Code 把记忆分成四类：

- `user`
- `feedback`
- `project`
- `reference`

这一步非常重要，因为它是在防止记忆系统膨胀成一个“什么都存”的垃圾场。

通过强制分类，模型每次写记忆时都必须想清楚：

**这到底是什么类型的信息。**

### 2. 它也明确规定“什么不该记” / It Also Defines What Should Not Be Stored

同样重要的是，Claude Code 很明确地排除了很多不该进记忆的内容，比如：

- 当前代码结构
- 文件路径细节
- Git 历史
- 当前会话里的临时状态

因为这些内容本来就应该从代码、Git 或当前上下文实时获得。  
如果把它们存进记忆，记忆很快就会变成“带权威感的过时信息”。

### 3. 它用索引 + 独立文件，而不是一个无边界的大文档 / It Uses An Index Plus Separate Files

Claude Code 的记忆不是全塞进一个文件里，而是：

- 一个轻量目录作为索引
- 多个独立记忆文件按需加载

这样做的好处是：

- Agent 永远知道有哪些记忆可用
- 但不会把所有记忆都塞进上下文
- 真正相关的条目才会被单独加载

### 4. 它用一个更便宜的小模型做“记忆秘书” / It Uses A Smaller Model As A Memory Secretary

在召回阶段，Claude Code 会先让一个更便宜、更快的模型扫描记忆头部信息，选出最相关的少数条目，再把这些条目交给主模型。

这是一个特别值得学的工程策略：

- 小模型负责筛选
- 大模型负责决策

不要什么事都交给最贵的模型。

### 5. 它还给记忆加了“陈旧度提醒” / It Adds Staleness Awareness

如果一条记忆已经很久没更新，系统会提醒模型：

这是一条过去某个时间点的观察，不一定仍然准确。

这件事看起来小，但非常关键。  
因为很多 Agent 失败，不是因为“没有记忆”，而是因为“过期记忆被当成实时事实”。

---

## 六、上下文窗口管理：为什么这是最硬的工程功夫 / Context Window Management: Why This Is The Hardest Engineering Work

上下文窗口管理，可能是整套源码里最复杂、也最容易被低估的部分。

因为长任务最容易出现的问题就是：

- 读了太多文件
- 执行了太多命令
- 消息越积越多
- 最后模型开始失忆

很多系统的做法很粗暴：

- 直接截断
- 或者直接整体摘要

Claude Code 的做法更讲究，它的思路是：

**压缩一定有信息损失，所以能不压就不压，必须压的时候从最轻的手段开始。**

### 它不是一步压缩，而是五步递进 / It Uses Five Progressive Compression Steps

从轻到重，大致是：

1. 大工具结果先存磁盘，只给模型看预览
2. 砍掉非常早、非常旧的消息
3. 清理老的、可重新获取的工具输出
4. 做读时投影，只在送 API 时计算压缩视图
5. 最后才做真正昂贵的全量摘要

这套设计最值得学习的地方在于：

- 先做几乎无损的压缩
- 再做低损压缩
- 最后才做高损摘要

也就是说，它把“上下文压缩”从一个单点动作，变成了一个分层策略系统。

### 为什么这比简单截断更好 / Why This Is Better Than Naive Truncation

因为简单截断会把“重要但旧”的信息也一起截掉。  
而分层策略更像是在做一场精细的空间管理：

- 能回磁盘的，就回磁盘
- 能重新读的，就不必一直留着
- 能投影压缩的，就先别动原始历史
- 实在没办法，才做摘要

这让 Agent 在长任务里更不容易突然降智。

### 为什么这比“动不动就摘要”也更好 / Why It Is Better Than Summarizing Too Early

因为摘要虽然节省空间，但会把很多细节永远丢掉。

Claude Code 非常克制地使用全量摘要，把它放到最后一道防线。

这其实体现的是一种很强的工程意识：

**不是所有上下文问题都应该交给大模型摘要去解决。**

很多时候，先做结构层面的分流和裁剪，效果更好、成本也更低。

---

## 七、Claude Code 最值得抄的 5 个设计原则 / Five Design Principles Most Worth Copying

如果把前面这些分析全部压缩成最值得迁移的工程启发，我会总结成五条。

### 1. 信任强模型推理，把应用层框架做简单 / Trust Strong Models, Keep The App Loop Simple

Claude Code 没有在应用层搞一个很复杂的 ReAct 外壳。  
它相信强模型能够内部推理，然后让应用层只做好：

- 调 API
- 执行工具
- 更新状态

### 2. 工具能力必须带安全属性出厂 / Tools Should Ship With Safety Metadata

工具不只是“能干什么”，还必须显式声明：

- 会不会修改东西
- 危不危险
- 能不能并发

这是把能力和边界一起工程化的典型做法。

### 3. Prompt 不是文本，而是控制面 / The Prompt Is Not Just Text, It Is A Control Surface

Claude Code 对 Prompt 的处理方式提醒我们：

- Prompt 要分层
- Prompt 要可缓存
- Prompt 要优化成本
- Prompt 要清楚划定行为边界

### 4. 记忆系统应该结构化，而不是无约束堆积 / Memory Should Be Structured, Not Just Retrieved

它没有默认走向量库万能论，而是先把记忆定义清楚：

- 哪些该记
- 哪些不该记
- 记忆应该分什么类型
- 记忆怎样按需召回

### 5. 上下文压缩必须分层递进 / Context Compression Must Be Layered

上下文窗口管理不能只靠“截断”或“摘要”两个按钮。

真正强的做法是：

- 先做低损处理
- 再做中损处理
- 最后才做高损摘要

这件事对所有长任务 Agent 都非常关键。

---

## 八、写在最后 / Final Thoughts

说到底，Claude Code 源码真正厉害的地方，并不是某一个局部功能，而是它把很多“看起来不起眼”的工程问题，系统地做成了一套能长期工作的方案。

比如：

- 主循环不复杂，但足够稳定
- Prompt 不是随便写写，而是可缓存、可分层的控制面
- 记忆不是一坨检索文本，而是结构化、按需召回的系统
- 上下文压缩不是最后才救火，而是从最轻策略一路递进

这给我一个很大的启发：

做 Agent，不能只盯着模型能力看。

模型是发动机。  
但一辆车能不能安全上路，决定因素往往是那些不那么显眼的东西：

- 刹车
- 方向盘
- 安全带
- 仪表盘

Claude Code 的价值，就在于它把这些“缰绳系统”做得非常完整。

如果要用一句话总结整篇文章，我会这么说：

**Claude Code 值得学习的，不只是它用了什么模型，而是它怎样把一个编程 Agent 变成了真正可用的工程系统。**
