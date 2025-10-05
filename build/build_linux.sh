#!/bin/bash
# Linux PyInstaller打包脚本
# 将src/click_demo.py打包成Linux可执行文件

echo "Starting click_demo packaging..."
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

# 清理并创建目录
rm -rf "$BUILD_TEMP"
mkdir -p "$BUILD_TEMP"

rm -rf "$BUILD_DIST_DIR"
mkdir -p "$BUILD_DIST_DIR"

# 复制源文件到临时目录
echo "Copying source file..."
cp "$PROJECT_DIR/src/click_demo.py" "$BUILD_TEMP/"
echo

# 运行PyInstaller打包
echo "Running PyInstaller..."
pyinstaller --onefile --distpath "$BUILD_DIST_DIR" --workpath "$BUILD_TEMP/build" --specpath "$BUILD_TEMP" "$BUILD_TEMP/click_demo.py"
echo

# 清理临时文件
echo "Cleaning up temporary files..."
rm -rf "$BUILD_TEMP"
echo

echo "Packaging complete! Executable is located at: $BUILD_DIST_DIR/click_demo"
echo

# 检查生成的可执行文件
if [ -f "$BUILD_DIST_DIR/click_demo" ]; then
    echo "Executable successfully generated."
    
    # 创建根目录下的dist目录（如果不存在）
    if [ ! -d "$ROOT_DIST_DIR" ]; then
        echo "Creating root dist directory..."
        mkdir -p "$ROOT_DIST_DIR"
    fi
    
    # 复制可执行文件到根目录下的dist目录
    echo "Copying executable to root dist directory..."
    cp "$BUILD_DIST_DIR/click_demo" "$ROOT_DIST_DIR/"
    
    if [ -f "$ROOT_DIST_DIR/click_demo" ]; then
        echo "Executable successfully archived to root dist directory."
    else
        echo "Warning: Failed to copy executable to root dist directory."
    fi
else
    echo "Warning: Executable not found."
fi

echo