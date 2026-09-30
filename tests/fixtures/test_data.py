"""测试fixtures

提供测试所需的公共fixtures。
"""

import contextlib
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest

from src.business.models import AnalysisResult, DataRecord, ProcessedData
from src.business.repositories import RepositoryError


class InMemoryRepository:
    """内存仓储实现（满足 DataRepositoryProtocol）

    演示如何面向接口替换存储后端：测试与示例可直接注入本实现。
    """

    def __init__(self) -> None:
        self.records: list[DataRecord] = []
        self.processed: list[ProcessedData] = []
        self.analysis_results: list[AnalysisResult] = []

    def load_data_from_csv(self, file_path: str) -> list[DataRecord]:
        raise RepositoryError("内存仓储不支持CSV加载")

    def save_data_records(self, data_records: list[DataRecord]) -> list[DataRecord]:
        self.records.extend(data_records)
        return list(data_records)

    def save_processed_data(self, processed_data: ProcessedData) -> None:
        self.processed.append(processed_data)

    def save_processed_data_batch(self, processed_data_list: list[ProcessedData]) -> None:
        self.processed.extend(processed_data_list)

    def save_analysis_result(self, analysis_result: AnalysisResult) -> None:
        self.analysis_results.append(analysis_result)

    def get_data_records(self, limit: int = 100) -> list[DataRecord]:
        return self.records[:limit]

    def get_processed_data(self, original_id: str) -> ProcessedData | None:
        return next((item for item in self.processed if item.original_id == original_id), None)


@pytest.fixture
def in_memory_repository() -> InMemoryRepository:
    """提供内存仓储实例"""
    return InMemoryRepository()


@pytest.fixture
def analysis_csv_test_data() -> Generator[dict[str, Any], None, None]:
    """创建分析域的CSV测试数据文件（name/value/category）"""
    test_data = """name,value,category
alpha,10.0,sales
beta,20.0,sales
gamma,30.0,marketing
delta,40.0,marketing
echo,50.0,sales"""

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", encoding="utf-8") as f:
        f.write(test_data)
        temp_file_path = f.name

    yield {"file_path": temp_file_path, "data": test_data, "row_count": 5}

    with contextlib.suppress(FileNotFoundError):
        Path(temp_file_path).unlink()


@pytest.fixture
def csv_with_invalid_rows() -> Generator[str, None, None]:
    """创建含无效行的CSV（负值行应被跳过，其余正常加载）"""
    test_data = """name,value,category
ok_one,10.0,sales
bad_negative,-5.0,sales
ok_two,30.0,marketing
empty_name,,sales"""

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", encoding="utf-8") as f:
        f.write(test_data)
        temp_file_path = f.name

    yield temp_file_path

    with contextlib.suppress(FileNotFoundError):
        Path(temp_file_path).unlink()


@pytest.fixture
def empty_csv_file() -> Generator[str, None, None]:
    """创建空的CSV文件"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", encoding="utf-8") as f:
        f.write("")
        temp_file_path = f.name

    yield temp_file_path

    with contextlib.suppress(FileNotFoundError):
        Path(temp_file_path).unlink()
