# 测试目录说明

## 目录结构

```
tests/
├── conftest.py               # 全局 fixtures：sqlite_db_manager（独立临时库）
├── fixtures/
│   └── test_data.py          # CSV 测试数据、InMemoryRepository（协议的内存实现）
├── unit/
│   └── test_database.py      # 数据库管理器 / CRUD / 事务与重试装饰器
├── core/
│   ├── test_core_modules.py  # 配置 / 日志 / 异常
│   ├── test_app.py           # 应用启动流程
│   └── test_security.py      # URL 脱敏
├── business/
│   ├── test_business_logic.py      # 组件创建
│   ├── test_analysis_service.py    # 统计/趋势分析、数据处理服务
│   ├── test_entities.py            # 领域模型与验证器
│   └── test_strategies.py          # 处理策略
├── integration/
│   └── test_application.py   # 全链路：CSV → 入库 → 处理 → 分析 → 回读
├── interfaces/
│   └── test_cli.py           # CLI 命令
└── test_data_processor.py    # 数据处理器
```

## 约定

- 数据库测试使用 `sqlite_db_manager` fixture（pytest `tmp_path`，每个测试独立库文件）
- 服务层测试优先注入 `InMemoryRepository`（演示面向 `DataRepositoryProtocol` 替换实现）
- 覆盖率门禁：CI 要求 `--cov-fail-under=80`
