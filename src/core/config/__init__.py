"""核心配置管理模块

提供统一的配置管理功能，包括环境变量加载、配置验证和类型转换。
支持多环境配置文件和环境变量覆盖。
"""

from .settings import Settings, get_settings
from .environment import Environment, detect_environment

__all__ = [
    'Settings',
    'get_settings',
    'Environment',
    'detect_environment'
]