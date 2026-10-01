# Hello-Python

数据分析基础项目框架：分层架构、多数据库、真实持久化、CLI 入口，开箱即用地支撑快速二次开发。

技术栈：`uv` · Python 3.10+ · Pydantic v2 · SQLAlchemy 2.0 · loguru · Click · pandas

## 质量门禁

| 工具 | 状态 |
|------|------|
| ruff（lint + format） | ✅ 强制通过 |
| mypy（`disallow_untyped_defs` + Pydantic 插件） | ✅ 强制通过 |
| pytest（107 个测试） | ✅ 强制通过 |
| 覆盖率 | ✅ CI 门禁 ≥ 80%（当前 84%） |

以上检查由 GitHub Actions（`.github/workflows/ci.yml`）在 push/PR 时自动执行。

## 项目结构

```
Hello-Python/
├── pyproject.toml           # 项目配置：依赖、脚本入口、ruff/mypy/pytest/coverage 统一配置
├── .pre-commit-config.yaml  # Pre-commit 钩子（ruff + mypy）
├── .env.example             # 环境变量模板，复制为 .env 使用
├── src/
│   ├── core/                # 核心层：配置、日志、异常、数据库基座（引擎/事务/CRUD/重试）
│   ├── business/            # 业务层：领域模型(Pydantic) + 表模型(ORM)、仓储、服务、处理器
│   ├── interfaces/          # 接口层：Click 命令行入口
│   └── app.py               # 应用组合根：装配配置/日志/数据库并自动建表
├── tests/                   # 单元测试、集成测试（独立 sqlite，互不影响）
├── examples/                # 二次开发参考示例
├── docs/                    # 文档（历史文档在 docs/archive/）
└── build/                   # PyInstaller 打包脚本
```

## 快速开始

```bash
uv venv && .venv\Scripts\activate      # Windows；Linux/Mac: source .venv/bin/activate
uv sync --extra test                   # 安装依赖（开发用 --extra develop）
cp .env.example .env                   # 按需修改
uv run python -m src.app               # 启动应用（自动建表）
```

## CLI

```bash
uv run hello-python --help
uv run hello-python process-csv --input-file data/sample_data.csv
uv run hello-python analyze-data --input-file data/sample_data.csv --analysis-type statistical
uv run hello-python status
```

## 开发

```bash
uv run python run_tests.py              # 一键质量门禁：lint + 格式 + 类型 + 单元测试
uv run python run_tests.py --tests-only # 仅单元测试（含覆盖率门禁 80%）
uv run ruff check . --fix && uv run ruff format .   # lint + 格式化
uv run mypy src                                     # 类型检查
pre-commit install                                  # 提交钩子
```

> 测试与 mock 纪律（禁止无效 mock、必须基于真实业务场景、每次变更/会话结束必须跑门禁）见 `AGENTS.md`。

## 二次开发入口

| 想做的事 | 位置 | 参考 |
|----------|------|------|
| 新增业务表（自动获得 CRUD） | `src/business/models/tables.py` | [开发指南](docs/development_guide.md) |
| 替换/扩展仓储 | 实现 `DataRepositoryProtocol` 并注入 | `tests/fixtures/test_data.py` 的 `InMemoryRepository` |
| 新增处理算法 | 在 `strategies.py` 注册策略函数 | `src/business/processors/strategies.py` |
| 新增分析服务 | `src/business/services/` | `analysis_service.py` |
| 新增 CLI 命令 | `src/interfaces/cli/commands.py` | [开发指南](docs/development_guide.md) |

## 文档

| 文档 | 说明 |
|------|------|
| [使用入门](docs/getting_started.md) | 环境配置与基本使用 |
| [业务二次开发指南](docs/development_guide.md) | 架构说明与扩展模式 |
| [项目质量报告](docs/project_quality_report.md) | 2026-09 质量评估基线 |
| [优化记录](docs/optimization_2026-09-30.md) | 本轮质量优化清单 |

## License

MIT
