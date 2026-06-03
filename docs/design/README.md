---
last_updated: 2026-05-08
status: active
owner: core
---

# Design / 设计

This directory stores lightweight design templates and future feature writeup scaffolds.

## Canonical Set / 当前建议保留

For the harness learning material itself, the recommended long-term kept set is:

- [`harness-blog-feishu-copyready.md`](./harness-blog-feishu-copyready.md): final unified Feishu article for direct publishing
- [`harness-blog-feishu-promotion-summary.md`](./harness-blog-feishu-promotion-summary.md): short preview / group-post summary
- [`harness-feishu-distribution-kit.md`](./harness-feishu-distribution-kit.md): publishing copy for topic cover, group post, and resource-library submission
- [`harness-docs-retention-plan.md`](./harness-docs-retention-plan.md): keep/delete recommendation for cleaning redundant local learning docs

Related standalone articles that are not part of the core harness learning set:

- [`harness-knowledge-moat-feishu.md`](./harness-knowledge-moat-feishu.md): standalone perspective piece arguing that knowledge retention matters more than workflow complexity
- [`claude-code-source-analysis-feishu.md`](./claude-code-source-analysis-feishu.md): standalone source-analysis article on what Claude Code teaches about engineering coding agents

## Cleanup Candidates / 冗余候选

The local redundant harness-learning drafts and split companion docs have been removed.

If the team later wants to re-introduce a topic-series packaging format, add those files back only when they provide value beyond the unified article.

## Full Inventory / 全量清单

Current files:

- [`template.md`](./template.md)
- [`acceptance-report.md`](./acceptance-report.md): lightweight contract for unattended release acceptance JSON artifacts
- [`acceptance-report-example.md`](./acceptance-report-example.md): human-readable example acceptance report
- [`acceptance-report-example.json`](./acceptance-report-example.json): structured example acceptance report
- [`intent-clarifier.md`](./intent-clarifier.md): first-version pre-execution clarification control point for ambiguous requests
- [`harness-blog-feishu-copyready.md`](./harness-blog-feishu-copyready.md): final unified Feishu article for direct publishing, with cleaner hierarchy and paste-friendly spacing
- [`harness-blog-feishu-promotion-summary.md`](./harness-blog-feishu-promotion-summary.md): compact promotion-material summary version focused on conclusions and engineering structure
- [`harness-knowledge-moat-feishu.md`](./harness-knowledge-moat-feishu.md): standalone perspective piece arguing that knowledge retention matters more than workflow complexity
- [`claude-code-source-analysis-feishu.md`](./claude-code-source-analysis-feishu.md): standalone source-analysis article on what Claude Code teaches about engineering coding agents
- [`harness-feishu-distribution-kit.md`](./harness-feishu-distribution-kit.md): group-post copy, topic-cover copy, and resource-library submission note
- [`harness-docs-retention-plan.md`](./harness-docs-retention-plan.md): keep/delete recommendation for removing redundant local harness-learning docs
- [`long-task-game-execution.md`](./long-task-game-execution.md): runbook for unattended long-running browser mini-game tasks and reruns
- [`long-task-game-task-template.md`](./long-task-game-task-template.md): copy-paste template for starting a long-task browser mini-game run
- [`long-task-game-launch-phrase.md`](./long-task-game-launch-phrase.md): short copy-paste phrase for starting the default long-task flow
- [`long-task-game-session-log-template.md`](./long-task-game-session-log-template.md): evidence template for proving a long-task run actually sustained its target duration
- [`long-task-game-optimization-strategy.md`](./long-task-game-optimization-strategy.md): convergence-focused strategy for improving the same game across a sustained long-task session
- [`fc-style-long-play-principles.md`](./fc-style-long-play-principles.md): design principles for small games that stay engaging for a long time
- [`auto-experience-diagnostics.md`](./auto-experience-diagnostics.md): diagnostic loop for detecting game-experience problems automatically during long-task runs
- [`start_long_task_game_session.sh`](../../scripts/start_long_task_game_session.sh): script entrypoint that creates a session log and runs the long-task game session with timeout handling
- [`long-task-game-upgrade.md`](./long-task-game-upgrade.md): historical 600-second mini-game upgrade record for `Void Breaker`
- [`long-task-game-rerun-2026-04-24.md`](./long-task-game-rerun-2026-04-24.md): historical rerun record for `Starforge Relay`

## Teaching Drafts / 教学草稿

The harness learning docs no longer need to be used equally.

The smallest stable retained set is now:

- keep [`harness-blog-feishu-copyready.md`](./harness-blog-feishu-copyready.md)
- keep [`harness-blog-feishu-promotion-summary.md`](./harness-blog-feishu-promotion-summary.md)
- keep [`harness-feishu-distribution-kit.md`](./harness-feishu-distribution-kit.md)
- consult [`harness-docs-retention-plan.md`](./harness-docs-retention-plan.md) before deleting old companion drafts

If you prefer a single merged document instead of a topic series, use [`harness-blog-feishu-copyready.md`](./harness-blog-feishu-copyready.md) only.

For a separate opinionated practice article on knowledge as the durable moat beyond workflow design, use [`harness-knowledge-moat-feishu.md`](./harness-knowledge-moat-feishu.md).

For a separate source-analysis article focused on Claude Code implementation patterns, use [`claude-code-source-analysis-feishu.md`](./claude-code-source-analysis-feishu.md).

For a repository-level teaching order, see [`../guides/harness-teaching-path.md`](../guides/harness-teaching-path.md).
