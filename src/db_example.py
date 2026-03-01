# src/db_example.py
"""
数据库操作示例
演示如何使用db模块进行数据表操作
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import Session
from src.infrastructure.database import (
    BaseModel,
    DatabaseManager,
    db_manager,
    initialize_databases,
    transactional,
    with_db_session,
    get_db
)
from loguru import logger


# ==================== 第一步：定义数据模型 ====================

class Article(BaseModel):
    """文章模型示例"""
    
    __tablename__ = 'articles'
    
    title = Column(String(200), index=True, nullable=False, comment='文章标题')
    content = Column(String(5000), comment='文章内容')
    author = Column(String(50), index=True, comment='作者')
    views = Column(Integer, default=0, comment='浏览次数')
    status = Column(String(20), default='draft', comment='状态：draft/published')
    
    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title}', author='{self.author}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'author': self.author,
            'views': self.views,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Category(BaseModel):
    """分类模型示例"""
    
    __tablename__ = 'categories'
    
    name = Column(String(50), unique=True, index=True, nullable=False, comment='分类名称')
    description = Column(String(500), comment='分类描述')
    sort_order = Column(Integer, default=0, comment='排序顺序')
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"


# ==================== 第二步：初始化数据库 ====================

def setup_database():
    """初始化数据库配置"""
    # 配置多个数据库
    DATABASE_CONFIG = {
        "default": os.getenv("DATABASE_URL", "sqlite:///./example.db"),
        "analytics": os.getenv("ANALYTICS_DATABASE_URL", "sqlite:///./analytics.db"),
        "logs": os.getenv("LOGS_DATABASE_URL", "sqlite:///./logs.db"),
    }
    
    # 初始化数据库（会自动创建表）
    initialize_databases(DATABASE_CONFIG)
    logger.info("数据库初始化完成:")
    for name, url in DATABASE_CONFIG.items():
        logger.info(f"  - {name}: {url}")


# ==================== 第三步：CRUD操作示例 ====================

def demo_create():
    """演示创建操作"""
    logger.info("=== 创建操作示例 ===")
    
    with db_manager.get_db_session() as db:
        # 创建文章
        article1 = Article.create(
            db,
            title="Python数据库操作指南",
            content="这是一篇关于Python数据库操作的详细指南...",
            author="张三",
            views=0,
            status="published"
        )
        logger.info(f"创建文章: {article1}")
        
        # 创建分类
        category1 = Category.create(
            db,
            name="技术文章",
            description="技术相关的文章分类",
            sort_order=1
        )
        logger.info(f"创建分类: {category1}")
        
        # 提交事务
        db.commit()
    
    return article1.id, category1.id


def demo_query():
    """演示查询操作"""
    logger.info("=== 查询操作示例 ===")
    
    with db_manager.get_db_session() as db:
        # 1. 根据ID查询
        articles = Article.get_all(db, limit=10)
        if articles:
            first_article = articles[0]
            article_by_id = Article.get_by_id(db, first_article.id)
            logger.info(f"根据ID查询: {article_by_id}")
        
        # 2. 查询所有记录
        all_articles = Article.get_all(db)
        logger.info(f"所有文章数量: {len(all_articles)}")
        
        # 3. 分页查询
        paginated_articles = Article.get_all(db, skip=0, limit=5)
        logger.info(f"分页查询结果数量: {len(paginated_articles)}")
        
        # 4. 条件过滤
        published_articles = Article.filter(db, status="published")
        logger.info(f"已发布文章数量: {len(published_articles)}")
        
        # 5. 使用原生SQL查询（高级用法）
        from sqlalchemy import text
        result = db.execute(text("SELECT COUNT(*) as count FROM articles"))
        count = result.scalar()
        logger.info(f"文章总数（SQL查询）: {count}")


def demo_update():
    """演示更新操作"""
    logger.info("=== 更新操作示例 ===")
    
    with db_manager.get_db_session() as db:
        # 获取第一篇文章
        articles = Article.get_all(db, limit=1)
        if not articles:
            logger.warning("没有文章可更新")
            return
        
        article = articles[0]
        article_id = article.id
        
        # 更新文章
        updated_article = Article.update(
            db,
            article_id,
            views=article.views + 1,
            status="published"
        )
        
        if updated_article:
            logger.info(f"更新后的文章: {updated_article}")
            db.commit()
        else:
            logger.warning(f"未找到ID为 {article_id} 的文章")


def demo_delete():
    """演示删除操作"""
    logger.info("=== 删除操作示例 ===")
    
    with db_manager.get_db_session() as db:
        # 获取第一篇文章
        articles = Article.get_all(db, limit=1)
        if not articles:
            logger.warning("没有文章可删除")
            return
        
        article_id = articles[0].id
        
        # 删除文章
        result = Article.delete(db, article_id)
        
        if result:
            logger.info(f"成功删除文章 ID: {article_id}")
            db.commit()
        else:
            logger.warning(f"删除失败，未找到ID为 {article_id} 的文章")


# ==================== 第四步：使用装饰器 ====================

@transactional()
def create_article_with_decorator(db: Session, title: str, content: str, author: str):
    """
    使用装饰器创建文章（自动处理事务）
    
    Args:
        db: 数据库会话（装饰器自动注入）
        title: 文章标题
        content: 文章内容
        author: 作者
    """
    article = Article.create(
        db,
        title=title,
        content=content,
        author=author,
        status="draft"
    )
    logger.info(f"使用装饰器创建文章: {article}")
    return article.id


@with_db_session()
def list_articles_with_decorator(db: Session):
    """
    使用装饰器查询文章列表（自动提供数据库会话）
    
    Args:
        db: 数据库会话（装饰器自动注入）
    """
    articles = Article.get_all(db)
    logger.info(f"文章列表（共 {len(articles)} 篇）:")
    for article in articles:
        logger.info(f"  - {article.title} (作者: {article.author})")
    return articles


# ==================== 第五步：批量操作示例 ====================

def demo_batch_operations():
    """演示批量操作"""
    logger.info("=== 批量操作示例 ===")
    
    with db_manager.get_db_session() as db:
        # 批量创建
        articles_data = [
            {"title": f"文章{i}", "content": f"这是第{i}篇文章的内容", "author": "作者A", "status": "published"}
            for i in range(1, 6)
        ]
        
        created_articles = []
        for data in articles_data:
            article = Article.create(db, **data)
            created_articles.append(article)
        
        logger.info(f"批量创建了 {len(created_articles)} 篇文章")
        
        # 批量更新
        for article in created_articles:
            Article.update(db, article.id, views=100)
        
        logger.info("批量更新完成")
        
        # 提交事务
        db.commit()


# ==================== 第六步：多数据库操作示例 ====================

def demo_multi_database():
    """演示多数据库操作"""
    logger.info("=== 多数据库操作示例 ===")
    
    # 方式1：使用上下文管理器指定数据库
    logger.info("\n1. 使用上下文管理器在不同数据库中操作:")
    
    # 在默认数据库中创建文章
    with db_manager.get_db_session("default") as db:
        article1 = Article.create(
            db,
            title="默认数据库文章",
            content="这篇文章存储在默认数据库中",
            author="作者A",
            status="published"
        )
        db.commit()
        logger.info(f"  默认数据库 - 创建文章: {article1.title} (ID: {article1.id})")
    
    # 在分析数据库中创建文章
    with db_manager.get_db_session("analytics") as db:
        article2 = Article.create(
            db,
            title="分析数据库文章",
            content="这篇文章存储在分析数据库中",
            author="作者B",
            status="published"
        )
        db.commit()
        logger.info(f"  分析数据库 - 创建文章: {article2.title} (ID: {article2.id})")
    
    # 在日志数据库中创建文章
    with db_manager.get_db_session("logs") as db:
        article3 = Article.create(
            db,
            title="日志数据库文章",
            content="这篇文章存储在日志数据库中",
            author="作者C",
            status="published"
        )
        db.commit()
        logger.info(f"  日志数据库 - 创建文章: {article3.title} (ID: {article3.id})")
    
    # 方式2：使用装饰器指定数据库
    logger.info("\n2. 使用装饰器指定数据库:")
    
    @transactional("analytics")
    def create_analytics_article(db: Session, title: str, content: str, author: str):
        """在分析数据库中创建文章"""
        article = Article.create(db, title=title, content=content, author=author, status="published")
        logger.info(f"  使用装饰器在分析数据库创建: {article.title}")
        return article.id
    
    @transactional("logs")
    def create_logs_article(db: Session, title: str, content: str, author: str):
        """在日志数据库中创建文章"""
        article = Article.create(db, title=title, content=content, author=author, status="published")
        logger.info(f"  使用装饰器在日志数据库创建: {article.title}")
        return article.id
    
    # 使用装饰器创建文章
    create_analytics_article("装饰器分析文章", "使用装饰器创建的分析文章", "装饰器作者")
    create_logs_article("装饰器日志文章", "使用装饰器创建的日志文章", "装饰器作者")
    
    # 方式3：手动切换当前数据库
    logger.info("\n3. 手动切换当前数据库:")
    
    # 设置当前数据库为analytics
    db_manager.set_current_db_name("analytics")
    with db_manager.get_db_session() as db:  # 使用当前数据库（analytics）
        articles = Article.get_all(db)
        logger.info(f"  当前数据库(analytics)中的文章数量: {len(articles)}")
    
    # 切换回默认数据库
    db_manager.set_current_db_name("default")
    with db_manager.get_db_session() as db:  # 使用当前数据库（default）
        articles = Article.get_all(db)
        logger.info(f"  当前数据库(default)中的文章数量: {len(articles)}")
    
    # 方式4：查询不同数据库中的数据
    logger.info("\n4. 查询不同数据库中的数据:")
    
    for db_name in ["default", "analytics", "logs"]:
        with db_manager.get_db_session(db_name) as db:
            articles = Article.get_all(db)
            logger.info(f"  {db_name} 数据库中的文章:")
            for article in articles:
                logger.info(f"    - {article.title} (作者: {article.author})")
    
    # 方式5：演示数据库隔离性
    logger.info("\n5. 数据库隔离性演示:")
    logger.info("  不同数据库中的数据完全独立，互不影响")
    
    # 在默认数据库中查询
    with db_manager.get_db_session("default") as db:
        default_count = len(Article.get_all(db))
        logger.info(f"  默认数据库文章数: {default_count}")
    
    # 在分析数据库中查询
    with db_manager.get_db_session("analytics") as db:
        analytics_count = len(Article.get_all(db))
        logger.info(f"  分析数据库文章数: {analytics_count}")
    
    # 在日志数据库中查询
    with db_manager.get_db_session("logs") as db:
        logs_count = len(Article.get_all(db))
        logger.info(f"  日志数据库文章数: {logs_count}")


@with_db_session("analytics")
def query_analytics_articles(db: Session):
    """查询分析数据库中的文章（使用装饰器）"""
    articles = Article.get_all(db)
    logger.info(f"分析数据库中的文章（共 {len(articles)} 篇）:")
    for article in articles:
        logger.info(f"  - {article.title} (作者: {article.author})")
    return articles


@transactional("logs")
def create_log_entry(db: Session, title: str, content: str):
    """在日志数据库中创建日志条目（使用装饰器）"""
    article = Article.create(db, title=title, content=content, author="系统", status="published")
    logger.info(f"创建日志条目: {article.title}")
    return article.id


# ==================== 第七步：事务管理示例 ====================

def demo_transaction():
    """演示事务管理"""
    logger.info("=== 事务管理示例 ===")
    
    # 方式1：使用上下文管理器（推荐）
    try:
        with db_manager.get_db_session() as db:
            # 创建文章1
            article1 = Article.create(db, title="事务测试1", content="内容1", author="测试")
            
            # 创建文章2
            article2 = Article.create(db, title="事务测试2", content="内容2", author="测试")
            
            # 如果这里出现异常，上面的操作都会回滚
            # raise Exception("模拟错误")
            
            db.commit()
            logger.info("事务提交成功")
    except Exception as e:
        logger.error(f"事务回滚: {e}")
    
    # 方式2：使用装饰器
    try:
        create_article_with_decorator("装饰器测试", "内容", "测试作者")
    except Exception as e:
        logger.error(f"装饰器事务回滚: {e}")


# ==================== 主函数 ====================

def main():
    """主函数：运行所有示例"""
    logger.info("=" * 60)
    logger.info("数据库操作示例程序")
    logger.info("=" * 60)
    
    # 初始化数据库
    setup_database()
    logger.info("")
    
    # 创建操作
    try:
        article_id, category_id = demo_create()
        logger.info("")
    except Exception as e:
        logger.error(f"创建操作失败: {e}")
        logger.info("")
    
    # 查询操作
    try:
        demo_query()
        logger.info("")
    except Exception as e:
        logger.error(f"查询操作失败: {e}")
        logger.info("")
    
    # 更新操作
    try:
        demo_update()
        logger.info("")
    except Exception as e:
        logger.error(f"更新操作失败: {e}")
        logger.info("")
    
    # 装饰器使用
    try:
        create_article_with_decorator("装饰器示例文章", "这是使用装饰器创建的文章", "装饰器作者")
        list_articles_with_decorator()
        logger.info("")
    except Exception as e:
        logger.error(f"装饰器操作失败: {e}")
        logger.info("")
    
    # 批量操作
    try:
        demo_batch_operations()
        logger.info("")
    except Exception as e:
        logger.error(f"批量操作失败: {e}")
        logger.info("")
    
    # 事务管理
    try:
        demo_transaction()
        logger.info("")
    except Exception as e:
        logger.error(f"事务管理失败: {e}")
        logger.info("")
    
    # 多数据库操作
    try:
        demo_multi_database()
        logger.info("")
    except Exception as e:
        logger.error(f"多数据库操作失败: {e}")
        logger.info("")
    
    # 最终查询
    try:
        logger.info("=== 最终数据统计 ===")
        
        # 默认数据库统计
        with db_manager.get_db_session("default") as db:
            articles = Article.get_all(db)
            categories = Category.get_all(db)
            logger.info(f"默认数据库 - 文章总数: {len(articles)}, 分类总数: {len(categories)}")
        
        # 分析数据库统计
        with db_manager.get_db_session("analytics") as db:
            articles = Article.get_all(db)
            logger.info(f"分析数据库 - 文章总数: {len(articles)}")
        
        # 日志数据库统计
        with db_manager.get_db_session("logs") as db:
            articles = Article.get_all(db)
            logger.info(f"日志数据库 - 文章总数: {len(articles)}")
    except Exception as e:
        logger.error(f"统计失败: {e}")
    
    logger.info("=" * 60)
    logger.info("示例程序执行完成")
    logger.info("=" * 60)


if __name__ == "__main__":
    # 如果没有配置日志，可以简单设置
    if not logger._core.handlers:
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
            level="INFO"
        )
    
    main()

