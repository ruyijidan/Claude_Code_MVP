# Tech Spec

## Token CLI（scripts/dev.py）

- **编码**：tiktoken cl100k_base（与 scripts/measure_token_comparison.py 保持一致）
- **依赖**：`tiktoken>=0.7`（已声明在 pyproject.toml [project.dependencies]）
- **实现**：argparse subparser 模式；模块级 `_enc` 单例避免重复加载编码器；`count_tokens(path: str) -> int` 作为 token-count 工具函数；`count_words(path: str) -> int` 作为 word-count 工具函数，用 `str.split()` 分词，无内部 exists 检查（调用方负责文件存在性校验，与 `count_tokens` 一致）
- **scan 子命令新增实现**：
  - `_SKIP_DIRS: frozenset[str]`：跳过目录常量集合（`.git` / `node_modules` / `__pycache__` / `.venv` / `dist` / `build`）
  - `_is_binary(path: Path) -> bool`：读取前 1024 字节，含 `\x00` 判为二进制；OSError 向上抛出
  - `_scan_files(directory, exts, skip_dirs) -> list[Path]`：rglob 遍历，按相对路径各部分过滤 skip_dirs（避免绝对路径误匹配），exts 非空时按后缀过滤
  - `_format_scan_table(rows) -> str`：对齐表格，列宽自适应最长路径；sep 宽 = file_col_width + 两个 8-char 数字列 + 两个 2-space 分隔符
  - `_cmd_scan(args)`：校验目录存在，捕获 OSError（_is_binary 阶段）和 OSError + UnicodeDecodeError（读取阶段）分别给出 warning，binary 文件单独 warning，无有效行时提示 exit 0
- **测试**：`tests/test_dev.py`，subprocess 驱动 CLI，23 个测试用例（含 9 个 ScanTests，覆盖 US1/US2/US3 全部场景：ext 过滤、binary 跳过、单文件、多扩展名、全 binary 等）
