@echo off
REM 测试生成的可执行文件

echo Testing click_demo executable...
echo.

echo Running: dist\click_demo.exe --help
echo ----------------------------------------
dist\click_demo.exe --help
echo ----------------------------------------
echo.

echo Testing hello command:
echo ----------------------------------------
dist\click_demo.exe hello --count 2 --name "Test User"
echo ----------------------------------------
echo.

echo Test completed.
pause