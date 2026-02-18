@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    Hardware Masquerade Build Script
echo ========================================
echo.

REM Check for Visual Studio
set VSWHERE="C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe"
if exist %VSWHERE% (
    for /f "usebackq tokens=*" %%i in (`%VSWHERE% -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do (
        set VS_PATH=%%i
    )
)

if not defined VS_PATH (
    echo Visual Studio not found! Please install Visual Studio 2019 or 2022.
    pause
    exit /b 1
)

echo Found Visual Studio at: %VS_PATH%

REM Load Visual Studio environment
call "%VS_PATH%\VC\Auxiliary\Build\vcvars64.bat"
if errorlevel 1 (
    echo Failed to load Visual Studio environment!
    pause
    exit /b 1
)

REM Find latest WDK
set WDK_FOUND=0
for /f "usebackq tokens=*" %%d in (`dir "C:\Program Files (x86)\Windows Kits\10\Include" /b /ad /o-n`) do (
    if exist "C:\Program Files (x86)\Windows Kits\10\Include\%%d\km" (
        set WDK_VERSION=%%d
        set WDK_FOUND=1
        goto :found_wdk
    )
)
:found_wdk

if %WDK_FOUND%==0 (
    echo Windows Driver Kit not found! Please install WDK.
    pause
    exit /b 1
)

echo Found WDK version: %WDK_VERSION%

REM Set WDK environment variables
set WDK_INCLUDE=C:\Program Files (x86)\Windows Kits\10\Include\%WDK_VERSION%
set WDK_LIB=C:\Program Files (x86)\Windows Kits\10\Lib\%WDK_VERSION%

REM Create output directory
if not exist output mkdir output

echo.
echo Building kernel driver...

cl.exe /nologo /O2 /MT /W4 /Gz /kernel ^
    /I"%WDK_INCLUDE%\km" ^
    /I"%WDK_INCLUDE%\um" ^
    /I"%WDK_INCLUDE%\shared" ^
    /I"common" ^
    /D_KERNEL_MODE /DDBG=1 /DUNICODE /D_UNICODE ^
    /Feoutput\HardwareSpoofer.sys ^
    driver\HardwareSpoofer.c ^
    /link /subsystem:native /driver /entry:DriverEntry ^
    ntoskrnl.lib hal.lib

if errorlevel 1 (
    echo Driver build failed!
) else (
    echo Driver built successfully!
)

echo.
echo Building driver loader...

cl.exe /nologo /O2 /W4 ^
    /I"common" ^
    /Feoutput\loader.exe ^
    driver_loader\loader.c ^
    /link advapi32.lib user32.lib

if errorlevel 1 (
    echo Loader build failed!
) else (
    echo Loader built successfully!
)

echo.
echo Building service...

cl.exe /nologo /O2 /W4 ^
    /I"common" ^
    /Feoutput\service.exe ^
    service\service.c ^
    /link advapi32.lib user32.lib

if errorlevel 1 (
    echo Service build failed!
) else (
    echo Service built successfully!
)

echo.
echo ========================================
echo           Build Complete
echo ========================================
echo Output files are in the 'output' directory
echo.

dir output

pause