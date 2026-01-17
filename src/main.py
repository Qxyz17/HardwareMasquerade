import sys
import os
import random
import string
import psutil
import wmi
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QListWidget, QListWidgetItem,
    QGroupBox, QRadioButton, QButtonGroup, QMessageBox, QTabWidget,
    QMenuBar, QMenu, QFileIconProvider
)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QTimer, QTranslator, QCoreApplication
from PyQt6.QtGui import QFont, QAction, QActionGroup

class HardwareMasquerade(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Language definitions
        self.languages = {
            'zh': {
                'title': 'Hardware Masquerade - 硬件伪装大师',
                'subtitle': 'By Qxyz17',
                'author': '作者Qxyz17',
                'github': 'https://github.com/Qxyz17/HardwareMasquerade',
                'process_tab': '进程级欺骗',
                'global_tab': '全局伪装',
                'select_process': '选择进程',
                'refresh_process': '刷新进程列表',
                'spoof_options': '欺骗选项',
                'permanent_spoof': '永久欺骗（重启后保持）',
                'start_spoofing': '开始欺骗',
                'stop_spoofing': '停止欺骗',
                'global_spoofing': '全局伪装',
                'start_global': '开始全局伪装',
                'stop_global': '停止全局伪装',
                'global_info': '全局伪装将影响系统中所有运行的进程。',
                'ready': '就绪',
                'error': '错误',
                'failed_process_list': '获取进程列表失败：',
                'warning': '警告',
                'select_process_first': '请先选择一个进程！',
                'success': '成功',
                'started_spoofing': '已开始欺骗进程：',
                'stopped_spoofing': '进程欺骗已停止',
                'started_global': '已开始全局伪装',
                'stopped_global': '全局伪装已停止',
                'spoof_error': '欺骗错误',
                'failed_spoof': '欺骗硬件ID失败：',
                'system_backup': '系统备份',
                'backup_system': '备份系统信息',
                'restore_system': '恢复系统信息',
                'language': '语言',
                'english': 'English',
                'chinese': '中文'
            },
            'en': {
                'title': 'Hardware Masquerade',
                'subtitle': 'By Qxyz17',
                'author': 'Author: Qxyz17',
                'github': 'https://github.com/Qxyz17/HardwareMasquerade',
                'process_tab': 'Process-Specific Spoofing',
                'global_tab': 'Global Spoofing',
                'select_process': 'Select Process',
                'refresh_process': 'Refresh Process List',
                'spoof_options': 'Spoof Options',
                'permanent_spoof': 'Permanent Spoof (Persist after reboot)',
                'start_spoofing': 'Start Spoofing',
                'stop_spoofing': 'Stop Spoofing',
                'global_spoofing': 'Global Spoofing',
                'start_global': 'Start Global Spoofing',
                'stop_global': 'Stop Global Spoofing',
                'global_info': 'Global spoofing will affect all processes running on the system.',
                'ready': 'Ready',
                'error': 'Error',
                'failed_process_list': 'Failed to get process list: ',
                'warning': 'Warning',
                'select_process_first': 'Please select a process first!',
                'success': 'Success',
                'started_spoofing': 'Started spoofing process: ',
                'stopped_spoofing': 'Process spoofing stopped',
                'started_global': 'Started global spoofing',
                'stopped_global': 'Global spoofing stopped',
                'spoof_error': 'Spoof Error',
                'failed_spoof': 'Failed to spoof machine ID: ',
                'system_backup': 'System Backup',
                'backup_system': 'Backup System Info',
                'restore_system': 'Restore System Info',
                'language': 'Language',
                'english': 'English',
                'chinese': '中文'
            }
        }
        
        # Current language
        self.current_language = 'zh'
        
        self.setWindowTitle(self.languages[self.current_language]['title'])
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
                color: #333333;
            }
            QLabel {
                color: #333333;
            }
            QGroupBox {
                border: 2px solid #ccc;
                border-radius: 8px;
                margin-top: 10px;
                padding: 10px;
                background-color: white;
                color: #333333;
            }
            QGroupBox::title {
                color: #333333;
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: #333333;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                color: white;
                background-color: #333333;
            }
            QListWidget::item {
                color: white;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
                color: white;
            }
            QTabWidget {
                color: #333333;
            }
            QTabWidget::pane {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar {
                color: #333333;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-bottom-color: transparent;
                padding: 8px 16px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                color: #333333;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #333333;
            }
            QMenuBar {
                color: #333333;
            }
            QMenu {
                color: #333333;
                background-color: white;
            }
            QMenu::item {
                color: #333333;
            }
            QMenu::item:selected {
                background-color: #4CAF50;
                color: #333333;
            }
            /* QMessageBox styles */
            QMessageBox {
                background-color: #333333;
                color: white;
            }
            QMessageBox QLabel {
                color: white;
            }
            QMessageBox QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QMessageBox QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        self.initUI()
        self.initProcessList()
        self.current_spoofed_processes = set()
        self.global_spoofed = False
    
    def initUI(self):
        # Create menubar with language switch
        self.createMenuBar()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        self.title_label = QLabel(self.languages[self.current_language]['title'])
        self.title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.title_label)
        
        # Author and GitHub information
        self.subtitle_label = QLabel(self.languages[self.current_language]['subtitle'])
        self.subtitle_label.setFont(QFont("Arial", 12))
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.subtitle_label)
        
        self.github_label = QLabel(f"<a href='{self.languages[self.current_language]['github']}' style='color: #4CAF50; font-weight: bold;'>{self.languages[self.current_language]['github']}</a>")
        self.github_label.setFont(QFont("Arial", 10))
        self.github_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.github_label.setOpenExternalLinks(True)
        main_layout.addWidget(self.github_label)
        
        # Tab Widget for different spoofing modes
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Process-specific spoofing tab
        self.process_tab = QWidget()
        self.tab_widget.addTab(self.process_tab, self.languages[self.current_language]['process_tab'])
        self.initProcessTab()
        
        # Global spoofing tab
        self.global_tab = QWidget()
        self.tab_widget.addTab(self.global_tab, self.languages[self.current_language]['global_tab'])
        self.initGlobalTab()
        
        # System backup tab
        self.backup_tab = QWidget()
        self.tab_widget.addTab(self.backup_tab, self.languages[self.current_language]['system_backup'])
        self.initBackupTab()
        
        # Permanent spoofing tab
        self.permanent_tab = QWidget()
        self.tab_widget.addTab(self.permanent_tab, self.languages[self.current_language]['permanent_spoof'])
        self.initPermanentSpoofTab()
        
        # Status bar
        self.status_label = QLabel(self.languages[self.current_language]['ready'])
        main_layout.addWidget(self.status_label)
    
    def createMenuBar(self):
        menubar = self.menuBar()
        
        # Language menu
        lang_menu = menubar.addMenu(self.languages[self.current_language]['language'])
        
        # Language action group
        self.lang_group = QActionGroup(self)
        self.lang_group.setExclusive(True)
        
        # Chinese action
        self.zh_action = QAction(self.languages[self.current_language]['chinese'], self)
        self.zh_action.setCheckable(True)
        self.zh_action.setChecked(self.current_language == 'zh')
        self.zh_action.triggered.connect(lambda: self.switchLanguage('zh'))
        self.lang_group.addAction(self.zh_action)
        lang_menu.addAction(self.zh_action)
        
        # English action
        self.en_action = QAction(self.languages[self.current_language]['english'], self)
        self.en_action.setCheckable(True)
        self.en_action.setChecked(self.current_language == 'en')
        self.en_action.triggered.connect(lambda: self.switchLanguage('en'))
        self.lang_group.addAction(self.en_action)
        lang_menu.addAction(self.en_action)
    
    def initProcessTab(self):
        layout = QVBoxLayout(self.process_tab)
        
        # Process selection group
        self.process_group = QGroupBox(self.languages[self.current_language]['select_process'])
        process_layout = QVBoxLayout(self.process_group)
        
        self.process_list = QListWidget()
        process_layout.addWidget(self.process_list)
        
        self.refresh_btn = QPushButton(self.languages[self.current_language]['refresh_process'])
        self.refresh_btn.clicked.connect(self.refreshProcessList)
        process_layout.addWidget(self.refresh_btn)
        
        layout.addWidget(self.process_group)
        
        # Spoof options group
        self.spoof_group = QGroupBox(self.languages[self.current_language]['spoof_options'])
        spoof_layout = QVBoxLayout(self.spoof_group)
        
        self.spoof_btn = QPushButton(self.languages[self.current_language]['start_spoofing'])
        self.spoof_btn.clicked.connect(self.startProcessSpoof)
        spoof_layout.addWidget(self.spoof_btn)
        
        self.stop_spoof_btn = QPushButton(self.languages[self.current_language]['stop_spoofing'])
        self.stop_spoof_btn.clicked.connect(self.stopProcessSpoof)
        self.stop_spoof_btn.setEnabled(False)
        spoof_layout.addWidget(self.stop_spoof_btn)
        
        layout.addWidget(self.spoof_group)
    
    def initGlobalTab(self):
        layout = QVBoxLayout(self.global_tab)
        
        self.global_group = QGroupBox(self.languages[self.current_language]['global_spoofing'])
        global_layout = QVBoxLayout(self.global_group)
        
        self.global_spoof_btn = QPushButton(self.languages[self.current_language]['start_global'])
        self.global_spoof_btn.clicked.connect(self.startGlobalSpoof)
        global_layout.addWidget(self.global_spoof_btn)
        
        self.global_stop_btn = QPushButton(self.languages[self.current_language]['stop_global'])
        self.global_stop_btn.clicked.connect(self.stopGlobalSpoof)
        self.global_stop_btn.setEnabled(False)
        global_layout.addWidget(self.global_stop_btn)
        
        layout.addWidget(self.global_group)
        
        self.info_label = QLabel(self.languages[self.current_language]['global_info'])
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("color: #666;")
        layout.addWidget(self.info_label)
    
    def initBackupTab(self):
        layout = QVBoxLayout(self.backup_tab)
        
        # System backup group
        self.backup_group = QGroupBox(self.languages[self.current_language]['system_backup'])
        backup_layout = QVBoxLayout(self.backup_group)
        
        self.backup_btn = QPushButton(self.languages[self.current_language]['backup_system'])
        self.backup_btn.clicked.connect(self.backupSystemInfo)
        backup_layout.addWidget(self.backup_btn)
        
        self.restore_btn = QPushButton(self.languages[self.current_language]['restore_system'])
        self.restore_btn.clicked.connect(self.restoreSystemInfo)
        backup_layout.addWidget(self.restore_btn)
        
        # Backup info label
        self.backup_info_label = QLabel("\n" + self.languages[self.current_language]['global_info'])
        self.backup_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.backup_info_label.setStyleSheet("color: #666;")
        backup_layout.addWidget(self.backup_info_label)
        
        layout.addWidget(self.backup_group)
    
    def initPermanentSpoofTab(self):
        layout = QVBoxLayout(self.permanent_tab)
        
        # Permanent spoofing group
        self.permanent_group = QGroupBox(self.languages[self.current_language]['permanent_spoof'])
        permanent_layout = QVBoxLayout(self.permanent_group)
        
        # Permanent spoof toggle button
        self.permanent_spoof_toggle = QPushButton(self.languages[self.current_language]['start_global'])
        self.permanent_spoof_toggle.clicked.connect(self.togglePermanentSpoof)
        permanent_layout.addWidget(self.permanent_spoof_toggle)
        
        # Permanent spoof info
        self.permanent_info_label = QLabel("\n" + self.languages[self.current_language]['global_info'])
        self.permanent_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.permanent_info_label.setStyleSheet("color: #666;")
        permanent_layout.addWidget(self.permanent_info_label)
        
        layout.addWidget(self.permanent_group)
    
    def initProcessList(self):
        self.refreshProcessList()
        # Refresh process list every 5 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.refreshProcessList)
        self.timer.start(5000)
    
    def refreshProcessList(self):
        self.process_list.clear()
        
        # Create icon provider to get file icons
        icon_provider = QFileIconProvider()
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    pid = proc.info['pid']
                    name = proc.info['name']
                    exe = proc.info['exe'] or 'N/A'
                    
                    item_text = f"{name} (PID: {pid}) - {exe}"
                    item = QListWidgetItem()
                    item.setData(Qt.ItemDataRole.UserRole, proc)
                    item.setData(Qt.ItemDataRole.DisplayRole, item_text)
                    
                    # Set flags to allow item to be selectable and checkable
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    item.setCheckState(Qt.CheckState.Unchecked)
                    
                    # Set process icon
                    if exe != 'N/A' and os.path.exists(exe):
                        try:
                            icon = icon_provider.icon(QFileIconProvider.IconType.Exe)
                            item.setIcon(icon)
                        except Exception as e:
                            # If we can't get the icon, use a default one
                            default_icon = QIcon()
                            item.setIcon(default_icon)
                    else:
                        # Use default icon for processes without exe path
                        default_icon = QIcon()
                        item.setIcon(default_icon)
                    
                    self.process_list.addItem(item)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            QMessageBox.critical(self, self.languages[self.current_language]['error'], 
                                f"{self.languages[self.current_language]['failed_process_list']}{str(e)}")
    
    def switchLanguage(self, lang_code):
        if self.current_language == lang_code:
            return
        
        self.current_language = lang_code
        
        # Update all UI elements
        self.setWindowTitle(self.languages[lang_code]['title'])
        self.title_label.setText(self.languages[lang_code]['title'])
        
        # Update author and GitHub information
        self.subtitle_label.setText(self.languages[lang_code]['subtitle'])
        self.github_label.setText(f"<a href='{self.languages[lang_code]['github']}' style='color: #4CAF50; font-weight: bold;'>{self.languages[lang_code]['github']}</a>")
        
        # Update tabs
        self.tab_widget.setTabText(0, self.languages[lang_code]['process_tab'])
        self.tab_widget.setTabText(1, self.languages[lang_code]['global_tab'])
        self.tab_widget.setTabText(2, self.languages[lang_code]['system_backup'])
        self.tab_widget.setTabText(3, self.languages[lang_code]['permanent_spoof'])
        
        # Update process tab
        self.process_group.setTitle(self.languages[lang_code]['select_process'])
        self.refresh_btn.setText(self.languages[lang_code]['refresh_process'])
        self.spoof_group.setTitle(self.languages[lang_code]['spoof_options'])
        self.spoof_btn.setText(self.languages[lang_code]['start_spoofing'])
        self.stop_spoof_btn.setText(self.languages[lang_code]['stop_spoofing'])
        
        # Update global tab
        self.global_group.setTitle(self.languages[lang_code]['global_spoofing'])
        self.global_spoof_btn.setText(self.languages[lang_code]['start_global'])
        self.global_stop_btn.setText(self.languages[lang_code]['stop_global'])
        self.info_label.setText(self.languages[lang_code]['global_info'])
        
        # Update backup tab
        self.backup_group.setTitle(self.languages[lang_code]['system_backup'])
        self.backup_btn.setText(self.languages[lang_code]['backup_system'])
        self.restore_btn.setText(self.languages[lang_code]['restore_system'])
        self.backup_info_label.setText("\n" + self.languages[lang_code]['global_info'])
        
        # Update permanent spoof tab
        self.permanent_group.setTitle(self.languages[lang_code]['permanent_spoof'])
        if hasattr(self, 'permanent_spoof_toggle'):
            self.permanent_spoof_toggle.setText(self.languages[lang_code]['start_global'])
        self.permanent_info_label.setText("\n" + self.languages[lang_code]['global_info'])
        
        # Update status bar
        self.status_label.setText(self.languages[lang_code]['ready'])
        
        # Update menu
        menubar = self.menuBar()
        menubar.clear()
        self.createMenuBar()
        
        # Update message boxes will use new language when called
    
    def generateRandomMachineID(self):
        # Generate a random machine ID
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))
    
    def spoofMachineID(self, process=None):
        # Core spoofing logic
        try:
            # Generate random machine ID
            fake_id = self.generateRandomMachineID()
            
            if process:
                # Process-specific spoofing
                pid = process.info['pid']
                self.current_spoofed_processes.add(pid)
                self.status_label.setText(f"PID {pid} {self.languages[self.current_language]['ready']}: {fake_id}")
            else:
                # Global spoofing
                self.global_spoofed = True
                self.status_label.setText(f"{self.languages[self.current_language]['global_spoofing']} {self.languages[self.current_language]['ready']}: {fake_id}")
            
            # Permanent spoofing is now handled in its own tab
            # This code has been moved to the permanent spoofing tab's toggle method
            
            # Implement comprehensive hardware ID spoofing for anti-cheat systems like ACE
            self.modifyRegistryMachineID(fake_id)
            self.modifyEnvironmentMachineID(fake_id)
            
            # Add advanced anti-detection measures
            self.spoofDiskID()
            self.spoofMACAddress()
            self.spoofCPUInfo()
            self.spoofBIOSInfo()
            self.spoofGPUInfo()
            self.spoofRAMInfo()
            self.spoofSystemInfo()
            self.spoofMotherboardInfo()
            self.spoofMonitorInfo()
            
            # Anti-cheat specific countermeasures
            self.antiHookDetection()
            self.antiDebugDetection()
            self.antiVMDetection()
            self.antiFileIntegrityCheck()
            self.antiACEDetection()
            
            return True
        except Exception as e:
            QMessageBox.critical(self, self.languages[self.current_language]['spoof_error'], 
                                f"{self.languages[self.current_language]['failed_spoof']}{str(e)}")
            return False
    
    def modifyRegistryMachineID(self, fake_id):
        # Modify registry keys related to machine ID
        # This is a simplified example
        try:
            import winreg
            
            # Example registry keys to modify
            keys_to_modify = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography", "MachineGuid"),
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\IDConfigDB\Hardware Profiles\0001", "HwProfileGuid")
            ]
            
            for root, path, value_name in keys_to_modify:
                try:
                    with winreg.OpenKey(root, path, 0, winreg.KEY_WRITE) as key:
                        winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, fake_id)
                except Exception as e:
                    print("Failed to modify registry key {}:{}".format(path + "\\" + value_name, str(e)))
        except ImportError:
            print("winreg module not available (non-Windows system)")
    
    def modifyEnvironmentMachineID(self, fake_id):
        # Modify environment variables related to machine ID
        os.environ['MACHINE_ID'] = fake_id
        os.environ['COMPUTER_ID'] = fake_id
        os.environ['HWID'] = fake_id
        os.environ['UUID'] = fake_id
        os.environ['SYSTEM_ID'] = fake_id
        os.environ['DEVICE_ID'] = fake_id
        os.environ['PC_ID'] = fake_id
    
    def generateRandomHex(self, length):
        # Generate random hex string
        return ''.join(random.choices(string.hexdigits.upper(), k=length))
    
    def generateRandomMAC(self):
        # Generate a random MAC address
        mac = [0x00, 0x16, 0x3e, 
               random.randint(0x00, 0x7f), 
               random.randint(0x00, 0xff), 
               random.randint(0x00, 0xff)]
        return ':'.join(map(lambda x: "%02x" % x, mac))
    
    def spoofDiskID(self):
        # Spoof disk IDs for anti-cheat detection
        try:
            import winreg
            
            # Generate fake disk IDs
            fake_disk_id = self.generateRandomHex(16)
            fake_volume_id = self.generateRandomHex(8)
            
            # Modify disk-related registry keys
            disk_keys = [
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\Disk\Enum", "0"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon", "DefaultDomainName"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", "ProductId"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", "DigitalProductId")
            ]
            
            for root, path, value_name in disk_keys:
                try:
                    with winreg.OpenKey(root, path, 0, winreg.KEY_WRITE) as key:
                        if value_name == "DigitalProductId":
                            # Generate random binary data for DigitalProductId
                            binary_data = bytes(random.getrandbits(8) for _ in range(164))
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_BINARY, binary_data)
                        else:
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, fake_disk_id)
                except Exception as e:
                    print(f"Failed to modify disk registry key: {e}")
                    continue
            
            # Spoof volume IDs for all drives
            for drive in string.ascii_uppercase:
                drive_letter = f"{drive}:\\"
                if os.path.exists(drive_letter):
                    try:
                        # This is a placeholder - actual volume ID spoofing requires low-level access
                        os.environ[f"VOLUME_ID_{drive}"] = fake_volume_id
                    except Exception as e:
                        print(f"Failed to spoof volume ID for {drive_letter}: {e}")
        except Exception as e:
            print(f"Disk ID spoofing failed: {e}")
    
    def spoofMACAddress(self):
        # Spoof MAC addresses for network adapters
        try:
            import winreg
            
            # Generate fake MAC address
            fake_mac = self.generateRandomMAC()
            
            # Modify MAC address registry keys
            mac_reg_path = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"
            
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, mac_reg_path, 0, winreg.KEY_READ) as base_key:
                    for i in range(100):
                        try:
                            subkey_name = winreg.EnumKey(base_key, i)
                            subkey_path = f"{mac_reg_path}\\{subkey_name}"
                            
                            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey_path, 0, winreg.KEY_WRITE) as subkey:
                                try:
                                    # Set fake MAC address
                                    winreg.SetValueEx(subkey, "NetworkAddress", 0, winreg.REG_SZ, fake_mac.replace(":", ""))
                                    # Disable and re-enable adapter (placeholder)
                                    os.environ[f"MAC_{subkey_name}"] = fake_mac
                                except Exception as e:
                                    continue
                        except OSError:
                            break
            except Exception as e:
                print(f"MAC address spoofing failed: {e}")
            
            # Set environment variables for MAC addresses
            os.environ['MAC_ADDRESS'] = fake_mac
            os.environ['ETHERNET_ADDRESS'] = fake_mac
        except Exception as e:
            print(f"MAC address spoofing failed: {e}")
    
    def spoofCPUInfo(self):
        # Spoof CPU information for anti-cheat detection
        try:
            import winreg
            
            # Generate fake CPU info
            fake_cpu_id = self.generateRandomHex(32)
            fake_cpu_name = f"Intel(R) Core(TM) i{random.randint(7, 13)}-{random.randint(7000, 13000)}K CPU @ {random.uniform(3.0, 5.5):.1f}GHz"
            
            # Modify CPU-related registry keys
            cpu_keys = [
                (winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0", "ProcessorNameString"),
                (winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0", "Identifier"),
                (winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0", "VendorIdentifier"),
                (winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0", "~MHz")
            ]
            
            for root, path, value_name in cpu_keys:
                try:
                    with winreg.OpenKey(root, path, 0, winreg.KEY_WRITE) as key:
                        if value_name == "ProcessorNameString":
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, fake_cpu_name)
                        elif value_name == "~MHz":
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, random.randint(3000, 5500))
                        else:
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, fake_cpu_id)
                except Exception as e:
                    print(f"Failed to modify CPU registry key: {e}")
                    continue
            
            # Set environment variables for CPU info
            os.environ['CPU_ID'] = fake_cpu_id
            os.environ['PROCESSOR_IDENTIFIER'] = fake_cpu_name
        except Exception as e:
            print(f"CPU info spoofing failed: {e}")
    
    def spoofBIOSInfo(self):
        # Spoof BIOS information for anti-cheat detection
        try:
            import winreg
            
            # Generate fake BIOS info
            fake_bios_vendor = random.choice(["American Megatrends Inc.", "Phoenix Technologies Ltd.", "Dell Inc.", "HP Inc."])
            fake_bios_version = f"{random.randint(1, 5)}.{random.randint(0, 20)}"
            fake_bios_date = f"{random.randint(2020, 2025)}/{random.randint(1, 12):02d}/{random.randint(1, 28):02d}"
            
            # Modify BIOS-related registry keys
            bios_keys = [
                (winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System", "BIOSVendor"),
                (winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System", "BIOSVersion"),
                (winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System", "BIOSReleaseDate"),
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\mssmbios\Data", "SMBiosData")
            ]
            
            for root, path, value_name in bios_keys:
                try:
                    with winreg.OpenKey(root, path, 0, winreg.KEY_WRITE) as key:
                        if value_name == "SMBiosData":
                            # Generate random binary data for SMBiosData
                            binary_data = bytes(random.getrandbits(8) for _ in range(4096))
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_BINARY, binary_data)
                        elif value_name == "BIOSReleaseDate":
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, fake_bios_date)
                        elif value_name == "BIOSVendor":
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, fake_bios_vendor)
                        else:
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, fake_bios_version)
                except Exception as e:
                    print(f"Failed to modify BIOS registry key: {e}")
                    continue
        except Exception as e:
            print(f"BIOS info spoofing failed: {e}")
    
    def spoofGPUInfo(self):
        # Spoof GPU information for anti-cheat detection
        try:
            import winreg
            
            # Generate fake GPU info
            gpu_vendors = ["NVIDIA Corporation", "Advanced Micro Devices, Inc.", "Intel Corporation"]
            fake_gpu_vendor = random.choice(gpu_vendors)
            
            if fake_gpu_vendor == "NVIDIA Corporation":
                fake_gpu_name = f"NVIDIA GeForce RTX {random.choice([3060, 3070, 3080, 4060, 4070, 4080])} {random.choice(['Ti', 'Super', '']).strip()}"
            elif fake_gpu_vendor == "Advanced Micro Devices, Inc.":
                fake_gpu_name = f"AMD Radeon RX {random.choice([6700, 6800, 7600, 7700, 7800])} {random.choice(['XT', 'XTX', '']).strip()}"
            else:
                fake_gpu_name = f"Intel UHD Graphics {random.randint(600, 770)}"
            
            # Modify GPU-related registry keys
            gpu_keys = [
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000", "DriverDesc"),
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000", "ProviderName"),
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000", "DriverVersion")
            ]
            
            for root, path, value_name in gpu_keys:
                try:
                    with winreg.OpenKey(root, path, 0, winreg.KEY_WRITE) as key:
                        if value_name == "DriverDesc":
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, fake_gpu_name)
                        elif value_name == "ProviderName":
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, fake_gpu_vendor)
                        else:
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, f"{random.randint(2020, 2025)}.{random.randint(1000, 5000)}")
                except Exception as e:
                    continue
            
            # Set environment variables for GPU info
            os.environ['GPU_NAME'] = fake_gpu_name
            os.environ['GPU_VENDOR'] = fake_gpu_vendor
        except Exception as e:
            print(f"GPU info spoofing failed: {e}")
    
    def spoofRAMInfo(self):
        # Spoof RAM information for anti-cheat detection
        try:
            import winreg
            
            # Generate fake RAM info
            fake_ram_size = random.choice([8, 16, 32, 64, 128])  # GB
            fake_ram_speed = random.choice([2666, 3200, 3600, 4000, 4800])  # MHz
            
            # Modify RAM-related registry keys
            ram_keys = [
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "PhysicalMemorySectionSize"),
                (winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\RESOURCEMAP\System Resources\Physical Memory", "0000")
            ]
            
            for root, path, value_name in ram_keys:
                try:
                    with winreg.OpenKey(root, path, 0, winreg.KEY_WRITE) as key:
                        if value_name == "PhysicalMemorySectionSize":
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, fake_ram_size * 1024 * 1024 * 1024)
                        else:
                            binary_data = bytes(random.getrandbits(8) for _ in range(16))
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_BINARY, binary_data)
                except Exception as e:
                    print(f"Failed to modify RAM registry key: {e}")
                    continue
            
            # Set environment variables for RAM info
            os.environ['RAM_SIZE_GB'] = str(fake_ram_size)
            os.environ['RAM_SPEED_MHZ'] = str(fake_ram_speed)
            os.environ['PHYSICAL_MEMORY'] = str(fake_ram_size * 1024 * 1024 * 1024)
        except Exception as e:
            print(f"RAM info spoofing failed: {e}")
    
    def spoofSystemInfo(self):
        # Spoof general system information for anti-cheat detection
        try:
            import winreg
            
            # Generate fake system info
            fake_computer_name = f"PC-{self.generateRandomHex(8)}"
            fake_user_name = f"User_{random.randint(1000, 9999)}"
            fake_system_version = random.choice(["10.0.22621", "10.0.19045", "10.0.18363"])
            
            # Modify system-related registry keys
            system_keys = [
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\ComputerName\ComputerName", "ComputerName"),
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\ComputerName\ActiveComputerName", "ComputerName"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", "ProductName"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", "CurrentBuildNumber"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", "CurrentVersion")
            ]
            
            for root, path, value_name in system_keys:
                try:
                    with winreg.OpenKey(root, path, 0, winreg.KEY_WRITE) as key:
                        if value_name == "ComputerName":
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, fake_computer_name)
                        elif value_name == "ProductName":
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, f"Windows 10 Pro")
                        elif value_name == "CurrentBuildNumber":
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, fake_system_version.split('.')[2])
                        elif value_name == "CurrentVersion":
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, fake_system_version.split('.')[0] + '.' + fake_system_version.split('.')[1])
                except Exception as e:
                    print(f"Failed to modify system registry key: {e}")
                    continue
            
            # Set environment variables for system info
            os.environ['COMPUTERNAME'] = fake_computer_name
            os.environ['USERNAME'] = fake_user_name
            os.environ['OS_VERSION'] = fake_system_version
        except Exception as e:
            print(f"System info spoofing failed: {e}")
    
    def spoofMotherboardInfo(self):
        # Spoof motherboard information for anti-cheat detection
        try:
            import winreg
            
            # Generate fake motherboard info
            mb_vendors = ["ASUS", "MSI", "Gigabyte", "ASRock", "Dell", "HP"]
            fake_mb_vendor = random.choice(mb_vendors)
            fake_mb_model = f"{fake_mb_vendor} {random.choice(['Z690', 'Z790', 'B660', 'B760', 'X670', 'X770'])}-{self.generateRandomHex(4)}"
            
            # Modify motherboard-related registry keys
            mb_keys = [
                (winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\BIOS", "BaseBoardManufacturer"),
                (winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\BIOS", "BaseBoardProduct")
            ]
            
            for root, path, value_name in mb_keys:
                try:
                    with winreg.OpenKey(root, path, 0, winreg.KEY_WRITE) as key:
                        if value_name == "BaseBoardManufacturer":
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, fake_mb_vendor)
                        else:
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, fake_mb_model)
                except Exception as e:
                    print(f"Failed to modify motherboard registry key: {e}")
                    continue
        except Exception as e:
            print(f"Motherboard info spoofing failed: {e}")
    
    def spoofMonitorInfo(self):
        # Spoof monitor information for anti-cheat detection
        try:
            import winreg
            
            # Generate fake monitor info
            monitor_vendors = ["Samsung", "LG", "Dell", "HP", "AOC", "Asus"]
            fake_monitor_vendor = random.choice(monitor_vendors)
            fake_monitor_model = f"{fake_monitor_vendor} {random.randint(20, 32)} {random.choice(['FHD', 'QHD', '4K'])}"
            
            # Modify monitor-related registry keys
            monitor_keys = [
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Enum\DISPLAY", fake_monitor_model)
            ]
            
            for root, path, value_name in monitor_keys:
                try:
                    with winreg.OpenKey(root, path, 0, winreg.KEY_WRITE) as key:
                        winreg.SetValueEx(key, "DeviceDesc", 0, winreg.REG_SZ, fake_monitor_model)
                except Exception as e:
                    continue
            
            # Set environment variables for monitor info
            os.environ['MONITOR_VENDOR'] = fake_monitor_vendor
            os.environ['MONITOR_MODEL'] = fake_monitor_model
        except Exception as e:
            print(f"Monitor info spoofing failed: {e}")
    
    def antiHookDetection(self):
        # Countermeasure for hook detection
        try:
            import winreg
            
            # Modify registry keys to prevent hook detection
            hook_keys = [
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\WdFilter", "Start"),
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\WdBoot", "Start")
            ]
            
            for root, path, value_name in hook_keys:
                try:
                    with winreg.OpenKey(root, path, 0, winreg.KEY_WRITE) as key:
                        # Disable Windows Defender filter drivers (careful with this!)
                        winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 4)  # 4 = Disabled
                except Exception as e:
                    continue
            
            # Set environment variables to hide hooks
            os.environ['NO_HOOKS'] = '1'
            os.environ['ANTI_HOOK_ENABLED'] = '1'
        except Exception as e:
            print(f"Anti-hook detection failed: {e}")
    
    def antiDebugDetection(self):
        # Countermeasure for debug detection
        try:
            import winreg
            
            # Modify registry keys to prevent debug detection
            debug_keys = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\ntdll.dll", "Debugger"),
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager", "GlobalFlag")
            ]
            
            for root, path, value_name in debug_keys:
                try:
                    with winreg.OpenKey(root, path, 0, winreg.KEY_WRITE) as key:
                        if value_name == "GlobalFlag":
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 0)  # Clear debug flags
                except Exception as e:
                    continue
            
            # Set environment variables to hide debugging
            os.environ['DEBUGGER_PRESENT'] = '0'
            os.environ['ANTI_DEBUG_ENABLED'] = '1'
        except Exception as e:
            print(f"Anti-debug detection failed: {e}")
    
    def antiVMDetection(self):
        # Countermeasure for virtual machine detection
        try:
            import winreg
            
            # Modify registry keys to hide VM artifacts
            vm_keys = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\VMware, Inc.", "VMware Tools"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Oracle\VirtualBox Guest Additions"),
                (winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\ACPI\DSDT\VBOX__"),
                (winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\ACPI\FADT\VBOX__"),
                (winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\ACPI\RSDT\VBOX__")
            ]
            
            for root, path, _ in vm_keys:
                try:
                    # Try to delete VM-related keys
                    winreg.DeleteKeyTree(root, path)
                except Exception as e:
                    continue
            
            # Set environment variables to hide VM
            os.environ['VIRTUAL_MACHINE'] = '0'
            os.environ['VM_DETECTED'] = '0'
            os.environ['ANTI_VM_ENABLED'] = '1'
        except Exception as e:
            print(f"Anti-VM detection failed: {e}")
    
    def antiFileIntegrityCheck(self):
        # Countermeasure for file integrity checks
        try:
            import winreg
            
            # Set environment variables to bypass file checks
            os.environ['FILE_INTEGRITY_SKIP'] = '1'
            os.environ['ANTI_INTEGRITY_ENABLED'] = '1'
            
            # Modify registry to disable file integrity monitoring
            integrity_keys = [
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\WinDefend", "Start"),
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\Sense", "Start")
            ]
            
            for root, path, value_name in integrity_keys:
                try:
                    with winreg.OpenKey(root, path, 0, winreg.KEY_WRITE) as key:
                        winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 4)  # 4 = Disabled
                except Exception as e:
                    continue
        except Exception as e:
            print(f"Anti-file integrity check failed: {e}")
    
    def antiACEDetection(self):
        # Specific countermeasures for ACE anti-cheat
        try:
            import winreg
            
            # ACE-specific registry modifications
            ace_keys = [
                (winreg.HKEY_CURRENT_USER, r"Software\ACE Anti-Cheat", "Installed"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\ACE Anti-Cheat", "Installed")
            ]
            
            for root, path, value_name in ace_keys:
                try:
                    # Try to delete ACE-related keys
                    winreg.DeleteKeyTree(root, path)
                except Exception as e:
                    continue
            
            # Set environment variables to bypass ACE detection
            os.environ['ACE_BYPASS'] = '1'
            os.environ['ACE_DETECTED'] = '0'
            os.environ['ANTI_ACE_ENABLED'] = '1'
            
            # Generate fake ACE-related files (placeholder)
            ace_fake_files = [
                "C:\\Windows\\System32\\ace32.dll",
                "C:\\Windows\\System32\\acedriver.sys",
                "C:\\Program Files\\ACE Anti-Cheat\\ace.exe"
            ]
            
            for file_path in ace_fake_files:
                try:
                    with open(file_path, 'w') as f:
                        f.write(self.generateRandomHex(1024))
                except Exception as e:
                    continue
        except Exception as e:
            print(f"Anti-ACE detection failed: {e}")
    
    def backupSystemInfo(self):
        # Backup current system hardware information
        try:
            import json
            import datetime
            
            # Create backup directory if it doesn't exist
            backup_dir = "backup"
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # Get current date and time for backup filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"system_backup_{timestamp}.json")
            
            # Read current registry keys for backup
            import winreg
            backup_data = {
                'timestamp': timestamp,
                'machine_guids': {},
                'system_info': {}
            }
            
            # Backup machine ID related keys
            keys_to_backup = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography", "MachineGuid"),
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\IDConfigDB\Hardware Profiles\0001", "HwProfileGuid")
            ]
            
            for root, path, value_name in keys_to_backup:
                try:
                    with winreg.OpenKey(root, path, 0, winreg.KEY_READ) as key:
                        value, _ = winreg.QueryValueEx(key, value_name)
                        backup_data['machine_guids'][f"{root}_{path}_{value_name}"] = value
                except Exception as e:
                    continue
            
            # Save backup to file
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=4)
            
            QMessageBox.information(self, self.languages[self.current_language]['success'], 
                                  f"{self.languages[self.current_language]['backup_system']} {self.languages[self.current_language]['success']}!\n{backup_file}")
        except Exception as e:
            QMessageBox.critical(self, self.languages[self.current_language]['error'], 
                                f"{self.languages[self.current_language]['backup_system']} {self.languages[self.current_language]['error']}: {str(e)}")
    
    def restoreSystemInfo(self):
        # Restore system hardware information from backup
        try:
            import json
            import winreg
            
            # Get list of backup files
            backup_dir = "backup"
            if not os.path.exists(backup_dir):
                QMessageBox.warning(self, self.languages[self.current_language]['warning'], 
                                   f"{self.languages[self.current_language]['backup_system']} {self.languages[self.current_language]['error']}: {backup_dir} {self.languages[self.current_language]['failed_process_list']}")
                return
            
            backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.json')]
            if not backup_files:
                QMessageBox.warning(self, self.languages[self.current_language]['warning'], 
                                   f"{self.languages[self.current_language]['backup_system']} {self.languages[self.current_language]['failed_process_list']}")
                return
            
            # Sort backup files by date (newest first)
            backup_files.sort(reverse=True)
            
            # Use the latest backup file
            latest_backup = os.path.join(backup_dir, backup_files[0])
            
            # Read backup data
            with open(latest_backup, 'r') as f:
                backup_data = json.load(f)
            
            # Restore registry keys
            for key_path, value in backup_data['machine_guids'].items():
                try:
                    # Parse key path
                    parts = key_path.split('_', 2)
                    if len(parts) != 3:
                        continue
                    
                    root_str, path, value_name = parts
                    root = getattr(winreg, root_str)
                    
                    with winreg.OpenKey(root, path, 0, winreg.KEY_WRITE) as key:
                        winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, value)
                except Exception as e:
                    continue
            
            QMessageBox.information(self, self.languages[self.current_language]['success'], 
                                  f"{self.languages[self.current_language]['restore_system']} {self.languages[self.current_language]['success']}!\n{latest_backup}")
        except Exception as e:
            QMessageBox.critical(self, self.languages[self.current_language]['error'], 
                                f"{self.languages[self.current_language]['restore_system']} {self.languages[self.current_language]['error']}: {str(e)}")
    
    def enablePermanentSpoofing(self):
        # Enable permanent spoofing that persists after reboot
        try:
            import winreg
            
            # Add the application to startup
            startup_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, startup_path, 0, winreg.KEY_WRITE) as key:
                # Set the application to run at startup
                exe_path = sys.executable
                script_path = os.path.abspath(__file__)
                winreg.SetValueEx(key, "HardwareMasquerade", 0, winreg.REG_SZ, f'"{exe_path}" "{script_path}" --auto-spoof')
            
            QMessageBox.information(self, self.languages[self.current_language]['success'], 
                                  f"{self.languages[self.current_language]['permanent_spoof']} {self.languages[self.current_language]['success']}!")
        except Exception as e:
            QMessageBox.critical(self, self.languages[self.current_language]['error'], 
                                f"{self.languages[self.current_language]['permanent_spoof']} {self.languages[self.current_language]['error']}: {str(e)}")
    
    def disablePermanentSpoofing(self):
        # Disable permanent spoofing
        try:
            import winreg
            
            # Remove the application from startup
            startup_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, startup_path, 0, winreg.KEY_WRITE) as key:
                try:
                    winreg.DeleteValue(key, "HardwareMasquerade")
                    QMessageBox.information(self, self.languages[self.current_language]['success'], 
                                          f"{self.languages[self.current_language]['permanent_spoof']} {self.languages[self.current_language]['stopped_spoofing']}!")
                except FileNotFoundError:
                    QMessageBox.information(self, self.languages[self.current_language]['success'], 
                                          f"{self.languages[self.current_language]['permanent_spoof']} {self.languages[self.current_language]['ready']}!")
        except Exception as e:
            QMessageBox.critical(self, self.languages[self.current_language]['error'], 
                                f"{self.languages[self.current_language]['permanent_spoof']} {self.languages[self.current_language]['error']}: {str(e)}")
    
    def togglePermanentSpoof(self):
        # Toggle permanent spoofing
        try:
            import winreg
            
            # Check if permanent spoofing is already enabled
            startup_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            permanent_enabled = False
            
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, startup_path, 0, winreg.KEY_READ) as key:
                    value, _ = winreg.QueryValueEx(key, "HardwareMasquerade")
                    permanent_enabled = True
            except FileNotFoundError:
                pass
            
            if permanent_enabled:
                # Disable permanent spoofing
                self.disablePermanentSpoofing()
                self.permanent_spoof_toggle.setText(self.languages[self.current_language]['start_global'])
            else:
                # Enable permanent spoofing
                self.enablePermanentSpoofing()
                self.permanent_spoof_toggle.setText(self.languages[self.current_language]['stop_global'])
        except Exception as e:
            QMessageBox.critical(self, self.languages[self.current_language]['error'], 
                                f"{self.languages[self.current_language]['permanent_spoof']} {self.languages[self.current_language]['error']}: {str(e)}")
    
    def startProcessSpoof(self):
        # Get all checked items instead of selected items
        checked_processes = []
        for i in range(self.process_list.count()):
            item = self.process_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                process = item.data(Qt.ItemDataRole.UserRole)
                checked_processes.append(process)
        
        if not checked_processes:
            QMessageBox.warning(self, self.languages[self.current_language]['warning'], 
                               self.languages[self.current_language]['select_process_first'])
            return
        
        # Spoof each checked process
        spoofed_processes = []
        for process in checked_processes:
            try:
                if self.spoofMachineID(process):
                    spoofed_processes.append(process)
            except Exception as e:
                QMessageBox.warning(self, self.languages[self.current_language]['warning'], 
                                   f"Failed to spoof {process.info['name']}: {str(e)}")
                continue
        
        if spoofed_processes:
            self.spoof_btn.setEnabled(False)
            self.stop_spoof_btn.setEnabled(True)
            
            # Show success message with all spoofed processes
            process_names = ', '.join([f"{p.info['name']} (PID: {p.info['pid']})" for p in spoofed_processes])
            QMessageBox.information(self, self.languages[self.current_language]['success'], 
                                  f"{self.languages[self.current_language]['started_spoofing']}{process_names}")
    
    def stopProcessSpoof(self, show_message=True):
        self.current_spoofed_processes.clear()
        self.spoof_btn.setEnabled(True)
        self.stop_spoof_btn.setEnabled(False)
        
        # Permanent spoofing is now handled in its own tab
        # This code has been removed
        
        self.status_label.setText(self.languages[self.current_language]['stopped_spoofing'])
        if show_message:
            QMessageBox.information(self, self.languages[self.current_language]['success'], 
                                  self.languages[self.current_language]['stopped_spoofing'])
    
    def startGlobalSpoof(self):
        if self.spoofMachineID():
            self.global_spoof_btn.setEnabled(False)
            self.global_stop_btn.setEnabled(True)
            QMessageBox.information(self, self.languages[self.current_language]['success'], 
                                  self.languages[self.current_language]['started_global'])
    
    def stopGlobalSpoof(self, show_message=True):
        self.global_spoofed = False
        self.global_spoof_btn.setEnabled(True)
        self.global_stop_btn.setEnabled(False)
        self.status_label.setText(self.languages[self.current_language]['stopped_global'])
        if show_message:
            QMessageBox.information(self, self.languages[self.current_language]['success'], 
                                  self.languages[self.current_language]['stopped_global'])
    
    def closeEvent(self, event):
        # Clean up on exit without showing messages
        self.stopProcessSpoof(show_message=False)
        self.stopGlobalSpoof(show_message=False)
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show main window
    window = HardwareMasquerade()
    window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
