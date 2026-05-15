---
last_updated: 2026-05-15
status: active
owner: core
---

# Harness 学习文档清理方案 / Harness Learning Docs Retention Plan

## 目标 / Goal

在不丢失最终可发布学习材料的前提下，收缩 `docs/design/` 里与 Harness 学习相关的冗余文档。

这份方案默认采用一个更小、更稳定的长期保留集合：

- 一篇统一主文
- 一篇短摘要
- 一份分发物料

其他文档则按“是否仍然提供独立价值”来判断保留或删除。

## 建议长期保留 / Recommended Long-Term Keep Set

### 1. 主学习文 / Primary Learning Article

- [`harness-blog-feishu-copyready.md`](./harness-blog-feishu-copyready.md)

理由：

- 已经是最终统一稿
- 已经吸收 `01` 到 `04` 的核心内容
- 已按本工程当前实现状态校准
- 可以直接贴飞书，不依赖其他 companion docs

### 2. 短摘要 / Short Summary

- [`harness-blog-feishu-promotion-summary.md`](./harness-blog-feishu-promotion-summary.md)

理由：

- 适合群发、预热、资源库导读
- 与主学习文分工明确
- 不与主文重复承担主体讲解职责

### 3. 分发物料 / Distribution Kit

- [`harness-feishu-distribution-kit.md`](./harness-feishu-distribution-kit.md)

理由：

- 这是“发出去怎么说”的外围文案，不是正文重复件
- 适合长期作为发布和转发配套材料保留

## 可独立保留但不属于核心学习集 / Keep Separately But Not In The Core Learning Set

### 1. 知识护城河文章 / Knowledge-Moat Article

- [`harness-knowledge-moat-feishu.md`](./harness-knowledge-moat-feishu.md)

理由：

- 主题不是基础 Harness 学习，而是团队知识沉淀方法论
- 与主学习文不是替代关系

### 2. Claude Code 源码分析文 / Claude Code Source Analysis

- [`claude-code-source-analysis-feishu.md`](./claude-code-source-analysis-feishu.md)

理由：

- 这是独立源码分析型长文
- 与基础学习专题不是替代关系

## 优先删除候选 / Priority Deletion Candidates

这些文件的内容价值大多已经被主学习文吸收，或者只承担过渡包装作用。

### 1. 旧草稿 / Old Drafts

- [`harness-blog-feishu-draft.md`](./harness-blog-feishu-draft.md)
- [`harness-blog-feishu-longform.md`](./harness-blog-feishu-longform.md)

删除理由：

- 叙事职责已经被 `copyready` 覆盖
- 如果团队不再打算回退到“多版本并行写作”，保留它们只会增加选择成本

### 2. 专题包装件 / Topic Packaging Files

- [`harness-blog-feishu-cover-note.md`](./harness-blog-feishu-cover-note.md)
- [`harness-feishu-topic-index.md`](./harness-feishu-topic-index.md)

删除理由：

- 当团队决定以单篇统一主文为主时，这两份的存在价值会明显下降
- 其内容大多是包装和导流，而不是核心学习内容

### 3. 拆分 companion docs / Split Companion Docs

- [`harness-feishu-01-what-is-harness.md`](./harness-feishu-01-what-is-harness.md)
- [`harness-feishu-02-how-to-build-a-minimal-harness.md`](./harness-feishu-02-how-to-build-a-minimal-harness.md)
- [`harness-feishu-03-how-to-evaluate-a-harness-project.md`](./harness-feishu-03-how-to-evaluate-a-harness-project.md)
- [`harness-feishu-04-how-harness-looks-in-a-real-project.md`](./harness-feishu-04-how-harness-looks-in-a-real-project.md)

删除理由：

- 核心内容已经被 `harness-blog-feishu-copyready.md` 吸收
- 继续保留会让“到底发哪篇、读哪篇”变得模糊
- 它们现在更像编辑过程产物，而不是必须长期存在的学习资产

## 推荐删除顺序 / Recommended Deletion Order

如果要分批删，建议按这个顺序：

1. 先删 `harness-blog-feishu-draft.md`
2. 再删 `harness-blog-feishu-longform.md`
3. 再删 `harness-blog-feishu-cover-note.md`
4. 再删 `harness-feishu-topic-index.md`
5. 最后再删 `harness-feishu-01` 到 `04`

这个顺序的原因是：

- 先去掉最明显的写作过程文件
- 再去掉只服务于“专题打包”的导流文件
- 最后再删已经被统一稿覆盖的拆分 companion docs

## 当前执行结果 / Current Execution Result

As of `2026-05-15`, the following redundant local learning docs have already been removed:

- `harness-blog-feishu-draft.md`
- `harness-blog-feishu-longform.md`
- `harness-blog-feishu-cover-note.md`
- `harness-feishu-topic-index.md`
- `harness-feishu-01-what-is-harness.md`
- `harness-feishu-02-how-to-build-a-minimal-harness.md`
- `harness-feishu-03-how-to-evaluate-a-harness-project.md`
- `harness-feishu-04-how-harness-looks-in-a-real-project.md`

## 删除前最后确认 / Final Checks Before Deletion

在真正删除前，只需要确认三件事：

1. 团队后续默认只发一篇主文，而不是维护一个专题包
2. `harness-blog-feishu-copyready.md` 已经被视为唯一正文源
3. 没有人还依赖 `01-04` 进行单篇拆分发布

如果这三件事都成立，就可以放心开始删冗余。

## 最小保留集合 / Smallest Stable Retained Set

如果目标是把 Harness 学习文档缩到最小且仍然完整，建议最终只保留：

- [`harness-blog-feishu-copyready.md`](./harness-blog-feishu-copyready.md)
- [`harness-blog-feishu-promotion-summary.md`](./harness-blog-feishu-promotion-summary.md)
- [`harness-feishu-distribution-kit.md`](./harness-feishu-distribution-kit.md)

再加上两个不属于基础学习集、但可单独长期保留的独立文章：

- [`harness-knowledge-moat-feishu.md`](./harness-knowledge-moat-feishu.md)
- [`claude-code-source-analysis-feishu.md`](./claude-code-source-analysis-feishu.md)
