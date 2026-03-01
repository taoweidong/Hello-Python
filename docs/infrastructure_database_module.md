#基础设施数据库模块文档

##概

基础设施数据库模块是一个独立的、可复用的数据库操作库，位于 `src/infrastructure/database/` 目录下。该模块设计为完全独立，不依赖项目其他代码，可以完整复制到其他项目中使用。

## 模块特点

###独性
- 不依赖项目特定代码
-可独立复制到其他项目使用
-移除了对loguru等项目特定库的依赖
- 使用Python标准库作为默认依赖

###功能完整
- 数据库连接管理
- CRUD操作基类
-装器工具
- 事务处理功能
-基础模型类

##目录结构

```
src/infrastructure/database/
├── __init__.py              #模块初始化文件
├── database.py             # 数据库管理器核心
├── models.py               #基础模型类
├── crud.py                 # CRUD操作混入类
├── decorators.py           # 数据库装饰器
├── example_models.py       # 示例模型
└── README.md               #模块说明文档
```

##核心组件

### DatabaseManager (数据库管理器)
管理多个数据库连接和会话。

```python
from src.infrastructure.database import DatabaseManager

# 创建数据库管理器
db_manager = DatabaseManager("sqlite:///./app.db")

# 添加额外数据库
db_manager.add_database("analytics", "sqlite:///./analytics.db")

# 创建表
db_manager.create_tables()
```

### BaseModel (基础模型类)
提供基础的CRUD功能和时间戳字段。

```python
from src.infrastructure.database import BaseModel
from sqlalchemy import Column, String, Integer

class User(BaseModel):
    __tablename__ = 'users'
    
    name = Column(String(50), index=True)
    email = Column(String(100), unique=True, index=True)
    age = Column(Integer)
```

###装器
提供便捷的数据库操作方式。

```python
from src.infrastructure.database import transactional, with_db_session
from sqlalchemy.orm import Session

@transactional()
def create_user(db: Session, name: str, email: str):
    """创建用户（自动处理事务）"""
    user = User.create(db, name=name, email=email, age=25)
    return user.id

@with_db_session()
def list_users(db: Session):
    """获取所有用户（自动提供数据库会话）"""
    return User.get_all(db)
```

## 使用示例

###基本使用

```python
from src.infrastructure.database import (
    DatabaseManager, 
    transactional, 
    with_db_session
)
from src.infrastructure.database.example_models import User

# 初始化数据库
db_manager = DatabaseManager()
db_manager.create_tables()

# 使用装饰器创建用户
@transactional()
def create_sample_user(db):
    user = User.create(db, name="Alice", email="alice@example.com", age=25)
    return user.id

# 使用装饰器查询用户
@with_db_session()
def get_all_users(db):
    return User.get_all(db)

#执行操作
user_id = create_sample_user()
users = get_all_users()
print(f"创建了用户，ID: {user_id}")
print(f"总用户数: {len(users)}")
```

###多数据库支持

```python
#配置多个数据库
db_manager.add_database("default", "sqlite:///./app.db")
db_manager.add_database("analytics", "sqlite:///./analytics.db")
db_manager.add_database("logs", "sqlite:///./logs.db")

# 在不同数据库中操作
@transactional("analytics")
def create_analytics_record(db):
    # 在分析数据库中创建记录
    pass

@with_db_session("logs")
def get_logs(db):
    # 从日志数据库中获取数据
    pass
```

##使用说明

要将此模块复制到其他项目中使用：

1.复整个 `src/infrastructure/database/` 目录
2.确保目标项目有以下依赖：
   - SQLAlchemy
   - Python 3.7+
3. 在目标项目中使用相对导入或调整导入路径

```python
# 在独立项目中使用
from .database import DatabaseManager, transactional, with_db_session
# 或
from infrastructure.database import DatabaseManager, transactional, with_db_session
```

## 注意事项

1. **日志配置**：模块默认使用Python标准库logging，如需使用其他日志库，可通过`set_logger()`方法配置
2. **数据库初始化**：使用前需要调用`create_tables()`方法创建表结构
3. **事务管理**：推荐使用装饰器进行事务管理，确保数据一致性
4. **线程安全**：模块支持多线程环境下的数据库操作

## API参考

详细API文档请参考各模块文件中的文档字符串。
