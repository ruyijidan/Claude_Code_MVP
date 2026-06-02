# Specs Diff Archive — 001-token-cli

**Date**: 2026-06-02
**Branch**: 001-token-cli
**Confirmed by**: user（"同意"）

---

## specs/product.md

**来源**：specs/001-token-cli/spec.md（已通过 final code review）
**冲突检查**：无冲突（首次创建）

```
[ADDED] ## Token CLI

开发者 CLI 工具，支持两个子命令：

- token-count <file> [file ...]：统计一个或多个文件的 token 数（cl100k_base 编码），
  多文件时输出每个文件单独数值和 total 合计行；缺失文件报错退出（非零退出码）
- compare <baseline> <target>：对比两个文件的 token 数，输出各自数量、绝对差值（含正负号）
  和百分比差异；参数不足/超过 2 个由 argparse 拦截报错

入口：python scripts/dev.py <subcommand>
```

---

## specs/tech.md

**来源**：specs/001-token-cli/design.md + specs/001-token-cli/spec.md（已通过 final code review）
**冲突检查**：无冲突（首次创建）

```
[ADDED] ## Token CLI（scripts/dev.py）

- 编码：tiktoken cl100k_base（与 scripts/measure_token_comparison.py 保持一致）
- 依赖：tiktoken>=0.7（已声明在 pyproject.toml [project.dependencies]）
- 实现：argparse subparser 模式；模块级 _enc 单例避免重复加载编码器；
  count_tokens(path: str) -> int 作为共享工具函数
- 测试：tests/test_dev.py，subprocess 驱动 CLI，9 个测试用例覆盖正常路径 + 边界
```
