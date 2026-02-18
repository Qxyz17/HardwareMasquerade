@echo off
echo Building Hardware Masquerade Driver

REM 设置 VS 环境
call "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat"

REM 设置 WDK 环境
set WDK_ROOT=C:\Program Files (x86)\Windows Kits\10
set INCLUDE=%WDK_ROOT%\Include\10.0.19041.0\km;%WDK_ROOT%\Include\10.0.19041.0\um;%WDK_ROOT%\Include\10.0.19041.0\shared;%INCLUDE%
set LIB=%WDK_ROOT%\Lib\10.0.19041.0\km\x64;%WDK_ROOT%\Lib\10.0.19041.0\um\x64;%LIB%

REM 编译驱动
cl.exe /nologo /O2 /MT /W4 /Gz /kernel ^
    /I"%WDK_ROOT%\Include\10.0.19041.0\km" ^
    /I"%WDK_ROOT%\Include\10.0.19041.0\um" ^
    /I"%WDK_ROOT%\Include\10.0.19041.0\shared" ^
    /D"_KERNEL_MODE" /D"DBG=1" ^
    /FeHardwareSpoofer.sys ^
    driver/HardwareSpoofer.c ^
    /link /subsystem:native /driver /entry:DriverEntry ^
    ntoskrnl.lib hal.lib

echo Build complete!
pause