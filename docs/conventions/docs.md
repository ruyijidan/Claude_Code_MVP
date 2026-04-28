---
last_updated: 2026-04-27
status: active
owner: core
---

# Documentation Hygiene / 文档卫生

## Rules / 规则

- Keep `AGENTS.md` short and navigation-oriented.
- Put durable architectural knowledge in `docs/architecture/`.
- Put frequently changing execution plans in `docs/plans/`.
- Mark stale or superseded designs with `status: deprecated`.
- Give every document title a bilingual heading in the form `English Title / 中文标题`.
- Section headings should also prefer bilingual form when practical so the documentation style stays consistent.
- Body content can be written freely as long as the structure stays clear and the document remains easy to scan.

## Freshness / 新鲜度

- Update `last_updated` when a document changes materially.
- Review active design docs periodically.
- Prefer many focused docs over one giant rules file.
