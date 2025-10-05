# Python项目框架

## 项目概述

本框架提供了一个现代化、可打包的Python项目结构，所有打包生成的文件均归档到指定`dist`目录，项目根目录不产生任何临时文件或残留。框架使用`uv`作为包管理器，`loguru`进行日志记录，`click`处理命令行接口，`pandas`进行数据处理，并通过`.env`文件管理配置。

## 项目结构

```
Hello-Python/
├── .env.example
├── .env
├── .env.development
├── .env.staging
├── .env.production
├── .gitignore
├── pyproject.toml
├── build/
│   ├── build_linux.sh
│   └── build_windows.bat
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── click_demo.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   └── logging_config.py
│   ├── data_processor.py
│   ├── models.py
│   └── db/
│       ├── __init__.py
│       ├── database.py
│       ├── decorators.py
│       ├── crud.py
│       ├── models.py
│       └── example_models.py
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_logger.py
│   ├── test_data_processor.py
│   ├── test_cli.py
│   ├── test_pydantic_validation.py
│   ├── test_database.py
│   ├── test_db.py
│   └── test_env_config.py
├── examples/
│   ├── pydantic_validation_demo.py
│   ├── env_config_demo.py
│   ├── click_demo_guide.py
│   └── db_example.py
└── README.md
```

**关键说明**：
- 所有打包生成的文件**仅存在于`dist`目录**，项目根目录**无任何残留文件**
- `build/`目录仅包含打包脚本，不包含任何生成文件
- `.env.example`是配置模板，**不被包含在打包输出中**（需用户手动创建`.env`）

## 项目初始化

### 安装依赖

```bash
# 安装uv（如果未安装）
pip install uv

# 创建虚拟环境
uv venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
# source .venv/bin/activate

# 安装项目依赖
uv pip install -e .
```

### 配置环境变量

```bash
# 创建配置文件
cp .env.example .env

# 编辑配置文件
nano .env
```

项目支持基于`APP_ENV`环境变量的不同配置文件：
- `.env.development` - 开发环境配置
- `.env.staging` - 测试环境配置
- `.env.production` - 生产环境配置

## 运行应用（开发模式）

```bash
# 运行主应用
python -m src.main process_data

# 运行Click示例
python src/click_demo.py --help

# 运行数据库示例
python examples/db_example.py
```

## 打包流程

### Windows 打包

```batch
cd build
build_windows.bat
```

### Linux 打包

```bash
cd build
chmod +x build_linux.sh
./build_linux.sh
```

**运行打包后应用**：
1. 进入打包目录：`cd dist\Hello-Python` (Windows) 或 `cd dist/Hello-Python` (Linux)
2. 创建配置文件：`cp .env.example .env`
3. 编辑 `.env` 文件
4. 运行应用：`Hello-Python.exe process_data` (Windows) 或 `./Hello-Python process_data` (Linux)

## 核心功能

### 配置管理
使用Pydantic Settings进行配置管理，支持环境变量加载和类型校验。

### 数据校验
使用Pydantic模型进行数据校验，确保数据的完整性和正确性。

### 数据库集成
项目集成了SQLAlchemy ORM，支持数据库操作。

### Click命令行接口
项目包含Click库的使用示例，展示如何创建功能丰富的命令行接口。

### 数据库操作库
项目封装了一套数据库操作库，支持通过装饰器的方式快速使用，并封装了单表的增删改查功能。

## 依赖管理

项目使用 `uv` 作为包管理工具，并通过 `pyproject.toml` 文件管理依赖。

安装依赖：
```bash
# 安装项目及其依赖
uv pip install -e .

# 激活虚拟环境(Windows)
.venv\Scripts\activate

# 激活虚拟环境(Linux)
source .venv/bin/activate
```

管理依赖：
```bash
# 添加新依赖
uv pip install package_name
uv pip install package_name --upgrade

# 导出依赖列表
uv pip freeze > requirements.txt

# 从requirements.txt安装依赖
uv pip install -r requirements.txt
```

## 单元测试与覆盖率报告

项目支持运行单元测试并生成覆盖率报告：

```bash
# 运行所有测试
python -m pytest tests/

# 运行测试并生成覆盖率报告
python -m pytest tests/ --cov=src

# 运行测试并生成详细覆盖率报告
python -m pytest tests/ --cov=src --cov-report=html

# 运行测试并检查覆盖率阈值
python -m pytest tests/ --cov=src --cov-fail-under=70
```

如果遇到依赖问题，请先安装测试依赖：

```bash
# 安装测试依赖
uv pip install pytest pytest-cov pytest-html

# 或者安装所有可选依赖
uv pip install -e .[test]
```

也可以使用 coverage 命令直接生成报告：

```bash
# 运行测试并生成覆盖率数据
python -m pytest tests/ --cov=src --cov-report=

# 生成详细报告
python -m coverage report

# 生成HTML报告
python -m coverage html

# 查看报告
# 打开 htmlcov/index.html 查看详细覆盖率报告
```

覆盖率报告将生成在 `htmlcov/` 目录中，可以通过浏览器打开 `htmlcov/index.html` 查看详细报告。

## 优势总结

1. **文件归档完美**：所有打包生成的文件仅存在于`dist/Hello-Python/`，项目根目录无任何临时文件或残留
2. **环境安全**：`.env.example`被打包到`dist/Hello-Python/`，提供配置模板
3. **跨平台支持**：Windows和Linux的打包脚本已优化
4. **动态路径定位**：`main.py`动态定位项目根目录，确保打包后能正确导入
5. **Pydantic集成**：使用Pydantic进行配置管理和数据校验
6. **多环境配置支持**：通过`APP_ENV`环境变量控制不同环境的配置文件加载
7. **现代化依赖管理**：使用`uv`作为包管理工具，提供快速依赖解析和安装
8. **Click命令行接口**：提供丰富的命令行接口示例
9. **数据库操作库**：封装了完整的数据库操作功能
10. **loguru日志**：统一日志处理
11. **测试覆盖率**：支持生成详细的单元测试覆盖率报告

## 最终验证

1. 执行打包脚本后，项目根目录**无任何新文件**（除`build/`目录外）
2. 打包生成的文件**仅存在于`dist/Hello-Python/`**
3. 运行打包后的应用**无需修改任何配置**（只需创建`.env`）