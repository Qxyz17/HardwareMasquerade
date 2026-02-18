@echo off
echo Installing Hardware Masquerade Driver
echo ========================================
echo.

REM Check for administrator rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Please run as Administrator!
    pause
    exit /b 1
)

REM Check if driver file exists
if not exist output\HardwareSpoofer.sys (
    echo Driver file not found! Please build first using build.bat
    pause
    exit /b 1
)

REM Copy driver to system directory
echo Copying driver to system32\drivers...
copy /Y output\HardwareSpoofer.sys %SystemRoot%\System32\drivers\

REM Install driver service
echo Installing driver service...
output\loader.exe /install

echo.
echo Driver installation complete!
pause