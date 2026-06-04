---
last_updated: 2026-05-15
status: draft
owner: core
---

# Harness Engineering 摘要 / Harness Engineering Summary

## 适用版本 / Suggested Use

这是当前最适合做预热、导读和发群配文的一版。

适合场景：

- 飞书群预热
- 分享前导读
- 文章发布前的短介绍
- 需要先统一核心观点，再引导阅读主文或专题文档

## 核心结论 / Core Takeaway

AI coding 系统从 demo 走向工程，关键不在于模型更强，而在于是否建立了一层 harness。

一句话概括：

> **Agent 是执行者，Harness 是运行环境。**

模型负责生成、判断、推理。  
harness 负责把一次 AI 执行变成一个可控、可验证、可复盘的工程闭环。

普通 AI coding demo 更像：

`prompt -> model -> output`

而最小可用 harness 更像：

`request -> context -> plan -> policy -> runtime -> verify -> repair -> replay`

这层差异决定了系统是在“展示能力”，还是在“稳定交付”。

因此，Harness 不是边角料，也不是一个实现细节，而是 Agent 系统的战略级基础设施。

## 为什么值得看这组材料 / Why This Series Is Worth Reading

AI coding 一旦进入真实工程环境，会立刻遇到模型能力之外的问题：

- 用户输入如何进入系统
- 仓库上下文如何组织
- 哪些操作允许直接执行，哪些必须确认或拦截
- 结果如何验证
- 失败之后如何重试、修复或停止
- 运行过程如何记录和复盘

这些问题都不属于模型生成本身，而属于模型外部的控制系统。

也正因为如此，在同一个模型固定不动的前提下，只调整模型外围工程，系统效果仍然会出现巨大差异。

换句话说，模型能力只是上限，Harness 决定的是可用性、稳定性和交付质量。

## 建议阅读方式 / Suggested Reading Order

如果只是想快速建立整体认知，建议按这个顺序读：

1. `什么是 Harness`
2. `最小可用 Harness 应该怎么搭`
3. `如何评估一个 Harness 项目`
4. `用一个真实项目看 Harness 落地`

如果你想只看一篇总览版，建议直接读主文。

如果你准备在群里转发，更推荐把这篇短摘要配在主文或专题目录前面。

## 一句话总结 / One-Line Summary

真正值得学习的，不是“怎么让模型多做一点事”，而是：

**怎么把模型放进一个可控、可验证、可复盘的工程系统里。**
