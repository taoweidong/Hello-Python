# tests/test_env_config.py
import unittest
import os
import tempfile
from src.config import settings

class TestEnvConfig(unittest.TestCase):
    def test_config_files_exist(self):
        """测试配置文件存在性"""
        # 检查各种环境配置文件是否存在
        self.assertTrue(os.path.exists(".env.production"))
        self.assertTrue(os.path.exists(".env.staging"))
        self.assertTrue(os.path.exists(".env.development"))
        
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