# tests/test_click_demo.py
import unittest
import tempfile
import os
from click.testing import CliRunner
from src.click_demo import cli, hello, process_file, generate_data

class TestClickDemo(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_hello_command(self):
        """测试hello命令"""
        result = self.runner.invoke(hello, ['--count', '2'], input='Alice\n')
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Hello Alice!', result.output)
        self.assertEqual(result.output.count('Hello Alice!'), 2)

    def test_process_command(self):
        """测试process命令"""
        # 创建临时测试文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_file = f.name

        try:
            result = self.runner.invoke(process_file, ['--verbose', temp_file])
            self.assertEqual(result.exit_code, 0)
            self.assertIn('Processing file:', result.output)
            self.assertIn('File processing completed.', result.output)
        finally:
            # 清理临时文件
            os.unlink(temp_file)

    def test_generate_command_json(self):
        """测试generate命令 - JSON格式"""
        result = self.runner.invoke(generate_data, ['--format', 'json', '--count', '2'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Generating 2 items in json format', result.output)
        self.assertIn('{"id": 0, "name": "Item 0"}', result.output)
        self.assertIn('{"id": 1, "name": "Item 1"}', result.output)

    def test_generate_command_csv(self):
        """测试generate命令 - CSV格式"""
        result = self.runner.invoke(generate_data, ['--format', 'csv', '--count', '2'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Generating 2 items in csv format', result.output)
        self.assertIn('id,name', result.output)
        self.assertIn('0,Item 0', result.output)
        self.assertIn('1,Item 1', result.output)

    def test_main_cli_help(self):
        """测试主CLI帮助信息"""
        result = self.runner.invoke(cli, ['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Click使用示例程序', result.output)
        self.assertIn('hello', result.output)
        self.assertIn('process', result.output)
        self.assertIn('generate', result.output)

if __name__ == '__main__':
    unittest.main()