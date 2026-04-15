# 测试报告

## 概览

这份报告记录了 `2026-04-10` 对 `Claude_Code_MVP` 进行的一次完整验证。

本次验证覆盖了三层：

- 单元测试
- worktree 隔离验证
- 代表性 CLI / 模型委托样例

## 1. 单元测试

执行命令：

```bash
cd /data/ji/code/Claude_Code_MVP
python3 -m unittest discover -s tests
```

结果：

- `Ran 33 tests`
- `OK`

日志：

- [`logs/test-run-2026-04-10-full.txt`](./logs/test-run-2026-04-10-full.txt)

## 2. Worktree 隔离验证

执行命令：

```bash
cd /data/ji/code/Claude_Code_MVP
bash scripts/agent_verify.sh
```

这一步验证的内容：

- 创建临时 git worktree
- 同步当前工作区到验证目录
- 安装项目
- 运行架构检查
- 运行单元测试
- 自动清理 worktree

结果：

- 架构检查通过
- 单元测试通过
- `main` 分支隔离验证通过

日志：

- [`logs/agent-verify-2026-04-10-full.txt`](./logs/agent-verify-2026-04-10-full.txt)

## 3. CLI 样例：Git 状态检查

执行命令：

```bash
cd /data/ji/code/Claude_Code_MVP
python3 -m app.cli.main --repo . --show-status --json
```

用途：

- 验证 CLI inspection 模式
- 验证 git status 的 JSON 输出路径

日志：

- [`logs/sample-show-status-2026-04-10.json`](./logs/sample-show-status-2026-04-10.json)

## 4. CLI 样例：权限检查

执行命令：

```bash
cd /data/ji/code/Claude_Code_MVP
python3 -m app.cli.main --repo . --show-permissions --json
```

用途：

- 验证 permission pipeline 输出
- 验证低风险 inspection 行为

日志：

- [`logs/sample-show-permissions-2026-04-10.json`](./logs/sample-show-permissions-2026-04-10.json)

## 5. CLI 样例：模型委托验证

执行命令：

```bash
cd /data/ji/code/Claude_Code_MVP
python3 -m app.cli.main \
  --repo . \
  --provider claude_code \
  --delegate-to-provider \
  --auto-approve \
  --json \
  "Reply with exactly MODEL_OK"
```

用途：

- 验证 delegated provider 执行路径
- 验证基于 `.env` 的 provider 配置已经生效
- 验证真实模型往返调用

结果：

- `returncode: 0`
- provider 返回 `MODEL_OK`

日志：

- [`logs/sample-delegated-provider-2026-04-10.json`](./logs/sample-delegated-provider-2026-04-10.json)

## 最终结论

当前项目已经通过：

- 完整单元测试
- Harness 风格隔离验证
- CLI inspection 样例验证
- 真实 delegated provider 样例验证

在这次检查点上，`Claude_Code_MVP` 可以确认具备：

- 可测试性
- 可隔离验证性
- 可通过 CLI 暴露 Harness 控制面
- 可成功委托到已配置的 Claude provider
