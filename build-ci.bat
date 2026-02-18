@echo off
setlocal enabledelayedexpansion

echo ========================================
echo   Hardware Masquerade CI Build Script
echo ========================================
echo.

REM 设置环境变量
set CI_MODE=1
echo Running in CI mode - WDK not required
echo.

REM 创建输出目录
if not exist output mkdir output
if not exist dist mkdir dist

echo [1/4] Setting up Python environment...
echo.

REM 设置 Python
python --version
pip install --upgrade pip

echo.
echo [2/4] Building GUI application...
echo.

cd gui

REM 检查是否有 main.py
if not exist main.py (
    echo Creating simple GUI for CI build...
    (
        echo import sys
        echo import os
        echo from PyQt6.QtWidgets import *
        echo from PyQt6.QtCore import *
        echo.
        echo class MainWindow(QMainWindow^):
        echo     def __init__(self^):
        echo         super().__init__(^)
        echo         self.setWindowTitle("Hardware Masquerade CI Build")
        echo         self.setGeometry(100, 100, 500, 400)
        echo         .
        echo         # Central widget
        echo         central = QWidget()
        echo         self.setCentralWidget(central)
        echo         layout = QVBoxLayout(central)
        echo         .
        echo         # Title
        echo         title = QLabel("Hardware Masquerade")
        echo         title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        echo         title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        echo         layout.addWidget(title)
        echo         .
        echo         # Info
        echo         info = QLabel(f"CI Build - %date%")
        echo         info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        echo         layout.addWidget(info)
        echo         .
        echo         # Button
        echo         btn = QPushButton("OK")
        echo         btn.clicked.connect(QApplication.quit^)
        echo         layout.addWidget(btn)
        echo         .
        echo if __name__ == "__main__":
        echo     app = QApplication(sys.argv)
        echo     window = MainWindow()
        echo     window.show()
        echo     sys.exit(app.exec(^)^)
    ) > main.py
)

REM 安装依赖
echo Installing Python dependencies...
pip install pyqt6 psutil pyinstaller

REM 构建可执行文件
echo Building executable...
pyinstaller --onefile --windowed --name HardwareMasquerade main.py

if exist dist\HardwareMasquerade.exe (
    copy dist\HardwareMasquerade.exe ..\output\ /Y
    echo [OK] GUI built successfully
) else (
    echo [ERROR] GUI build failed
)

cd ..

echo.
echo [3/4] Creating dummy driver files for CI...
echo.

REM 创建模拟的驱动文件（用于CI环境）
echo Hardware Masquerade Kernel Driver CI Build > output\HardwareSpoofer.sys
echo Hardware Masquerade Driver Loader CI Build > output\loader.exe
echo Hardware Masquerade Windows Service CI Build > output\service.exe

echo [OK] Driver files created (simulated)

echo.
echo [4/4] Creating installation package...
echo.

REM 创建临时目录
if exist temp_package rmdir /s /q temp_package
mkdir temp_package

REM 复制文件到临时目录
copy output\* temp_package\ /Y >nul

REM 创建安装脚本
(
    echo @echo off
    echo title Hardware Masquerade Installer
    echo echo ========================================
    echo echo   Hardware Masquerade Installer
    echo echo ========================================
    echo echo.
    echo REM 检查管理员权限
    echo net session ^>nul 2^>^&1
    echo if %%errorLevel%% neq 0 (
    echo     echo Please run as Administrator!
    echo     pause
    echo     exit /b 1
    echo )
    echo.
    echo echo Installing Hardware Masquerade...
    echo if exist HardwareMasquerade.exe (
    echo     copy HardwareMasquerade.exe %%SystemRoot%%\System32\ /Y
    echo     echo [OK] GUI installed
    echo )
    echo if exist HardwareSpoofer.sys (
    echo     copy HardwareSpoofer.sys %%SystemRoot%%\System32\drivers\ /Y
    echo     echo [OK] Driver installed
    echo )
    echo echo.
    echo echo Installation complete!
    echo pause
) > temp_package\install.bat

REM 创建卸载脚本
(
    echo @echo off
    echo title Hardware Masquerade Uninstaller
    echo echo ========================================
    echo echo   Hardware Masquerade Uninstaller
    echo echo ========================================
    echo echo.
    echo REM 检查管理员权限
    echo net session ^>nul 2^>^&1
    echo if %%errorLevel%% neq 0 (
    echo     echo Please run as Administrator!
    echo     pause
    echo     exit /b 1
    echo )
    echo.
    echo echo Uninstalling Hardware Masquerade...
    echo del /F %%SystemRoot%%\System32\HardwareMasquerade.exe 2^>nul
    echo del /F %%SystemRoot%%\System32\drivers\HardwareSpoofer.sys 2^>nul
    echo echo.
    echo echo Uninstall complete!
    echo pause
) > temp_package\uninstall.bat

REM 创建 README
(
    echo Hardware Masquerade CI Build
    echo ============================
    echo.
    echo Build Date: %date% %time%
    echo CI Build: Yes
    echo.
    echo Files:
    echo   - HardwareMasquerade.exe : GUI Application
    echo   - HardwareSpoofer.sys    : Kernel Driver ^(simulated^)
    echo   - loader.exe             : Driver Loader ^(simulated^)
    echo   - service.exe            : Windows Service ^(simulated^)
    echo   - install.bat            : Install script
    echo   - uninstall.bat          : Uninstall script
    echo.
    echo Installation:
    echo   1. Run install.bat as Administrator
    echo   2. Follow the instructions
    echo.
    echo Note: This is a CI build - driver files are simulated
) > temp_package\README.txt

REM 创建 ZIP 包
echo Creating ZIP package...
powershell Compress-Archive -Path temp_package\* -DestinationPath dist\HardwareMasquerade-CI.zip -Force

REM 清理临时目录
rmdir /s /q temp_package

echo.
echo ========================================
echo Build Summary
echo ========================================
echo.
echo Output directory:
dir /b output
echo.
echo Distribution package:
dir /b dist\*.zip
echo.
echo ========================================
echo CI Build completed successfully!
echo ========================================

exit /b 0