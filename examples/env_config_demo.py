# examples/env_config_demo.py
"""
环境变量配置示例
演示如何使用APP_ENV环境变量控制配置文件加载
"""

import os
import sys

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import settings

def demo_env_config():
    """演示环境配置"""
    print("=== 环境配置示例 ===\n")
    
    print("当前环境配置:")
    print(f"  应用名称: {settings.APP_NAME}")
    print(f"  日志级别: {settings.LOG_LEVEL}")
    print(f"  数据文件路径: {settings.DATA_FILE_PATH}")
    print(f"  数据库URL: {settings.DATABASE_URL}")
    print(f"  应用环境: {settings.APP_ENV}")
    print(f"  配置字典: {settings.model_dump()}")

if __name__ == "__main__":
    demo_env_config()