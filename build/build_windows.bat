@echo off
setlocal

:: 确保当前目录是项目根目录
cd /d %~dp0\..

:: 清理旧构建
if exist dist rmdir /s /q dist

:: 安装pyinstaller
pip install pyinstaller --upgrade

:: 创建dist目录
mkdir dist

:: 打包click示例应用
pyinstaller ^
    --onefile ^
    --add-data "src;src" ^
    --hidden-import=click._compat ^
    --name click-demo ^
    --distpath dist ^
    --workpath build\project-name ^
    --specpath build\project-name ^
    src\click_demo.py

echo.
echo ==============================
echo 项目已打包到 dist\project-name
echo ==============================
echo.
echo 请创建 .env 文件（基于 .env.example）并放置在 dist\project-name 目录中
echo.
echo 运行命令:
echo dist\project-name\click-demo.exe
echo ==============================