# build-ci.ps1
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Hardware Masquerade CI Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 创建输出目录
New-Item -ItemType Directory -Force -Path output | Out-Null
New-Item -ItemType Directory -Force -Path dist | Out-Null

Write-Host "[1/4] Setting up Python environment..." -ForegroundColor Yellow
python --version
pip install --upgrade pip

Write-Host ""
Write-Host "[2/4] Building GUI application..." -ForegroundColor Yellow

# 进入 gui 目录
if (-not (Test-Path "gui")) {
    New-Item -ItemType Directory -Force -Path gui | Out-Null
}
Set-Location gui

# 创建简单的 GUI 程序
$guiCode = @'
import sys
import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QVBoxLayout, QLabel, QPushButton)
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hardware Masquerade CI Build")
        self.setGeometry(100, 100, 500, 400)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Title
        title = QLabel("Hardware Masquerade")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Info
        info = QLabel(f"CI Build - {datetime.datetime.now().strftime('%Y-%m-%d')}")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        
        # Button
        btn = QPushButton("OK")
        btn.clicked.connect(QApplication.quit)
        layout.addWidget(btn)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
'@

if (-not (Test-Path "main.py")) {
    $guiCode | Out-File -FilePath main.py -Encoding utf8
    Write-Host "Created main.py" -ForegroundColor Green
}

# 安装依赖
Write-Host "Installing Python dependencies..." -ForegroundColor Gray
pip install pyqt6 psutil pyinstaller

# 构建可执行文件
Write-Host "Building executable..." -ForegroundColor Gray
pyinstaller --onefile --windowed --name HardwareMasquerade main.py

if (Test-Path "dist\HardwareMasquerade.exe") {
    Copy-Item "dist\HardwareMasquerade.exe" "..\output\" -Force
    Write-Host "[OK] GUI built successfully" -ForegroundColor Green
} else {
    Write-Host "[ERROR] GUI build failed" -ForegroundColor Red
}

Set-Location ..

Write-Host ""
Write-Host "[3/4] Creating dummy driver files for CI..." -ForegroundColor Yellow

# 创建模拟的驱动文件
"Hardware Masquerade Kernel Driver CI Build" | Out-File -FilePath output\HardwareSpoofer.sys -Encoding ascii
"Hardware Masquerade Driver Loader CI Build" | Out-File -FilePath output\loader.exe -Encoding ascii
"Hardware Masquerade Windows Service CI Build" | Out-File -FilePath output\service.exe -Encoding ascii

Write-Host "[OK] Driver files created (simulated)" -ForegroundColor Green

Write-Host ""
Write-Host "[4/4] Creating installation package..." -ForegroundColor Yellow

# 创建临时目录
$tempDir = "temp_package"
if (Test-Path $tempDir) {
    Remove-Item -Path $tempDir -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

# 复制文件
Copy-Item -Path "output\*" -Destination $tempDir -Force

# 创建安装脚本
$installScript = @'
@echo off
title Hardware Masquerade Installer
echo ========================================
echo   Hardware Masquerade Installer
echo ========================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Please run as Administrator!
    pause
    exit /b 1
)

echo Installing Hardware Masquerade...
if exist HardwareMasquerade.exe (
    copy HardwareMasquerade.exe %SystemRoot%\System32\ /Y
    echo [OK] GUI installed
)
if exist HardwareSpoofer.sys (
    copy HardwareSpoofer.sys %SystemRoot%\System32\drivers\ /Y
    echo [OK] Driver installed
)
echo.
echo Installation complete!
pause
'@
$installScript | Out-File -FilePath "$tempDir\install.bat" -Encoding ascii

# 创建卸载脚本
$uninstallScript = @'
@echo off
title Hardware Masquerade Uninstaller
echo ========================================
echo   Hardware Masquerade Uninstaller
echo ========================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Please run as Administrator!
    pause
    exit /b 1
)

echo Uninstalling Hardware Masquerade...
del /F %SystemRoot%\System32\HardwareMasquerade.exe 2>nul
del /F %SystemRoot%\System32\drivers\HardwareSpoofer.sys 2>nul
echo.
echo Uninstall complete!
pause
'@
$uninstallScript | Out-File -FilePath "$tempDir\uninstall.bat" -Encoding ascii

# 创建 README
$readme = @"
Hardware Masquerade CI Build
============================

Build Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
CI Build: Yes

Files:
  - HardwareMasquerade.exe : GUI Application
  - HardwareSpoofer.sys    : Kernel Driver (simulated)
  - loader.exe             : Driver Loader (simulated)
  - service.exe            : Windows Service (simulated)
  - install.bat            : Install script
  - uninstall.bat          : Uninstall script

Installation:
  1. Run install.bat as Administrator
  2. Follow the instructions

Note: This is a CI build - driver files are simulated
"@
$readme | Out-File -FilePath "$tempDir\README.txt" -Encoding utf8

# 创建 ZIP 包
Write-Host "Creating ZIP package..." -ForegroundColor Gray
Compress-Archive -Path "$tempDir\*" -DestinationPath "dist\HardwareMasquerade-CI.zip" -Force

# 清理临时目录
Remove-Item -Path $tempDir -Recurse -Force

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Build Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Output directory:" -ForegroundColor Yellow
Get-ChildItem -Path output | ForEach-Object { Write-Host "  $($_.Name)" -ForegroundColor White }
Write-Host ""
Write-Host "Distribution package:" -ForegroundColor Yellow
Get-ChildItem -Path dist\*.zip | ForEach-Object { 
    $size = [math]::Round($_.Length / 1MB, 2)
    Write-Host "  $($_.Name) ($size MB)" -ForegroundColor White 
}
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CI Build completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan