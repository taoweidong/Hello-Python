"""环境检测和管理模块

负责检测运行环境并提供环境相关的配置功能。
"""

import os
from enum import Enum
from typing import Optional


class Environment(Enum):
    """运行环境枚举"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


def detect_environment() -> Environment:
    """检测当前运行环境
    
    Returns:
        Environment:到的环境
    """
    env_name = os.getenv("APP_ENV", "development").lower()
    
    try:
        return Environment(env_name)
    except ValueError:
        # 如果环境变量值不匹配任何枚举值，默认为开发环境
        return Environment.DEVELOPMENT


def get_env_file(environment: Optional[Environment] = None) -> str:
    """获取对应环境的配置文件名
    
    Args:
        environment:环境枚举，如果为None则自动检测
        
    Returns:
        str:配置文件名
    """
    if environment is None:
        environment = detect_environment()
    
    if environment == Environment.DEVELOPMENT:
        return ".env"
    else:
        return f".env.{environment.value}"