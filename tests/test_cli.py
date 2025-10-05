# tests/test_cli.py
import unittest
from click.testing import CliRunner
from src.main import cli

class TestCLI(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_cli_help(self):
        """测试CLI帮助信息"""
        result = self.runner.invoke(cli, ['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Usage:', result.output)

if __name__ == '__main__':
    unittest.main()