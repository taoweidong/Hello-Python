"""集成测试

测试应用程序各组件之间的集成。
"""

# 导入测试fixtures
import sys

import pandas as pd
import pytest

from src.config import get_config_manager, setup_logger
from src.infrastructure.database import get_database_manager, initialize_database
from src.models import ProcessedUserData, UserData
from src.services import get_data_processor

sys.path.append("tests/fixtures")


class TestApplicationIntegration:
    """应用程序集成测试"""

    @pytest.fixture
    def app_components(self):
        """设置应用程序组件"""
        # 初始化配置
        config_manager = get_config_manager()
        config = config_manager.load_configuration()

        # 设置日志
        logger = setup_logger(config)

        # 初始化数据库
        initialize_database(default_url="sqlite:///:memory:")

        # 获取数据处理器
        data_processor = get_data_processor()

        return {"config": config, "logger": logger, "data_processor": data_processor}

    def test_config_and_logger_integration(self, app_components):
        """测试配置和日志集成"""
        config = app_components["config"]
        logger = app_components["logger"]

        assert config is not None
        assert logger is not None

        # 验证配置值
        assert hasattr(config, "APP_NAME")
        assert hasattr(config, "LOG_LEVEL")

        # 验证日志功能
        logger.info("集成测试日志消息")

    def test_data_processing_pipeline(self, app_components, csv_test_data):
        """测试数据处理完整流程"""
        data_processor = app_components["data_processor"]

        # 1. 加载数据
        df = data_processor.load_data(csv_test_data["file_path"])
        assert len(df) == csv_test_data["row_count"]

        # 2.验证数据模型
        for _, row in df.iterrows():
            user_data = UserData(name=str(row["name"]), age=int(row["age"]), city=str(row["city"]))
            assert user_data.name is not None
            assert user_data.age >= 0
            assert user_data.city is not None

        # 3.处理数据
        processed_df = data_processor.process_data(df)
        assert "processed" in processed_df.columns
        assert "processed_at" in processed_df.columns
        assert processed_df["processed"].all()

        # 4.验证处理后的数据模型
        for _, row in processed_df.iterrows():
            processed_data = ProcessedUserData(
                name=str(row["name"]), age=int(row["age"]), city=str(row["city"]), processed=bool(row["processed"])
            )
            assert processed_data.processed is True
            assert processed_data.processed_at is not None

        # 5.检查计数器
        assert data_processor.processed_count == len(processed_df)

    def test_error_handling_integration(self, app_components):
        """测试错误处理集成"""
        data_processor = app_components["data_processor"]

        # 测试文件不存在错误
        with pytest.raises(Exception) as exc_info:
            data_processor.load_data("nonexistent.csv")
        assert "不存在" in str(exc_info.value) or "not found" in str(exc_info.value).lower()

        # 测试数据验证错误
        invalid_data = pd.DataFrame(
            {
                "name": ["Alice", ""],  # 第二行有空姓名
                "age": [25, -5],  # 第二行有无效年龄
                "city": ["New York", "London"],
            }
        )

        with pytest.raises(Exception) as exc_info:
            data_processor.process_data(invalid_data)
        assert "验证" in str(exc_info.value) or "validation" in str(exc_info.value).lower()

    def test_configuration_based_processing(self, app_components, csv_test_data, test_output_dir):
        """测试基于配置的数据处理"""
        _ = app_components["config"]  # 验证 config 存在
        data_processor = app_components["data_processor"]

        # 使用配置中的数据文件路径
        input_path = csv_test_data["file_path"]
        output_path = test_output_dir / "config_based_output.csv"

        # 处理数据
        df = data_processor.load_data(input_path)
        processed_df = data_processor.process_data(df)
        data_processor.save_data(processed_df, str(output_path))

        # 验证结果
        assert output_path.exists()
        result_df = pd.read_csv(output_path)
        assert len(result_df) == len(processed_df)
        assert "processed" in result_df.columns


class TestDatabaseIntegration:
    """数据库集成测试"""

    @pytest.fixture
    def database_components(self):
        """设置数据库组件"""
        # 初始化数据库
        initialize_database(default_url="sqlite:///:memory:")
        database_manager = get_database_manager()

        return {"database_manager": database_manager}

    def test_database_connection_and_operations(self, database_components):
        """测试数据库连接和操作"""
        db_manager = database_components["database_manager"]

        # 测试连接
        assert db_manager.test_connection() is True

        # 测试数据库信息
        info = db_manager.get_database_info()
        assert info["name"] == "default"
        assert info["connected"] is True

        # 测试表创建
        db_manager.create_tables()

        # 测试获取引擎
        engine = db_manager.get_engine()
        assert engine is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
