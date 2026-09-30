# 使用入门指南

## 环境准备

需要 Python 3.10+ 与 [uv](https://docs.astral.sh/uv/)。

```bash
# 克隆项目
git clone <your-repo-url>
cd Hello-Python

# 创建虚拟环境并安装依赖
uv venv
.venv\Scripts\activate          # Windows；Linux/Mac: source .venv/bin/activate
uv sync --extra test
```

## 环境配置

复制模板并按需修改：

```bash
cp .env.example .env
```

常用配置项：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `APP_NAME` | Hello-Python | 应用名称 |
| `LOG_LEVEL` | INFO | 日志级别 |
| `LOG_DIR` | logs | 日志文件目录 |
| `DATABASE_URL` | sqlite:///./data/app.db | 数据库连接（默认零配置可用） |
| `DATA_INPUT_PATH` / `DATA_OUTPUT_PATH` | data/input / data/output | 数据目录 |

## 启动应用

```bash
uv run python -m src.app
```

启动过程自动完成：加载配置 → 初始化日志 → 连接数据库并建表。默认使用 SQLite，无需安装任何数据库服务。

## 命令行使用

```bash
# 查看帮助
uv run hello-python --help

# 处理 CSV 数据（min-max 归一化）
uv run hello-python process-csv --input-file data/sample_data.csv

# 数据分析（statistical / trend）
uv run hello-python analyze-data --input-file data/sample_data.csv --analysis-type statistical

# 查看应用状态
uv run hello-python status
```

## 运行示例

```bash
uv run python examples/basic_usage.py       # 基础分析流程
uv run python examples/db_usage_example.py  # 数据库/事务/多库用法
```

## 运行测试

```bash
uv run pytest tests/          # 全量测试 + 覆盖率
uv run mypy src               # 类型检查
uv run ruff check .           # 代码检查
```

## 下一步

阅读 [业务二次开发指南](development_guide.md)，了解分层约定与扩展模式（新增表、替换仓储、新增策略/命令）。
