# tests/test_config.py
import unittest
import os
from src.config.settings import settings

class TestConfig(unittest.TestCase):
    def test_config_loading(self):
        """测试配置加载"""
        # 检查配置是否正确加载
        self.assertIsNotNone(settings.APP_NAME)
        self.assertIsNotNone(settings.LOG_LEVEL)
        self.assertIsNotNone(settings.DATA_FILE_PATH)
        self.assertIsNotNone(settings.DATABASE_URL)
        self.assertIsNotNone(settings.APP_ENV)

if __name__ == '__main__':
    unittest.main()