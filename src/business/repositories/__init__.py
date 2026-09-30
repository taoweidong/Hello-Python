"""数据访问仓库模块

提供数据访问的抽象层：DataRepositoryProtocol 定义仓储接口，
DataRepository 是基于 SQLAlchemy 的默认实现。
"""

from __future__ import annotations

from .data_repository import DataRepository, DataRepositoryProtocol, RepositoryError, get_data_repository

__all__ = ["DataRepository", "DataRepositoryProtocol", "RepositoryError", "get_data_repository"]
