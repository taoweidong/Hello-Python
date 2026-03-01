"""测试fixtures

提供测试所需的公共fixtures和工具函数。
"""

import contextlib
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def sample_user_data() -> dict[str, Any]:
    """提供示例用户数据"""
    return {"name": "Alice", "age": 25, "city": "New York"}


@pytest.fixture
def sample_processed_user_data() -> dict[str, Any]:
    """提供示例处理后的用户数据"""
    return {"name": "Alice", "age": 25, "city": "New York", "processed": True, "processed_at": "2024-01-01T12:00:00"}


@pytest.fixture
def invalid_user_data() -> dict[str, Any]:
    """提供无效的用户数据"""
    return {
        "name": "",  # 空姓名
        "age": -5,  # 无效年龄
        "city": "   ",  # 空城市
    }


@pytest.fixture
def csv_test_data() -> Generator[dict[str, Any], None, None]:
    """创建临时CSV测试数据文件"""
    # 创建测试数据
    test_data = """name,age,city
Alice,25,New York
Bob,30,London
Charlie,35,Tokyo
Diana,28,Paris
Eve,32,Berlin"""

    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", encoding="utf-8") as f:
        f.write(test_data)
        temp_file_path = f.name

    yield {"file_path": temp_file_path, "data": test_data, "row_count": 5}

    # 清理临时文件
    with contextlib.suppress(FileNotFoundError):
        Path(temp_file_path).unlink()


@pytest.fixture
def empty_csv_file() -> Generator[str, None, None]:
    """创建空的CSV文件"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", encoding="utf-8") as f:
        f.write("")  # 空文件
        temp_file_path = f.name

    yield temp_file_path

    # 清理临时文件
    with contextlib.suppress(FileNotFoundError):
        Path(temp_file_path).unlink()


@pytest.fixture
def malformed_csv_file() -> Generator[str, None, None]:
    """创建格式错误的CSV文件"""
    malformed_data = """name,age,city
Alice,25,New York
Bob,30  #缺城市列
Charlie,35,Tokyo,extra"""  # 多的列

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", encoding="utf-8") as f:
        f.write(malformed_data)
        temp_file_path = f.name

    yield temp_file_path

    # 清理临时文件
    with contextlib.suppress(FileNotFoundError):
        Path(temp_file_path).unlink()


@pytest.fixture
def test_output_dir() -> Generator[Path, None, None]:
    """创建测试输出目录"""
    output_dir = Path("tests/temp_output")
    output_dir.mkdir(parents=True, exist_ok=True)

    yield output_dir

    # 清理输出目录
    import shutil

    with contextlib.suppress(Exception):
        shutil.rmtree(output_dir)
