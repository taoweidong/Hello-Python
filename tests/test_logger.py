# tests/test_logger.py
import unittest
from src.config.logging_config import setup_logger

class TestLogger(unittest.TestCase):
    def test_logger_setup(self):
        """测试日志记录器设置"""
        logger = setup_logger()
        self.assertIsNotNone(logger)

if __name__ == '__main__':
    unittest.main()