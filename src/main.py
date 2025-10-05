#!/usr/bin/env python3
import sys
import os
import logging
from pathlib import Path
import click

# 动态定位项目根目录（确保打包后能正确导入）
CURRENT_DIR = Path.cwd()
PROJECT_ROOT = CURRENT_DIR.parent if CURRENT_DIR.name == 'dist' else CURRENT_DIR

# 添加项目根目录到sys.path
sys.path.insert(0, str(PROJECT_ROOT))

from src.config.settings import settings
from src.config.logging_config import setup_logger
from src.data_processor import load_data, process_data

@click.group()
def cli():
    """项目命令行接口"""
    setup_logger()
    logging.info(f"Application started: {settings.APP_NAME}")
    logging.info(f"Environment: {settings.APP_ENV}")

@cli.command(name='process-data')
@click.option('--input', default=settings.DATA_FILE_PATH, help='输入数据文件路径')
@click.option('--output', default='data/output.csv', help='输出文件路径')
def process_data_cmd(input, output):
    """处理数据并保存到输出文件"""
    try:
        # 确保输入文件存在
        if not Path(input).exists():
            logging.error(f"输入文件不存在: {input}")
            click.echo(f"错误: 输入文件不存在: {input}", err=True)
            sys.exit(1)
            
        df = load_data(input)
        processed_df = process_data(df)
        processed_df.to_csv(output, index=False)
        click.echo(f"数据处理完成，已保存至: {output}")
        logging.info(f"数据处理完成，输出: {output}")
    except Exception as e:
        logging.error(f"数据处理出错: {str(e)}", exc_info=True)
        click.echo(f"数据处理出错: {str(e)}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    cli()