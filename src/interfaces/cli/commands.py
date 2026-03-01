"""命令行接口实现

提供标准的命令行命令和交互功能。
"""

import sys
from pathlib import Path

import click

# 添加项目根目录到sys.path
CURRENT_DIR = Path.cwd()
PROJECT_ROOT = CURRENT_DIR.parent if CURRENT_DIR.name == "dist" else CURRENT_DIR
sys.path.insert(0, str(PROJECT_ROOT))

from ...app import initialize_app
from ...business.processors import get_data_processor
from ...business.repositories import get_data_repository
from ...business.services import get_analysis_service
from ...core.exceptions import CoreException


@click.group()
@click.option("--env-file", help="环境配置文件路径")
@click.pass_context
def cli(ctx, env_file: str | None = None):
    """数据分析项目命令行接口"""
    try:
        # 初始化应用
        app = initialize_app(env_file)
        ctx.obj = {"app": app, "logger": app.logger}
        click.echo(f"应用已启动: {app.settings.APP_NAME} v{app.settings.APP_VERSION}")
    except CoreException as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"未知错误: {e}", err=True)
        sys.exit(1)


@cli.command(name="process-csv")
@click.option("--input-file", required=True, help="输入CSV文件路径")
@click.option(
    "--processing-type",
    default="normalization",
    type=click.Choice(["normalization", "standardization", "log_transformation"]),
    help="数据处理类型",
)
@click.pass_context
def process_csv_cmd(ctx, input_file: str, processing_type: str):
    """处理CSV数据文件"""
    try:
        app = ctx.obj["app"]
        logger = ctx.obj["logger"]

        logger.info(f"开始处理CSV文件: {input_file}")
        logger.info(f"处理类型: {processing_type}")

        # 获取数据处理器
        processor = get_data_processor()

        # 处理数据
        processed_data = processor.load_and_process_csv(
            input_file,
            processing_steps=None,  # 可以添加自定义处理步骤
        )

        click.echo(f"数据处理完成，共处理 {len(processed_data)}条记录")
        logger.info("CSV文件处理完成")

    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@cli.command(name="analyze-data")
@click.option("--input-file", required=True, help="输入CSV文件路径")
@click.option("--analysis-type", default="statistical", type=click.Choice(["statistical", "trend"]), help="分析类型")
@click.pass_context
def analyze_data_cmd(ctx, input_file: str, analysis_type: str):
    """分析数据"""
    try:
        app = ctx.obj["app"]
        logger = ctx.obj["logger"]

        logger.info(f"开始数据分析: {input_file}")
        logger.info(f"分析类型: {analysis_type}")

        # 获取数据仓库和分析服务
        repository = get_data_repository()
        analysis_service = get_analysis_service()

        # 加载数据
        data_records = repository.load_data_from_csv(input_file)

        if not data_records:
            click.echo("警告: 未加载到任何数据")
            return

        # 执行分析
        if analysis_type == "statistical":
            result = analysis_service.perform_statistical_analysis(data_records)
            click.echo("统计分析完成:")
            click.echo(f" 记录数: {result.statistics.get('count', 0)}")
            click.echo(f" 平值: {result.statistics.get('mean', 0):.2f}")
            click.echo(f" 标准差: {result.statistics.get('std_dev', 0):.2f}")
        elif analysis_type == "trend":
            result = analysis_service.perform_trend_analysis(data_records)
            trend_info = result.statistics
            click.echo("趋势分析完成:")
            click.echo(f" 趋方向: {trend_info.get('trend_direction', 'unknown')}")
            click.echo(f" 相关系数: {trend_info.get('correlation', 0):.3f}")

        logger.info("数据分析完成")

    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@cli.command(name="status")
@click.pass_context
def status_cmd(ctx):
    """显示应用状态"""
    try:
        app = ctx.obj["app"]
        logger = ctx.obj["logger"]

        click.echo("应用状态信息:")
        click.echo(f"  应用名称: {app.settings.APP_NAME}")
        click.echo(f" 版本: {app.settings.APP_VERSION}")
        click.echo(f" 环境: {app.settings.APP_ENV.value}")
        click.echo(f"  日志级别: {app.settings.LOG_LEVEL}")
        click.echo(f"  数据库URL: {app.settings.DATABASE_URL}")

        # 显示处理统计
        processor = get_data_processor()
        click.echo(f" 已处理记录数: {processor.processed_count}")

        logger.info("状态信息已显示")

    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@cli.command(name="reset")
@click.pass_context
def reset_cmd(ctx):
    """重置应用计数器"""
    try:
        app = ctx.obj["app"]
        logger = ctx.obj["logger"]

        processor = get_data_processor()
        processor.reset_counters()

        click.echo("计数器已重置")
        logger.info("计数器重置完成")

    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


def create_cli():
    """创建CLI应用

    Returns:
        click.Group: CLI命令组
    """
    return cli


if __name__ == "__main__":
    cli()
