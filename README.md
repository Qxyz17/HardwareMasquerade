# Hardware Masquerade - 硬件伪装大师

A Qt6-based hardware ID spoofing tool that supports process-specific and global system hardware ID masquerading.

一个基于Qt6开发的硬件ID欺骗工具，支持针对特定进程和全局系统的硬件ID伪装。

QQ交流群 : 


## Features - 功能特点

- **Process-Specific Spoofing**: Precisely select target processes for hardware ID masquerading without affecting other programs
- **Global Masquerade Mode**: Hardware ID spoofing that affects all running processes in the system
- **Real-time Process List**: Dynamically displays all currently running processes, supports manual refresh
- **Modern Qt6 Interface**: Clean and intuitive graphical user interface, easy to operate
- **Intelligent ID Generation**: Automatically generates random hardware IDs to ensure masquerade effectiveness

- **进程级欺骗**：精准选择目标进程进行硬件ID伪装，不影响其他程序
- **全局伪装模式**：对系统中所有运行进程生效的硬件ID欺骗
- **实时进程列表**：动态显示当前运行的所有进程，支持手动刷新
- **现代化Qt6界面**：简洁直观的图形用户界面，操作便捷
- **智能ID生成**：自动生成随机硬件ID，确保伪装效果

## System Requirements - 系统要求

- Windows operating system
- Python 3.8 or higher
- PyQt6 >= 6.4.0
- psutil >= 5.9.0
- wmi >= 1.5.1
- pywin32 >= 306

- Windows操作系统
- Python 3.8 或更高版本
- PyQt6 >= 6.4.0
- psutil >= 5.9.0
- wmi >= 1.5.1
- pywin32 >= 306

## Installation - 安装步骤

1. Clone or download this project to your local machine
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

1. 克隆或下载本项目到本地
2. 安装所需依赖包：
   ```
   pip install -r requirements.txt
   ```

## Usage - 使用方法

1. Run the application:
   ```
   python src/main.py
   ```

2. **Process-Specific Spoofing**:
   - Navigate to the "Process-Specific Spoofing" tab
   - Select a target process from the list
   - Click "Start Spoofing" to begin masquerading
   - Click "Stop Spoofing" to stop masquerading

3. **Global Spoofing**:
   - Navigate to the "Global Spoofing" tab
   - Click "Start Global Spoofing" to begin global masquerading
   - Click "Stop Global Spoofing" to stop global masquerading

4. **Language Switching**:
   - Click the "Language" menu in the menubar
   - Select your preferred language (English/中文)

1. 运行应用程序：
   ```
   python src/main.py
   ```

2. **进程级欺骗**：
   - 切换到"Process-Specific Spoofing"（进程级欺骗）标签页
   - 从列表中选择目标进程
   - 点击"Start Spoofing"（开始欺骗）开始伪装
   - 点击"Stop Spoofing"（停止欺骗）停止伪装

3. **全局伪装**：
   - 切换到"Global Spoofing"（全局伪装）标签页
   - 点击"Start Global Spoofing"（开始全局伪装）开启全局伪装
   - 点击"Stop Global Spoofing"（停止全局伪装）停止全局伪装

4. **语言切换**：
   - 点击菜单栏中的"Language"（语言）菜单
   - 选择您偏好的语言（English/中文）

## How It Works - 工作原理

The application achieves hardware ID spoofing by:
1. Generating random 32-bit hardware identifiers
2. Modifying relevant registry keys
3. Setting system environment variables
4. Applying masquerade strategies to selected processes

本工具通过以下方式实现硬件ID欺骗：
1. 生成随机的32位硬件标识符
2. 修改系统注册表中相关的硬件ID键值
3. 设置系统环境变量中的硬件ID信息
4. 针对选定进程应用伪装策略

## Registry Keys Modified - 修改的注册表键值

- `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Cryptography\MachineGuid`
- `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\IDConfigDB\Hardware Profiles\0001\HwProfileGuid`

## Environment Variables Set - 设置的环境变量

- `MACHINE_ID`
- `COMPUTER_ID`

## Disclaimer - 免责声明

This tool is for educational and research purposes only. Modifying system settings and registry keys may cause system instability. Use this tool at your own risk.

The author is not responsible for any damage or issues caused by using this tool.

本工具仅用于教育和研究目的。修改系统设置和注册表可能导致系统不稳定。使用本工具时，请确保您了解相关风险，并在自己的责任范围内操作。

作者不对使用本工具造成的任何损坏或问题负责。

## License - 许可证

Apache-2.0 license

## Contributing - 贡献

Contributions are welcome! Please feel free to submit a Pull Request.

欢迎提交Pull Request进行贡献！
