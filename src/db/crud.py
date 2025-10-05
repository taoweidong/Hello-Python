# src/db/crud.py
"""
CRUD操作混入类
提供基本的增删改查功能
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class CRUDMixin:
    """CRUD操作混入类"""
    
    __abstract__ = True
    
    @classmethod
    def create(cls, db: Session, **kwargs):
        """
        创建新记录
        
        Args:
            db: 数据库会话
            **kwargs: 模型字段值
            
        Returns:
            创建的模型实例
        """
        instance = cls(**kwargs)
        db.add(instance)
        db.flush()  # 获取ID但不提交事务
        return instance
    
    @classmethod
    def get_by_id(cls, db: Session, id: int):
        """
        根据ID获取记录
        
        Args:
            db: 数据库会话
            id: 记录ID
            
        Returns:
            模型实例或None
        """
        return db.query(cls).filter(cls.id == id).first()  # type: ignore
    
    @classmethod
    def get_all(cls, db: Session, skip: int = 0, limit: int = 100):
        """
        获取所有记录
        
        Args:
            db: 数据库会话
            skip: 跳过的记录数
            limit: 返回的记录数
            
        Returns:
            模型实例列表
        """
        return db.query(cls).offset(skip).limit(limit).all()
    
    @classmethod
    def update(cls, db: Session, id: int, **kwargs):
        """
        更新记录
        
        Args:
            db: 数据库会话
            id: 记录ID
            **kwargs: 要更新的字段值
            
        Returns:
            更新后的模型实例或None
        """
        instance = cls.get_by_id(db, id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            # 只有当实例有updated_at属性时才更新
            if hasattr(instance, 'updated_at'):
                setattr(instance, 'updated_at', datetime.utcnow())
            db.flush()
        return instance
    
    @classmethod
    def delete(cls, db: Session, id: int) -> bool:
        """
        删除记录
        
        Args:
            db: 数据库会话
            id: 记录ID
            
        Returns:
            bool: 是否成功删除
        """
        instance = cls.get_by_id(db, id)
        if instance:
            db.delete(instance)
            db.flush()
            return True
        return False
    
    @classmethod
    def filter(cls, db: Session, **kwargs):
        """
        根据条件过滤记录
        
        Args:
            db: 数据库会话
            **kwargs: 过滤条件
            
        Returns:
            符合条件的模型实例列表
        """
        query = db.query(cls)
        for key, value in kwargs.items():
            if hasattr(cls, key):
                query = query.filter(getattr(cls, key) == value)
        return query.all()