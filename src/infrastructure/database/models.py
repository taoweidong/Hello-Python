# src/infrastructure/database/models.py
"""
数据库模型基类

这是独立的基础设施模块，可在其他项目中直接使用。
不依赖任何项目特定代码，确保完全独立性和可复用性。
"""

from sqlalchemy import Column, String, DateTime
from datetime import datetime
import uuid
from .crud import CRUDMixin
from .database import Base  # 使用database.py中的Base

class BaseModel(CRUDMixin, Base):
    """基础模型类"""
    
    __abstract__ = True
    
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """
        将模型实例转换为字典
        
        Returns:
            dict: 包含模型字段的字典
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if value is not None:
                if isinstance(value, datetime):
                    value = value.isoformat()
                elif isinstance(value, uuid.UUID):
                    value = str(value)
                result[column.name] = value
        return result
    
    def update_from_dict(self, data: dict):
        """
        从字典更新模型字段
        
        Args:
            data: 包含字段值的字典
        """
        for key, value in data.items():
            if hasattr(self.__table__.columns, key):
                setattr(self, key, value)
        if hasattr(self, 'updated_at'):
            setattr(self, 'updated_at', datetime.utcnow())
    
    def __repr__(self):
        """
        返回模型的字符串表示
        
        Returns:
            str: 模型的字符串表示
        """
        return f"<{self.__class__.__name__}(id={getattr(self, 'id', 'N/A')})>"