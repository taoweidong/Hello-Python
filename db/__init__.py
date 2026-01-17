# db/__init__.py
"""
数据库操作库初始化文件
独立工具库，可快速复制到其他项目使用
"""

# 核心功能导入
from .models import BaseModel
from .database import DatabaseManager, get_db, db_manager, initialize_databases, Base, DatabaseConfig
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
    'initialize_databases'
]