"""主应用入口

提供命令行接口和应用程序的主要功能。
"""

import sys
import os
from pathlib import Path
from typing import Optional
import click

# 添加项目根目录到sys.path
CURRENT_DIR = Path.cwd()
PROJECT_ROOT = CURRENT_DIR.parent if CURRENT_DIR.name == 'dist' else CURRENT_DIR
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    get_config_manager,
    setup_logger,
    ConfigurationError,
    LoggerError
)
from src.services import (
    get_data_processor,
    DataProcessingError
)
from src.infrastructure.database import (
    get_database_manager,
    initialize_database,
    DatabaseError
)


class ApplicationError(Exception):
    """应用程序错误异常"""
    pass


class Application:
    """应用程序主类
    
   管应用程序的配置、日志和核心功能。
    """
    
    def __init__(self) -> None:
        """初始化应用程序"""
        self._config_manager = get_config_manager()
        self._logger = None
        self._data_processor = get_data_processor()
        self._database_manager = get_database_manager()
        
    def initialize(self, env_file: Optional[str] = None) -> None:
        """初始化应用程序
        
        Args:
            env_file:环境配置文件路径
            
        Raises:
            ApplicationError: 初始化失败时
        """
        try:
            # 加载配置
            if env_file:
                self._config_manager = get_config_manager(env_file)
            
            config = self._config_manager.load_configuration()
            
            #设置日志
            self._logger = setup_logger(config)
            self._logger.info(f"应用程序启动: {config.APP_NAME}")
            self._logger.info(f"环境: {config.APP_ENV}")
            
            #初始化数据库
            try:
                initialize_database(default_url=config.DATABASE_URL)
            except DatabaseError as e:
                self._logger.warning(f"数据库初始化失败: {e}")
            
        except ConfigurationError as e:
            raise ApplicationError(f"配置加载失败: {e}")
        except LoggerError as e:
            raise ApplicationError(f"日志配置失败: {e}")
        except Exception as e:
            raise ApplicationError(f"应用程序初始化失败: {e}")
    
    def process_data_command(self, input_file: str, output_file: str) -> None:
        """处理数据命令
        
        Args:
            input_file:输入文件路径
            output_file:输出文件路径
            
        Raises:
            ApplicationError: 数据处理失败时
        """
        if self._logger is None:
            raise ApplicationError("应用程序未初始化")
        
        try:
            #验证输入文件
            input_path = Path(input_file)
            if not input_path.exists():
                raise ApplicationError(f"输入文件不存在: {input_file}")
            
            self._logger.info(f"开始处理数据: {input_file} -> {output_file}")
            
            #加载和处理数据
            df = self._data_processor.load_data(str(input_path))
            processed_df = self._data_processor.process_data(df)
            
            #保存结果
            self._data_processor.save_data(processed_df, output_file)
            
            self._logger.info(f"数据处理完成，共处理 {len(processed_df)}条")
            
        except DataProcessingError as e:
            raise ApplicationError(f"数据处理失败: {e}")
        except Exception as e:
            raise ApplicationError(f"数据处理过程中发生错误: {e}")
    
    def get_status(self) -> dict:
        """获取应用程序状态
        
        Returns:
            dict:应用程序状态信息
        """
        status = {
            'initialized': self._logger is not None,
            'processed_count': self._data_processor.processed_count if self._logger else 0
        }
        
        if self._logger:
            try:
                config = self._config_manager.config
                status.update({
                    'app_name': config.APP_NAME,
                    'environment': config.APP_ENV,
                    'log_level': config.LOG_LEVEL
                })
            except ConfigurationError:
                pass
        
        return status


# 创建全局应用程序实例
_app: Optional[Application] = None


def get_application() -> Application:
    """获取全局应用程序实例
    
    Returns:
        Application:应用程序实例
    """
    global _app
    if _app is None:
        _app = Application()
    return _app


@click.group()
@click.option('--env-file', help='环境配置文件路径')
def cli(env_file: Optional[str] = None) -> None:
    """项目命令行接口"""
    try:
        app = get_application()
        app.initialize(env_file)
        status = app.get_status()
        click.echo(f"应用程序已启动: {status.get('app_name', 'Unknown')}")
        click.echo(f"环境: {status.get('environment', 'Unknown')}")
    except ApplicationError as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"未知错误: {e}", err=True)
        sys.exit(1)


@cli.command(name='process-data')
@click.option('--input', default='data/input.csv', help='输入数据文件路径')
@click.option('--output', default='data/output.csv', help='输出文件路径')
def process_data_cmd(input: str, output: str) -> None:
    """处理数据并保存到输出文件"""
    try:
        app = get_application()
        app.process_data_command(input, output)
        click.echo(f"数据处理完成，已保存至: {output}")
    except ApplicationError as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"未知错误: {e}", err=True)
        sys.exit(1)


@cli.command(name='status')
def status_cmd() -> None:
    """显示应用程序状态"""
    try:
        app = get_application()
        status = app.get_status()
        
        click.echo("应用程序状态:")
        click.echo(f"  初始化状态: {'已初始化' if status['initialized'] else '未初始化'}")
        click.echo(f" 已处理记录数: {status['processed_count']}")
        
        if status['initialized']:
            click.echo(f"  应用名称: {status.get('app_name', 'Unknown')}")
            click.echo(f" 环境: {status.get('environment', 'Unknown')}")
            click.echo(f"  日志级别: {status.get('log_level', 'Unknown')}")
            
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@cli.command(name='reset')
def reset_cmd() -> None:
    """重置应用程序计数器"""
    try:
        app = get_application()
        app._data_processor.reset_counters()
        click.echo("计数器已重置")
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()