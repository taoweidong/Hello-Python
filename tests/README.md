# 测试目录说明

## 一键运行

```bash
uv run python run_tests.py              # 完整门禁：ruff + 格式 + mypy + 单元测试
uv run python run_tests.py --tests-only # 仅单元测试
```

测试纪律与 mock 政策的完整规则见根目录 `AGENTS.md`。

## 目录结构

```
tests/
├── conftest.py               # 全局 fixtures：sqlite_db_manager（独立临时库）
├── fixtures/
│   └── test_data.py          # CSV 测试数据、InMemoryRepository（协议的真实第二实现）
├── unit/
│   └── test_database.py      # 数据库管理器 / CRUD / 事务与重试装饰器
├── core/
│   ├── test_core_modules.py  # 配置 / 日志 / 异常（tmp 目录隔离，真实文件写入）
│   ├── test_app.py           # 应用启动流程（含真实不可达数据库的降级路径）
│   └── test_security.py      # URL 脱敏
├── business/
│   ├── test_business_logic.py      # 工厂单例契约、DI 默认装配、仓储读写边界
│   ├── test_analysis_service.py    # 统计/趋势分析、数据处理服务
│   ├── test_entities.py            # 领域模型与验证器
│   └── test_strategies.py          # 处理策略
├── integration/
│   └── test_application.py   # 全链路：CSV → 入库 → 处理 → 分析 → 回读
├── interfaces/
│   └── test_cli.py           # CLI 端到端（零 mock：真实启动链路 + 直接查库验证）
└── test_data_processor.py    # 数据处理器与管道
```

## 零 mock 政策（强制）

1. **禁止 mock 被测逻辑本身**：不得 mock 服务/仓储/处理器再"测试"它们；只断言"方法被调用过"的测试视为无效。
2. **替身只允许在不可控边界**：不可达网络地址（如 `postgresql://...@127.0.0.1:1/...`）、真实临时文件。
3. **monkeypatch 仅限两类**（需在 docstring 说明理由）：全局单例隔离（`_settings`/`_global_logger`/`_database_manager`/`_app` 等）；无法通过真实输入触达的防御分支故障注入。
4. **持久化断言必须查落库结果**：直接查 sqlite 文件或经仓储读回，验证字段值而非调用记录。
5. `InMemoryRepository` 是 `DataRepositoryProtocol` 的真实第二实现（非 mock），用于验证面向接口设计。
6. 判断标准：**删掉被 mock 的真实实现、只留空壳，测试仍通过 ⇒ 该测试无效。**

## 约定

- 数据库测试使用 `sqlite_db_manager` fixture（pytest `tmp_path`，每个测试独立库文件）
- 服务层测试优先注入 `InMemoryRepository`（演示面向 `DataRepositoryProtocol` 替换实现）
- 覆盖率门禁：本地与 CI 均为 `--cov-fail-under=80`
