"""基础使用示例

演示如何使用重构后的项目进行基本的数据分析操作。
"""

import csv
import sys
from pathlib import Path

from loguru import logger as loguru_logger

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.app import initialize_app
from src.business.processors import get_data_processor
from src.business.repositories import get_data_repository
from src.business.services import get_analysis_service


def create_sample_data():
    """创建示例数据文件"""
    # 确保数据目录存在
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    # 创建示例CSV文件
    sample_file = data_dir / "sample_data.csv"

    sample_data = [
        ["name", "value", "category"],
        ["记录1", "100.5", "销售"],
        ["记录2", "200.0", "销售"],
        ["记录3", "150.2", "市场"],
        ["记录4", "300.8", "市场"],
        ["记录5", "75.3", "研发"],
    ]

    with open(sample_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(sample_data)

    loguru_logger.info(f"示例数据文件已创建: {sample_file}")
    return str(sample_file)


def basic_analysis_example():
    """基本分析示例"""
    loguru_logger.info("===基本数据分析示例 ===\n")

    try:
        # 1. 初始化应用
        loguru_logger.info("1. 初始化应用...")
        app = initialize_app()
        loguru_logger.info(f"   应用: {app.settings.APP_NAME} v{app.settings.APP_VERSION}")
        loguru_logger.info(f"   环境: {app.settings.APP_ENV.value}")

        # 2. 创建示例数据
        loguru_logger.info("\n2. 创建示例数据...")
        sample_file = create_sample_data()

        # 3. 数据处理
        loguru_logger.info("\n3.处理数据...")
        processor = get_data_processor()

        processed_data = processor.load_and_process_csv(sample_file)
        loguru_logger.info(f"   成功处理 {len(processed_data)}条记录")

        # 显示处理结果
        loguru_logger.info("\n   处理结果预览:")
        for i, data in enumerate(processed_data[:3]):  # 显示前3条
            loguru_logger.info(f"   {i + 1}. {data.name}: {data.original_value} -> {data.processed_value:.3f}")

        # 4. 数据分析
        loguru_logger.info("\n4.执行统计分析...")
        repository = get_data_repository()
        analysis_service = get_analysis_service()

        # 重新加载数据进行分析
        data_records = repository.load_data_from_csv(sample_file)

        # 统计分析
        stats_result = analysis_service.perform_statistical_analysis(data_records)
        loguru_logger.info("  统计分析完成:")
        loguru_logger.info(f"    记录数: {stats_result.statistics.get('count', 0)}")
        loguru_logger.info(f"    平值: {stats_result.statistics.get('mean', 0):.2f}")
        loguru_logger.info(f"     标准差: {stats_result.statistics.get('std_dev', 0):.2f}")

        # 趋分析
        loguru_logger.info("\n5. 执行趋势分析...")
        trend_result = analysis_service.perform_trend_analysis(data_records)
        trend_info = trend_result.statistics
        loguru_logger.info("  趋分析完成:")
        loguru_logger.info(f"     趋势方向: {trend_info.get('trend_direction', 'unknown')}")
        loguru_logger.info(f"     相关系数: {trend_info.get('correlation', 0):.3f}")

        # 6.显示状态
        loguru_logger.info("\n6.应用状态:")
        loguru_logger.info(f"  已处理记录数: {processor.processed_count}")

        loguru_logger.info("\n=== 示例完成 ===")

    except Exception:
        loguru_logger.exception("示例运行出错")


if __name__ == "__main__":
    basic_analysis_example()
