# src/db/config.py
"""
项目数据库配置文件
定义项目使用的数据库连接配置
"""

import os

# 数据库配置
DATABASE_CONFIG = {
    "default": os.getenv("DATABASE_URL", "sqlite:///./app.db"),
    "analytics": os.getenv("ANALYTICS_DATABASE_URL", "sqlite:///./analytics.db"),
    "logs": os.getenv("LOGS_DATABASE_URL", "sqlite:///./logs.db"),
}

# 是否在初始化时自动创建表
AUTO_CREATE_TABLES = os.getenv("AUTO_CREATE_TABLES", "true").lower() == "true"