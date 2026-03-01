# tests/config/test_settings.py
import os
import unittest
from unittest.mock import patch

from src.config.settings import Config, settings


class TestConfig(unittest.TestCase):
    def test_config_loading(self):
        """测试配置加载"""
        # 检查配置是否正确加载
        self.assertIsNotNone(settings.APP_NAME)
        self.assertIsNotNone(settings.LOG_LEVEL)
        self.assertIsNotNone(settings.DATA_FILE_PATH)
        self.assertIsNotNone(settings.DATABASE_URL)
        self.assertIsNotNone(settings.APP_ENV)

    def test_environment_variable_override(self):
        """测试环境变量覆盖配置"""
        # 测试环境变量覆盖
        with patch.dict(os.environ, {"APP_NAME": "TestApp", "LOG_LEVEL": "DEBUG"}):
            # 重新加载配置
            test_settings = Config()
            self.assertEqual(test_settings.APP_NAME, "TestApp")
            self.assertEqual(test_settings.LOG_LEVEL, "DEBUG")

    def test_default_values(self):
        """测试默认配置值"""
        # 清除环境变量影响
        with patch.dict(os.environ, {}, clear=True):
            test_settings = Config()
            self.assertEqual(test_settings.APP_NAME, "My Project")
            self.assertEqual(test_settings.LOG_LEVEL, "INFO")
            self.assertEqual(test_settings.APP_ENV, "development")

    def test_database_config(self):
        """测试数据库配置"""
        with patch.dict(os.environ, {"DATABASE_URL": "sqlite:///./sql/test.db"}):
            test_settings = Config()
            self.assertEqual(test_settings.DATABASE_URL, "sqlite:///./sql/test.db")

    def test_data_paths_config(self):
        """测试数据路径配置"""
        with patch.dict(os.environ, {"DATA_FILE_PATH": "./test_data/"}):
            test_settings = Config()
            self.assertEqual(test_settings.DATA_FILE_PATH, "./test_data/")


if __name__ == "__main__":
    unittest.main()
