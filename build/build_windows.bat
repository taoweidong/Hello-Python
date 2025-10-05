@echo off
chcp 65001 >nul
setlocal

:: 确保当前目录是项目根目录
cd /d %~dp0\..

:: 创建build目录结构（如果不存在）
if not exist build mkdir build
if not exist build\work mkdir build\work
if not exist build\spec mkdir build\spec

:: 清理旧构建
if exist dist rmdir /s /q dist

:: 安装pyinstaller
pip install pyinstaller --upgrade

:: 创建dist目录
mkdir dist

:: 打包click示例应用
pyinstaller ^
    --onefile ^
    --hidden-import=click._compat ^
    --name click-demo ^
    --distpath dist ^
    --workpath build\work ^
    --specpath build\spec ^
    src\click_demo.py

echo.
echo ==============================
echo 项目已打包到 dist 目录
echo ==============================
echo.
echo 请创建 .env 文件（基于 .env.example）并放置在 dist 目录中
echo.
echo 运行命令:
echo dist\click-demo.exe
echo ==============================