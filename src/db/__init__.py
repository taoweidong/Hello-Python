# src/db/__init__.py
"""
数据库操作库初始化文件
"""

# 核心功能导入
from .models import Base
from .database import DatabaseManager, get_db, db_manager, initialize_databases
from .decorators import transactional, with_db_session
from .crud import CRUDMixin
from .config import DATABASE_CONFIG, AUTO_CREATE_TABLES

# 自动初始化数据库
if AUTO_CREATE_TABLES:
    initialize_databases(DATABASE_CONFIG)

__all__ = ['DatabaseManager', 'get_db', 'transactional', 'with_db_session', 'CRUDMixin', 'Base', 'db_manager', 'initialize_databases']