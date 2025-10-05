# src/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os
from dotenv import load_dotenv

# 获取环境变量 APP_ENV，如果没有设置则默认为 "development"
app_env = os.getenv("APP_ENV", "development")

# 根据环境变量加载不同的.env文件
env_file = f".env.{app_env}" if app_env != "development" else ".env"

# 如果特定环境的.env文件不存在，则使用默认的.env文件
if not os.path.exists(env_file):
    env_file = ".env"

# 加载环境变量
load_dotenv(env_file)

class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file, env_file_encoding="utf-8")
    
    APP_NAME: str = Field(default="Default App", description="应用名称")
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    DATA_FILE_PATH: str = Field(default="data/input.csv", description="数据文件路径")
    DATABASE_URL: str = Field(default="sqlite:///./test.db", description="数据库URL")
    APP_ENV: str = Field(default=app_env, description="应用环境")

# 创建配置实例
settings = Config()