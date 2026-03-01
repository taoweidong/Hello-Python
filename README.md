# Python项目框架

现代化、可打包的 Python 项目结构，使用 `uv`、`loguru`、`click`、`pandas`，支持分层架构与多数据库。

## 项目结构

```
Hello-Python/
├── pyproject.toml           # 项目配置、依赖声明、脚本入口
├── pytest.ini               # 测试配置、覆盖率选项
├── mypy.ini                 # 类型检查配置
├── .ruff.toml               # Ruff 代码检查与格式化规则
├── .pre-commit-config.yaml  # Pre-commit 钩子（Ruff、mypy）
├── .env.example             # 环境变量模板，需复制为 .env 使用
├── .gitignore               # Git 忽略规则
├── README.md                # 项目说明
│
├── src/                     # 源代码
│   ├── core/                # 核心层：配置、日志、数据库基座、异常
│   ├── business/            # 业务层：模型、服务、仓储、处理器
│   ├── infrastructure/      # 基础设施层：数据库连接、ORM、CRUD
│   ├── interfaces/          # 接口层：CLI 命令行入口
│   ├── config/              # 配置模块
│   └── models/              # 数据模型
│
├── tests/                   # 单元测试、集成测试
├── examples/                # 使用示例与演示代码
├── docs/                    # 文档
├── build/                   # 打包脚本（Windows/Linux）
└── data/                    # 数据文件
```

## 快速开始

```bash
uv venv && .venv\Scripts\activate   # Windows
uv pip install -e .
cp .env.example .env
```

## 测试

```bash
# 运行所有测试
python -m pytest tests/

# 带覆盖率报告
python -m pytest tests/ --cov=src --cov-report=term-missing

# HTML 覆盖率报告
python -m pytest tests/ --cov=src --cov-report=html
```

安装测试依赖：`uv pip install -e .[test]`

## 格式化与检查

```bash
# Ruff 格式化和检查（需先安装开发依赖：uv pip install -e .[develop]）
uv run ruff check . --fix
uv run ruff format .

# mypy 类型检查
uv run mypy src

# 安装 pre-commit 钩子
pre-commit install

# 手动运行 pre-commit
pre-commit run --all-files
```

## 文档

| 文档 | 说明 |
|------|------|
| [业务二次开发指南](docs/development_guide.md) | 项目结构、初始化、打包、业务扩展 |
| [使用入门](docs/getting_started.md) | 环境配置与基本使用 |
| [多数据库支持](docs/multi_database_support.md) | 多数据库配置与使用 |
| [数据库自动初始化](docs/auto_database_initialization.md) | 数据库自动配置说明 |
| [数据库模块独立使用](docs/db_module_standalone_usage.md) | 数据库模块抽取与复用 |
