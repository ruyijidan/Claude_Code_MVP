# Product Spec

## Token CLI

开发者 CLI 工具，支持两个子命令：

- `token-count <file> [file ...]`：统计一个或多个文件的 token 数（cl100k_base 编码），多文件时输出每个文件单独数值和 `total` 合计行；缺失文件报错退出（非零退出码）
- `compare <baseline> <target>`：对比两个文件的 token 数，输出各自数量、绝对差值（含正负号）和百分比差异；参数不足/超过 2 个由 argparse 拦截报错
- `word-count <file> [file ...]`：统计一个或多个文件的词数（按空白字符分词），多文件时输出每文件单独数值和 `total` 合计行；缺失文件报错退出（非零退出码）
- `scan <dir> [--ext EXT ...]`：递归扫描目录下的文本文件，输出每文件的 token 数和词数（左对齐文件名 + 右对齐数字），按 token 数降序排列，末尾显示合计行（含文件数）；支持 `--ext` 按扩展名过滤；二进制文件跳过并打印 stderr warning；目录不存在 exit 1；无匹配文件时输出提示 exit 0；自动跳过 `.git` / `node_modules` / `__pycache__` / `.venv` / `dist` / `build`

入口：`python scripts/dev.py <subcommand>`
