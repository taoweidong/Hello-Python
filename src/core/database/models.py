"""数据库基础模型类

提供所有数据库模型的基类，包含通用字段和方法。
"""

from sqlalchemy import Column, String, DateTime
from datetime import datetime
import uuid
from .crud import CRUDMixin
from .base import Base


class BaseModel(CRUDMixin, Base):
    """基础模型类"""
    
    __abstract__ = True
    
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """将模型实例转换为字典
        
        Returns:
            dict:包含模型字段的字典
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
    
    def update_from_dict(self, data: dict) -> None:
        """从字典更新模型字段
        
        Args:
            data:包含字段值的字典
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        if hasattr(self, 'updated_at'):
            setattr(self, 'updated_at', datetime.utcnow())
    
    def __repr__(self) -> str:
        """返回模型的字符串表示
        
        Returns:
            str:模型的字符串表示
        """
        return f"<{self.__class__.__name__}(id={getattr(self, 'id', 'N/A')})>"