"""核心数据库基础设施模块

提供独立的数据库操作功能，可在其他项目中直接复用。
不依赖任何项目特定代码，确保完全独立性和可复用性。
"""

from .manager import DatabaseManager, get_database_manager, initialize_database
from .models import BaseModel
from .crud import CRUDMixin
from .decorators import transactional, with_db_session
from .base import Base

__all__ = [
    'DatabaseManager',
    'get_database_manager', 
    'initialize_database',
    'BaseModel',
    'CRUDMixin',
    'transactional',
    'with_db_session',
    'Base'
]