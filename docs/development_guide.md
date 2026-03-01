# 业务二次开发指南

## 项目概述

本框架提供现代化、可打包的 Python 项目结构，使用 `uv` 作为包管理器，`loguru` 进行日志记录，`click` 处理命令行接口，`pandas` 进行数据处理，并通过 `.env` 文件管理配置。所有打包生成的文件均归档到 `dist` 目录。

## 项目结构

```
Hello-Python/
├── .env.example
├── .env
├── .env.development / .env.staging / .env.production
├── pyproject.toml
├── build/
│   ├── build_linux.sh
│   └── build_windows.bat
├── src/
│   ├── core/              # 核心基础设施层
│   │   ├── config/        # 配置管理
│   │   ├── logging/       # 日志系统
│   │   ├── database/      # 数据库基础设施
│   │   └── exceptions/    # 核心异常
│   ├── business/          # 业务逻辑层
│   │   ├── models/        # 业务模型
│   │   ├── services/      # 业务服务
│   │   ├── repositories/  # 数据访问
│   │   └── processors/    # 数据处理
│   ├── infrastructure/    # 基础设施层
│   │   └── database/      # 数据库模块
│   ├── interfaces/        # 接口层
│   │   └── cli/           # 命令行接口
│   └── config/            # 配置模块
├── tests/
├── examples/
└── docs/
```

## 项目初始化

### 安装依赖

```bash
pip install uv
uv venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
uv pip install -e .
```

### 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 配置文件
```

支持基于 `APP_ENV` 的不同配置文件：`.env.development`、`.env.staging`、`.env.production`

## 运行应用（开发模式）

```bash
# 命令行入口
Hello-Python --help
analysis-tool --help

# 数据处理示例
Hello-Python process-csv --input-file data/sample.csv

# 数据库示例
python examples/db_example.py
python examples/db_multi_database_example.py
python examples/db_auto_init_example.py
```

## 打包流程

```bash
# Windows
cd build && build_windows.bat

# Linux
cd build && chmod +x build_linux.sh && ./build_linux.sh
```

打包输出位于 `dist/` 目录，包含 `Hello-Python.zip` 分发包。用户解压后可直接运行，无需手动配置。

## 核心功能

| 功能 | 说明 |
|------|------|
| 配置管理 | Pydantic Settings，支持环境变量和类型校验 |
| 数据校验 | Pydantic 模型校验 |
| 数据库 | SQLAlchemy ORM，支持多数据库、装饰器、CRUD 封装 |
| 命令行 | Click 命令行接口 |
| 日志 | loguru 统一日志，禁止使用 print |

## 依赖管理

```bash
uv pip install -e .
uv pip install package_name
uv pip install -e .[test]   # 测试依赖
uv pip install -e .[develop] # 开发工具
```

## 业务扩展示例

### 自定义数据模型

```python
# src/business/models/custom_models.py
from pydantic import BaseModel

class CustomData(BaseModel):
    id: str
    name: str
    value: float
```

### 自定义处理逻辑

```python
# src/business/processors/custom_processor.py
from src.business.processors.data_processor import DataProcessor

# 继承并扩展处理逻辑
```

### 自定义分析服务

```python
# src/business/services/custom_analysis.py
from src.business.services.analysis_service import AnalysisService

class CustomAnalysisService(AnalysisService):
    def custom_analysis(self, data):
        # 自定义分析逻辑
        pass
```

## 相关文档

- [使用入门](getting_started.md)
- [多数据库支持](multi_database_support.md)
- [数据库自动初始化](auto_database_initialization.md)
- [数据库模块独立使用](db_module_standalone_usage.md)
- [基础设施数据库模块](infrastructure_database_module.md)
