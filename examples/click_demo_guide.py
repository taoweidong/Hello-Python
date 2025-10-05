# examples/click_demo_guide.py
"""
Click库使用指南示例
展示如何使用Click库创建命令行接口
"""

import click
from datetime import datetime

# 1. 基本命令
@click.command()
@click.option('--count', default=1, help='Number of greetings.')
@click.option('--name', prompt='Your name', help='The person to greet.')
def hello(count, name):
    """Simple program that greets NAME for a total of COUNT times."""
    for x in range(count):
        click.echo(f"Hello {name}!")

# 2. 文件处理命令
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

# 3. 数据生成命令
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

# 4. 分组命令
@click.group()
def cli():
    """Click使用示例程序"""
    pass

# 添加子命令
cli.add_command(hello, 'hello')
cli.add_command(process_file, 'process')
cli.add_command(generate_data, 'generate')

# 5. 参数类型示例
@click.command()
@click.argument('input', type=click.File('rb'))
@click.argument('output', type=click.File('wb'))
@click.option('--hash-type', type=click.Choice(['md5', 'sha1', 'sha256']), default='sha256')
def crypto(input, output, hash_type):
    """演示不同参数类型的使用"""
    click.echo(f"Hashing with {hash_type}")
    # 这里可以添加实际的哈希计算逻辑
    output.write(input.read())

# 6. 回调和上下文示例
@click.group(invoke_without_command=True)
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli_with_context(ctx, debug):
    """带有上下文的CLI示例"""
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug
    
    if ctx.invoked_subcommand is None:
        click.echo("Running in default mode")

@cli_with_context.command()
@click.pass_context
def sync(ctx):
    """同步命令示例"""
    if ctx.obj['DEBUG']:
        click.echo("Debug mode enabled")
    click.echo("Syncing...")

# 7. 进度条示例
@click.command()
@click.option('--count', default=1000, help='Number of items to process.')
def process_with_progress(count):
    """演示进度条的使用"""
    with click.progressbar(range(count), label='Processing items') as bar:
        for i in bar:
            # 模拟处理时间
            pass
    click.echo("Processing completed!")

if __name__ == '__main__':
    # 运行主CLI
    cli()