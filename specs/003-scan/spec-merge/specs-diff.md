# Specs Diff: 003-scan

**Branch**: `004-scan-dir`  
**Date**: 2026-06-04  
**G2 Gate confirmed**: 2026-06-04

## 来源产物

- `specs/003-scan/spec.md`（已通过 spec compliance review — 9/9 acceptance scenarios）
- `specs/003-scan/plan.md`（已通过 G_SPEC 规格评审）
- `specs/003-scan/tasks.md`（12 tasks, T001–T012 全部完成）
- git log branch `004-scan-dir`（最新 commit: `89e208e`）

## 冲突检查

无冲突。`## Token CLI` 章节直接扩展，无重复或矛盾内容。

---

## specs/product.md

```diff
[MODIFIED] ## Token CLI

+ - `scan <dir> [--ext EXT ...]`：递归扫描目录下的文本文件，输出每文件的 token 数和词数
+   （左对齐文件名 + 右对齐数字），按 token 数降序排列，末尾显示合计行（含文件数）；
+   支持 `--ext` 按扩展名过滤；二进制文件跳过并打印 stderr warning；
+   目录不存在 exit 1；无匹配文件时输出提示 exit 0；
+   自动跳过 `.git` / `node_modules` / `__pycache__` / `.venv` / `dist` / `build`
```

---

## specs/tech.md

```diff
[MODIFIED] ## Token CLI（scripts/dev.py）

+ - **scan 子命令新增实现**：
+   - `_SKIP_DIRS: frozenset[str]`：跳过目录常量集合
+   - `_is_binary(path: Path) -> bool`：读取前 1024 字节，含 `\x00` 判为二进制；OSError 向上抛出
+   - `_scan_files(directory, exts, skip_dirs) -> list[Path]`：rglob 遍历，按相对路径各部分过滤
+     skip_dirs（避免绝对路径误匹配），exts 非空时按后缀过滤
+   - `_format_scan_table(rows) -> str`：对齐表格，列宽自适应最长路径
+   - `_cmd_scan(args)`：校验目录存在，捕获 OSError + UnicodeDecodeError 给 warning，
+     binary 文件单独 warning，无有效行时提示 exit 0

- 测试：14 个测试用例（含 5 个 WordCountTests）
+ 测试：23 个测试用例（含 9 个 ScanTests，覆盖 US1/US2/US3 全部场景）
```
