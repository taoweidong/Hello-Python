# 数据库操作工具库

这是一个独立的数据库操作工具库，可以快速复制到其他项目中使用。

## 特性

- ✅ **完全独立**：不依赖项目特定代码，可快速复制使用
- ✅ **多数据库支持**：支持配置和管理多个数据库连接
- ✅ **装饰器支持**：提供事务和会话装饰器，简化数据库操作
- ✅ **CRUD 混入**：提供基础 CRUD 操作混入类
- ✅ **基础模型**：提供带时间戳的基础模型类

## 快速开始

### 1. 复制到新项目

直接将 `db` 目录复制到你的项目根目录。

### 2. 初始化数据库

```python
from db import initialize_databases

# 配置数据库
DATABASE_CONFIG = {
    "default": "sqlite:///./app.db",
    "analytics": "sqlite:///./analytics.db",
}

# 初始化
initialize_databases(DATABASE_CONFIG)
```

### 3. 创建模型

```python
from sqlalchemy import Column, String, Integer
from db.models import BaseModel

class User(BaseModel):
    __tablename__ = 'users'
    
    name = Column(String(50), index=True)
    email = Column(String(100), unique=True, index=True)
```

### 4. 使用数据库功能

```python
from db import transactional, with_db_session, db_manager
from sqlalchemy.orm import Session

# 使用装饰器
@transactional("default")
def create_user(db: Session, name: str, email: str):
    return User.create(db, name=name, email=email)

# 使用上下文管理器
with db_manager.get_db_session("default") as db:
    users = User.get_all(db)
```

## 核心组件

- **DatabaseManager**: 数据库管理器，支持多数据库配置
- **transactional**: 事务装饰器，自动处理提交和回滚
- **with_db_session**: 会话装饰器，自动提供数据库会话
- **CRUDMixin**: CRUD 操作混入类
- **BaseModel**: 基础模型类，包含 id、created_at、updated_at 字段

## 依赖要求

- SQLAlchemy >= 1.4.0
- loguru (可选，用于日志记录)

## 文件说明

- `database.py`: 数据库管理器核心功能
- `decorators.py`: 装饰器功能
- `crud.py`: CRUD 操作混入类
- `models.py`: 基础模型类
- `example_models.py`: 示例模型（可删除）

## 注意事项

1. 在调用 `create_tables()` 之前，确保所有模型类已被导入
2. 如果不需要自动创建表，可以手动调用 `db_manager.create_tables()`
3. 确保目标项目包含必要的依赖

