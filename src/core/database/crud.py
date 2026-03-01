"""通用CRUD操作混入类

提供基本的增删改查功能，所有模型都可以继承使用。
"""

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session


class CRUDMixin:
    """CRUD操作混入类"""

    __abstract__ = True

    @classmethod
    def create(cls, db: Session, **kwargs):
        """创建新记录

        Args:
            db:数据库会话
            **kwargs:模型字段值

        Returns:
            创建的模型实例
        """
        instance = cls(**kwargs)
        db.add(instance)
        db.flush()  # 获取ID但不提交事务
        return instance

    @classmethod
    def get_by_id(cls, db: Session, id: str):
        """根据ID获取记录

        Args:
            db:数据库会话
            id:记录ID (UUID字符串)

        Returns:
           模型实例或None
        """
        return db.query(cls).filter(cls.id == id).first()  # type: ignore

    @classmethod
    def get_all(cls, db: Session, skip: int = 0, limit: int = 100, order_by=None):
        """获取所有记录

        Args:
            db:数据库会话
            skip:跳过的记录数
            limit:返回的记录数
            order_by:排序字段，例如 User.created_at.desc()

        Returns:
           模型实例列表
        """
        query = db.query(cls)
        if order_by is not None:
            query = query.order_by(order_by)
        return query.offset(skip).limit(limit).all()

    @classmethod
    def update(cls, db: Session, id: str, **kwargs):
        """更新记录

        Args:
            db:数据库会话
            id:记录ID (UUID字符串)
            **kwargs:要更新的字段值

        Returns:
            更新后的模型实例或None
        """
        instance = cls.get_by_id(db, id)
        if instance:
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            # 只有当实例有updated_at属性时才更新
            if hasattr(instance, "updated_at"):
                setattr(instance, "updated_at", datetime.utcnow())
            db.flush()
        return instance

    @classmethod
    def delete(cls, db: Session, id: str) -> bool:
        """删除记录

        Args:
            db:数据库会话
            id:记录ID (UUID字符串)

        Returns:
            bool:是否成功删除
        """
        instance = cls.get_by_id(db, id)
        if instance:
            db.delete(instance)
            db.flush()
            return True
        return False

    @classmethod
    def bulk_create(cls, db: Session, objects: list[dict[str, Any]]) -> list:
        """批量创建记录

        Args:
            db:数据库会话
            objects:对象字典列表

        Returns:
            创建的模型实例列表
        """
        instances = [cls(**obj) for obj in objects]
        db.add_all(instances)
        db.flush()
        return instances

    @classmethod
    def bulk_update(cls, db: Session, updates: list[dict[str, Any]], id_field: str = "id") -> int:
        """批量更新记录

        Args:
            db:数据库会话
            updates:包含id和其要更新字段的字典列表
            id_field:用于查找记录的ID字段名

        Returns:
            更新的记录数量
        """
        updated_count = 0
        for update_data in updates:
            if id_field in update_data:
                obj_id = update_data.pop(id_field)
                updated_instance = cls.update(db, obj_id, **update_data)
                if updated_instance:
                    updated_count += 1
        return updated_count

    @classmethod
    def exists(cls, db: Session, **kwargs) -> bool:
        """检查记录是否存在

        Args:
            db:数据库会话
            **kwargs:过滤条件

        Returns:
            bool:记录是否存在
        """
        query = db.query(cls)
        for key, value in kwargs.items():
            if hasattr(cls, key):
                query = query.filter(getattr(cls, key) == value)
        return db.query(query.exists()).scalar()

    @classmethod
    def filter(cls, db: Session, order_by=None, **kwargs):
        """根据条件过滤记录

        Args:
            db:数据库会话
            order_by:排序字段
            **kwargs:过滤条件

        Returns:
           符合条件的模型实例列表
        """
        query = db.query(cls)
        for key, value in kwargs.items():
            if hasattr(cls, key):
                query = query.filter(getattr(cls, key) == value)

        if order_by is not None:
            query = query.order_by(order_by)

        return query.all()

    @classmethod
    def filter_by_range(cls, db: Session, field_name: str, min_value=None, max_value=None, **kwargs):
        """根据范围条件过滤记录

        Args:
            db:数据库会话
            field_name:要过滤的字段名
            min_value:最小值
            max_value:最大值
            **kwargs:其他过滤条件

        Returns:
           符合条件的模型实例列表
        """
        from sqlalchemy import and_

        query = db.query(cls)

        if hasattr(cls, field_name):
            field = getattr(cls, field_name)
            conditions = []
            if min_value is not None:
                conditions.append(field >= min_value)
            if max_value is not None:
                conditions.append(field <= max_value)

            if conditions:
                query = query.filter(and_(*conditions))

        # 应用其他过滤条件
        for key, value in kwargs.items():
            if hasattr(cls, key):
                query = query.filter(getattr(cls, key) == value)

        return query.all()

    @classmethod
    def count(cls, db: Session, **kwargs) -> int:
        """统计符合条件的记录数量

        Args:
            db:数据库会话
            **kwargs:过滤条件

        Returns:
           符合条件的记录数量
        """
        query = db.query(cls)
        for key, value in kwargs.items():
            if hasattr(cls, key):
                query = query.filter(getattr(cls, key) == value)
        return query.count()
