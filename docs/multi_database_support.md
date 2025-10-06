# 多数据库支持使用说明

## 功能概述

本数据库封装库支持多数据库操作，可以通过装饰器参数快速切换不同的数据库，而无需在每个函数调用中手动传递数据库参数。

## 核心特性

1. **多数据库配置**：支持配置多个数据库连接
2. **装饰器切换**：通过装饰器参数指定目标数据库
3. **线程安全**：每个线程可以独立设置当前数据库
4. **无缝集成**：与现有CRUD操作完全兼容

## 使用方法

### 1. 配置多个数据库

```python
from src.db import db_manager

# 添加多个数据库配置
db_manager.add_database("default", "sqlite:///./default.db")
db_manager.add_database("analytics", "sqlite:///./analytics.db")
db_manager.add_database("logs", "sqlite:///./logs.db")
```

### 2. 使用装饰器指定数据库

#### 事务装饰器
```python
from src.db import transactional

@transactional("analytics")
def create_analytics_user(db: Session, name: str, email: str):
    """在分析数据库中创建用户"""
    user = User.create(db, name=name, email=email, age=25)
    return user.id
```

#### 会话装饰器
```python
from src.db import with_db_session

@with_db_session("logs")
def log_user_action(db: Session, user_id: int, action: str):
    """在日志数据库中记录用户操作"""
    log = UserActionLog.create(db, user_id=user_id, action=action)
    return log.id
```

### 3. 手动切换数据库

```python
from src.db import db_manager

# 设置当前线程的数据库
db_manager.set_current_db_name("analytics")

# 获取指定数据库的会话
with db_manager.get_db_session("analytics") as db:
    users = User.get_all(db)
```

## 完整示例

```python
from src.db import db_manager, transactional, with_db_session
from src.db.example_models import User
from sqlalchemy.orm import Session

# 配置数据库
db_manager.add_database("default", "sqlite:///./default.db")
db_manager.add_database("analytics", "sqlite:///./analytics.db")

# 在默认数据库中创建用户
@transactional("default")
def create_user_default(db: Session, name: str, email: str):
    return User.create(db, name=name, email=email, age=25)

# 在分析数据库中创建用户
@transactional("analytics")
def create_user_analytics(db: Session, name: str, email: str):
    return User.create(db, name=name, email=email, age=30)

# 查询默认数据库中的用户
@with_db_session("default")
def list_users_default(db: Session):
    return User.get_all(db)

# 查询分析数据库中的用户
@with_db_session("analytics")
def list_users_analytics(db: Session):
    return User.get_all(db)
```

## 数据库隔离性

每个数据库完全独立，数据不会互相干扰：

```python
# 可以在不同数据库中创建同名用户
@transactional("default")
def create_user_default(db: Session, name: str):
    return User.create(db, name=name, email=f"{name}@default.com")

@transactional("analytics")
def create_user_analytics(db: Session, name: str):
    return User.create(db, name=name, email=f"{name}@analytics.com")
```

## 注意事项

1. 数据库配置需要在使用前完成
2. 每个数据库需要单独创建表结构
3. 装饰器参数是可选的，省略时使用默认数据库
4. 线程安全：每个线程独立维护数据库选择状态