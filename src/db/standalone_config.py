# src/db/standalone_config.py
"""
独立配置模块
为独立使用db模块提供配置示例
"""

import os

# 数据库配置示例
STANDALONE_DATABASE_CONFIG = {
    "default": os.getenv("DATABASE_URL", "sqlite:///./app.db"),
    "analytics": os.getenv("ANALYTICS_DATABASE_URL", "sqlite:///./analytics.db"),
    "logs": os.getenv("LOGS_DATABASE_URL", "sqlite:///./logs.db"),
}

# 是否在初始化时自动创建表
STANDALONE_AUTO_CREATE_TABLES = os.getenv("AUTO_CREATE_TABLES", "true").lower() == "true"

def setup_standalone_db():
    """
    设置独立数据库配置
    """
    from .database import initialize_databases
    if STANDALONE_AUTO_CREATE_TABLES:
        initialize_databases(STANDALONE_DATABASE_CONFIG)