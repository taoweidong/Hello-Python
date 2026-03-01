"""核心模块测试

测试核心基础设施模块的功能。
"""

import pytest
from unittest.mock import patch, mock_open
import os
from pathlib import Path

from src.core.config import Settings, get_settings, detect_environment
from src.core.logging import Logger, get_logger, setup_logger
from src.core.exceptions import CoreException, ConfigurationError


class TestCoreConfig:
    """核心配置测试"""
    
    def test_settings_default_values(self):
        """测试默认配置值"""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            assert settings.APP_NAME == "My Project"
            assert settings.LOG_LEVEL == "INFO"
            assert settings.APP_ENV.value == "development"
    
    def test_settings_custom_values(self):
        """测试自定义配置值"""
        settings = Settings(
            APP_NAME="TestApp",
            LOG_LEVEL="DEBUG",
            APP_ENV="production"
        )
        assert settings.APP_NAME == "TestApp"
        assert settings.LOG_LEVEL == "DEBUG"
        assert settings.APP_ENV.value == "production"
    
    def test_environment_detection(self):
        """测试环境检测"""
        with patch.dict(os.environ, {"APP_ENV": "staging"}):
            env = detect_environment()
            assert env.value == "staging"


class TestCoreLogging:
    """核心日志测试"""
    
    def test_logger_creation(self):
        """测试日志器创建"""
        logger = Logger()
        assert logger is not None
        assert not logger.is_configured
    
    def test_logger_setup(self):
        """测试日志器设置"""
        logger = Logger()
        logger.setup()
        assert logger.is_configured


class TestCoreExceptions:
    """核心异常测试"""
    
    def test_core_exception_creation(self):
        """测试核心异常创建"""
        exception = CoreException("测试错误", "TEST_ERROR")
        assert str(exception) == "[TEST_ERROR] 测试错误"
    
    def test_configuration_error(self):
        """测试配置错误"""
        exception = ConfigurationError("配置错误")
        assert exception.error_code == "CONFIG_ERROR"