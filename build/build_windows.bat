@echo off
chcp 65001 >nul
REM Windows打包脚本
REM 自动将所有必要的资源压缩成一个zip文件

echo 正在打包Hello-Python项目...

REM 激活虚拟环境
call ..\.venv\Scripts\activate

REM 构建项目
echo 正在构建项目...
cd ..
python -m pip install -e .

REM 创建分发zip文件
echo 正在创建分发zip文件...
python -m build.create_dist_zip

echo.
echo 打包完成！分发文件位于 dist\Hello-Python.zip
echo 用户解压后可直接使用，无需手动配置！
pause
