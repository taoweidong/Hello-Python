# 数据库自动初始化功能

## 功能概述

数据库自动初始化功能允许在应用启动时自动配置和初始化多个数据库，无需在每次使用时手动初始化。

## 核心特性

1. **自动配置**：应用启动时自动加载数据库配置
2. **表自动创建**：自动为所有配置的数据库创建表结构
3. **环境变量支持**：通过环境变量配置数据库连接
4. **零配置使用**：初始化后可直接使用数据库功能

## 配置文件

数据库配置在 [src/db/config.py](file:///E:/GitHub/Hello-Python/src/db/config.py) 中定义：

```python
# 数据库配置
DATABASE_CONFIG = {
    "default": os.getenv("DATABASE_URL", "sqlite:///./app.db"),
    "analytics": os.getenv("ANALYTICS_DATABASE_URL", "sqlite:///./analytics.db"),
    "logs": os.getenv("LOGS_DATABASE_URL", "sqlite:///./logs.db"),
}

# 是否在初始化时自动创建表
AUTO_CREATE_TABLES = os.getenv("AUTO_CREATE_TABLES", "true").lower() == "true"
```

## 环境变量配置

可以通过以下环境变量自定义数据库配置：

- `DATABASE_URL` - 默认数据库连接URL
- `ANALYTICS_DATABASE_URL` - 分析数据库连接URL
- `LOGS_DATABASE_URL` - 日志数据库连接URL
- `AUTO_CREATE_TABLES` - 是否自动创建表（默认为true）

## 使用方法

### 1. 基本使用

数据库在应用启动时自动初始化，可直接使用：

```python
from src.db import transactional, with_db_session

@transactional("default")
def create_user(db: Session, name: str, email: str):
    return User.create(db, name=name, email=email)

@with_db_session("analytics")
def list_analytics_users(db: Session):
    return User.get_all(db)
```

### 2. 自定义配置

可以通过修改 [src/db/config.py](file:///E:/GitHub/Hello-Python/src/db/config.py) 文件来自定义数据库配置：

```python
# src/db/config.py
DATABASE_CONFIG = {
    "default": "sqlite:///./my_app.db",
    "analytics": "postgresql://user:pass@localhost/analytics",
    "logs": "mysql://user:pass@localhost/logs",
}
```

### 3. 手动初始化

如果需要手动控制初始化过程，可以禁用自动初始化：

```bash
export AUTO_CREATE_TABLES=false
```

然后在代码中手动调用：

```python
from src.db import initialize_databases, DATABASE_CONFIG

# 手动初始化
initialize_databases(DATABASE_CONFIG)
```

## 完整示例

```python
# examples/db_auto_init_example.py
from src.db import transactional, with_db_session
from src.db.example_models import User
from sqlalchemy.orm import Session

@transactional("default")
def create_user_default(db: Session, name: str, email: str):
    """在默认数据库中创建用户"""
    return User.create(db, name=name, email=email, age=25)

@with_db_session("analytics")
def list_users_analytics(db: Session):
    """列出分析数据库中的所有用户"""
    return User.get_all(db)

# 直接使用，无需初始化
user_id = create_user_default("Alice", "alice@example.com")
users = list_users_analytics()
```

## 注意事项

1. 数据库配置在应用启动时加载，运行时修改配置文件不会生效
2. 表结构基于模型定义自动创建
3. 如果禁用了自动创建表功能，需要手动调用 `create_tables()` 方法
4. 确保数据库文件路径有写入权限