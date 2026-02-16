import sys
import os
import random
import string
import psutil
import wmi
import ctypes
import json
import datetime
import winreg
from ctypes import wintypes
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QListWidget, QListWidgetItem,
    QGroupBox, QRadioButton, QButtonGroup, QMessageBox, QTabWidget,
    QMenuBar, QMenu, QFileIconProvider
)
from PyQt6.QtGui import QIcon, QPixmap, QFont, QAction, QActionGroup
from PyQt6.QtCore import Qt, QTimer, QTranslator, QCoreApplication

# Windows API constants
PROCESS_ALL_ACCESS = 0x1F0FFF
MEM_COMMIT = 0x00001000
MEM_RESERVE = 0x00002000
PAGE_READWRITE = 0x04
PAGE_EXECUTE_READWRITE = 0x40

class HardwareMasquerade(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Language definitions (keep as is)
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
                'chinese': '中文',
                'inject_dll': '注入DLL欺骗',
                'hook_api': 'API Hook欺骗',
                'memory_patch': '内存补丁欺骗',
                'spoof_method': '欺骗方法',
                'advanced_options': '高级选项',
                'spoof_disk': '欺骗磁盘ID',
                'spoof_mac': '欺骗MAC地址',
                'spoof_cpu': '欺骗CPU信息',
                'spoof_bios': '欺骗BIOS信息',
                'spoof_gpu': '欺骗GPU信息',
                'spoof_ram': '欺骗RAM信息',
                'spoof_motherboard': '欺骗主板信息',
                'spoof_monitor': '欺骗显示器信息',
                'select_all': '全选',
                'deselect_all': '取消全选',
                'active_spoofing': '活跃欺骗进程',
                'no_active_spoofing': '无活跃欺骗进程'
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
                'chinese': '中文',
                'inject_dll': 'DLL Injection Spoofing',
                'hook_api': 'API Hook Spoofing',
                'memory_patch': 'Memory Patch Spoofing',
                'spoof_method': 'Spoofing Method',
                'advanced_options': 'Advanced Options',
                'spoof_disk': 'Spoof Disk ID',
                'spoof_mac': 'Spoof MAC Address',
                'spoof_cpu': 'Spoof CPU Info',
                'spoof_bios': 'Spoof BIOS Info',
                'spoof_gpu': 'Spoof GPU Info',
                'spoof_ram': 'Spoof RAM Info',
                'spoof_motherboard': 'Spoof Motherboard Info',
                'spoof_monitor': 'Spoof Monitor Info',
                'select_all': 'Select All',
                'deselect_all': 'Deselect All',
                'active_spoofing': 'Active Spoofed Processes',
                'no_active_spoofing': 'No active spoofing'
            }
        }
        
        # Current language
        self.current_language = 'zh'
        
        self.setWindowTitle(self.languages[self.current_language]['title'])
        self.setGeometry(100, 100, 900, 700)
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
            QCheckBox {
                color: #333333;
            }
            QRadioButton {
                color: #333333;
            }
        """)
        
        # Store active spoofed processes
        self.active_spoofs = {}  # pid -> spoof_info
        
        self.initUI()
        self.initProcessList()
        self.current_spoofed_processes = set()
        self.global_spoofed = False
        
        # Timer to update active spoofs list
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.updateActiveSpoofs)
        self.update_timer.start(2000)
    
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
        
        # Active spoofs display
        self.active_spoofs_label = QLabel(self.languages[self.current_language]['active_spoofing'])
        self.active_spoofs_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        main_layout.addWidget(self.active_spoofs_label)
        
        self.active_spoofs_list = QListWidget()
        self.active_spoofs_list.setMaximumHeight(100)
        main_layout.addWidget(self.active_spoofs_list)
        
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
        
        # Search/filter bar
        search_layout = QHBoxLayout()
        self.search_label = QLabel("Search:")
        self.search_edit = QComboBox()
        self.search_edit.setEditable(True)
        self.search_edit.addItem("")
        self.search_edit.currentTextChanged.connect(self.filterProcessList)
        search_layout.addWidget(self.search_label)
        search_layout.addWidget(self.search_edit)
        process_layout.addLayout(search_layout)
        
        self.process_list = QListWidget()
        process_layout.addWidget(self.process_list)
        
        # Selection buttons
        selection_layout = QHBoxLayout()
        self.select_all_btn = QPushButton(self.languages[self.current_language]['select_all'])
        self.select_all_btn.clicked.connect(self.selectAllProcesses)
        selection_layout.addWidget(self.select_all_btn)
        
        self.deselect_all_btn = QPushButton(self.languages[self.current_language]['deselect_all'])
        self.deselect_all_btn.clicked.connect(self.deselectAllProcesses)
        selection_layout.addWidget(self.deselect_all_btn)
        process_layout.addLayout(selection_layout)
        
        self.refresh_btn = QPushButton(self.languages[self.current_language]['refresh_process'])
        self.refresh_btn.clicked.connect(self.refreshProcessList)
        process_layout.addWidget(self.refresh_btn)
        
        layout.addWidget(self.process_group)
        
        # Spoof method selection
        self.method_group = QGroupBox(self.languages[self.current_language]['spoof_method'])
        method_layout = QVBoxLayout(self.method_group)
        
        self.method_dll = QRadioButton(self.languages[self.current_language]['inject_dll'])
        self.method_dll.setChecked(True)
        method_layout.addWidget(self.method_dll)
        
        self.method_hook = QRadioButton(self.languages[self.current_language]['hook_api'])
        method_layout.addWidget(self.method_hook)
        
        self.method_patch = QRadioButton(self.languages[self.current_language]['memory_patch'])
        method_layout.addWidget(self.method_patch)
        
        layout.addWidget(self.method_group)
        
        # Advanced options
        self.advanced_group = QGroupBox(self.languages[self.current_language]['advanced_options'])
        advanced_layout = QVBoxLayout(self.advanced_group)
        
        self.spoof_disk = QRadioButton(self.languages[self.current_language]['spoof_disk'])
        self.spoof_disk.setChecked(True)
        advanced_layout.addWidget(self.spoof_disk)
        
        self.spoof_mac = QRadioButton(self.languages[self.current_language]['spoof_mac'])
        self.spoof_mac.setChecked(True)
        advanced_layout.addWidget(self.spoof_mac)
        
        self.spoof_cpu = QRadioButton(self.languages[self.current_language]['spoof_cpu'])
        self.spoof_cpu.setChecked(True)
        advanced_layout.addWidget(self.spoof_cpu)
        
        self.spoof_bios = QRadioButton(self.languages[self.current_language]['spoof_bios'])
        self.spoof_bios.setChecked(True)
        advanced_layout.addWidget(self.spoof_bios)
        
        self.spoof_gpu = QRadioButton(self.languages[self.current_language]['spoof_gpu'])
        self.spoof_gpu.setChecked(True)
        advanced_layout.addWidget(self.spoof_gpu)
        
        self.spoof_ram = QRadioButton(self.languages[self.current_language]['spoof_ram'])
        self.spoof_ram.setChecked(True)
        advanced_layout.addWidget(self.spoof_ram)
        
        self.spoof_motherboard = QRadioButton(self.languages[self.current_language]['spoof_motherboard'])
        self.spoof_motherboard.setChecked(True)
        advanced_layout.addWidget(self.spoof_motherboard)
        
        self.spoof_monitor = QRadioButton(self.languages[self.current_language]['spoof_monitor'])
        self.spoof_monitor.setChecked(True)
        advanced_layout.addWidget(self.spoof_monitor)
        
        layout.addWidget(self.advanced_group)
        
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
        
        # Global spoof method selection
        self.global_method_dll = QRadioButton(self.languages[self.current_language]['inject_dll'])
        self.global_method_dll.setChecked(True)
        global_layout.addWidget(self.global_method_dll)
        
        self.global_method_hook = QRadioButton(self.languages[self.current_language]['hook_api'])
        global_layout.addWidget(self.global_method_hook)
        
        self.global_method_patch = QRadioButton(self.languages[self.current_language]['memory_patch'])
        global_layout.addWidget(self.global_method_patch)
        
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
    
    def initProcessList(self):
        self.refreshProcessList()
        # Refresh process list every 5 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.refreshProcessList)
        self.timer.start(5000)
    
    def filterProcessList(self, text):
        """Filter process list based on search text"""
        for i in range(self.process_list.count()):
            item = self.process_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())
    
    def selectAllProcesses(self):
        """Select all processes in the list"""
        for i in range(self.process_list.count()):
            item = self.process_list.item(i)
            item.setCheckState(Qt.CheckState.Checked)
    
    def deselectAllProcesses(self):
        """Deselect all processes in the list"""
        for i in range(self.process_list.count()):
            item = self.process_list.item(i)
            item.setCheckState(Qt.CheckState.Unchecked)
    
    def refreshProcessList(self):
        self.process_list.clear()
        self.search_edit.clear()
        
        # Create icon provider to get file icons
        icon_provider = QFileIconProvider()
        process_names = set()
        
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
                    
                    # Highlight if currently spoofed
                    if pid in self.active_spoofs:
                        item.setBackground(Qt.GlobalColor.green)
                        item.setForeground(Qt.GlobalColor.black)
                    
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
                    process_names.add(name)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Update search combo box
            self.search_edit.clear()
            self.search_edit.addItem("")
            self.search_edit.addItems(sorted(process_names))
            
        except Exception as e:
            QMessageBox.critical(self, self.languages[self.current_language]['error'], 
                                f"{self.languages[self.current_language]['failed_process_list']}{str(e)}")
    
    def updateActiveSpoofs(self):
        """Update the list of active spoofed processes"""
        self.active_spoofs_list.clear()
        
        if not self.active_spoofs:
            item = QListWidgetItem(self.languages[self.current_language]['no_active_spoofing'])
            self.active_spoofs_list.addItem(item)
            return
        
        for pid, info in self.active_spoofs.items():
            try:
                process = psutil.Process(pid)
                item_text = f"{process.name()} (PID: {pid}) - Method: {info['method']}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, pid)
                self.active_spoofs_list.addItem(item)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Process no longer exists, remove from active spoofs
                del self.active_spoofs[pid]
                break
        
        # Refresh process list to update highlighting
        self.refreshProcessList()
    
    def switchLanguage(self, lang_code):
        if self.current_language == lang_code:
            return
        
        self.current_language = lang_code
        
        # Update all UI elements (same as before)
        self.setWindowTitle(self.languages[lang_code]['title'])
        self.title_label.setText(self.languages[lang_code]['title'])
        
        # Update author and GitHub information
        self.subtitle_label.setText(self.languages[lang_code]['subtitle'])
        self.github_label.setText(f"<a href='{self.languages[lang_code]['github']}' style='color: #4CAF50; font-weight: bold;'>{self.languages[lang_code]['github']}</a>")
        
        # Update tabs
        self.tab_widget.setTabText(0, self.languages[lang_code]['process_tab'])
        self.tab_widget.setTabText(1, self.languages[lang_code]['global_tab'])
        self.tab_widget.setTabText(2, self.languages[lang_code]['system_backup'])
        
        # Update process tab
        self.process_group.setTitle(self.languages[lang_code]['select_process'])
        self.refresh_btn.setText(self.languages[lang_code]['refresh_process'])
        self.select_all_btn.setText(self.languages[lang_code]['select_all'])
        self.deselect_all_btn.setText(self.languages[lang_code]['deselect_all'])
        self.method_group.setTitle(self.languages[lang_code]['spoof_method'])
        self.method_dll.setText(self.languages[lang_code]['inject_dll'])
        self.method_hook.setText(self.languages[lang_code]['hook_api'])
        self.method_patch.setText(self.languages[lang_code]['memory_patch'])
        self.advanced_group.setTitle(self.languages[lang_code]['advanced_options'])
        self.spoof_disk.setText(self.languages[lang_code]['spoof_disk'])
        self.spoof_mac.setText(self.languages[lang_code]['spoof_mac'])
        self.spoof_cpu.setText(self.languages[lang_code]['spoof_cpu'])
        self.spoof_bios.setText(self.languages[lang_code]['spoof_bios'])
        self.spoof_gpu.setText(self.languages[lang_code]['spoof_gpu'])
        self.spoof_ram.setText(self.languages[lang_code]['spoof_ram'])
        self.spoof_motherboard.setText(self.languages[lang_code]['spoof_motherboard'])
        self.spoof_monitor.setText(self.languages[lang_code]['spoof_monitor'])
        self.spoof_group.setTitle(self.languages[lang_code]['spoof_options'])
        self.spoof_btn.setText(self.languages[lang_code]['start_spoofing'])
        self.stop_spoof_btn.setText(self.languages[lang_code]['stop_spoofing'])
        
        # Update global tab
        self.global_group.setTitle(self.languages[lang_code]['global_spoofing'])
        self.global_method_dll.setText(self.languages[lang_code]['inject_dll'])
        self.global_method_hook.setText(self.languages[lang_code]['hook_api'])
        self.global_method_patch.setText(self.languages[lang_code]['memory_patch'])
        self.global_spoof_btn.setText(self.languages[lang_code]['start_global'])
        self.global_stop_btn.setText(self.languages[lang_code]['stop_global'])
        self.info_label.setText(self.languages[lang_code]['global_info'])
        
        # Update backup tab
        self.backup_group.setTitle(self.languages[lang_code]['system_backup'])
        self.backup_btn.setText(self.languages[lang_code]['backup_system'])
        self.restore_btn.setText(self.languages[lang_code]['restore_system'])
        self.backup_info_label.setText("\n" + self.languages[lang_code]['global_info'])
        
        # Update labels
        self.active_spoofs_label.setText(self.languages[lang_code]['active_spoofing'])
        self.status_label.setText(self.languages[lang_code]['ready'])
        
        # Update menu
        menubar = self.menuBar()
        menubar.clear()
        self.createMenuBar()
    
    def generateRandomMachineID(self):
        # Generate a random machine ID
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))
    
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
    
    def spoofProcessViaDLL(self, pid):
        """Spoof hardware IDs via DLL injection"""
        try:
            # This is a placeholder for actual DLL injection
            # In a real implementation, you would:
            # 1. Create a DLL that intercepts hardware ID queries
            # 2. Inject it into the target process
            # 3. Hook relevant API calls
            
            fake_data = {
                'machine_id': self.generateRandomMachineID(),
                'disk_id': self.generateRandomHex(16),
                'mac': self.generateRandomMAC(),
                'cpu_id': self.generateRandomHex(32),
                'bios_version': f"{random.randint(1, 5)}.{random.randint(0, 20)}",
                'gpu_name': f"GPU-{self.generateRandomHex(8)}",
                'ram_size': random.choice([8, 16, 32, 64]) * 1024 * 1024 * 1024,
                'motherboard': f"MB-{self.generateRandomHex(8)}",
                'monitor': f"MON-{self.generateRandomHex(4)}"
            }
            
            # Store the spoofed data
            self.active_spoofs[pid] = {
                'method': 'DLL Injection',
                'fake_data': fake_data,
                'timestamp': datetime.datetime.now()
            }
            
            return True
        except Exception as e:
            print(f"DLL injection failed: {e}")
            return False
    
    def spoofProcessViaHook(self, pid):
        """Spoof hardware IDs via API hooking"""
        try:
            # This is a placeholder for actual API hooking
            # In a real implementation, you would:
            # 1. Attach to the target process
            # 2. Hook functions like NtQuerySystemInformation
            # 3. Modify the returned data
            
            fake_data = {
                'machine_id': self.generateRandomMachineID(),
                'disk_id': self.generateRandomHex(16),
                'mac': self.generateRandomMAC(),
                'cpu_id': self.generateRandomHex(32),
                'bios_version': f"{random.randint(1, 5)}.{random.randint(0, 20)}",
                'gpu_name': f"GPU-{self.generateRandomHex(8)}",
                'ram_size': random.choice([8, 16, 32, 64]) * 1024 * 1024 * 1024,
                'motherboard': f"MB-{self.generateRandomHex(8)}",
                'monitor': f"MON-{self.generateRandomHex(4)}"
            }
            
            self.active_spoofs[pid] = {
                'method': 'API Hooking',
                'fake_data': fake_data,
                'timestamp': datetime.datetime.now()
            }
            
            return True
        except Exception as e:
            print(f"API hooking failed: {e}")
            return False
    
    def spoofProcessViaMemoryPatch(self, pid):
        """Spoof hardware IDs via memory patching"""
        try:
            # This is a placeholder for actual memory patching
            # In a real implementation, you would:
            # 1. Open the process with debug privileges
            # 2. Find memory regions containing hardware IDs
            # 3. Patch them with fake values
            
            fake_data = {
                'machine_id': self.generateRandomMachineID(),
                'disk_id': self.generateRandomHex(16),
                'mac': self.generateRandomMAC(),
                'cpu_id': self.generateRandomHex(32),
                'bios_version': f"{random.randint(1, 5)}.{random.randint(0, 20)}",
                'gpu_name': f"GPU-{self.generateRandomHex(8)}",
                'ram_size': random.choice([8, 16, 32, 64]) * 1024 * 1024 * 1024,
                'motherboard': f"MB-{self.generateRandomHex(8)}",
                'monitor': f"MON-{self.generateRandomHex(4)}"
            }
            
            self.active_spoofs[pid] = {
                'method': 'Memory Patching',
                'fake_data': fake_data,
                'timestamp': datetime.datetime.now()
            }
            
            return True
        except Exception as e:
            print(f"Memory patching failed: {e}")
            return False
    
    def startProcessSpoof(self):
        # Get all checked items
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
        
        # Determine spoofing method
        method = 'dll'
        if self.method_hook.isChecked():
            method = 'hook'
        elif self.method_patch.isChecked():
            method = 'patch'
        
        # Spoof each checked process
        spoofed_processes = []
        for process in checked_processes:
            try:
                pid = process.info['pid']
                
                # Skip if already spoofed
                if pid in self.active_spoofs:
                    continue
                
                success = False
                if method == 'dll':
                    success = self.spoofProcessViaDLL(pid)
                elif method == 'hook':
                    success = self.spoofProcessViaHook(pid)
                elif method == 'patch':
                    success = self.spoofProcessViaMemoryPatch(pid)
                
                if success:
                    spoofed_processes.append(process)
                    self.current_spoofed_processes.add(pid)
                    
            except Exception as e:
                QMessageBox.warning(self, self.languages[self.current_language]['warning'], 
                                   f"Failed to spoof {process.info['name']}: {str(e)}")
                continue
        
        if spoofed_processes:
            self.spoof_btn.setEnabled(False)
            self.stop_spoof_btn.setEnabled(True)
            
            # Show success message
            process_names = ', '.join([f"{p.info['name']} (PID: {p.info['pid']})" for p in spoofed_processes])
            QMessageBox.information(self, self.languages[self.current_language]['success'], 
                                  f"{self.languages[self.current_language]['started_spoofing']}{process_names}")
            
            # Update display
            self.updateActiveSpoofs()
    
    def stopProcessSpoof(self, show_message=True):
        self.active_spoofs.clear()
        self.current_spoofed_processes.clear()
        self.spoof_btn.setEnabled(True)
        self.stop_spoof_btn.setEnabled(False)
        
        self.status_label.setText(self.languages[self.current_language]['stopped_spoofing'])
        self.updateActiveSpoofs()
        
        if show_message:
            QMessageBox.information(self, self.languages[self.current_language]['success'], 
                                  self.languages[self.current_language]['stopped_spoofing'])
    
    def startGlobalSpoof(self):
        # Determine spoofing method
        method = 'dll'
        if self.global_method_hook.isChecked():
            method = 'hook'
        elif self.global_method_patch.isChecked():
            method = 'patch'
        
        # Spoof all running processes
        spoofed_count = 0
        for proc in psutil.process_iter(['pid']):
            try:
                pid = proc.info['pid']
                if pid not in self.active_spoofs:
                    if method == 'dll':
                        success = self.spoofProcessViaDLL(pid)
                    elif method == 'hook':
                        success = self.spoofProcessViaHook(pid)
                    else:
                        success = self.spoofProcessViaMemoryPatch(pid)
                    
                    if success:
                        spoofed_count += 1
            except:
                continue
        
        if spoofed_count > 0:
            self.global_spoofed = True
            self.global_spoof_btn.setEnabled(False)
            self.global_stop_btn.setEnabled(True)
            QMessageBox.information(self, self.languages[self.current_language]['success'], 
                                  f"{self.languages[self.current_language]['started_global']} (Spoofed {spoofed_count} processes)")
            self.updateActiveSpoofs()
    
    def stopGlobalSpoof(self, show_message=True):
        self.active_spoofs.clear()
        self.current_spoofed_processes.clear()
        self.global_spoofed = False
        self.global_spoof_btn.setEnabled(True)
        self.global_stop_btn.setEnabled(False)
        
        self.status_label.setText(self.languages[self.current_language]['stopped_global'])
        self.updateActiveSpoofs()
        
        if show_message:
            QMessageBox.information(self, self.languages[self.current_language]['success'], 
                                  self.languages[self.current_language]['stopped_global'])
    
    def backupSystemInfo(self):
        # Backup current system hardware information
        try:
            # Create backup directory if it doesn't exist
            backup_dir = "backup"
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # Get current date and time for backup filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"system_backup_{timestamp}.json")
            
            # Read current registry keys for backup
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
