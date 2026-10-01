"""数据仓库实现

提供数据访问的抽象层：CSV 加载、持久化读写。
默认基于 SQLAlchemy 实现，二次开发可面向 DataRepositoryProtocol 替换任意存储后端。
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

import pandas as pd

from ...core.database import DatabaseManager, get_database_manager
from ...core.exceptions import CoreException
from ...core.logging import get_logger
from ..models import (
    AnalysisResult,
    DataRecord,
    ProcessedData,
    analysis_result_to_table,
    data_record_to_table,
    processed_data_to_table,
    table_to_data_record,
    table_to_processed_data,
)
from ..models.tables import DataRecordTable, ProcessedDataTable


class RepositoryError(CoreException):
    """仓库错误异常"""


class DataRepositoryProtocol(Protocol):
    """数据仓储接口（结构化类型）

    二次开发时，服务层只依赖本接口；替换存储后端（数据库/文件/API）
    只需提供满足同样方法签名的实现并注入即可。
    """

    def load_data_from_csv(self, file_path: str) -> list[DataRecord]: ...

    def save_data_records(self, data_records: list[DataRecord]) -> list[DataRecord]: ...

    def save_processed_data(self, processed_data: ProcessedData) -> None: ...

    def save_processed_data_batch(self, processed_data_list: list[ProcessedData]) -> None: ...

    def save_analysis_result(self, analysis_result: AnalysisResult) -> None: ...

    def get_data_records(self, limit: int = 100) -> list[DataRecord]: ...

    def get_processed_data(self, original_id: str) -> ProcessedData | None: ...


class DataRepository:
    """基于 SQLAlchemy 的数据仓库（DataRepositoryProtocol 的默认实现）"""

    def __init__(self, db_manager: DatabaseManager | None = None) -> None:
        """
        Args:
            db_manager: 数据库管理器，默认使用全局实例；测试时可注入独立的内存库管理器
        """
        self._manager_ref = db_manager
        self._logger = get_logger()

    @property
    def _db_manager(self) -> DatabaseManager:
        """惰性解析数据库管理器

        构造仓储不应依赖数据库驱动的可用性（例如未安装 psycopg2 时
        status 等不涉及库操作的命令仍应正常工作），首次真正使用时才创建。
        """
        if self._manager_ref is None:
            self._manager_ref = get_database_manager()
        return self._manager_ref

    def load_data_from_csv(self, file_path: str) -> list[DataRecord]:
        """从CSV文件加载数据

        无效行（字段缺失/类型不符）会跳过并记录警告，不会中断整体加载。

        Args:
            file_path:CSV文件路径

        Returns:
            List[DataRecord]:数据记录列表

        Raises:
            RepositoryError:文件不存在或读取失败时
        """
        path = Path(file_path)
        if not path.exists():
            raise RepositoryError(f"数据文件不存在: {file_path}")

        try:
            df = pd.read_csv(path)
        except Exception as e:
            raise RepositoryError(f"CSV 文件读取失败: {file_path}") from e

        records: list[DataRecord] = []
        for row in df.to_dict("records"):
            try:
                raw_name = row.get("name", "")
                raw_value = row.get("value", 0)
                # pandas 把缺失值读成 NaN，NaN 能绕过常规比较，必须显式拒绝
                if pd.isna(raw_name) or pd.isna(raw_value):
                    raise ValueError("name/value 存在缺失值")
                records.append(
                    DataRecord(
                        name=str(raw_name),
                        value=float(raw_value),
                        category=str(row.get("category", "default")),
                        metadata={"source": "csv", "file": file_path},
                    )
                )
            except Exception as e:
                self._logger.warning(f"跳过无效数据行: {e}")

        self._logger.info(f"CSV 加载完成: {len(records)}/{len(df)} 行有效")
        return records

    def save_data_records(self, data_records: list[DataRecord]) -> list[DataRecord]:
        """批量保存原始数据记录，返回带数据库 ID 的记录

        Args:
            data_records:数据记录列表

        Returns:
            List[DataRecord]:携带数据库生成 ID 的记录列表

        Raises:
            RepositoryError:保存失败时
        """
        if not data_records:
            return []
        try:
            with self._db_manager.get_db_session() as db:
                rows = [data_record_to_table(item) for item in data_records]
                db.add_all(rows)
                db.commit()
                result = [table_to_data_record(row) for row in rows]
            self._logger.info(f"批量保存数据记录，数量: {len(result)}")
            return result
        except Exception as e:
            raise RepositoryError("批量保存数据记录失败") from e

    def save_processed_data(self, processed_data: ProcessedData) -> None:
        """保存单条处理后的数据

        Args:
            processed_data:处理后的数据

        Raises:
            RepositoryError:保存失败时
        """
        self.save_processed_data_batch([processed_data])

    def save_processed_data_batch(self, processed_data_list: list[ProcessedData]) -> None:
        """批量保存处理后的数据

        Args:
            processed_data_list:处理后的数据列表

        Raises:
            RepositoryError:保存失败时
        """
        if not processed_data_list:
            return
        try:
            with self._db_manager.get_db_session() as db:
                for item in processed_data_list:
                    db.add(processed_data_to_table(item))
                db.commit()
            self._logger.info(f"批量保存处理后数据，数量: {len(processed_data_list)}")
        except Exception as e:
            raise RepositoryError("批量保存处理后数据失败") from e

    def save_analysis_result(self, analysis_result: AnalysisResult) -> None:
        """保存分析结果

        Args:
            analysis_result:分析结果

        Raises:
            RepositoryError:保存失败时
        """
        try:
            with self._db_manager.get_db_session() as db:
                db.add(analysis_result_to_table(analysis_result))
                db.commit()
            self._logger.debug(f"保存分析结果: {analysis_result.id}")
        except Exception as e:
            raise RepositoryError("保存分析结果失败") from e

    def get_data_records(self, limit: int = 100) -> list[DataRecord]:
        """按创建时间倒序获取数据记录

        Args:
            limit:返回记录数上限

        Returns:
            List[DataRecord]:数据记录列表

        Raises:
            RepositoryError:查询失败时
        """
        try:
            with self._db_manager.get_db_session() as db:
                rows = DataRecordTable.get_all(db, limit=limit, order_by=DataRecordTable.created_at.desc())
                return [table_to_data_record(row) for row in rows]
        except Exception as e:
            raise RepositoryError("查询数据记录失败") from e

    def get_processed_data(self, original_id: str) -> ProcessedData | None:
        """根据原始ID获取处理后的数据

        Args:
            original_id:原始数据ID

        Returns:
            ProcessedData | None:处理后的数据，不存在时返回 None

        Raises:
            RepositoryError:查询失败时
        """
        try:
            with self._db_manager.get_db_session() as db:
                row = db.query(ProcessedDataTable).filter(ProcessedDataTable.original_id == original_id).first()
                return table_to_processed_data(row) if row else None
        except Exception as e:
            raise RepositoryError("查询处理后数据失败") from e


# 全局数据仓库实例
_data_repository: DataRepository | None = None


def get_data_repository() -> DataRepository:
    """获取全局数据仓库实例

    Returns:
        DataRepository:数据仓库实例
    """
    global _data_repository
    if _data_repository is None:
        _data_repository = DataRepository()
    return _data_repository
