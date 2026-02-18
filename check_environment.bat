@echo off
echo Checking development environment...

echo.
echo Visual Studio:
if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" (
    echo   VS 2022 Community found
) else if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat" (
    echo   VS 2019 Community found
) else (
    echo   Visual Studio not found!
)

echo.
echo Windows SDK:
set SDK_FOUND=0
for /d %%i in ("C:\Program Files (x86)\Windows Kits\10\Include\*") do (
    if exist "%%i\km\ntddk.h" (
        echo   Windows SDK %%i found
        set SDK_FOUND=1
    )
)
if %SDK_FOUND%==0 echo   Windows SDK not found!

echo.
echo WDK:
if exist "C:\Program Files (x86)\Windows Kits\10\Include\10.0.19041.0\km" (
    echo   WDK 10.0.19041.0 found
) else (
    echo   WDK not found!
)

echo.
echo Environment variables:
echo   INCLUDE=%INCLUDE%
echo   LIB=%LIB%

pause