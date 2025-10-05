#!/usr/bin/env python3
"""
Click库使用示例
展示Click库的各种功能和用法
"""

import click
from datetime import datetime

@click.command()
@click.option('--count', default=1, help='Number of greetings.')
@click.option('--name', prompt='Your name', help='The person to greet.')
def hello(count, name):
    """Simple program that greets NAME for a total of COUNT times."""
    for x in range(count):
        click.echo(f"Hello {name}!")

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