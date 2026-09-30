"""业务数据模型模块

定义业务逻辑中使用的数据模型：
- entities: Pydantic 领域模型（验证与序列化）
- tables:   SQLAlchemy 持久化表模型（ORM）
"""

from __future__ import annotations

from .entities import (
    AnalysisResult,
    DataRecord,
    DataStatus,
    DataValidator,
    ProcessedData,
    ValidationResult,
    get_data_validator,
)
from .tables import (
    AnalysisResultTable,
    DataRecordTable,
    ProcessedDataTable,
    analysis_result_to_table,
    data_record_to_table,
    processed_data_to_table,
    table_to_analysis_result,
    table_to_data_record,
    table_to_processed_data,
)

__all__ = [
    "DataRecord",
    "ProcessedData",
    "AnalysisResult",
    "DataStatus",
    "DataValidator",
    "ValidationResult",
    "get_data_validator",
    "DataRecordTable",
    "ProcessedDataTable",
    "AnalysisResultTable",
    "data_record_to_table",
    "table_to_data_record",
    "processed_data_to_table",
    "table_to_processed_data",
    "analysis_result_to_table",
    "table_to_analysis_result",
]
