"""数据库基础模型定义

提供数据库模型的基类和基础功能。
"""

from sqlalchemy.orm import declarative_base

# 创建基础模型类
Base = declarative_base()
