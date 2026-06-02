# Tech Spec

## Token CLI（scripts/dev.py）

- **编码**：tiktoken cl100k_base（与 scripts/measure_token_comparison.py 保持一致）
- **依赖**：`tiktoken>=0.7`（已声明在 pyproject.toml [project.dependencies]）
- **实现**：argparse subparser 模式；模块级 `_enc` 单例避免重复加载编码器；`count_tokens(path: str) -> int` 作为共享工具函数
- **测试**：`tests/test_dev.py`，subprocess 驱动 CLI，9 个测试用例覆盖正常路径 + 边界
