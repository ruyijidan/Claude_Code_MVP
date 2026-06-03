# Design：scan 子命令（scripts/dev.py）

**日期**：2026-06-03
**功能**：扫描目录，输出文本文件的 token 数与词数统计表

## 目标

给 `scripts/dev.py` 加 `scan <dir>` 子命令，让开发者快速了解目录内文件的 token/词数分布，
辅助 context 规划和文档体量管理。

## 子命令接口

```
python scripts/dev.py scan <dir> [--ext EXT [EXT ...]]
```

- `<dir>`：必填，目标目录路径
- `--ext`：可选，白名单扩展名（如 `--ext .md .txt .py`）；不传则扫描所有可读文本文件

## 输出格式

对齐表格，按 token 数降序，末尾输出合计行：

```
file                            tokens    words
scripts/dev.py                     890      201
docs/design/spec-kit.md            620      148
specs/product.md                   210       52
────────────────────────────────────────────────
total (3 files)                   1720      401
```

- `file` 列：相对于 `<dir>` 的路径
- 列宽自适应最长文件名
- 分隔线宽度与表格对齐

## 核心设计决策

### 目录遍历

- 递归扫描（`Path.rglob("*")`），自动跳过噪音目录：
  `.git`、`node_modules`、`__pycache__`、`.venv`、`dist`、`build`
- 无需用户配置，开箱即用

### 二进制文件检测

读取前 1024 字节，含 null byte（`\x00`）则判定为二进制，跳过并向 stderr 打印：
```
warning: skipped <rel_path> (binary)
```

### 权限/读取失败

同样 stderr warning，继续处理其余文件：
```
warning: skipped <rel_path> (unreadable: <reason>)
```

### 目录不存在

打印错误到 stderr，exit 1（与现有子命令行为一致）。

## 新增函数

| 函数 | 职责 |
|------|------|
| `_is_binary(path: Path) -> bool` | 检测二进制文件（null byte 法） |
| `_scan_files(directory: Path, exts: set[str], skip_dirs: set[str]) -> list[Path]` | 递归遍历，返回符合条件的文件列表 |
| `_format_scan_table(rows: list[tuple[str, int, int]], rel_dir: Path) -> str` | 生成对齐表格字符串（含表头和合计行） |
| `_cmd_scan(args: argparse.Namespace) -> None` | CLI handler，串联上述函数 |

复用已有：`count_tokens(path: str) -> int`、`count_words(path: str) -> int`

## 实现范围

- 仅修改 `scripts/dev.py`（新增约 80 行）
- 无新依赖（全部使用标准库 + 已有 tiktoken）
- 不重构现有子命令（DRY 问题留给独立 issue）
