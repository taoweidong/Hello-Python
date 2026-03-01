# tests/test_data_processor.py
import unittest
import pandas as pd
import os
import tempfile
from src.business.processors.data_processor import DataProcessor

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
        processor = DataProcessor()
        # 使用临时的数据仓库进行测试
        # 由于DataProcessor的load_and_process_csv方法依赖于数据仓库，
        # 我们直接测试它能正确处理CSV文件
        processed_data = processor.load_and_process_csv(self.temp_file.name)
        self.assertEqual(len(processed_data), 3)
        self.assertTrue(all(hasattr(item, 'name') for item in processed_data))
    
    def test_process_data(self):
        """测试数据处理功能"""
        processor = DataProcessor()
        # 由于DataProcessor的处理逻辑与之前的简单实现不同，
        # 它返回ProcessedData对象列表而不是DataFrame
        processed_data = processor.load_and_process_csv(self.temp_file.name)
        
        # 验证结果
        self.assertTrue(len(processed_data) > 0)
        self.assertTrue(all(hasattr(item, 'processed_value') for item in processed_data))

if __name__ == '__main__':
    unittest.main()