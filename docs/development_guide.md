# 业务二次开发指南

本指南说明项目分层约定与常见扩展模式。二次开发的原则：**业务代码只写在 business 层与 interfaces 层，core 层保持通用稳定**。

## 分层架构

```
请求 → interfaces(CLI) → business(服务/处理器) → business(仓储) → core(数据库基座) → DB
                ↘ core(配置/日志/异常) 贯穿各层
```

| 层 | 目录 | 职责 | 依赖方向 |
|----|------|------|----------|
| 核心层 | `src/core/` | 配置(Settings)、日志(loguru 封装)、异常体系、数据库基座(引擎/事务装饰器/CRUDMixin) | 不依赖其他层 |
| 业务层 | `src/business/` | 领域模型(Pydantic)、表模型(ORM)、仓储、服务、处理策略 | 只依赖 core |
| 接口层 | `src/interfaces/` | CLI 命令、输出展示 | 依赖 core + business |
| 组合根 | `src/app.py` | 启动装配：加载配置 → 初始化日志 → 连接数据库并自动建表 | 装配所有层 |

## 应用启动流程（`src/app.py`）

1. `get_settings(env_file)` 加载配置（pydantic-settings，自动读 `.env`）
2. `setup_logger(settings)` 初始化 loguru（控制台 + 文件轮转，目录取 `LOG_DIR`）
3. `initialize_database(...)` 建立数据库连接，随后 `create_tables()` **自动创建所有业务表**
4. 二次开发新增的表只要定义在 `src/business/models/tables.py`（或启动前 import），无需手写建表 SQL

## 扩展模式

### 1. 新增业务表 + 读写

```python
# src/business/models/tables.py
from sqlalchemy import Float, Mapped, String, mapped_column
from ...core.database.models import BaseModel  # 继承即拥有 CRUD 能力


class SalesOrderTable(BaseModel):
    """销售订单表"""

    __tablename__ = "sales_orders"

    order_no: Mapped[str] = mapped_column(String(50), unique=True)
    amount: Mapped[float] = mapped_column(Float, index=True)
```

同时在 `src/business/models/entities.py` 定义对应的 Pydantic 领域模型（校验/序列化），并仿照文件内已有的转换函数编写双向转换。仓储中即可使用：

```python
with self._db_manager.get_db_session() as db:
    db.add(SalesOrderTable(order_no="S001", amount=99.9))
    db.commit()
```

### 2. 替换/扩展仓储

服务层只依赖 `DataRepositoryProtocol` 接口。更换存储后端（如改用文件或外部 API）时实现同样方法签名并注入即可，服务代码零修改：

```python
from src.business.repositories import DataRepositoryProtocol


class ApiRepository:
    """满足协议的远程实现"""

    def load_data_from_csv(self, file_path: str) -> list[DataRecord]: ...
    def save_data_records(self, data_records): ...

    # ... 其余方法见协议定义


service = AnalysisService(repository=ApiRepository())
```

完整可运行示例见 `tests/fixtures/test_data.py` 的 `InMemoryRepository`。

### 3. 新增数据处理算法

在策略注册表添加函数即可，调用方自动可用，无需改任何分支：

```python
# src/business/processors/strategies.py
def square_root(values: list[float]) -> list[float]:
    return [v**0.5 for v in values]


PROCESSING_STRATEGIES["square_root"] = square_root
```

### 4. 新增 CLI 命令

```python
# src/interfaces/cli/commands.py
@cli.command(name="export-report")
@click.option("--output-file", required=True)
@click.pass_context
def export_report_cmd(ctx, output_file: str):
    """导出分析报表"""
    logger = ctx.obj["logger"]
    service = get_analysis_service()
    ...
```

命令实现保持薄：只做参数解析与输出，业务逻辑放 service/processor。

## 配置项

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `APP_NAME` / `APP_VERSION` / `APP_ENV` | Hello-Python / 1.0.0 / 自动检测 | 应用信息 |
| `LOG_LEVEL` / `LOG_DIR` | INFO / logs | 日志级别与目录 |
| `DATABASE_URL` | sqlite:///./data/app.db | 数据库连接 |
| `DATABASE_ECHO` | false | 打印 SQL |
| `DATA_INPUT_PATH` / `DATA_OUTPUT_PATH` | data/input / data/output | 数据目录 |

## 测试约定

- 单元测试靠近被测模块目录（`tests/business/`、`tests/core/`…）
- 数据库测试用 `sqlite_db_manager` fixture（独立临时库）或 `InMemoryRepository`
- 集成测试在 `tests/integration/`，演示完整链路

```bash
uv run pytest tests/                                # 全量 + 覆盖率
uv run pytest tests/business -q                     # 指定目录
```

## 打包

```bash
build/build_windows.bat <示例文件名>   # Windows，产物在 dist/
build/build_linux.sh <示例文件名>      # Linux
```

## 相关文档

- [使用入门](getting_started.md)
- [项目质量报告](project_quality_report.md)
- [优化记录](optimization_2026-09-30.md)
