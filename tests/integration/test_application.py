"""集成测试

验证 core + business 全链路：CSV 加载 → 入库 → 处理 → 分析 → 持久化查询。
使用 tmp_path 独立 sqlite 文件，测试间完全隔离。
"""

from pathlib import Path

import pytest

from src.business.models import DataRecord, tables  # noqa: F401  tables 确保业务表注册到 Base.metadata
from src.business.repositories import DataRepository, RepositoryError
from src.business.services import AnalysisError, AnalysisService, DataProcessingService
from src.core.database import DatabaseManager
from src.core.database.base import Base


@pytest.fixture
def integration_db(tmp_path: Path) -> DatabaseManager:
    """创建独立的集成测试数据库（已建业务表）"""
    manager = DatabaseManager(f"sqlite:///{tmp_path / 'integration.db'}")
    Base.metadata.create_all(bind=manager.get_engine())
    return manager


class TestDataPipelineIntegration:
    """数据管道集成测试"""

    def test_csv_to_persistence_to_analysis(self, integration_db, analysis_csv_test_data):
        """完整链路：加载CSV → 原始记录入库 → 处理入库 → 统计分析入库"""
        repository = DataRepository(db_manager=integration_db)

        # 1. 加载并入库原始记录
        records = repository.load_data_from_csv(analysis_csv_test_data["file_path"])
        assert len(records) == analysis_csv_test_data["row_count"]

        saved = repository.save_data_records(records)
        assert all(record.id is not None for record in saved), "入库后记录应携带数据库ID"

        # 2. 处理数据（内部会批量保存处理结果）
        service = DataProcessingService(repository=repository)
        processed = service.process_data_records(saved, "normalization")
        assert len(processed) == len(saved)

        # 3. 处理结果已持久化，可按原始ID查询
        fetched = repository.get_processed_data(processed[0].original_id)
        assert fetched is not None
        assert fetched.name == processed[0].name
        assert fetched.processing_type == "normalization"

        # 4. 统计分析（结果入库）
        analysis = AnalysisService(repository=repository).perform_statistical_analysis(saved)
        assert analysis.statistics is not None
        assert analysis.statistics["count"] == len(saved)

    def test_get_data_records_roundtrip(self, integration_db, analysis_csv_test_data):
        """原始记录保存后可查询回读"""
        repository = DataRepository(db_manager=integration_db)
        records = repository.load_data_from_csv(analysis_csv_test_data["file_path"])
        repository.save_data_records(records)

        fetched = repository.get_data_records(limit=100)
        assert len(fetched) == analysis_csv_test_data["row_count"]
        assert {record.name for record in fetched} == {record.name for record in records}

    def test_invalid_rows_skipped_not_fatal(self, integration_db, csv_with_invalid_rows):
        """无效行（负值/空名称）跳过并告警，不中断整体加载"""
        repository = DataRepository(db_manager=integration_db)
        records = repository.load_data_from_csv(csv_with_invalid_rows)
        assert len(records) == 2  # ok_one / ok_two
        assert all(record.value >= 0 for record in records)

    def test_load_missing_csv_raises(self, integration_db):
        """加载不存在的文件应抛出 RepositoryError"""
        repository = DataRepository(db_manager=integration_db)
        with pytest.raises(RepositoryError, match="数据文件不存在"):
            repository.load_data_from_csv("no_such_file.csv")

    def test_analysis_empty_input_raises(self, integration_db):
        """空数据触发 AnalysisError，且不被二次包裹"""
        service = AnalysisService(repository=DataRepository(db_manager=integration_db))
        with pytest.raises(AnalysisError, match="数据记录为空"):
            service.perform_statistical_analysis([])

    def test_di_injection(self, integration_db):
        """服务依赖可注入：同一数据库上各组件共享数据"""
        repository = DataRepository(db_manager=integration_db)
        processing = DataProcessingService(repository=repository)
        analysis = AnalysisService(repository=repository)

        records = repository.save_data_records(
            [DataRecord(name=f"item_{i}", value=float(i), category="demo") for i in range(1, 6)]
        )
        processed = processing.process_data_records(records, "standardization")
        result = analysis.perform_statistical_analysis(records)

        assert len(processed) == 5
        assert result.statistics["mean"] == 3.0
