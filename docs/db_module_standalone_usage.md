# 数据库模块独立使用指南

## 概述

[src/db](file:///E:/GitHub/Hello-Python/src/db) 模块设计为可独立使用的数据库操作库，除了配置依赖外，其他功能都可以快速复制到其他项目使用。

## 核心组件

### 1. 主要文件结构

```
db/
├── __init__.py           # 核心功能导入
├── database.py           # 数据库管理器核心功能
├── decorators.py         # 装饰器功能（事务处理等）
├── crud.py               # CRUD操作混入类
├── models.py             # 基础模型类
└── standalone_config.py  # 独立使用配置示例
```

### 2. 核心功能

- **DatabaseManager**: 数据库管理器，支持多数据库配置
- **装饰器**: [transactional](file:///E:/GitHub/Hello-Python/src/db/decorators.py#L15-L73) 和 [with_db_session](file:///E:/GitHub/Hello-Python/src/db/decorators.py#L75-L109) 用于简化数据库操作
- **CRUDMixin**: 提供基础的增删改查功能
- **BaseModel**: 基础模型类，继承CRUDMixin

## 独立使用步骤

### 1. 复制核心文件

将以下文件复制到新项目中：
```
db/
├── __init__.py
├── database.py
├── decorators.py
├── crud.py
├── models.py
└── standalone_config.py
```

### 2. 配置数据库

在新项目中创建配置文件或直接在代码中配置：

```python
from src.db import initialize_databases

# 数据库配置
DATABASE_CONFIG = {
    "default": "sqlite:///./app.db",
    "analytics": "sqlite:///./analytics.db",
}

# 初始化数据库
initialize_databases(DATABASE_CONFIG)
```

### 3. 创建模型

创建自己的数据模型，继承 [BaseModel](file:///E:/GitHub/Hello-Python/src/db/models.py#L10-L17)：

```python
from sqlalchemy import Column, String, Integer
from src.db.models import BaseModel

class User(BaseModel):
    __tablename__ = 'users'
    
    name = Column(String(50), index=True)
    email = Column(String(100), unique=True, index=True)
```

### 4. 使用数据库功能

```python
from src.db import transactional, with_db_session
from sqlalchemy.orm import Session

@transactional("default")
def create_user(db: Session, name: str, email: str):
    return User.create(db, name=name, email=email)

@with_db_session("analytics")
def list_users(db: Session):
    return User.get_all(db)
```

## 配置选项

### 环境变量

- `DATABASE_URL`: 默认数据库连接URL
- `ANALYTICS_DATABASE_URL`: 分析数据库连接URL
- `LOGS_DATABASE_URL`: 日志数据库连接URL
- `AUTO_CREATE_TABLES`: 是否自动创建表（默认为true）

### 程序化配置

```python
from src.db import initialize_databases

# 自定义配置
config = {
    "default": "postgresql://user:pass@localhost/mydb",
    "secondary": "mysql://user:pass@localhost/otherdb",
}

# 初始化
initialize_databases(config)
```

## 多数据库支持

### 装饰器参数

```python
# 指定数据库
@transactional("secondary")
def create_record(db: Session):
    # 在secondary数据库中执行
    pass

# 使用默认数据库
@transactional()
def create_default_record(db: Session):
    # 在default数据库中执行
    pass
```

### 手动会话管理

```python
from src.db import db_manager

# 获取特定数据库的会话
with db_manager.get_db_session("analytics") as db:
    users = User.get_all(db)
```

## 注意事项

1. **模型导入**: 在调用 `create_tables()` 之前，确保所有模型类已被导入
2. **表创建**: 如果禁用了自动创建表，需要手动调用 `db_manager.create_tables()`
3. **依赖管理**: 确保目标项目包含SQLAlchemy和其他必要依赖
4. **配置分离**: [standalone_config.py](file:///E:/GitHub/Hello-Python/src/db/standalone_config.py) 提供了配置示例，可根据需要自定义

## 示例项目结构

```
my_project/
├── src/
│   ├── db/              # 复制的数据库模块
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── decorators.py
│   │   ├── crud.py
│   │   ├── models.py
│   │   └── standalone_config.py
│   ├── models/          # 自定义模型
│   │   └── user.py
│   └── main.py          # 主应用
└── requirements.txt
```

## 依赖要求

确保目标项目包含以下依赖：

```txt
SQLAlchemy>=1.4.0
```

## 迁移指南

从现有项目迁移时：

1. 复制 [src/db](file:///E:/GitHub/Hello-Python/src/db) 目录到新项目
2. 移除 [example_models.py](file:///E:/GitHub/Hello-Python/src/db/example_models.py)（仅用于示例）
3. 根据需要调整配置
4. 创建自己的数据模型
5. 开始使用数据库功能