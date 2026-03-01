"""统一配置管理模块

使用Pydantic Settings提供类型安全的配置管理，支持环境变量覆盖。
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from dotenv import load_dotenv
import os

from .environment import Environment, detect_environment, get_env_file


class Settings(BaseSettings):
    """应用配置模型"""
    
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    #应用基本信息
    APP_NAME: str = Field(default="Hello-Python", description="应用名称")
    APP_VERSION: str = Field(default="1.0.0", description="应用版本")
    APP_DESCRIPTION: str = Field(default="Python分析项目模板", description="应用描述")
    
    #环境配置
    APP_ENV: Environment = Field(default_factory=detect_environment, description="运行环境")
    
    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    LOG_FORMAT: str = Field(default="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}", description="日志格式")
    
    # 数据配置
    DATA_INPUT_PATH: str = Field(default="data/input", description="数据输入目录")
    DATA_OUTPUT_PATH: str = Field(default="data/output", description="数据输出目录")
    DATA_SAMPLES_PATH: str = Field(default="data/samples", description="示例数据目录")
    
    # 数据库配置
    DATABASE_URL: str = Field(default="sqlite:///./sql/app.db", description="数据库URL")
    DATABASE_ECHO: bool = Field(default=False, description="是否输出SQL语句")
    
    #其配置
    DEBUG: bool = Field(default=False, description="调试模式")
    
    def __init__(self, env_file: Optional[str] = None, **kwargs):
        """初始化配置
        
        Args:
            env_file:配置文件路径，如果为None则自动检测
            **kwargs:其配置参数
        """
        # 如果没有指定环境文件，根据环境自动检测
        if env_file is None:
            env_file = get_env_file()
            
        #确保配置文件存在
        if not os.path.exists(env_file):
            # 如果特定环境文件不存在，使用默认的.env文件
            if env_file != ".env" and os.path.exists(".env"):
                env_file = ".env"
            else:
                # 如果连默认文件都不存在，创建一个基本的配置文件
                self._create_default_env_file()
                env_file = ".env"
        
        # 加载环境变量
        load_dotenv(env_file, override=True)
        
        #调父类初始化
        super().__init__(**kwargs)
    
    def _create_default_env_file(self) -> None:
        """创建默认的环境配置文件"""
        default_content = """#应用配置
APP_NAME=Hello-Python
APP_VERSION=1.0.0
APP_DESCRIPTION=Python分析项目模板

#环境配置
APP_ENV=development

# 日志配置
LOG_LEVEL=INFO
LOG_FORMAT={time:YYYY-MM-DD HH:mm:ss} | {level} | {message}

# 数据配置
DATA_INPUT_PATH=data/input
DATA_OUTPUT_PATH=data/output
DATA_SAMPLES_PATH=data/samples

# 数据库配置
DATABASE_URL=sqlite:///./sql/app.db
DATABASE_ECHO=false

#调试配置
DEBUG=false
"""
        
        with open(".env", "w", encoding="utf-8") as f:
            f.write(default_content)


#全局配置实例
_settings: Optional[Settings] = None


def get_settings(env_file: Optional[str] = None) -> Settings:
    """获取全局配置实例
    
    Args:
        env_file:配置文件路径，如果为None则自动检测
        
    Returns:
        Settings:配置实例
    """
    global _settings
    if _settings is None:
        _settings = Settings(env_file=env_file)
    return _settings


def reload_settings(env_file: Optional[str] = None) -> Settings:
    """重新加载配置
    
    Args:
        env_file: 配置文件路径，如果为None则自动检测
        
    Returns:
        Settings: 重新加载的配置实例
    """
    global _settings
    _settings = Settings(env_file=env_file)
    return _settings