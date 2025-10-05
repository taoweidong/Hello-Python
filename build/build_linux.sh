#!/bin/bash
# Linux打包脚本
# 自动将所有必要的资源压缩成一个zip文件

echo "正在打包Hello-Python项目..."

# 激活虚拟环境
source ../.venv/bin/activate

# 构建项目
echo "正在构建项目..."
cd ..
python3 -m pip install -e .

# 创建分发zip文件
echo "正在创建分发zip文件..."
python3 -m build.create_dist_zip

echo ""
echo "打包完成！分发文件位于 dist/Hello-Python.zip"
echo "用户解压后可直接使用，无需手动配置！"