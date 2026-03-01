"""数据访问仓库模块

提供数据访问的抽象层，处理数据的持久化和查询。
"""

from .data_repository import DataRepository, get_data_repository

__all__ = ["DataRepository", "get_data_repository"]
