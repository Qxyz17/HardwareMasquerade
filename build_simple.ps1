# build_simple.ps1 - 修复版

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Hardware Masquerade Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 设置错误时停止
$ErrorActionPreference = "Stop"

# 函数：查找 Visual Studio
function Find-VisualStudioEnvironment {
    $vsPaths = @(
        "C:\Program Files\Microsoft Visual Studio\2022\Community",
        "C:\Program Files\Microsoft Visual Studio\2022\Professional",
        "C:\Program Files\Microsoft Visual Studio\2022\Enterprise",
        "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community",
        "C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional",
        "C:\Program Files (x86)\Microsoft Visual Studio\2019\Enterprise"
    )
    
    $vcvarsPaths = @(
        "VC\Auxiliary\Build\vcvars64.bat",
        "VC\Auxiliary\Build\vcvars32.bat"
    )
    
    foreach ($vsPath in $vsPaths) {
        foreach ($vcvars in $vcvarsPaths) {
            $fullPath = Join-Path $vsPath $vcvars
            if (Test-Path $fullPath) {
                Write-Host "找到 Visual Studio: $vsPath" -ForegroundColor Green
                return $fullPath
            }
        }
    }
    
    return $null
}

# 函数：查找最新的 WDK
function Get-WDKInfo {
    $kitRoot = "C:\Program Files (x86)\Windows Kits\10"
    $includePath = Join-Path $kitRoot "Include"
    
    if (Test-Path $includePath) {
        $versions = Get-ChildItem $includePath -Directory | Sort-Object Name -Descending
        foreach ($version in $versions) {
            $kmPath = Join-Path $version.FullName "km"
            if (Test-Path $kmPath) {
                Write-Host "找到 WDK 版本: $($version.Name)" -ForegroundColor Green
                return @{
                    Root = $kitRoot
                    Version = $version.Name
                    Include = $version.FullName
                    Lib = Join-Path $kitRoot "Lib\$($version.Name)"
                }
            }
        }
    }
    
    return $null
}

# 函数：设置环境
function Initialize-BuildEnvironment {
    param(
        [string]$VcVarsPath,
        [hashtable]$WDKInfo
    )
    
    Write-Host "`n设置构建环境..." -ForegroundColor Yellow
    
    # 调用 vcvars
    if ($VcVarsPath) {
        Write-Host "加载 Visual Studio 环境: $VcVarsPath"
        $vcvarsDir = Split-Path $VcVarsPath -Parent
        Set-Location $vcvarsDir
        cmd /c "$(Split-Path $VcVarsPath -Leaf) && set" | ForEach-Object {
            if ($_ -match "=") {
                $key, $value = $_.Split('=', 2)
                [Environment]::SetEnvironmentVariable($key, $value, 'Process')
            }
        }
        Set-Location $PSScriptRoot
    }
    
    # 设置 WDK 环境变量
    if ($WDKInfo) {
        $env:WDK_ROOT = $WDKInfo.Root
        $env:WDK_VERSION = $WDKInfo.Version
        $env:WDK_INCLUDE = $WDKInfo.Include
        $env:WDK_LIB = $WDKInfo.Lib
        $env:INCLUDE = "$($WDKInfo.Include)\km;$($WDKInfo.Include)\um;$($WDKInfo.Include)\shared;$env:INCLUDE"
        $env:LIB = "$($WDKInfo.Lib)\km\x64;$($WDKInfo.Lib)\um\x64;$env:LIB"
    }
    
    Write-Host "环境设置完成!" -ForegroundColor Green
}

# 函数：编译驱动
function Invoke-DriverBuild {
    Write-Host "`n编译内核驱动..." -ForegroundColor Yellow
    
    # 创建输出目录
    $outputDir = Join-Path $PSScriptRoot "output"
    New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
    
    # 编译驱动
    $source = Join-Path $PSScriptRoot "driver\HardwareSpoofer.c"
    $output = Join-Path $outputDir "HardwareSpoofer.sys"
    
    # 检查源文件
    if (-not (Test-Path $source)) {
        Write-Host "错误: 找不到源文件 $source" -ForegroundColor Red
        return $false
    }
    
    $clArguments = @(
        "/nologo",
        "/O2",
        "/MT",
        "/W4",
        "/Gz",
        "/kernel",
        "/I`"$env:WDK_INCLUDE\km`"",
        "/I`"$env:WDK_INCLUDE\um`"",
        "/I`"$env:WDK_INCLUDE\shared`"",
        "/I`"$PSScriptRoot\common`"",
        "/D_KERNEL_MODE",
        "/DDBG=1",
        "/DUNICODE",
        "/D_UNICODE",
        "/Fe$output",
        "`"$source`"",
        "/link",
        "/subsystem:native",
        "/driver",
        "/entry:DriverEntry",
        "ntoskrnl.lib",
        "hal.lib"
    )
    
    Write-Host "运行: cl.exe $clArguments"
    $process = Start-Process -FilePath "cl.exe" -ArgumentList $clArguments -NoNewWindow -Wait -PassThru
    
    if ($process.ExitCode -eq 0) {
        Write-Host "驱动编译成功: $output" -ForegroundColor Green
        return $true
    } else {
        Write-Host "驱动编译失败!" -ForegroundColor Red
        return $false
    }
}

# 函数：编译加载器
function Invoke-LoaderBuild {
    Write-Host "`n编译驱动加载器..." -ForegroundColor Yellow
    
    $outputDir = Join-Path $PSScriptRoot "output"
    $source = Join-Path $PSScriptRoot "driver_loader\loader.c"
    $output = Join-Path $outputDir "loader.exe"
    
    if (-not (Test-Path $source)) {
        Write-Host "错误: 找不到源文件 $source" -ForegroundColor Red
        return $false
    }
    
    $clArguments = @(
        "/nologo",
        "/O2",
        "/W4",
        "/I`"$PSScriptRoot\common`"",
        "/Fe$output",
        "`"$source`"",
        "/link",
        "advapi32.lib",
        "user32.lib"
    )
    
    Write-Host "运行: cl.exe $clArguments"
    $process = Start-Process -FilePath "cl.exe" -ArgumentList $clArguments -NoNewWindow -Wait -PassThru
    
    if ($process.ExitCode -eq 0) {
        Write-Host "加载器编译成功: $output" -ForegroundColor Green
        return $true
    } else {
        Write-Host "加载器编译失败!" -ForegroundColor Red
        return $false
    }
}

# 函数：编译服务
function Invoke-ServiceBuild {
    Write-Host "`n编译 Windows 服务..." -ForegroundColor Yellow
    
    $outputDir = Join-Path $PSScriptRoot "output"
    $source = Join-Path $PSScriptRoot "service\service.c"
    $output = Join-Path $outputDir "service.exe"
    
    if (-not (Test-Path $source)) {
        Write-Host "错误: 找不到源文件 $source" -ForegroundColor Red
        return $false
    }
    
    $clArguments = @(
        "/nologo",
        "/O2",
        "/W4",
        "/I`"$PSScriptRoot\common`"",
        "/Fe$output",
        "`"$source`"",
        "/link",
        "advapi32.lib",
        "user32.lib"
    )
    
    Write-Host "运行: cl.exe $clArguments"
    $process = Start-Process -FilePath "cl.exe" -ArgumentList $clArguments -NoNewWindow -Wait -PassThru
    
    if ($process.ExitCode -eq 0) {
        Write-Host "服务编译成功: $output" -ForegroundColor Green
        return $true
    } else {
        Write-Host "服务编译失败!" -ForegroundColor Red
        return $false
    }
}

# 主构建流程
try {
    # 1. 查找 Visual Studio
    Write-Host "步骤 1: 查找 Visual Studio..." -ForegroundColor Cyan
    $vcvarsPath = Find-VisualStudioEnvironment
    if (-not $vcvarsPath) {
        throw "未找到 Visual Studio！请安装 Visual Studio 2019 或 2022。"
    }
    
    # 2. 查找 WDK
    Write-Host "`n步骤 2: 查找 Windows Driver Kit..." -ForegroundColor Cyan
    $wdkInfo = Get-WDKInfo
    if (-not $wdkInfo) {
        throw "未找到 Windows Driver Kit！请安装 WDK。"
    }
    
    # 3. 设置环境
    Write-Host "`n步骤 3: 设置环境..." -ForegroundColor Cyan
    Initialize-BuildEnvironment -VcVarsPath $vcvarsPath -WDKInfo $wdkInfo
    
    # 4. 创建输出目录
    $outputDir = Join-Path $PSScriptRoot "output"
    New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
    
    # 5. 编译各组件
    Write-Host "`n步骤 4: 编译组件..." -ForegroundColor Cyan
    
    $driverSuccess = Invoke-DriverBuild
    $loaderSuccess = Invoke-LoaderBuild
    $serviceSuccess = Invoke-ServiceBuild
    
    # 6. 显示结果
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "           构建总结" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    
    if ($driverSuccess) { Write-Host "驱动:        成功" -ForegroundColor Green }
    else { Write-Host "驱动:        失败" -ForegroundColor Red }
    
    if ($loaderSuccess) { Write-Host "加载器:      成功" -ForegroundColor Green }
    else { Write-Host "加载器:      失败" -ForegroundColor Red }
    
    if ($serviceSuccess) { Write-Host "服务:        成功" -ForegroundColor Green }
    else { Write-Host "服务:        失败" -ForegroundColor Red }
    
    if ($driverSuccess -and $loaderSuccess -and $serviceSuccess) {
        Write-Host "`n所有组件编译成功!" -ForegroundColor Green
        Write-Host "输出目录: $outputDir" -ForegroundColor Yellow
        
        # 显示文件列表
        Write-Host "`n生成的文件:" -ForegroundColor Cyan
        Get-ChildItem $outputDir | ForEach-Object {
            Write-Host "  $($_.Name) ($($_.Length) 字节)" -ForegroundColor White
        }
    } else {
        Write-Host "`n部分组件编译失败!" -ForegroundColor Red
    }
    
} catch {
    Write-Host "`n构建失败: $_" -ForegroundColor Red
    Read-Host "按 Enter 键退出"
    exit 1
}

Read-Host "`n按 Enter 键退出"