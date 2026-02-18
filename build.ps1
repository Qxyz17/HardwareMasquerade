# build.ps1 - Hardware Masquerade Build Script (English Version)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Hardware Masquerade Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Stop on errors
$ErrorActionPreference = "Stop"

# Function: Find Visual Studio
function Find-VisualStudio {
    $vsPaths = @(
        "C:\Program Files\Microsoft Visual Studio\2022\Community",
        "C:\Program Files\Microsoft Visual Studio\2022\Professional",
        "C:\Program Files\Microsoft Visual Studio\2022\Enterprise",
        "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community",
        "C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional",
        "C:\Program Files (x86)\Microsoft Visual Studio\2019\Enterprise",
        "C:\Program Files (x86)\Microsoft Visual Studio\2017\Community",
        "C:\Program Files (x86)\Microsoft Visual Studio\2017\Professional",
        "C:\Program Files (x86)\Microsoft Visual Studio\2017\Enterprise"
    )
    
    $vcvarsPaths = @(
        "VC\Auxiliary\Build\vcvars64.bat",
        "VC\Auxiliary\Build\vcvars32.bat"
    )
    
    foreach ($vsPath in $vsPaths) {
        foreach ($vcvars in $vcvarsPaths) {
            $fullPath = Join-Path $vsPath $vcvars
            if (Test-Path $fullPath) {
                Write-Host "Found Visual Studio at: $vsPath" -ForegroundColor Green
                return $fullPath
            }
        }
    }
    
    return $null
}

# Function: Find WDK
function Find-WDK {
    $kitRoot = "C:\Program Files (x86)\Windows Kits\10"
    $includePath = Join-Path $kitRoot "Include"
    
    if (Test-Path $includePath) {
        $versions = Get-ChildItem $includePath -Directory | Sort-Object Name -Descending
        foreach ($version in $versions) {
            $kmPath = Join-Path $version.FullName "km"
            if (Test-Path $kmPath) {
                Write-Host "Found WDK version: $($version.Name)" -ForegroundColor Green
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

# Function: Setup build environment
function Setup-BuildEnvironment {
    param(
        [string]$VcVarsPath,
        [hashtable]$WDKInfo
    )
    
    Write-Host "`nSetting up build environment..." -ForegroundColor Yellow
    
    # Load vcvars
    if ($VcVarsPath) {
        Write-Host "Loading Visual Studio environment: $VcVarsPath"
        $vcvarsDir = Split-Path $VcVarsPath -Parent
        Push-Location $vcvarsDir
        cmd /c "$(Split-Path $VcVarsPath -Leaf) && set" | ForEach-Object {
            if ($_ -match "=") {
                $key, $value = $_.Split('=', 2)
                [Environment]::SetEnvironmentVariable($key, $value, 'Process')
            }
        }
        Pop-Location
    }
    
    # Set WDK environment variables
    if ($WDKInfo) {
        $env:WDK_ROOT = $WDKInfo.Root
        $env:WDK_VERSION = $WDKInfo.Version
        $env:WDK_INCLUDE = $WDKInfo.Include
        $env:WDK_LIB = $WDKInfo.Lib
        $env:INCLUDE = "$($WDKInfo.Include)\km;$($WDKInfo.Include)\um;$($WDKInfo.Include)\shared;$env:INCLUDE"
        $env:LIB = "$($WDKInfo.Lib)\km\x64;$($WDKInfo.Lib)\um\x64;$env:LIB"
    }
    
    Write-Host "Environment setup complete!" -ForegroundColor Green
}

# Function: Build driver
function Build-Driver {
    Write-Host "`nBuilding kernel driver..." -ForegroundColor Yellow
    
    # Create output directory
    $outputDir = Join-Path $PSScriptRoot "output"
    New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
    
    # Compile driver
    $source = Join-Path $PSScriptRoot "driver\HardwareSpoofer.c"
    $output = Join-Path $outputDir "HardwareSpoofer.sys"
    
    # Check source file
    if (-not (Test-Path $source)) {
        Write-Host "ERROR: Source file not found: $source" -ForegroundColor Red
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
        "/Fe`"$output`"",
        "`"$source`"",
        "/link",
        "/subsystem:native",
        "/driver",
        "/entry:DriverEntry",
        "ntoskrnl.lib",
        "hal.lib"
    )
    
    Write-Host "Running: cl.exe $clArguments"
    & cl.exe $clArguments
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Driver built successfully: $output" -ForegroundColor Green
        return $true
    } else {
        Write-Host "Driver build failed!" -ForegroundColor Red
        return $false
    }
}

# Function: Build loader
function Build-Loader {
    Write-Host "`nBuilding driver loader..." -ForegroundColor Yellow
    
    $outputDir = Join-Path $PSScriptRoot "output"
    $source = Join-Path $PSScriptRoot "driver_loader\loader.c"
    $output = Join-Path $outputDir "loader.exe"
    
    if (-not (Test-Path $source)) {
        Write-Host "ERROR: Source file not found: $source" -ForegroundColor Red
        return $false
    }
    
    $clArguments = @(
        "/nologo",
        "/O2",
        "/W4",
        "/I`"$PSScriptRoot\common`"",
        "/Fe`"$output`"",
        "`"$source`"",
        "/link",
        "advapi32.lib",
        "user32.lib"
    )
    
    Write-Host "Running: cl.exe $clArguments"
    & cl.exe $clArguments
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Loader built successfully: $output" -ForegroundColor Green
        return $true
    } else {
        Write-Host "Loader build failed!" -ForegroundColor Red
        return $false
    }
}

# Function: Build service
function Build-Service {
    Write-Host "`nBuilding Windows service..." -ForegroundColor Yellow
    
    $outputDir = Join-Path $PSScriptRoot "output"
    $source = Join-Path $PSScriptRoot "service\service.c"
    $output = Join-Path $outputDir "service.exe"
    
    if (-not (Test-Path $source)) {
        Write-Host "ERROR: Source file not found: $source" -ForegroundColor Red
        return $false
    }
    
    $clArguments = @(
        "/nologo",
        "/O2",
        "/W4",
        "/I`"$PSScriptRoot\common`"",
        "/Fe`"$output`"",
        "`"$source`"",
        "/link",
        "advapi32.lib",
        "user32.lib"
    )
    
    Write-Host "Running: cl.exe $clArguments"
    & cl.exe $clArguments
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Service built successfully: $output" -ForegroundColor Green
        return $true
    } else {
        Write-Host "Service build failed!" -ForegroundColor Red
        return $false
    }
}

# Main build process
try {
    # Step 1: Find Visual Studio
    Write-Host "Step 1: Finding Visual Studio..." -ForegroundColor Cyan
    $vcvarsPath = Find-VisualStudio
    if (-not $vcvarsPath) {
        throw "Visual Studio not found! Please install Visual Studio 2019 or 2022."
    }
    
    # Step 2: Find WDK
    Write-Host "`nStep 2: Finding Windows Driver Kit..." -ForegroundColor Cyan
    $wdkInfo = Find-WDK
    if (-not $wdkInfo) {
        throw "Windows Driver Kit not found! Please install WDK."
    }
    
    # Step 3: Setup environment
    Write-Host "`nStep 3: Setting up environment..." -ForegroundColor Cyan
    Setup-BuildEnvironment -VcVarsPath $vcvarsPath -WDKInfo $wdkInfo
    
    # Step 4: Create output directory
    $outputDir = Join-Path $PSScriptRoot "output"
    New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
    
    # Step 5: Build components
    Write-Host "`nStep 4: Building components..." -ForegroundColor Cyan
    
    $driverSuccess = Build-Driver
    $loaderSuccess = Build-Loader
    $serviceSuccess = Build-Service
    
    # Step 6: Show results
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "           Build Summary" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    
    if ($driverSuccess) { Write-Host "Driver:        SUCCESS" -ForegroundColor Green }
    else { Write-Host "Driver:        FAILED" -ForegroundColor Red }
    
    if ($loaderSuccess) { Write-Host "Loader:        SUCCESS" -ForegroundColor Green }
    else { Write-Host "Loader:        FAILED" -ForegroundColor Red }
    
    if ($serviceSuccess) { Write-Host "Service:       SUCCESS" -ForegroundColor Green }
    else { Write-Host "Service:       FAILED" -ForegroundColor Red }
    
    if ($driverSuccess -and $loaderSuccess -and $serviceSuccess) {
        Write-Host "`nAll components built successfully!" -ForegroundColor Green
        Write-Host "Output directory: $outputDir" -ForegroundColor Yellow
        
        # Show file list
        Write-Host "`nGenerated files:" -ForegroundColor Cyan
        Get-ChildItem $outputDir | ForEach-Object {
            Write-Host "  $($_.Name) ($($_.Length) bytes)" -ForegroundColor White
        }
    } else {
        Write-Host "`nSome components failed to build!" -ForegroundColor Red
    }
    
} catch {
    Write-Host "`nBuild failed: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Read-Host "`nPress Enter to exit"