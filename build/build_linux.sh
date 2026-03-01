#!/bin/bash
# Linux PyInstaller打包脚本
# 将examples目录下的指定Python文件打包成Linux可执行文件
# 使用方法: ./build_linux.sh <filename> (不带.py扩展名)

if [ $# -eq 0 ]; then
    echo "用法: $0 <filename>"
    echo "示例: $0 basic_usage"
    echo "      $0 advanced_analysis"
    exit 1
fi

FILENAME=$1
if [[ "$FILENAME" != *.py ]]; then
    PYTHON_FILE="$FILENAME.py"
else
    PYTHON_FILE="$FILENAME"
    FILENAME="${FILENAME%.py}"
fi

echo "Starting packaging $PYTHON_FILE from examples..."
echo

# 设置路径变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ROOT_DIST_DIR="$PROJECT_DIR/dist"
BUILD_TEMP="$SCRIPT_DIR/temp"
BUILD_DIST_DIR="$SCRIPT_DIR/dist"

echo "SCRIPT_DIR: $SCRIPT_DIR"
echo "PROJECT_DIR: $PROJECT_DIR"
echo "ROOT_DIST_DIR: $ROOT_DIST_DIR"
echo "BUILD_TEMP: $BUILD_TEMP"
echo "BUILD_DIST_DIR: $BUILD_DIST_DIR"
echo

# 检查文件是否存在
EXAMPLES_FILE="$PROJECT_DIR/examples/$PYTHON_FILE"
if [ ! -f "$EXAMPLES_FILE" ]; then
    echo "错误: 文件 $EXAMPLES_FILE 不存在!"
    echo "examples目录中的可用文件:"
    ls -la "$PROJECT_DIR/examples/"*.py
    exit 1
fi

# 清理并创建目录
rm -rf "$BUILD_TEMP"
mkdir -p "$BUILD_TEMP"

rm -rf "$BUILD_DIST_DIR"
mkdir -p "$BUILD_DIST_DIR"

# 创建一个包含所有依赖的入口脚本
ENTRY_SCRIPT="$BUILD_TEMP/${FILENAME%.py}_entry.py"
cat > "$ENTRY_SCRIPT" << 'EOF'
#!/usr/bin/env python3

import sys
import os
from pathlib import Path

# 添加项目根目录到路径，以便导入模块
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 导入必要的模块以确保PyInstaller能检测到它们
try:
    import src.app
    import src.core.config
    import src.core.logging
    import src.core.database
    import src.core.exceptions
    import src.business.models
    import src.business.services
    import src.business.repositories
    import src.business.processors
    import src.interfaces.cli.commands
    import pydantic
    import pydantic_settings
    import sqlalchemy
    import loguru
    import click
    import pandas
    import dotenv
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

# 现在执行原始脚本的内容
if __name__ == "__main__":
    # 这里我们会插入原始脚本的内容
EOF

# 添加原始脚本的内容到入口脚本
cat "$EXAMPLES_FILE" >> "$ENTRY_SCRIPT"

echo "Packaging $PYTHON_FILE..."
echo

# 运行PyInstaller打包，包含所有必要的依赖
pyinstaller --onefile \
    --name="$FILENAME" \
    --distpath "$BUILD_DIST_DIR" \
    --workpath "$BUILD_TEMP/build" \
    --specpath "$BUILD_TEMP" \
    --add-data "$PROJECT_DIR/src:src" \
    --add-data "$PROJECT_DIR/examples:examples" \
    --add-data "$PROJECT_DIR/data:data" \
    --hidden-import="src" \
    --hidden-import="src.app" \
    --hidden-import="src.core" \
    --hidden-import="src.core.config" \
    --hidden-import="src.core.logging" \
    --hidden-import="src.core.database" \
    --hidden-import="src.core.exceptions" \
    --hidden-import="src.business" \
    --hidden-import="src.business.models" \
    --hidden-import="src.business.services" \
    --hidden-import="src.business.repositories" \
    --hidden-import="src.business.processors" \
    --hidden-import="src.interfaces" \
    --hidden-import="src.interfaces.cli" \
    --hidden-import="src.interfaces.cli.commands" \
    --hidden-import="pydantic" \
    --hidden-import="pydantic_settings" \
    --hidden-import="sqlalchemy" \
    --hidden-import="loguru" \
    --hidden-import="click" \
    --hidden-import="pandas" \
    --hidden-import="dotenv" \
    "$ENTRY_SCRIPT"

# 清理临时文件
echo "Cleaning up temporary files..."
rm -rf "$BUILD_TEMP"
echo

echo "Packaging complete! Executable is located at: $BUILD_DIST_DIR/$FILENAME"
echo

# 检查生成的可执行文件
if [ -f "$BUILD_DIST_DIR/$FILENAME" ]; then
    echo "Executable successfully generated."
    
    # 创建根目录下的dist目录（如果不存在）
    if [ ! -d "$ROOT_DIST_DIR" ]; then
        echo "Creating root dist directory..."
        mkdir -p "$ROOT_DIST_DIR"
    fi
    
    # 复制可执行文件到根目录下的dist目录
    echo "Copying executable to root dist directory..."
    cp "$BUILD_DIST_DIR/$FILENAME" "$ROOT_DIST_DIR/"
    
    if [ $? -eq 0 ]; then
        echo "Executable successfully archived to root dist directory."
    else
        echo "Warning: Failed to copy executable to root dist directory."
    fi
else
    echo "Warning: Executable not found."
fi

echo