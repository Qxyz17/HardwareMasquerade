import sys
import os
import ctypes
import random
import string
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import psutil

# Windows API constants
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 3
FILE_ATTRIBUTE_NORMAL = 0x80
IOCTL_SET_SPOOF_CONFIG = 0x222003  # Custom IOCTL code
IOCTL_ENABLE_SPOOFING = 0x222007
IOCTL_DISABLE_SPOOFING = 0x22200B

class SPOOF_CONFIG(ctypes.Structure):
    _fields_ = [
        ("SpoofDiskId", ctypes.c_bool),
        ("SpoofMacAddress", ctypes.c_bool),
        ("SpoofCpuId", ctypes.c_bool),
        ("SpoofBiosInfo", ctypes.c_bool),
        ("SpoofGpuInfo", ctypes.c_bool),
        ("SpoofRamInfo", ctypes.c_bool),
        ("SpoofMotherboard", ctypes.c_bool),
        ("SpoofMonitorInfo", ctypes.c_bool),
        ("FakeDiskId", ctypes.c_wchar * 64),
        ("FakeMacAddress", ctypes.c_wchar * 18),
        ("FakeCpuId", ctypes.c_wchar * 64),
        ("FakeBiosVersion", ctypes.c_wchar * 64),
        ("FakeGpuName", ctypes.c_wchar * 128),
        ("FakeRamSize", ctypes.c_ulong),
        ("FakeMotherboard", ctypes.c_wchar * 64),
        ("FakeMonitorInfo", ctypes.c_wchar * 128),
        ("EnableProcessFilter", ctypes.c_bool),
        ("TargetProcessIds", ctypes.c_ulong * 32),
        ("ProcessCount", ctypes.c_ulong),
    ]

class HardwareSpooferGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.driver_handle = None
        self.spoofing_enabled = False
        self.translations = self.load_translations()
        self.current_lang = 'en'
        
        self.initUI()
        self.load_driver()
        
    def load_translations(self):
        return {
            'en': {
                'window_title': 'Hardware Masquerade - Kernel Mode',
                'process_tab': 'Process Selection',
                'hardware_tab': 'Hardware Spoofing',
                'driver_tab': 'Driver Control',
                'select_processes': 'Select Processes to Spoof',
                'refresh': 'Refresh',
                'select_all': 'Select All',
                'deselect_all': 'Deselect All',
                'hardware_options': 'Hardware Spoofing Options',
                'disk_id': 'Spoof Disk ID',
                'mac_address': 'Spoof MAC Address',
                'cpu_id': 'Spoof CPU ID',
                'bios_info': 'Spoof BIOS Info',
                'gpu_info': 'Spoof GPU Info',
                'ram_info': 'Spoof RAM Info',
                'motherboard': 'Spoof Motherboard',
                'monitor': 'Spoof Monitor Info',
                'fake_values': 'Fake Values',
                'generate': 'Generate Random',
                'apply': 'Apply Settings',
                'enable': 'Enable Spoofing',
                'disable': 'Disable Spoofing',
                'driver_status': 'Driver Status:',
                'not_loaded': 'Not Loaded',
                'loaded': 'Loaded',
                'load_driver': 'Load Driver',
                'unload_driver': 'Unload Driver',
                'status': 'Status:',
                'inactive': 'Inactive',
                'active': 'Active',
                'success': 'Success',
                'error': 'Error',
                'warning': 'Warning',
                'info': 'Information',
                'driver_loaded': 'Driver loaded successfully',
                'driver_unloaded': 'Driver unloaded successfully',
                'spoofing_enabled': 'Spoofing enabled',
                'spoofing_disabled': 'Spoofing disabled',
                'admin_required': 'Administrator privileges required!',
                'language': 'Language',
                'chinese': 'Chinese',
                'english': 'English',
            },
            'zh': {
                'window_title': '硬件伪装大师 - 内核模式',
                'process_tab': '进程选择',
                'hardware_tab': '硬件伪装',
                'driver_tab': '驱动控制',
                'select_processes': '选择要伪装的进程',
                'refresh': '刷新',
                'select_all': '全选',
                'deselect_all': '取消全选',
                'hardware_options': '硬件伪装选项',
                'disk_id': '伪装磁盘ID',
                'mac_address': '伪装MAC地址',
                'cpu_id': '伪装CPU ID',
                'bios_info': '伪装BIOS信息',
                'gpu_info': '伪装GPU信息',
                'ram_info': '伪装RAM信息',
                'motherboard': '伪装主板信息',
                'monitor': '伪装显示器信息',
                'fake_values': '伪造值',
                'generate': '随机生成',
                'apply': '应用设置',
                'enable': '启用伪装',
                'disable': '禁用伪装',
                'driver_status': '驱动状态:',
                'not_loaded': '未加载',
                'loaded': '已加载',
                'load_driver': '加载驱动',
                'unload_driver': '卸载驱动',
                'status': '状态:',
                'inactive': '未激活',
                'active': '已激活',
                'success': '成功',
                'error': '错误',
                'warning': '警告',
                'info': '信息',
                'driver_loaded': '驱动加载成功',
                'driver_unloaded': '驱动卸载成功',
                'spoofing_enabled': '伪装已启用',
                'spoofing_disabled': '伪装已禁用',
                'admin_required': '需要管理员权限！',
                'language': '语言',
                'chinese': '中文',
                'english': 'English',
            }
        }
    
    def initUI(self):
        self.setWindowTitle(self.translations[self.current_lang]['window_title'])
        self.setGeometry(100, 100, 800, 600)
        
        # Check admin rights
        if not ctypes.windll.shell32.IsUserAnAdmin():
            QMessageBox.warning(self, self.translations[self.current_lang]['warning'],
                              self.translations[self.current_lang]['admin_required'])
        
        # Create menu bar
        menubar = self.menuBar()
        lang_menu = menubar.addMenu(self.translations[self.current_lang]['language'])
        
        en_action = QAction(self.translations[self.current_lang]['english'], self)
        en_action.triggered.connect(lambda: self.switch_language('en'))
        lang_menu.addAction(en_action)
        
        zh_action = QAction(self.translations[self.current_lang]['chinese'], self)
        zh_action.triggered.connect(lambda: self.switch_language('zh'))
        lang_menu.addAction(zh_action)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Tab widget
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Process tab
        process_tab = self.create_process_tab()
        tabs.addTab(process_tab, self.translations[self.current_lang]['process_tab'])
        
        # Hardware tab
        hardware_tab = self.create_hardware_tab()
        tabs.addTab(hardware_tab, self.translations[self.current_lang]['hardware_tab'])
        
        # Driver tab
        driver_tab = self.create_driver_tab()
        tabs.addTab(driver_tab, self.translations[self.current_lang]['driver_tab'])
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(self.translations[self.current_lang]['inactive'])
    
    def create_process_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Process list
        layout.addWidget(QLabel(self.translations[self.current_lang]['select_processes']))
        
        self.process_list = QListWidget()
        self.process_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        layout.addWidget(self.process_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton(self.translations[self.current_lang]['refresh'])
        refresh_btn.clicked.connect(self.refresh_processes)
        btn_layout.addWidget(refresh_btn)
        
        select_all_btn = QPushButton(self.translations[self.current_lang]['select_all'])
        select_all_btn.clicked.connect(self.select_all_processes)
        btn_layout.addWidget(select_all_btn)
        
        deselect_all_btn = QPushButton(self.translations[self.current_lang]['deselect_all'])
        deselect_all_btn.clicked.connect(self.deselect_all_processes)
        btn_layout.addWidget(deselect_all_btn)
        
        layout.addLayout(btn_layout)
        
        self.refresh_processes()
        return tab
    
    def create_hardware_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Hardware options group
        options_group = QGroupBox(self.translations[self.current_lang]['hardware_options'])
        options_layout = QVBoxLayout(options_group)
        
        self.hw_checkboxes = {}
        hw_options = [
            ('disk_id', self.translations[self.current_lang]['disk_id']),
            ('mac_address', self.translations[self.current_lang]['mac_address']),
            ('cpu_id', self.translations[self.current_lang]['cpu_id']),
            ('bios_info', self.translations[self.current_lang]['bios_info']),
            ('gpu_info', self.translations[self.current_lang]['gpu_info']),
            ('ram_info', self.translations[self.current_lang]['ram_info']),
            ('motherboard', self.translations[self.current_lang]['motherboard']),
            ('monitor', self.translations[self.current_lang]['monitor']),
        ]
        
        for key, text in hw_options:
            cb = QCheckBox(text)
            cb.setChecked(True)
            self.hw_checkboxes[key] = cb
            options_layout.addWidget(cb)
        
        layout.addWidget(options_group)
        
        # Fake values group
        values_group = QGroupBox(self.translations[self.current_lang]['fake_values'])
        values_layout = QGridLayout(values_group)
        
        # Fake values inputs
        self.fake_inputs = {}
        row = 0
        
        # Disk ID
        values_layout.addWidget(QLabel('Disk ID:'), row, 0)
        self.fake_inputs['disk_id'] = QLineEdit(self.generate_random_disk_id())
        values_layout.addWidget(self.fake_inputs['disk_id'], row, 1)
        row += 1
        
        # MAC Address
        values_layout.addWidget(QLabel('MAC Address:'), row, 0)
        self.fake_inputs['mac'] = QLineEdit(self.generate_random_mac())
        values_layout.addWidget(self.fake_inputs['mac'], row, 1)
        row += 1
        
        # CPU ID
        values_layout.addWidget(QLabel('CPU ID:'), row, 0)
        self.fake_inputs['cpu'] = QLineEdit(self.generate_random_cpu_id())
        values_layout.addWidget(self.fake_inputs['cpu'], row, 1)
        row += 1
        
        # BIOS Version
        values_layout.addWidget(QLabel('BIOS Version:'), row, 0)
        self.fake_inputs['bios'] = QLineEdit(self.generate_random_bios())
        values_layout.addWidget(self.fake_inputs['bios'], row, 1)
        row += 1
        
        # GPU Name
        values_layout.addWidget(QLabel('GPU Name:'), row, 0)
        self.fake_inputs['gpu'] = QLineEdit(self.generate_random_gpu())
        values_layout.addWidget(self.fake_inputs['gpu'], row, 1)
        row += 1
        
        # RAM Size (MB)
        values_layout.addWidget(QLabel('RAM Size (MB):'), row, 0)
        self.fake_inputs['ram'] = QLineEdit(str(random.choice([8192, 16384, 32768, 65536])))
        values_layout.addWidget(self.fake_inputs['ram'], row, 1)
        row += 1
        
        # Generate button
        generate_btn = QPushButton(self.translations[self.current_lang]['generate'])
        generate_btn.clicked.connect(self.generate_random_values)
        values_layout.addWidget(generate_btn, row, 0, 1, 2)
        
        layout.addWidget(values_group)
        
        # Apply button
        apply_btn = QPushButton(self.translations[self.current_lang]['apply'])
        apply_btn.clicked.connect(self.apply_settings)
        layout.addWidget(apply_btn)
        
        return tab
    
    def create_driver_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Driver status
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel(self.translations[self.current_lang]['driver_status']))
        
        self.driver_status_label = QLabel(self.translations[self.current_lang]['not_loaded'])
        self.driver_status_label.setStyleSheet("color: red; font-weight: bold;")
        status_layout.addWidget(self.driver_status_label)
        
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        # Spoofing status
        spoof_layout = QHBoxLayout()
        spoof_layout.addWidget(QLabel(self.translations[self.current_lang]['status']))
        
        self.spoof_status_label = QLabel(self.translations[self.current_lang]['inactive'])
        self.spoof_status_label.setStyleSheet("color: orange; font-weight: bold;")
        spoof_layout.addWidget(self.spoof_status_label)
        
        spoof_layout.addStretch()
        layout.addLayout(spoof_layout)
        
        # Driver control buttons
        btn_layout = QHBoxLayout()
        
        self.load_btn = QPushButton(self.translations[self.current_lang]['load_driver'])
        self.load_btn.clicked.connect(self.load_driver)
        btn_layout.addWidget(self.load_btn)
        
        self.unload_btn = QPushButton(self.translations[self.current_lang]['unload_driver'])
        self.unload_btn.clicked.connect(self.unload_driver)
        self.unload_btn.setEnabled(False)
        btn_layout.addWidget(self.unload_btn)
        
        layout.addLayout(btn_layout)
        
        # Spoofing control buttons
        spoof_btn_layout = QHBoxLayout()
        
        self.enable_btn = QPushButton(self.translations[self.current_lang]['enable'])
        self.enable_btn.clicked.connect(self.enable_spoofing)
        self.enable_btn.setEnabled(False)
        spoof_btn_layout.addWidget(self.enable_btn)
        
        self.disable_btn = QPushButton(self.translations[self.current_lang]['disable'])
        self.disable_btn.clicked.connect(self.disable_spoofing)
        self.disable_btn.setEnabled(False)
        spoof_btn_layout.addWidget(self.disable_btn)
        
        layout.addLayout(spoof_btn_layout)
        layout.addStretch()
        
        return tab
    
    def refresh_processes(self):
        self.process_list.clear()
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                item = QListWidgetItem(f"{proc.info['name']} (PID: {proc.info['pid']})")
                item.setData(Qt.ItemDataRole.UserRole, proc.info['pid'])
                self.process_list.addItem(item)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    
    def select_all_processes(self):
        self.process_list.selectAll()
    
    def deselect_all_processes(self):
        self.process_list.clearSelection()
    
    def generate_random_disk_id(self):
        return ''.join(random.choices('0123456789ABCDEF', k=16))
    
    def generate_random_mac(self):
        mac = [0x00, 0x16, 0x3E, 
               random.randint(0x00, 0x7F),
               random.randint(0x00, 0xFF),
               random.randint(0x00, 0xFF)]
        return ':'.join(f'{b:02x}' for b in mac)
    
    def generate_random_cpu_id(self):
        return ''.join(random.choices('0123456789ABCDEF', k=32))
    
    def generate_random_bios(self):
        vendors = ['American Megatrends', 'Phoenix', 'Dell', 'HP', 'Lenovo']
        versions = ['1.0', '1.5', '2.0', '2.5', '3.0']
        return f"{random.choice(vendors)} {random.choice(versions)}"
    
    def generate_random_gpu(self):
        vendors = ['NVIDIA', 'AMD', 'Intel']
        models = ['RTX 3060', 'RTX 3070', 'RTX 3080', 'RX 6800', 'RX 6900', 'UHD Graphics']
        return f"{random.choice(vendors)} {random.choice(models)}"
    
    def generate_random_values(self):
        self.fake_inputs['disk_id'].setText(self.generate_random_disk_id())
        self.fake_inputs['mac'].setText(self.generate_random_mac())
        self.fake_inputs['cpu'].setText(self.generate_random_cpu_id())
        self.fake_inputs['bios'].setText(self.generate_random_bios())
        self.fake_inputs['gpu'].setText(self.generate_random_gpu())
        self.fake_inputs['ram'].setText(str(random.choice([8192, 16384, 32768, 65536])))
    
    def load_driver(self):
        try:
            # Load driver using service manager
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            
            # Create service for driver
            scm = ctypes.windll.advapi32.OpenSCManagerW(None, None, 0xF003F)
            if not scm:
                raise Exception("Failed to open Service Control Manager")
            
            driver_path = os.path.abspath("HardwareSpoofer.sys")
            service = ctypes.windll.advapi32.CreateServiceW(
                scm,
                "HardwareSpoofer",
                "HardwareSpoofer",
                0xF01FF,
                1,  # SERVICE_KERNEL_DRIVER
                3,  # SERVICE_DEMAND_START
                1,  # SERVICE_ERROR_NORMAL
                driver_path,
                None, None, None, None, None
            )
            
            if not service:
                err = ctypes.get_last_error()
                if err == 1073:  # ERROR_SERVICE_EXISTS
                    service = ctypes.windll.advapi32.OpenServiceW(scm, "HardwareSpoofer", 0xF01FF)
            
            if service:
                ctypes.windll.advapi32.StartServiceW(service, 0, None)
                ctypes.windll.advapi32.CloseServiceHandle(service)
            
            ctypes.windll.advapi32.CloseServiceHandle(scm)
            
            # Open device handle
            self.driver_handle = kernel32.CreateFileW(
                "\\\\.\\HardwareSpoofer",
                GENERIC_READ | GENERIC_WRITE,
                0, None, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, None
            )
            
            if self.driver_handle and self.driver_handle != -1:
                self.driver_status_label.setText(self.translations[self.current_lang]['loaded'])
                self.driver_status_label.setStyleSheet("color: green; font-weight: bold;")
                self.load_btn.setEnabled(False)
                self.unload_btn.setEnabled(True)
                self.enable_btn.setEnabled(True)
                QMessageBox.information(self, self.translations[self.current_lang]['success'],
                                      self.translations[self.current_lang]['driver_loaded'])
            else:
                raise Exception("Failed to open driver device")
                
        except Exception as e:
            QMessageBox.critical(self, self.translations[self.current_lang]['error'],
                               f"Failed to load driver: {str(e)}")
    
    def unload_driver(self):
        try:
            if self.driver_handle and self.driver_handle != -1:
                ctypes.windll.kernel32.CloseHandle(self.driver_handle)
                self.driver_handle = None
            
            # Stop and remove service
            scm = ctypes.windll.advapi32.OpenSCManagerW(None, None, 0xF003F)
            if scm:
                service = ctypes.windll.advapi32.OpenServiceW(scm, "HardwareSpoofer", 0xF01FF)
                if service:
                    # Stop service
                    service_status = ctypes.c_ulong()
                    ctypes.windll.advapi32.ControlService(service, 1, ctypes.byref(service_status))
                    
                    # Delete service
                    ctypes.windll.advapi32.DeleteService(service)
                    ctypes.windll.advapi32.CloseServiceHandle(service)
                
                ctypes.windll.advapi32.CloseServiceHandle(scm)
            
            self.driver_status_label.setText(self.translations[self.current_lang]['not_loaded'])
            self.driver_status_label.setStyleSheet("color: red; font-weight: bold;")
            self.load_btn.setEnabled(True)
            self.unload_btn.setEnabled(False)
            self.enable_btn.setEnabled(False)
            self.disable_btn.setEnabled(False)
            self.spoof_status_label.setText(self.translations[self.current_lang]['inactive'])
            self.spoof_status_label.setStyleSheet("color: orange; font-weight: bold;")
            
            QMessageBox.information(self, self.translations[self.current_lang]['success'],
                                  self.translations[self.current_lang]['driver_unloaded'])
            
        except Exception as e:
            QMessageBox.critical(self, self.translations[self.current_lang]['error'],
                               f"Failed to unload driver: {str(e)}")
    
    def apply_settings(self):
        if not self.driver_handle or self.driver_handle == -1:
            QMessageBox.warning(self, self.translations[self.current_lang]['warning'],
                              "Driver not loaded!")
            return
        
        try:
            # Get selected processes
            selected_pids = []
            for item in self.process_list.selectedItems():
                pid = item.data(Qt.ItemDataRole.UserRole)
                selected_pids.append(pid)
            
            # Create config structure
            config = SPOOF_CONFIG()
            config.SpoofDiskId = self.hw_checkboxes['disk_id'].isChecked()
            config.SpoofMacAddress = self.hw_checkboxes['mac_address'].isChecked()
            config.SpoofCpuId = self.hw_checkboxes['cpu_id'].isChecked()
            config.SpoofBiosInfo = self.hw_checkboxes['bios_info'].isChecked()
            config.SpoofGpuInfo = self.hw_checkboxes['gpu_info'].isChecked()
            config.SpoofRamInfo = self.hw_checkboxes['ram_info'].isChecked()
            config.SpoofMotherboard = self.hw_checkboxes['motherboard'].isChecked()
            config.SpoofMonitorInfo = self.hw_checkboxes['monitor'].isChecked()
            
            # Set fake values
            config.FakeDiskId = self.fake_inputs['disk_id'].text()
            config.FakeMacAddress = self.fake_inputs['mac'].text()
            config.FakeCpuId = self.fake_inputs['cpu'].text()
            config.FakeBiosVersion = self.fake_inputs['bios'].text()
            config.FakeGpuName = self.fake_inputs['gpu'].text()
            config.FakeRamSize = int(self.fake_inputs['ram'].text())
            
            # Set process filter
            config.EnableProcessFilter = len(selected_pids) > 0
            config.ProcessCount = len(selected_pids)
            for i, pid in enumerate(selected_pids[:32]):
                config.TargetProcessIds[i] = pid
            
            # Send config to driver
            bytes_returned = ctypes.c_ulong()
            result = ctypes.windll.kernel32.DeviceIoControl(
                self.driver_handle,
                IOCTL_SET_SPOOF_CONFIG,
                ctypes.byref(config),
                ctypes.sizeof(config),
                None,
                0,
                ctypes.byref(bytes_returned),
                None
            )
            
            if result:
                QMessageBox.information(self, self.translations[self.current_lang]['success'],
                                      "Settings applied successfully!")
            else:
                raise Exception(f"DeviceIoControl failed: {ctypes.get_last_error()}")
                
        except Exception as e:
            QMessageBox.critical(self, self.translations[self.current_lang]['error'],
                               f"Failed to apply settings: {str(e)}")
    
    def enable_spoofing(self):
        if not self.driver_handle or self.driver_handle == -1:
            return
        
        try:
            bytes_returned = ctypes.c_ulong()
            result = ctypes.windll.kernel32.DeviceIoControl(
                self.driver_handle,
                IOCTL_ENABLE_SPOOFING,
                None,
                0,
                None,
                0,
                ctypes.byref(bytes_returned),
                None
            )
            
            if result:
                self.spoofing_enabled = True
                self.spoof_status_label.setText(self.translations[self.current_lang]['active'])
                self.spoof_status_label.setStyleSheet("color: green; font-weight: bold;")
                self.enable_btn.setEnabled(False)
                self.disable_btn.setEnabled(True)
                self.status_bar.showMessage(self.translations[self.current_lang]['active'])
                
                QMessageBox.information(self, self.translations[self.current_lang]['success'],
                                      self.translations[self.current_lang]['spoofing_enabled'])
            else:
                raise Exception(f"DeviceIoControl failed: {ctypes.get_last_error()}")
                
        except Exception as e:
            QMessageBox.critical(self, self.translations[self.current_lang]['error'],
                               f"Failed to enable spoofing: {str(e)}")
    
    def disable_spoofing(self):
        if not self.driver_handle or self.driver_handle == -1:
            return
        
        try:
            bytes_returned = ctypes.c_ulong()
            result = ctypes.windll.kernel32.DeviceIoControl(
                self.driver_handle,
                IOCTL_DISABLE_SPOOFING,
                None,
                0,
                None,
                0,
                ctypes.byref(bytes_returned),
                None
            )
            
            if result:
                self.spoofing_enabled = False
                self.spoof_status_label.setText(self.translations[self.current_lang]['inactive'])
                self.spoof_status_label.setStyleSheet("color: orange; font-weight: bold;")
                self.enable_btn.setEnabled(True)
                self.disable_btn.setEnabled(False)
                self.status_bar.showMessage(self.translations[self.current_lang]['inactive'])
                
                QMessageBox.information(self, self.translations[self.current_lang]['success'],
                                      self.translations[self.current_lang]['spoofing_disabled'])
            else:
                raise Exception(f"DeviceIoControl failed: {ctypes.get_last_error()}")
                
        except Exception as e:
            QMessageBox.critical(self, self.translations[self.current_lang]['error'],
                               f"Failed to disable spoofing: {str(e)}")
    
    def switch_language(self, lang):
        self.current_lang = lang
        self.setWindowTitle(self.translations[lang]['window_title'])
        
        # Update UI elements (simplified - would need to update all labels)
        QMessageBox.information(self, self.translations[lang]['info'],
                              "Language changed. Please restart application for full effect.")
    
    def closeEvent(self, event):
        if self.spoofing_enabled:
            self.disable_spoofing()
        if self.driver_handle:
            self.unload_driver()
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = HardwareSpooferGUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()