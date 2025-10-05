# src/db/example_models.py
"""
示例数据库模型
演示如何使用数据库操作库
"""

from sqlalchemy import Column, String, Integer
from .models import BaseModel

class User(BaseModel):
    """用户模型"""
    
    __tablename__ = 'users'
    
    name = Column(String(50), index=True)
    age = Column(Integer)
    email = Column(String(100), unique=True, index=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at is not None else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at is not None else None
        }

class Product(BaseModel):
    """产品模型"""
    
    __tablename__ = 'products'
    
    name = Column(String(100), index=True)
    price = Column(Integer)  # 以分为单位存储价格
    description = Column(String(500))
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at is not None else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at is not None else None
        }