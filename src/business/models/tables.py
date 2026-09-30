"""业务数据持久化表定义

基于 core.database.BaseModel 定义业务表结构，供仓储层读写。
使用 SQLAlchemy 2.0 的 Mapped 类型化声明。
二次开发新增表时，参照本文件继承 BaseModel 即可自动获得 CRUD 能力，
应用启动时会由 Base.metadata.create_all 自动建表。
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from ...core.database.models import BaseModel
from .entities import AnalysisResult, DataRecord, DataStatus, ProcessedData


class DataRecordTable(BaseModel):
    """原始数据记录表"""

    __tablename__ = "data_records"

    name: Mapped[str] = mapped_column(String(200), comment="记录名称")
    value: Mapped[float] = mapped_column(Float, index=True, comment="数值")
    category: Mapped[str] = mapped_column(String(100), default="default", index=True, comment="分类")
    status: Mapped[str] = mapped_column(String(20), default=DataStatus.PENDING.value, comment="状态")
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, comment="记录时间")
    record_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=None, comment="元数据")


class ProcessedDataTable(BaseModel):
    """处理后的数据表"""

    __tablename__ = "processed_data"

    original_id: Mapped[str] = mapped_column(String(36), index=True, comment="原始记录ID")
    name: Mapped[str] = mapped_column(String(200), comment="记录名称")
    original_value: Mapped[float] = mapped_column(Float, comment="原始数值")
    processed_value: Mapped[float] = mapped_column(Float, index=True, comment="处理后数值")
    category: Mapped[str] = mapped_column(String(100), index=True, comment="分类")
    processing_type: Mapped[str] = mapped_column(String(50), comment="处理类型")
    status: Mapped[str] = mapped_column(String(20), default=DataStatus.COMPLETED.value, comment="状态")
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, comment="处理时间")
    record_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=None, comment="处理元数据")


class AnalysisResultTable(BaseModel):
    """分析结果表"""

    __tablename__ = "analysis_results"

    analysis_type: Mapped[str] = mapped_column(String(50), index=True, comment="分析类型")
    input_data_ids: Mapped[list[str]] = mapped_column(JSON, default=list, comment="输入数据ID列表")
    result_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, comment="结果数据")
    statistics: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=None, comment="统计信息")
    duration: Mapped[float | None] = mapped_column(Float, default=None, comment="耗时(秒)")
    status: Mapped[str] = mapped_column(String(20), default=DataStatus.COMPLETED.value, comment="状态")
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, comment="分析时间")


# ---------- Pydantic 模型 <-> ORM 表对象 转换 ----------


def data_record_to_table(record: DataRecord) -> DataRecordTable:
    """将 Pydantic 数据记录转换为 ORM 表对象

    id 为空时由数据库默认值（UUID）生成；已设置时必须原样保留，
    否则会破坏调用方的 ID 引用。
    """
    return DataRecordTable(
        id=record.id,
        name=record.name,
        value=record.value,
        category=record.category,
        status=record.status.value,
        timestamp=record.timestamp,
        record_metadata=record.metadata,
    )


def table_to_data_record(row: DataRecordTable) -> DataRecord:
    """将 ORM 表对象转换为 Pydantic 数据记录"""
    return DataRecord(
        id=row.id,
        name=row.name,
        value=row.value,
        category=row.category,
        timestamp=row.timestamp or datetime.now(),
        status=DataStatus(row.status) if row.status else DataStatus.PENDING,
        metadata=row.record_metadata,
    )


def processed_data_to_table(data: ProcessedData) -> ProcessedDataTable:
    """将 Pydantic 处理后数据转换为 ORM 表对象"""
    return ProcessedDataTable(
        id=data.id,
        original_id=data.original_id,
        name=data.name,
        original_value=data.original_value,
        processed_value=data.processed_value,
        category=data.category,
        processing_type=data.processing_type,
        status=data.status.value,
        timestamp=data.timestamp,
        record_metadata=data.metadata,
    )


def table_to_processed_data(row: ProcessedDataTable) -> ProcessedData:
    """将 ORM 表对象转换为 Pydantic 处理后数据"""
    return ProcessedData(
        id=row.id,
        original_id=row.original_id,
        name=row.name,
        original_value=row.original_value,
        processed_value=row.processed_value,
        category=row.category,
        processing_type=row.processing_type,
        timestamp=row.timestamp or datetime.now(),
        status=DataStatus(row.status) if row.status else DataStatus.COMPLETED,
        metadata=row.record_metadata,
    )


def analysis_result_to_table(result: AnalysisResult) -> AnalysisResultTable:
    """将 Pydantic 分析结果转换为 ORM 表对象"""
    return AnalysisResultTable(
        analysis_type=result.analysis_type,
        input_data_ids=result.input_data_ids,
        result_data=result.result_data,
        statistics=result.statistics,
        duration=result.duration,
        status=result.status.value,
        timestamp=result.timestamp,
    )


def table_to_analysis_result(row: AnalysisResultTable) -> AnalysisResult:
    """将 ORM 表对象转换为 Pydantic 分析结果"""
    return AnalysisResult(
        id=row.id,
        analysis_type=row.analysis_type,
        input_data_ids=row.input_data_ids or [],
        result_data=row.result_data or {},
        statistics=row.statistics,
        duration=row.duration,
        timestamp=row.timestamp or datetime.now(),
        status=DataStatus(row.status) if row.status else DataStatus.COMPLETED,
    )
