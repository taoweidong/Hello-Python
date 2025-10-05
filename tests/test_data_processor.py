# tests/test_data_processor.py
import unittest
import pandas as pd
import os
import tempfile
from src.data_processor import load_data, process_data

class TestDataProcessor(unittest.TestCase):
    def setUp(self):
        # 创建临时测试数据文件
        self.test_data = """name,age,city
Alice,25,New York
Bob,30,London
Charlie,35,Tokyo"""
        
        # 创建临时文件
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
        self.temp_file.write(self.test_data)
        self.temp_file.close()
        
    def tearDown(self):
        # 清理临时文件
        os.unlink(self.temp_file.name)
    
    def test_load_data(self):
        """测试数据加载功能"""
        df = load_data(self.temp_file.name)
        self.assertEqual(len(df), 3)
        self.assertIn('name', df.columns)
        self.assertIn('age', df.columns)
        self.assertIn('city', df.columns)
    
    def test_process_data(self):
        """测试数据处理功能"""
        # 创建示例数据
        df = load_data(self.temp_file.name)
        
        # 处理数据
        result = process_data(df)
        
        # 验证结果
        self.assertIn('processed', result.columns)
        self.assertTrue(result['processed'].all())

if __name__ == '__main__':
    unittest.main()