"""测试配置"""

import pytest

from src.core.database import DatabaseManager
from src.core.database.base import Base

# 加载公共 fixtures（csv_test_data, test_output_dir 等）
pytest_plugins = ["tests.fixtures.test_data"]


@pytest.fixture
def sqlite_db_manager(tmp_path):
    """创建已建表的独立 sqlite 测试库（每个测试独立文件，互不影响）"""
    import src.business.models.tables  # noqa: F401  确保业务表注册到 Base.metadata

    manager = DatabaseManager(f"sqlite:///{tmp_path / 'test.db'}")
    Base.metadata.create_all(bind=manager.get_engine())
    yield manager
    manager.get_engine().dispose()
