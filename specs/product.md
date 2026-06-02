# Product Spec

## Token CLI

开发者 CLI 工具，支持两个子命令：

- `token-count <file> [file ...]`：统计一个或多个文件的 token 数（cl100k_base 编码），多文件时输出每个文件单独数值和 `total` 合计行；缺失文件报错退出（非零退出码）
- `compare <baseline> <target>`：对比两个文件的 token 数，输出各自数量、绝对差值（含正负号）和百分比差异；参数不足/超过 2 个由 argparse 拦截报错

入口：`python scripts/dev.py <subcommand>`
