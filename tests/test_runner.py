#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单元测试入口文件
可以快速运行所有单元测试
"""

import unittest
import sys
import os

import unittest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_all_tests():
    """运行所有单元测试"""
    print("开始运行所有单元测试...")
    print("=" * 50)
    
    # 发现并运行所有测试
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test*.py')
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果摘要
    print("=" * 50)
    print(f"测试运行完成:")
    print(f"  运行测试数: {result.testsRun}")
    print(f"  失败数: {len(result.failures)}")
    print(f"  错误数: {len(result.errors)}")
    print(f"  成功: {result.wasSuccessful()}")
    
    # 返回测试结果
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)