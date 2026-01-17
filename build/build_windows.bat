@echo on
REM Windows PyInstaller packaging script
REM Package specified Python file from src directory into a Windows executable

REM Set code page to UTF-8 to avoid garbled characters
chcp 65001 >nul

REM Check if argument is provided
if "%~1"=="" goto :show_usage

REM 参数存在，继续执行主逻辑
echo Parameter received: %1

REM Get the filename without extension for processing
set "INPUT_FILE=%~1"

REM Check if extension is included, if not, add .py
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
set SOURCE_FILE=%PROJECT_DIR%\src\%PYTHON_FILENAME%

REM Validate that the source file exists
if not exist "%SOURCE_FILE%" (
    echo Error: Source file %SOURCE_FILE% does not exist!
    echo Available Python files in src directory:
    dir "%PROJECT_DIR%\src\*.py" /B
    pause
    exit /b 1
)

echo Starting %PYTHON_FILENAME% packaging...
echo.

REM Create temporary directories for packaging
set BUILD_TEMP=%BUILD_DIR%temp_%BASENAME%
set BUILD_DIST_DIR=%BUILD_DIR%dist

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

REM Copy source file to temporary directory
echo Copying source file...
copy "%SOURCE_FILE%" "%BUILD_TEMP%\"
echo.

REM Check if file copy was successful
if not exist "%BUILD_TEMP%\%PYTHON_FILENAME%" (
    echo Error: Failed to copy source file
    pause
    exit /b 1
)

REM Run PyInstaller packaging
echo Starting PyInstaller packaging...
pyinstaller --onefile --distpath "%BUILD_DIST_DIR%" --workpath "%BUILD_TEMP%\build" --specpath "%BUILD_TEMP%" "%BUILD_TEMP%\%PYTHON_FILENAME%"
echo.

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
    
    if exist "%ROOT_DIST_DIR%\%BASENAME%.exe" (
        echo Executable successfully archived to root dist directory.
    ) else (
        echo Warning: Failed to copy executable to root dist directory.
    )
) else (
    echo Warning: Executable not found.
)

pause
goto :eof

:show_usage
echo Usage: %0 ^<python_filename^>
echo Example: %0 click_demo.py
echo Or: %0 click_demo (without extension)
pause
exit /b 1