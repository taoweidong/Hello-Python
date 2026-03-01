"""数据库基础设施模块

独立的数据库操作库，提供:
- 数据库连接管理
- CRUD操作基类
-装器工具
- 事务处理功能
-基础模型类

本模块设计为独立可复用组件，无需依赖项目其他代码。
可完整复制到其他项目中使用。
"""

#核功能导入
from .models import BaseModel
from .database import DatabaseManager, get_db, db_manager, initialize_databases, Base, DatabaseConfig, get_database_manager, initialize_database, DatabaseError
from .decorators import transactional, with_db_session
from .crud import CRUDMixin

__all__ = [
    'DatabaseManager', 
    'DatabaseConfig',
    'get_db', 
    'transactional', 
    'with_db_session', 
    'CRUDMixin', 
    'BaseModel',
    'Base',
    'db_manager', 
    'initialize_databases',
    'get_database_manager',
    'initialize_database',
    'DatabaseError'
]
