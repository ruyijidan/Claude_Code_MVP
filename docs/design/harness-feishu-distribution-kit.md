---
last_updated: 2026-05-15
status: draft
owner: core
---

# Harness 飞书分发物料 / Harness Feishu Distribution Kit

这份文档用于统一存放飞书专题发布时常用的外围文案。

包括：

- 飞书群发文案
- 飞书专题首页文案
- 资源库提交说明

---

## 飞书群发文案 / Feishu Group Post Copy

最近整理了一组关于 `Harness Engineering` 的学习材料，核心不是讲“模型怎么更强”，而是讲：

**AI coding 系统从 demo 走向工程，真正缺的往往不是模型能力，而是一层 harness。**

也就是：

- 任务怎么进入系统
- 上下文怎么组织
- 哪些行为可以做，哪些必须拦住
- 做完以后怎么验证
- 失败以后怎么修复或停止
- 一轮执行结束后，如何留下可回看的证据

这组材料分成 4 篇，适合按顺序阅读：

1. `什么是 Harness`
2. `最小可用 Harness 应该怎么搭`
3. `如何评估一个 Harness 项目`
4. `用一个真实项目看 Harness 落地`

如果只想快速建立整体认知，也可以直接看总览长文。

这组内容更适合把 AI coding 从“prompt 和模型能力”的讨论，推进到“工程控制闭环”的讨论。  
如果你最近也在关注 coding agent、repo-aware execution、tool use、verification、agent runtime 这些方向，应该会比较有帮助。

---

## 飞书专题首页文案 / Feishu Topic Cover Copy

### 标题

Harness Learning Series

### 副标题

从 AI Coding Demo 到 Harness Engineering

### 导语

这是一组关于 Harness Engineering 的学习材料。

如果只看 AI coding demo，很多系统会显得很强。  
但只要真正进入工程流程，问题就会迅速从“模型会不会写代码”转向：

- 任务是怎么进入系统的
- 上下文是怎么组织的
- 哪些行为可以做，哪些必须拦住
- 做完以后怎么验证
- 失败以后该重试、修复还是停止
- 这一轮到底做了什么，下一轮又该如何继续

这些问题并不属于模型本身，而属于模型外部的控制系统。  
这个控制系统，就是 harness。

这组材料不打算把 focus 放在某个具体产品上，而是想系统回答四个问题：

1. 什么是 Harness
2. 最小可用 Harness 应该怎么搭
3. 如何评估一个 Harness 项目
4. 这些概念在一个真实样本里是怎样落地的

### 阅读顺序

1. `什么是 Harness`
2. `最小可用 Harness 应该怎么搭`
3. `如何评估一个 Harness 项目`
4. `用一个真实项目看 Harness 落地`

### 适合谁看

- 想系统理解 AI coding 工程化的人
- 正在做 agent / coding workflow / tool use 的人
- 想把系统从 demo 推进到可控闭环的人
- 想评估一个 Harness 项目成熟度的人

---

## 资源库提交说明 / Resource Library Submission Note

### 资源名称

Harness Learning Series：从 AI Coding Demo 到 Harness Engineering

### 资源简介

这是一组围绕 `Harness Engineering` 的学习材料，关注点不在于“模型会不会写代码”，而在于：

**如何把模型放进一个可控、可验证、可复盘的工程执行环境里。**

材料从四个层面展开：

1. `什么是 Harness`
   解释 Harness 的定义、它和 Agent / prompt wrapper 的区别，以及为什么很多 AI coding 系统会停留在 demo 阶段。

2. `最小可用 Harness 应该怎么搭`
   说明第一版 Harness 最少需要哪些部件，以及推荐的搭建顺序和常见误区。

3. `如何评估一个 Harness 项目`
   提供一套面向工程控制闭环的评估视角，用来判断一个项目是不是在做真实 Harness，而不只是堆功能。

4. `用一个真实项目看 Harness 落地`
   用一个真实样本工程，把入口、澄清、权限、验证、修复和回放这些控制点映射到具体实现形态上。

### 推荐理由

这组材料的价值主要在于三点：

- 它回答的是一个高价值但经常被混淆的问题  
  很多团队已经在讨论 AI coding、tool use、repo-aware execution，但真正决定系统能不能进入工程流程的，往往是 harness，而不是模型本身。

- 它既有方法论，也有工程映射  
  不是纯概念文章，也不是只有代码没有解释，而是把控制闭环拆成可以理解、可以迁移的结构。

- 它强调边界和成熟度判断  
  不把所有能力都包装成“成熟平台”，而是帮助读者区分哪些是 MVP 必需、哪些是后续增强、哪些问题必须在 Harness 层显式解决。

### 适合读者

- 对 AI coding 工程化感兴趣的研发同学
- 正在做 coding agent、tool system、runtime orchestration 的团队
- 希望从 demo 走向可控工程系统的实践者
- 需要评估 agent / harness 项目成熟度的人

### 使用建议

- 作为专题阅读，建议按 4 篇顺序阅读
- 作为快速导读，可以先看摘要版或总览版
- 作为内部讨论材料，适合用于统一“什么是 Harness、第一版该怎么做、如何判断一个项目是否靠谱”这几类问题的口径
