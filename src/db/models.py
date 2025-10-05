# src/db/models.py
"""
数据库模型基类
"""

from sqlalchemy import Column, Integer, DateTime, String
from datetime import datetime
from .crud import CRUDMixin
from .database import Base  # 使用database.py中的Base

class BaseModel(CRUDMixin, Base):
    """基础模型类"""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)