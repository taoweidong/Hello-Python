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
│       ├── example_models.py
│       └── config.py
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
├── docs/
│   ├── multi_database_support.md
│   └── auto_database_initialization.md
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

# 运行多数据库示例
python examples/db_switch_database_example.py

# 运行自动初始化数据库示例
python examples/db_auto_init_example.py
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

### 一键分发包

新的打包流程会自动创建一个包含所有必要资源的zip文件，用户解压后可直接使用：

1. 运行对应平台的打包脚本（如上所示）
2. 在 `dist/` 目录下找到 `Hello-Python.zip` 文件
3. 将zip文件发送给用户
4. 用户解压后可直接运行应用，无需手动配置

**运行打包后应用**：
1. 解压 `Hello-Python.zip` 文件
2. 进入解压后的目录
3. 根据需要编辑 `.env` 配置文件（已包含默认配置）
4. 运行应用：`run.bat` (Windows) 或 `./run.sh` (Linux)

**注意**：用户无需手动创建配置文件，`.env` 文件已包含在分发包中。

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

### 多数据库支持
项目支持多数据库操作，可以通过装饰器参数快速切换不同的数据库。详细使用说明请参见 [docs/multi_database_support.md](docs/multi_database_support.md)。

### 数据库自动初始化
数据库在应用启动时自动配置和初始化，无需手动操作。详细使用说明请参见 [docs/auto_database_initialization.md](docs/auto_database_initialization.md)。

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

### 测试目录结构

测试文件已按照src目录结构重新组织：

```
tests/
├── config/                 # 配置相关测试
│   ├── test_settings.py    # 设置模块测试
│   └── test_logging_config.py  # 日志配置测试
├── db/                     # 数据库相关测试
│   ├── test_database.py    # 数据库功能测试
│   └── test_simple.py      # 数据库简单功能测试
├── test_cli.py             # CLI测试
├── test_click_demo.py      # Click命令行工具测试
├── test_data_processor.py  # 数据处理模块测试
├── test_env_config.py      # 环境配置测试
├── test_pydantic_validation.py  # Pydantic数据验证测试
└── test_runner.py          # 测试入口文件
```

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/

# 或者使用测试入口文件运行所有测试
python tests/test_runner.py

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

1. **文件归档完美**：所有打包生成的文件仅存在于`dist/`目录，项目根目录无任何临时文件或残留
2. **一键分发**：自动创建包含所有必要资源的zip文件，用户解压后可直接使用
3. **配置完整**：`.env`配置文件已包含在分发包中，用户无需手动创建
3. **跨平台支持**：Windows和Linux的打包脚本已优化
4. **动态路径定位**：`main.py`动态定位项目根目录，确保打包后能正确导入
5. **Pydantic集成**：使用Pydantic进行配置管理和数据校验
6. **多环境配置支持**：通过`APP_ENV`环境变量控制不同环境的配置文件加载
7. **现代化依赖管理**：使用`uv`作为包管理工具，提供快速依赖解析和安装
8. **Click命令行接口**：提供丰富的命令行接口示例
9. **数据库操作库**：封装了完整的数据库操作功能
10. **多数据库支持**：支持通过装饰器参数快速切换不同数据库
11. **数据库自动初始化**：应用启动时自动配置和初始化数据库
12. **loguru日志**：统一日志处理
13. **测试覆盖率**：支持生成详细的单元测试覆盖率报告

## 最终验证

1. 执行打包脚本后，项目根目录**无任何新文件**（除`build/`目录外）
2. 打包生成的文件**仅存在于`dist/`目录**
3. 运行打包后的应用**无需手动配置**（所有必要文件已包含在分发包中）