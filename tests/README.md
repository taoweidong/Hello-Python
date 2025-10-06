# 测试目录说明

## 目录结构

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

## 运行测试

### 运行所有测试

```bash
python tests/test_runner.py
```

或者：

```bash
python -m tests.test_runner
```

### 运行单个测试文件

```bash
python -m tests.config.test_settings
python -m tests.db.test_database
# ... 其他测试文件
```

### 运行特定测试类或方法

```bash
python -m unittest tests.config.test_settings.TestConfig
python -m unittest tests.config.test_settings.TestConfig.test_config_loading
```