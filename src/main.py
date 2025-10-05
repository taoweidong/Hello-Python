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

from src.config import settings
from src.logger import setup_logger
from src.data_processor import load_data, process_data

if __name__ == "__main__":
    logging.info(f"Starting command line interface: {settings.APP_NAME}")