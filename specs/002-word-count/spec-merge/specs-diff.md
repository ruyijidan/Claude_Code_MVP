# Specs Diff：002-word-count

**日期**：2026-06-03
**来源产物**：specs/002-word-count/spec.md（已通过 spec compliance review + code quality review）
**冲突检查**：无冲突，word-count 是 Token CLI 能力的新增子命令，与已有 token-count/compare 条目无矛盾

---

## specs/product.md

[MODIFIED] ## Token CLI

```diff
  - `compare <baseline> <target>`：对比两个文件的 token 数，输出各自数量、绝对差值（含正负号）和百分比差异；参数不足/超过 2 个由 argparse 拦截报错
+ - `word-count <file> [file ...]`：统计一个或多个文件的词数（按空白字符分词），多文件时输出每文件单独数值和 `total` 合计行；缺失文件报错退出（非零退出码）
```

---

## specs/tech.md

[MODIFIED] ## Token CLI（scripts/dev.py）

```diff
- - **实现**：argparse subparser 模式；模块级 `_enc` 单例避免重复加载编码器；`count_tokens(path: str) -> int` 作为共享工具函数
- - **测试**：`tests/test_dev.py`，subprocess 驱动 CLI，9 个测试用例覆盖正常路径 + 边界
+ - **实现**：argparse subparser 模式；模块级 `_enc` 单例避免重复加载编码器；`count_tokens(path: str) -> int` 作为 token-count 工具函数；`count_words(path: str) -> int` 作为 word-count 工具函数，用 `str.split()` 分词，无内部 exists 检查（调用方负责文件存在性校验，与 `count_tokens` 一致）
+ - **测试**：`tests/test_dev.py`，subprocess 驱动 CLI，14 个测试用例覆盖正常路径 + 边界（含 5 个 WordCountTests）
```
