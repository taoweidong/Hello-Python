#!/usr/bin/env python3
"""
Click库使用示例
展示Click库的各种功能和用法
"""

import click
from datetime import datetime
import sys
import os
import logging
from pathlib import Path

# 修复打包后路径问题
def get_project_root():
    """获取项目根目录"""
    # 如果是打包后的可执行文件
    if getattr(sys, 'frozen', False):
        # frozen状态下，exe文件位于dist目录中
        exe_dir = Path(sys.executable).parent
        # 项目根目录是exe文件所在目录的父目录
        return exe_dir.parent
    else:
        # 开发状态下，使用当前工作目录
        return Path.cwd()

# 设置项目根目录
PROJECT_ROOT = get_project_root()

# 添加项目根目录到sys.path
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# 现在可以安全地导入项目模块
try:
    from src.config.settings import settings
except ImportError:
    # 如果直接运行脚本时的备用导入方式
    try:
        import src.config.settings as settings_module
        settings = settings_module.settings
    except ImportError:
        # 创建一个简单的配置对象作为后备
        class MockSettings:
            APP_ENV = "development"
        settings = MockSettings()

@click.command()
@click.option('--count', default=1, help='Number of greetings.')
@click.option('--name', prompt='Your name', help='The person to greet.')
def hello(count, name):
    """Simple program that greets NAME for a total of COUNT times."""
    for x in range(count):
        click.echo(f"Hello {name}!")
        click.echo(f"Environment: {settings.APP_ENV}")

@click.command()
@click.option('--verbose', is_flag=True, help="Enable verbose output.")
@click.option('--output', type=click.File('w'), default='-', help='Output file.')
@click.argument('input_file', type=click.Path(exists=True))
def process_file(verbose, output, input_file):
    """Process a file and output results."""
    if verbose:
        click.echo(f"Processing file: {input_file}")
    
    # 模拟文件处理
    output.write(f"Processed file: {input_file} at {datetime.now()}\n")
    
    if verbose:
        click.echo("File processing completed.")

@click.command()
@click.option('--format', type=click.Choice(['json', 'csv', 'xml']), default='json', help='Output format.')
@click.option('--count', type=int, default=10, help='Number of items to generate.')
def generate_data(format, count):
    """Generate sample data in specified format."""
    click.echo(f"Generating {count} items in {format} format...")
    
    if format == 'json':
        click.echo("[")
        for i in range(count):
            click.echo(f'  {{"id": {i}, "name": "Item {i}"}}' + (',' if i < count-1 else ''))
        click.echo("]")
    elif format == 'csv':
        click.echo("id,name")
        for i in range(count):
            click.echo(f"{i},Item {i}")
    elif format == 'xml':
        click.echo("<items>")
        for i in range(count):
            click.echo(f"  <item id='{i}'>Item {i}</item>")
        click.echo("</items>")

@click.group()
def cli():
    """Click使用示例程序"""
    pass

# 添加子命令
cli.add_command(hello, 'hello')
cli.add_command(process_file, 'process')
cli.add_command(generate_data, 'generate')

if __name__ == '__main__':
    cli()