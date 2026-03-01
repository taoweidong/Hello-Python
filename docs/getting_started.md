# 使用入门指南

## 项目概述

Hello-Python是一个Python数据分析项目初始化模板，采用分层架构设计，提供标准的项目结构和组件，便于快速开发数据分析应用。

##安和配置

### 1. 环境准备

```bash
#克项目
git clone <your-repo-url>
cd Hello-Python

# 创建虚拟环境
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

#安装依赖
pip install -e .
```

### 2.环境配置

创建或编辑 `.env` 文件：

```bash
#复配置模板
cp .env.example .env

#编辑配置文件
nano .env
```

支持的环境：`development`、`testing`、`staging`、`production`

## 项目架构

###目结构结构

```
src/
├── app.py              #应用入口
├── core/               #核心基础设施层
│   ├── config/        #配置管理
│   ├── logging/       # 日志系统
│   ├── database/      # 数据库基础设施
│  └── exceptions/    #核心异常
├── business/           # 业务逻辑层
│   ├── models/        # 数据模型
│   ├── services/      # 业务服务
│   ├── repositories/  # 数据访问
│  └── processors/   # 数据处理
└── interfaces/        #接口层
   └── cli/          #命行接口
```

### 分层说明

1. **核心层 (core)**：提供基础设施组件，完全独立可复用
2. **业务层 (business)**：包含业务逻辑和数据处理
3. **接口层 (interfaces)**：提供用户交互接口

##基本使用

### 1.命令行使用

```bash
# 查看帮助
Hello-Python --help

#处理CSV数据
Hello-Python process-csv --input-file data/sample.csv

# 数据分析
Hello-Python analyze-data --input-file data/sample.csv --analysis-type statistical

# 查看应用状态
Hello-Python status

# 重置计数器
Hello-Python reset
```

### 2.编程接口使用

```python
from src.app import initialize_app
from src.business.processors import get_data_processor
from src.business.services import get_analysis_service

# 初始化应用
app = initialize_app()

# 数据处理
processor = get_data_processor()
processed_data = processor.load_and_process_csv('data/input.csv')

# 数据分析
analysis_service = get_analysis_service()
result = analysis_service.perform_statistical_analysis(data_records)
```

##配置管理

###环境变量

```bash
#应用配置
APP_NAME=MyAnalysisApp
APP_VERSION=1.0.0
APP_ENV=development

# 日志配置
LOG_LEVEL=INFO
LOG_FORMAT={time:YYYY-MM-DD HH:mm:ss} | {level} | {message}

# 数据库配置
DATABASE_URL=sqlite:///./app.db
DATABASE_ECHO=false

# 数据路径
DATA_INPUT_PATH=data/input
DATA_OUTPUT_PATH=data/output
```

###多环境支持

不同环境使用不同的配置文件：
- `.env` - 开发环境
- `.env.testing` -测试环境  
- `.env.staging` -环境
- `.env.production` - 生产环境

##扩例

### 自定义数据模型

```python
# src/business/models/custom_models.py
from pydantic import BaseModel

class CustomData(BaseModel):
    id: str
    name: str
    value: float
    custom_field: str
```

### 自定义处理逻辑

```python
# src/business/processors/custom_processor.py
from src.business.processors import DataProcessingPipeline

def custom_processing_step(data_records):
    # 自定义处理逻辑
    return processed_records

# 使用自定义处理步骤
pipeline = DataProcessingPipeline()
pipeline.add_step(custom_processing_step)
```

### 自定义分析服务

```python
# src/business/services/custom_analysis.py
from src.business.services import AnalysisService

class CustomAnalysisService(AnalysisService):
    def custom_analysis(self, data):
        # 自定义分析逻辑
        pass
```

##测试

运行测试：

```bash
#运行所有测试
pytest tests/

#运行特定模块测试
pytest tests/core/
pytest tests/business/

# 生成覆盖率报告
pytest tests/ --cov=src --cov-report=html
```

## 最佳实践

1. **保持分层清晰**：各层职责明确，避免跨层调用
2. **使用配置管理**：通过环境变量和配置文件管理设置
3. **统一异常处理**：使用核心异常基类
4. **日志记录**：使用统一的日志接口
5. **数据验证**：使用Pydantic进行数据验证

##常见问题

### 1.配置文件找不到

确保 `.env` 文件存在，或使用 `--env-file` 参数指定配置文件。

### 2. 数据库连接失败

检查 `DATABASE_URL`配置是否正确，确保数据库服务可用。

### 3. 依赖安装失败

确保使用支持的Python版本，尝试升级pip：`pip install --upgrade pip`

##进学习

- 查看 `examples/` 目录中的完整示例
-源代码了解具体实现
-参测试测试用例了解使用方法