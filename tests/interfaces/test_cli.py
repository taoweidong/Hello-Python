"""接口层测试

测试命令行接口和其他用户接口功能。
"""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, Mock

from src.interfaces.cli.commands import create_cli


class TestCLIInterface:
    """命令行接口测试"""
    
    def setup_method(self):
        """测试方法设置"""
        self.runner = CliRunner()
        self.cli = create_cli()
    
    def test_cli_help(self):
        """测试CLI帮助命令"""
        result = self.runner.invoke(self.cli, ['--help'])
        assert result.exit_code == 0
        assert '数据分析项目命令行接口' in result.output
    
    def test_status_command(self):
        """测试状态命令"""
        with patch('src.interfaces.cli.commands.initialize_app') as mock_init:
            mock_app = Mock()
            mock_app.settings.APP_NAME = "TestApp"
            mock_app.settings.APP_VERSION = "1.0.0"
            mock_app.settings.APP_ENV.value = "development"
            mock_app.logger = Mock()
            mock_init.return_value = mock_app
            
            result = self.runner.invoke(self.cli, ['status'])
            assert result.exit_code == 0
    
    def test_process_csv_command_validation(self):
        """测试CSV处理命令参数验证"""
        result = self.runner.invoke(self.cli, ['process-csv'])
        assert result.exit_code != 0  #应该失败，因为缺少必需参数