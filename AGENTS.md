# AGENTS.md — AI 协作与质量纪律

本文件对在本仓库工作的 AI 助手（ZCode 等）与开发者生效。**修改代码前先读本文件；提交前必须满足其中的门禁要求。**

项目：数据分析基础项目框架（core / business / interfaces 三层 + `src/app.py` 组合根）。
架构与扩展模式见 `docs/development_guide.md`；历史见 `docs/optimization_2026-09-30.md`。

## 一键质量门禁（每次必须运行）

```bash
uv run python run_tests.py              # 完整门禁：ruff lint + 格式检查 + mypy + 单元测试
uv run python run_tests.py --tests-only # 仅单元测试（含覆盖率门禁 80%）
```

**强制规则：**

1. **每次代码变更后**必须运行一键门禁，全部通过才算完成变更；未通过不得声称"已完成"。
2. **每次会话结束前**必须再次运行一键门禁，并向用户报告结果（通过项数、测试数、覆盖率）。
3. 覆盖率门禁为 80%（`--cov-fail-under=80`，CI 同步强制）；降低覆盖率或删除测试来"修复"失败是被禁止的。

## 单元测试纪律（强制）

### 禁止无效 mock

- **禁止 mock 被测逻辑本身**：不得 mock 服务/仓储/处理器/模型再"测试"它们；`assert Mock().method.called` 这类"验证调用过"的测试视为无效测试。
- **替身只允许出现在不可控边界**：进程外网络、时钟、随机数等。即使如此，也应优先使用真实手段（不可达地址、`tmp_path` 真实文件、独立 sqlite）。
- **允许的 monkeypatch 仅有两类**，且必须在测试 docstring 中说明理由：
  1. 全局单例隔离（`_settings`、`_global_logger`、`_database_manager`、`_app` 等——目的是测试间互不污染，不是绕过逻辑）；
  2. 不可达分支的故障注入（例如防御性异常包装分支，无法通过真实输入触发时）。
- 逐条判断标准：**如果删掉被 mock 的真实实现、只留空壳，测试仍能通过，则这个测试是无效的。**

### 基于真实业务场景

- 单元测试应模拟真实使用路径：真实 `.env` 文件、真实 CSV、真实 sqlite 落库（`sqlite_db_manager` fixture）、真实 CLI 启动链路。
- 持久化类断言必须**直接查询落库结果**（sqlite 文件 / 仓储读回），不允许只断言"保存方法被调用"。
- 仓储替身只允许使用 `tests/fixtures/test_data.py` 的 `InMemoryRepository`——它是协议的**真实第二实现**，用于验证面向接口设计，不属于 mock。
- 每个测试失败时给出的信息应能定位真实缺陷；一个测试只能失败于一种原因。

## 工程约定

- Python 3.10+；所有函数必须有类型注解（mypy `disallow_untyped_defs = true` + Pydantic 插件，不得放宽）。
- 异常必须 `raise XxxError(...) from e` 保留异常链；禁止静默吞错（`except: pass` 或返回默认值不留日志）。
- 日志统一 loguru（`from src.core.logging import get_logger`），**禁止 print**。
- 涉及数据库 URL 的日志/输出必须经过 `mask_database_url` 脱敏。
- 提交前依次运行：`uv run ruff check . --fix && uv run ruff format . && uv run mypy src`，然后一键门禁。

## 常用命令

```bash
uv run pytest tests/ -q --no-cov            # 快速跑测试
uv run python run_tests.py                  # 一键门禁（见上）
uv run hello-python --help                  # CLI 入口
```

## 提交

- 提交信息用中文 + conventional 前缀（feat/fix/refactor/test/docs/chore）。
- 每次提交前确认一键门禁全绿；CI（`.github/workflows/ci.yml`）会在 push/PR 时重复执行同样门禁。
