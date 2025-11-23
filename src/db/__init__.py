# src/db/__init__.py
"""
数据库操作库初始化文件
"""

# 核心功能导入
from src.db.models import Base
from src.db.database import DatabaseManager, get_db, db_manager, initialize_databases
from src.db.decorators import transactional, with_db_session
from src.db.crud import CRUDMixin
from src.db.config import DATABASE_CONFIG, AUTO_CREATE_TABLES

# 自动初始化数据库
if AUTO_CREATE_TABLES:
    initialize_databases(DATABASE_CONFIG)

__all__ = ['DatabaseManager', 'get_db', 'transactional', 'with_db_session', 'CRUDMixin', 'Base', 'db_manager', 'initialize_databases']