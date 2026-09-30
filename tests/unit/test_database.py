"""数据库模块测试（针对 src.core.database）"""

import uuid

import pytest
import sqlalchemy
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from src.core.database import Base, CRUDMixin, DatabaseManager, get_database_manager, initialize_database
from src.core.database.decorators import TransactionError, retry_on_db_error, transactional, with_db_session
from src.core.exceptions import ConfigurationError, DatabaseError


class TestDatabaseManager:
    """数据库管理器测试"""

    @pytest.fixture
    def manager(self):
        """创建数据库管理器实例"""
        return DatabaseManager("sqlite:///:memory:")

    def test_init_with_default_url(self):
        """测试使用默认URL初始化"""
        manager = DatabaseManager()
        assert "default" in manager.databases
        assert manager.get_current_db_name() == "default"

    def test_init_with_custom_url(self):
        """测试使用自定义URL初始化"""
        custom_url = "sqlite:///./data/test.db"
        manager = DatabaseManager(custom_url)
        assert manager._databases["default"].url == custom_url

    def test_add_database_success(self, manager):
        """测试成功添加数据库"""
        manager.add_database("test_db", "sqlite:///:memory:")
        assert "test_db" in manager.databases
        assert len(manager.databases) == 2  # default + test_db

    def test_add_database_duplicate(self, manager):
        """测试添加重复数据库"""
        with pytest.raises(ConfigurationError, match="已存在"):
            manager.add_database("default", "sqlite:///:memory:")

    def test_set_current_db_name_success(self, manager):
        """测试成功设置当前数据库"""
        manager.add_database("test_db", "sqlite:///:memory:")
        original_db_name = manager.get_current_db_name()
        try:
            manager.set_current_db_name("test_db")
            assert manager.get_current_db_name() == "test_db"
        finally:
            # 重置为原始数据库名称
            manager.set_current_db_name(original_db_name)

    def test_set_current_db_name_not_exists(self, manager):
        """测试设置不存在的数据库"""
        with pytest.raises(ConfigurationError, match="未配置"):
            manager.set_current_db_name("nonexistent")

    def test_get_engine_success(self, manager):
        """测试成功获取引擎：类型正确，且默认名与显式名指向同一引擎"""
        from sqlalchemy import Engine

        engine = manager.get_engine()
        assert isinstance(engine, Engine)
        assert manager.get_engine("default") is engine

    def test_get_engine_not_exists(self, manager):
        """测试获取不存在的引擎"""
        with pytest.raises(DatabaseError, match="未找到"):
            manager.get_engine("nonexistent")

    def test_get_session_factory_success(self, manager):
        """测试成功获取会话工厂：返回可调用对象且能产生会话"""
        session_factory = manager.get_session_factory()
        assert callable(session_factory)
        session = session_factory()
        assert isinstance(session, Session)
        session.close()

    def test_get_session_success(self, manager):
        """测试成功获取会话"""
        session = manager.get_session()
        assert isinstance(session, Session)
        session.close()

    def test_get_db_session_context_manager(self, manager):
        """测试数据库会话上下文管理器"""
        with manager.get_db_session() as session:
            assert isinstance(session, Session)
            # 执行简单查询
            from sqlalchemy import text

            result = session.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1

    def test_create_tables(self, manager, monkeypatch):
        """测试创建表"""
        # 创建一个简单的测试模型
        from sqlalchemy import Column, Integer, String
        from sqlalchemy.orm import declarative_base

        TestBase = declarative_base()

        class TestModel(TestBase):
            __tablename__ = "test_table_" + str(id(TestBase))  # 使用唯一表名
            id = Column(Integer, primary_key=True)
            name = Column(String(50))

        # 替换 manager 模块使用的 Base
        monkeypatch.setattr("src.core.database.manager.Base", TestBase)
        manager.create_tables()
        # 验证表是否创建
        engine = manager.get_engine()
        inspector = sqlalchemy.inspect(engine)
        tables = inspector.get_table_names()
        assert any("test_table" in table for table in tables)

    def test_test_connection_success(self, manager):
        """测试连接成功"""
        assert manager.test_connection() is True

    def test_test_connection_failure(self):
        """测试连接失败"""
        # 创建一个无效的数据库URL
        manager = DatabaseManager("sqlite:///invalid/path.db")
        assert manager.test_connection() is False

    def test_get_database_info(self, manager):
        """测试获取数据库信息"""
        info = manager.get_database_info()
        assert info["name"] == "default"
        assert info["connected"] is True
        assert "url" in info
        assert "echo" in info

    def test_global_database_manager(self, monkeypatch):
        """测试全局数据库管理器"""
        # 重置全局实例
        monkeypatch.setattr("src.core.database.manager._database_manager", None)

        manager1 = get_database_manager()
        manager2 = get_database_manager()

        assert manager1 is manager2
        assert isinstance(manager1, DatabaseManager)

    def test_initialize_database(self, monkeypatch):
        """测试初始化数据库"""
        monkeypatch.setattr("src.core.database.manager._database_manager", None)
        config = {"analytics": "sqlite:///:memory:", "logs": "sqlite:///:memory:"}

        initialize_database(config, "sqlite:///:memory:")

        # 验证数据库管理器已创建并配置
        manager = get_database_manager()
        assert "analytics" in manager.databases
        assert "logs" in manager.databases


class TestCRUDMixin:
    """CRUD混入类测试"""

    @pytest.fixture
    def model_class_factory(self):
        """创建测试模型类"""
        from datetime import datetime

        from sqlalchemy import Column, DateTime, Integer, String

        # 使用唯一表名和类名避免冲突
        table_name = f"test_models_{id(self)}"
        class_name = f"TestModel_{id(self)}"

        # 动态创建类避免重复
        TestModel = type(
            class_name,
            (CRUDMixin, Base),
            {
                "__tablename__": table_name,
                "id": Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
                "name": Column(String(50)),
                "age": Column(Integer),
                "created_at": Column(DateTime, default=datetime.utcnow),
                "updated_at": Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
            },
        )

        return TestModel

    @pytest.fixture
    def session(self):
        """创建数据库会话"""
        # 使用内存数据库避免表名冲突
        memory_manager = DatabaseManager("sqlite:///:memory:")
        with memory_manager.get_db_session() as session:
            # 创建测试表
            Base.metadata.create_all(bind=memory_manager.get_engine())
            yield session
            # 清理
            Base.metadata.drop_all(bind=memory_manager.get_engine())

    def test_create(self, model_class_factory, session):
        """测试创建记录"""
        instance = model_class_factory.create(session, name="Alice", age=25)
        assert instance.id is not None
        assert instance.name == "Alice"
        assert instance.age == 25
        assert instance.created_at is not None

    def test_get_by_id(self, model_class_factory, session):
        """测试根据ID获取记录"""
        # 先创建记录
        instance = model_class_factory.create(session, name="Alice", age=25)
        session.commit()

        # 根据ID获取
        retrieved = model_class_factory.get_by_id(session, instance.id)
        assert retrieved is not None
        assert retrieved.name == "Alice"
        assert retrieved.age == 25

    def test_get_by_id_not_found(self, model_class_factory, session):
        """测试根据ID获取不存在的记录"""
        retrieved = model_class_factory.get_by_id(session, "nonexistent-id")
        assert retrieved is None

    def test_get_all(self, model_class_factory, session):
        """测试获取所有记录"""
        # 创建多个记录
        model_class_factory.create(session, name="Alice", age=25)
        model_class_factory.create(session, name="Bob", age=30)
        session.commit()

        all_records = model_class_factory.get_all(session)
        assert len(all_records) == 2

    def test_update(self, model_class_factory, session):
        """测试更新记录"""
        # 创建记录
        instance = model_class_factory.create(session, name="Alice", age=25)
        session.commit()

        # 更新记录
        updated = model_class_factory.update(session, instance.id, name="Alice Updated", age=26)
        assert updated is not None
        assert updated.name == "Alice Updated"
        assert updated.age == 26
        assert updated.updated_at is not None

    def test_delete(self, model_class_factory, session):
        """测试删除记录"""
        # 创建记录
        instance = model_class_factory.create(session, name="Alice", age=25)
        session.commit()

        # 删除记录
        result = model_class_factory.delete(session, instance.id)
        assert result is True

        # 验证记录已删除
        deleted = model_class_factory.get_by_id(session, instance.id)
        assert deleted is None

    def test_exists(self, model_class_factory, session):
        """测试检查记录存在性"""
        # 创建记录
        model_class_factory.create(session, name="Alice", age=25)
        session.commit()

        # 检查存在
        assert model_class_factory.exists(session, name="Alice") is True
        assert model_class_factory.exists(session, name="Nonexistent") is False

    def test_filter(self, model_class_factory, session):
        """测试过滤查询"""
        # 创建记录
        model_class_factory.create(session, name="Alice", age=25)
        model_class_factory.create(session, name="Bob", age=30)
        model_class_factory.create(session, name="Charlie", age=25)
        session.commit()

        # 过滤查询
        results = model_class_factory.filter(session, age=25)
        assert len(results) == 2
        assert all(r.age == 25 for r in results)

    def test_count(self, model_class_factory, session):
        """测试统计记录数量"""
        # 创建记录
        model_class_factory.create(session, name="Alice", age=25)
        model_class_factory.create(session, name="Bob", age=30)
        session.commit()

        # 统计总数
        total = model_class_factory.count(session)
        assert total == 2

        # 按条件统计
        count_25 = model_class_factory.count(session, age=25)
        assert count_25 == 1


class TestDatabaseDecorators:
    """数据库装饰器测试"""

    @pytest.fixture
    def patch_global_manager(self, monkeypatch):
        """用独立的内存库管理器替换全局管理器，避免测试间相互影响"""

        def _patch():
            manager = DatabaseManager("sqlite:///:memory:")
            monkeypatch.setattr("src.core.database.manager._database_manager", manager)
            return manager

        return _patch

    def test_with_db_session_decorator(self, patch_global_manager):
        """测试数据库会话装饰器"""
        patch_global_manager()

        @with_db_session()
        def test_function(session):
            assert isinstance(session, Session)
            return "success"

        assert test_function() == "success"

    def test_transactional_decorator_success(self, patch_global_manager):
        """测试事务装饰器 - 成功情况（自动提交并落库）"""
        manager = patch_global_manager()

        @transactional()
        def test_function(session):
            from sqlalchemy import text

            session.execute(text("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)"))
            session.execute(text("INSERT INTO test (name) VALUES ('Alice')"))
            return "success"

        assert test_function() == "success"

        # 验证事务已提交
        with manager.get_db_session() as session:
            from sqlalchemy import text

            result = session.execute(text("SELECT COUNT(*) FROM test")).fetchone()
            assert result[0] == 1

    def test_transactional_decorator_rollback(self, patch_global_manager):
        """测试事务装饰器 - 回滚情况"""
        manager = patch_global_manager()

        @transactional()
        def test_function(session):
            from sqlalchemy import text

            session.execute(text("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)"))
            session.execute(text("INSERT INTO test (name) VALUES ('Alice')"))
            raise Exception("Test error")

        with pytest.raises(Exception, match="Test error"):
            test_function()

        # 验证事务已回滚
        with manager.get_db_session() as session:
            from sqlalchemy import text

            result = session.execute(text("SELECT COUNT(*) FROM test")).fetchone()
            assert result[0] == 0

    def test_transactional_with_external_session(self, patch_global_manager):
        """测试事务装饰器 - 外部传入会话时不重复提交/关闭"""
        from sqlalchemy import text

        manager = patch_global_manager()

        @transactional(auto_commit=False)
        def test_function(session):
            session.execute(text("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)"))
            session.execute(text("INSERT INTO test (name) VALUES ('Alice')"))

        with manager.get_db_session() as session:
            test_function(session)
            # 会话仍可用（未被装饰器关闭），由调用方控制提交
            session.commit()
            assert session.execute(text("SELECT COUNT(*) FROM test")).fetchone()[0] == 1

    def test_retry_on_db_error_decorator(self):
        """测试数据库错误重试装饰器"""
        call_count = 0

        @retry_on_db_error(max_retries=2, delay=0.01)
        def test_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:  # 前几次调用失败
                raise OperationalError("SELECT 1", {}, Exception("database is locked"))
            return "success"

        result = test_function()
        assert result == "success"
        assert call_count == 2  # 应该重试一次

    def test_retry_exhausted_raises_transaction_error(self):
        """测试重试耗尽后抛出 TransactionError 并保留异常链"""
        call_count = 0

        @retry_on_db_error(max_retries=2, delay=0.01)
        def always_fails():
            nonlocal call_count
            call_count += 1
            raise OperationalError("SELECT 1", {}, Exception("database is locked"))

        with pytest.raises(TransactionError, match="重试"):
            always_fails()
        assert call_count == 3  # 1 次原始调用 + 2 次重试

    def test_retry_non_db_error_not_retried(self):
        """测试非数据库错误不重试（不再基于错误消息字符串判断）"""
        call_count = 0

        @retry_on_db_error(max_retries=3, delay=0.01)
        def invalid_input():
            nonlocal call_count
            call_count += 1
            raise ValueError("Invalid db parameter")  # 消息含 db 关键词但不是数据库异常

        with pytest.raises(ValueError):
            invalid_input()
        assert call_count == 1  # 未重试


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
