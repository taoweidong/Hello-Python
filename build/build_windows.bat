@echo off
REM Windows PyInstaller packaging script
REM Package src\click_demo.py into a Windows executable

REM Set code page to UTF-8 to avoid garbled characters
chcp 65001 >nul

echo Starting click_demo packaging...
echo.

REM Get current directories
set BUILD_DIR=%~dp0
set PROJECT_DIR=%~dp0..
set ROOT_DIST_DIR=%PROJECT_DIR%\dist

echo BUILD_DIR: %BUILD_DIR%
echo PROJECT_DIR: %PROJECT_DIR%
echo ROOT_DIST_DIR: %ROOT_DIST_DIR%
echo.

REM Create temporary directories for packaging
set BUILD_TEMP=%BUILD_DIR%temp
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
copy "%PROJECT_DIR%\src\click_demo.py" "%BUILD_TEMP%\"
echo.

REM Check if file copy was successful
if not exist "%BUILD_TEMP%\click_demo.py" (
    echo Error: Failed to copy source file
    pause
    exit /b 1
)

REM Run PyInstaller packaging
echo Starting PyInstaller packaging...
pyinstaller --onefile --distpath "%BUILD_DIST_DIR%" --workpath "%BUILD_TEMP%\build" --specpath "%BUILD_TEMP%" "%BUILD_TEMP%\click_demo.py"
echo.

REM Clean temporary files
echo Cleaning temporary files...
rmdir /s /q "%BUILD_TEMP%"
echo.

echo Packaging completed! Executable is located at: %BUILD_DIST_DIR%\click_demo.exe
echo.

REM Check generated executable
if exist "%BUILD_DIST_DIR%\click_demo.exe" (
    echo Executable successfully generated.
    
    REM Create root dist directory if it doesn't exist
    if not exist "%ROOT_DIST_DIR%" (
        echo Creating root dist directory...
        mkdir "%ROOT_DIST_DIR%"
    )
    
    REM Copy executable to root dist directory
    echo Copying executable to root dist directory...
    copy "%BUILD_DIST_DIR%\click_demo.exe" "%ROOT_DIST_DIR%\"
    
    if exist "%ROOT_DIST_DIR%\click_demo.exe" (
        echo Executable successfully archived to root dist directory.
    ) else (
        echo Warning: Failed to copy executable to root dist directory.
    )
) else (
    echo Warning: Executable not found.
)

pause