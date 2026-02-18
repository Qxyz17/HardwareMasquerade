import os
import sys
import subprocess
import shutil

def build_driver():
    """Build kernel driver using Windows DDK/WDK"""
    print("Building kernel driver...")
    
    # Check for WDK environment
    wdk_path = os.environ.get('WDK_ROOT', r'C:\Program Files (x86)\Windows Kits\10')
    build_cmd = [
        'msbuild',
        'driver/HardwareSpoofer.vcxproj',
        '/p:Configuration=Release',
        '/p:Platform=x64'
    ]
    
    try:
        subprocess.run(build_cmd, check=True)
        print("Driver built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to build driver: {e}")
        return False

def build_loader():
    """Build driver loader"""
    print("Building driver loader...")
    
    loader_cmd = [
        'cl.exe',
        '/nologo',
        '/O2',
        '/MT',
        '/W4',
        'driver_loader/loader.c',
        '/Fe:loader.exe',
        '/link',
        'advapi32.lib',
        'kernel32.lib',
        'user32.lib'
    ]
    
    try:
        subprocess.run(loader_cmd, check=True, shell=True)
        print("Loader built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to build loader: {e}")
        return False

def sign_driver():
    """Sign the driver with a test certificate"""
    print("Signing driver...")
    
    # Create test certificate if not exists
    if not os.path.exists('HardwareSpoofer.cer'):
        makecert_cmd = [
            'makecert',
            '-r',
            '-pe',
            '-ss', 'PrivateCertStore',
            '-n', 'CN=HardwareSpoofer',
            '-eku', '1.3.6.1.5.5.7.3.3',
            'HardwareSpoofer.cer'
        ]
        subprocess.run(makecert_cmd, check=True)
    
    # Sign driver
    sign_cmd = [
        'signtool',
        'sign',
        '/fd', 'SHA256',
        '/a',
        '/s', 'PrivateCertStore',
        '/n', 'HardwareSpoofer',
        '/t', 'http://timestamp.digicert.com',
        'driver/Release/HardwareSpoofer.sys'
    ]
    
    try:
        subprocess.run(sign_cmd, check=True)
        print("Driver signed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to sign driver: {e}")
        return False

def create_installer():
    """Create installer package"""
    print("Creating installer...")
    
    # Create distribution directory
    dist_dir = 'dist'
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    
    # Copy files
    shutil.copy('driver/Release/HardwareSpoofer.sys', dist_dir)
    shutil.copy('loader.exe', dist_dir)
    shutil.copy('gui/main.py', dist_dir)
    
    # Create requirements.txt
    with open(os.path.join(dist_dir, 'requirements.txt'), 'w') as f:
        f.write('PyQt6>=6.4.0\npsutil>=5.9.0\n')
    
    # Create batch file for installation
    with open(os.path.join(dist_dir, 'install.bat'), 'w') as f:
        f.write("""@echo off
echo Installing Hardware Masquerade...

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Please run as Administrator!
    pause
    exit /b 1
)

REM Install Python dependencies
pip install -r requirements.txt

REM Register driver
copy HardwareSpoofer.sys %SystemRoot%\\System32\\drivers\\

echo Installation complete!
pause
""")
    
    print(f"Installer created in {dist_dir}")

def main():
    print("=== Hardware Masquerade Build Script ===\n")
    
    # Check for admin rights
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    
    if not is_admin:
        print("Warning: Building driver may require administrator privileges")
    
    # Build components
    if not build_driver():
        print("Driver build failed!")
        return 1
    
    if not build_loader():
        print("Loader build failed!")
        return 1
    
    # Sign driver
    if not sign_driver():
        print("Driver signing failed!")
        return 1
    
    # Create installer
    create_installer()
    
    print("\n=== Build Complete ===")
    print("Distribution files are in the 'dist' directory")
    print("Run install.bat as administrator to install")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())