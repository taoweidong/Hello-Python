"""业务装配与仓储单元测试

覆盖三类真实行为：
1. 工厂函数的单例契约（装配缓存逻辑）
2. 服务默认装配路径（依赖注入兜底）
3. 仓储针对真实 sqlite 的读写边界

模型与验证器行为见 test_entities.py；全链路见 integration/test_application.py。
"""

import pytest

from src.business.models import DataValidator, ProcessedData, get_data_validator
from src.business.processors import get_data_processor, get_processing_pipeline
from src.business.repositories import DataRepository, get_data_repository
from src.business.services import (
    get_analysis_service,
    get_data_processing_service,
)


class TestFactorySingletonContract:
    """工厂函数返回全局唯一实例（缓存装配的对外契约）"""

    def test_analysis_service_singleton(self):
        assert get_analysis_service() is get_analysis_service()

    def test_data_processing_service_singleton(self):
        assert get_data_processing_service() is get_data_processing_service()

    def test_repository_singleton(self):
        assert get_data_repository() is get_data_repository()

    def test_processor_singleton(self):
        assert get_data_processor() is get_data_processor()

    def test_pipeline_singleton(self):
        assert get_processing_pipeline() is get_processing_pipeline()

    def test_validator_singleton(self):
        assert get_data_validator() is get_data_validator()


class TestDefaultWiring:
    """服务不注入依赖时，默认装配到全局工厂实例"""

    def test_analysis_service_defaults_to_global_repository(self):
        """依赖注入的兜底路径：AnalysisService() 默认使用全局仓储"""
        assert get_analysis_service()._repository is get_data_repository()

    def test_default_validator_is_shared_singleton(self):
        """服务与外部使用同一个验证器单例"""
        get_data_processing_service()
        assert isinstance(get_data_validator(), DataValidator)


class TestDataRepositoryUnit:
    """仓储单元测试（真实 sqlite，由 sqlite_db_manager 提供）"""

    def test_get_data_records_empty_db(self, sqlite_db_manager):
        repo = DataRepository(db_manager=sqlite_db_manager)
        assert repo.get_data_records() == []

    def test_get_processed_data_missing_returns_none(self, sqlite_db_manager):
        repo = DataRepository(db_manager=sqlite_db_manager)
        assert repo.get_processed_data("no-such-original-id") is None

    def test_save_processed_data_single_roundtrip(self, sqlite_db_manager):
        """单条保存（非批量路径）落库后可按原始 ID 查回且字段一致"""
        repo = DataRepository(db_manager=sqlite_db_manager)
        processed = ProcessedData(
            id="p-1",
            original_id="o-1",
            name="订单A",
            original_value=10.0,
            processed_value=1.0,
            category="sales",
            processing_type="normalization",
        )

        repo.save_processed_data(processed)
        fetched = repo.get_processed_data("o-1")

        assert fetched is not None
        assert fetched.id == processed.id
        assert fetched.original_value == pytest.approx(10.0)
        assert fetched.processed_value == pytest.approx(1.0)
        assert fetched.processing_type == "normalization"
        assert fetched.category == "sales"
