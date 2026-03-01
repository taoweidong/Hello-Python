@echo off
REM Windows PyInstaller打包脚本
REM 将examples目录下的指定Python文件打包成Windows可执行文件
REM 使用方法: build_windows.bat <filename> (不带.py扩展名)

REM Set code page to UTF-8 to avoid garbled characters
chcp 65001 >nul

REM Check if argument is provided
if "%~1"=="" goto :show_usage

set "INPUT_FILE=%~1"
if "%INPUT_FILE:~-3%"==".py" (
    set "PYTHON_FILENAME=%INPUT_FILE%"
    set "BASENAME=%INPUT_FILE:~0,-3%"
) else (
    set "PYTHON_FILENAME=%INPUT_FILE%.py"
    set "BASENAME=%INPUT_FILE%"
)

REM Define paths
set BUILD_DIR=%~dp0
set PROJECT_DIR=%~dp0..
set ROOT_DIST_DIR=%PROJECT_DIR%\dist
set BUILD_TEMP=%BUILD_DIR%temp
set BUILD_DIST_DIR=%BUILD_DIR%dist

REM Validate that the source file exists in examples directory
set "SOURCE_FILE=%PROJECT_DIR%\examples\%PYTHON_FILENAME%"
if not exist "%SOURCE_FILE%" (
    echo 错误: 文件 %SOURCE_FILE% 不存在!
    echo examples目录中的可用文件:
    dir "%PROJECT_DIR%\examples\*.py"
    pause
    exit /b 1
)

echo Starting packaging %PYTHON_FILENAME% from examples...
echo.

REM Clean old temporary directories
if exist "%BUILD_TEMP%" (
    echo Cleaning old temporary directory...
    rmdir /s /q "%BUILD_TEMP%"
)

REM Clean old build dist directory
if exist "%BUILD_DIST_DIR%" (
    echo Cleaning old build dist directory...
    rmdir /s /q "%BUILD_DIST_DIR%"
)

REM Create new directories
echo Creating temporary directories...
mkdir "%BUILD_TEMP%"
mkdir "%BUILD_DIST_DIR%"

REM Create a standalone entry script that includes all necessary imports and paths
set "ENTRY_SCRIPT=%BUILD_TEMP%\%BASENAME%_entry.py"

echo #!/usr/bin/env python3 > "%ENTRY_SCRIPT%"
echo. >> "%ENTRY_SCRIPT%"
echo import sys >> "%ENTRY_SCRIPT%"
echo import os >> "%ENTRY_SCRIPT%"
echo from pathlib import Path >> "%ENTRY_SCRIPT%"
echo. >> "%ENTRY_SCRIPT%"
echo # Add project root to path to allow imports >> "%ENTRY_SCRIPT%"
echo PROJECT_ROOT = Path(__file__).parent.parent.parent >> "%ENTRY_SCRIPT%"
echo sys.path.insert(0, str(PROJECT_ROOT)) >> "%ENTRY_SCRIPT%"
echo. >> "%ENTRY_SCRIPT%"
echo # Import required modules >> "%ENTRY_SCRIPT%"
echo try: >> "%ENTRY_SCRIPT%"
echo     from src.app import initialize_app >> "%ENTRY_SCRIPT%"
echo     from src.business.processors import get_data_processor >> "%ENTRY_SCRIPT%"
echo     from src.business.services import get_analysis_service >> "%ENTRY_SCRIPT%"
echo     from src.business.repositories import get_data_repository >> "%ENTRY_SCRIPT%"
echo except ImportError as e: >> "%ENTRY_SCRIPT%"
echo     print(f"Import error: {e}") >> "%ENTRY_SCRIPT%"
echo     sys.exit(1) >> "%ENTRY_SCRIPT%"
echo. >> "%ENTRY_SCRIPT%"
echo # Now include the original script content >> "%ENTRY_SCRIPT%"
type "%SOURCE_FILE%" >> "%ENTRY_SCRIPT%"

REM Run PyInstaller packaging
echo Packaging %PYTHON_FILENAME%...
echo.

pyinstaller --onefile --name=%BASENAME% ^
    --distpath "%BUILD_DIST_DIR%" ^
    --workpath "%BUILD_TEMP%\build" ^
    --specpath "%BUILD_TEMP%" ^
    --add-data "%PROJECT_DIR%\src;src" ^
    --add-data "%PROJECT_DIR%\examples;examples" ^
    --add-data "%PROJECT_DIR%\data;data" ^
    --hidden-import="src" ^
    --hidden-import="examples" ^
    --hidden-import="src.core" ^
    --hidden-import="src.business" ^
    --hidden-import="src.interfaces" ^
    --hidden-import="src.app" ^
    --hidden-import="src.business.processors" ^
    --hidden-import="src.business.services" ^
    --hidden-import="src.business.repositories" ^
    --hidden-import="src.core.config" ^
    --hidden-import="src.core.logging" ^
    --hidden-import="src.core.database" ^
    --hidden-import="src.core.exceptions" ^
    "%ENTRY_SCRIPT%"

REM Clean temporary files
echo Cleaning temporary files...
rmdir /s /q "%BUILD_TEMP%"
echo.

echo Packaging completed! Executable is located at: %BUILD_DIST_DIR%\%BASENAME%.exe
echo.

REM Check generated executable
if exist "%BUILD_DIST_DIR%\%BASENAME%.exe" (
    echo Executable successfully generated.
    
    REM Create root dist directory if it doesn't exist
    if not exist "%ROOT_DIST_DIR%" (
        echo Creating root dist directory...
        mkdir "%ROOT_DIST_DIR%"
    )
    
    REM Copy executable to root dist directory
    echo Copying executable to root dist directory...
    copy "%BUILD_DIST_DIR%\%BASENAME%.exe" "%ROOT_DIST_DIR%\"
    
    if errorlevel 1 (
        echo Warning: Failed to copy executable to root dist directory.
    ) else (
        echo Executable successfully archived to root dist directory.
    )
) else (
    echo Warning: Executable not found.
)

goto :eof

:show_usage
echo 使用方法: %0 ^<filename^>
echo 示例: %0 basic_usage
echo       %0 advanced_analysis
echo       %0 custom_extensions
pause
exit /b 1