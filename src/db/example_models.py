# src/db/example_models.py
"""
示例数据库模型
演示如何使用数据库操作库
"""

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .models import BaseModel

class User(BaseModel):
    """用户模型"""
    
    __tablename__ = 'users'
    
    name = Column(String(50), index=True)
    age = Column(Integer)
    email = Column(String(100), unique=True, index=True)
    
    # 关联关系
    orders = relationship("Order", back_populates="user")
    
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
    
    # 关联关系
    orders = relationship("Order", back_populates="product")
    
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

class Order(BaseModel):
    """订单模型"""
    
    __tablename__ = 'orders'
    
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, default=1)
    total_price = Column(Integer)  # 以分为单位存储总价
    
    # 关联关系
    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")
    
    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id}, product_id={self.product_id}, quantity={self.quantity})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'total_price': self.total_price,
            'created_at': self.created_at.isoformat() if self.created_at is not None else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at is not None else None
        }