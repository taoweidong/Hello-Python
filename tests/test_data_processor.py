"""数据处理器测试"""

import pytest

from src.business.models import DataRecord
from src.business.processors.data_processor import DataProcessingPipeline, DataProcessor, ProcessingError
from src.business.repositories import DataRepository


@pytest.fixture
def processor(sqlite_db_manager) -> DataProcessor:
    """注入真实 sqlite 仓储的数据处理器（持久化路径可验证）"""
    return DataProcessor(repository=DataRepository(db_manager=sqlite_db_manager))


class TestDataProcessor:
    """数据处理器测试"""

    def test_load_and_process_csv_persists(self, processor, analysis_csv_test_data):
        """CSV 加载 → 归一化处理 → 结果落库"""
        processed = processor.load_and_process_csv(analysis_csv_test_data["file_path"])

        assert len(processed) == analysis_csv_test_data["row_count"]
        assert all(0.0 <= item.processed_value <= 1.0 for item in processed)
        assert processor.processed_count == len(processed)

    def test_processed_count_reset(self, processor, analysis_csv_test_data):
        processor.load_and_process_csv(analysis_csv_test_data["file_path"])
        processor.reset_counters()
        assert processor.processed_count == 0

    def test_missing_file_raises_processing_error(self, processor):
        with pytest.raises(ProcessingError):
            processor.load_and_process_csv("no_such_file.csv")


class TestDataProcessingPipeline:
    """处理管道测试"""

    def test_empty_pipeline_returns_original(self):
        pipeline = DataProcessingPipeline()
        records = []
        assert pipeline.process(records) is records

    def test_steps_applied_in_order(self):
        """多步骤按添加顺序执行，且每步真实变换数据"""
        records = [DataRecord(name=f"r{i}", value=float(i), category="keep" if i % 2 else "drop") for i in range(4)]

        def filter_keep(step_records):
            return [record for record in step_records if record.category == "keep"]

        def uppercase_names(step_records):
            return [DataRecord(**{**record.model_dump(), "name": record.name.upper()}) for record in step_records]

        pipeline = DataProcessingPipeline().add_step(filter_keep).add_step(uppercase_names)
        result = pipeline.process(records)

        assert [record.name for record in result] == ["R1", "R3"]

    def test_add_step_returns_self_and_clear_empties(self):
        """链式调用契约；清空后管道恢复直通行为"""
        pipeline = DataProcessingPipeline()
        assert pipeline.add_step(lambda step_records: step_records) is pipeline

        pipeline.clear()
        records = [DataRecord(name="a", value=1.0, category="c")]
        assert pipeline.process(records) is records

    def test_step_failure_wraps_in_processing_error(self):
        def broken(step_records):
            raise RuntimeError("boom")

        pipeline = DataProcessingPipeline().add_step(broken)
        with pytest.raises(ProcessingError, match="处理步骤 1"):
            pipeline.process([])
