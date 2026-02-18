#include "loader.h"

// Global variables
static SC_HANDLE g_hSCManager = NULL;
static SC_HANDLE g_hService = NULL;
static HANDLE g_hDevice = INVALID_HANDLE_VALUE;

// Open Service Control Manager
SC_HANDLE OpenServiceManager(void)
{
    if (!g_hSCManager) {
        g_hSCManager = OpenSCManager(NULL, NULL, SC_MANAGER_ALL_ACCESS);
        if (!g_hSCManager) {
            PrintLastError("OpenSCManager");
        }
    }
    return g_hSCManager;
}

// Create driver service
SC_HANDLE CreateDriverService(LPCWSTR DriverName, LPCWSTR DriverPath)
{
    SC_HANDLE hSCManager = OpenServiceManager();
    if (!hSCManager) return NULL;
    
    SC_HANDLE hService = CreateService(
        hSCManager,
        DriverName,
        DriverName,
        SERVICE_ALL_ACCESS,
        SERVICE_KERNEL_DRIVER,
        SERVICE_DEMAND_START,
        SERVICE_ERROR_NORMAL,
        DriverPath,
        NULL, NULL, NULL, NULL, NULL
    );
    
    if (!hService) {
        DWORD err = GetLastError();
        if (err == ERROR_SERVICE_EXISTS) {
            hService = OpenService(hSCManager, DriverName, SERVICE_ALL_ACCESS);
            wprintf(L"Service already exists, opening existing service\n");
        } else {
            PrintLastError("CreateService");
        }
    }
    
    return hService;
}

// Open driver service
SC_HANDLE OpenDriverService(LPCWSTR DriverName)
{
    SC_HANDLE hSCManager = OpenServiceManager();
    if (!hSCManager) return NULL;
    
    if (!g_hService) {
        g_hService = OpenService(hSCManager, DriverName, SERVICE_ALL_ACCESS);
        if (!g_hService) {
            PrintLastError("OpenService");
        }
    }
    
    return g_hService;
}

// Delete driver service
BOOL DeleteDriverService(LPCWSTR DriverName)
{
    BOOL result = FALSE;
    SC_HANDLE hService = OpenDriverService(DriverName);
    
    if (hService) {
        // Stop service if running
        SERVICE_STATUS status;
        ControlService(hService, SERVICE_CONTROL_STOP, &status);
        
        // Delete service
        if (DeleteService(hService)) {
            wprintf(L"Service deleted successfully\n");
            result = TRUE;
        } else {
            PrintLastError("DeleteService");
        }
        
        CloseServiceHandle(hService);
        g_hService = NULL;
    }
    
    return result;
}

// Start driver service
BOOL StartDriverService(SC_HANDLE hService)
{
    if (!hService) return FALSE;
    
    if (StartService(hService, 0, NULL)) {
        wprintf(L"Service started successfully\n");
        return TRUE;
    } else {
        DWORD err = GetLastError();
        if (err == ERROR_SERVICE_ALREADY_RUNNING) {
            wprintf(L"Service is already running\n");
            return TRUE;
        } else {
            PrintLastError("StartService");
            return FALSE;
        }
    }
}

// Stop driver service
BOOL StopDriverService(SC_HANDLE hService)
{
    if (!hService) return FALSE;
    
    SERVICE_STATUS status;
    if (ControlService(hService, SERVICE_CONTROL_STOP, &status)) {
        wprintf(L"Service stopped successfully\n");
        return TRUE;
    } else {
        DWORD err = GetLastError();
        if (err == ERROR_SERVICE_NOT_ACTIVE) {
            wprintf(L"Service is not running\n");
            return TRUE;
        } else {
            PrintLastError("ControlService");
            return FALSE;
        }
    }
}

// Control driver service
BOOL ControlDriver(SC_HANDLE hService, DWORD ControlCode)
{
    if (!hService) return FALSE;
    
    SERVICE_STATUS status;
    return ControlService(hService, ControlCode, &status);
}

// Open driver device
HANDLE OpenDriverDevice(LPCWSTR DeviceName)
{
    if (g_hDevice != INVALID_HANDLE_VALUE) {
        return g_hDevice;
    }
    
    g_hDevice = CreateFile(
        DeviceName,
        GENERIC_READ | GENERIC_WRITE,
        0,
        NULL,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );
    
    if (g_hDevice == INVALID_HANDLE_VALUE) {
        PrintLastError("CreateFile");
    } else {
        wprintf(L"Device opened successfully\n");
    }
    
    return g_hDevice;
}

// Close driver device
BOOL CloseDriverDevice(HANDLE hDevice)
{
    if (hDevice != INVALID_HANDLE_VALUE) {
        CloseHandle(hDevice);
        if (hDevice == g_hDevice) {
            g_hDevice = INVALID_HANDLE_VALUE;
        }
        return TRUE;
    }
    return FALSE;
}

// Send spoof config to driver
BOOL SendSpoofConfig(HANDLE hDevice, PSPOOF_CONFIG Config)
{
    if (hDevice == INVALID_HANDLE_VALUE) return FALSE;
    
    DWORD bytesReturned;
    BOOL result = DeviceIoControl(
        hDevice,
        IOCTL_SET_SPOOF_CONFIG,
        Config,
        sizeof(SPOOF_CONFIG),
        NULL,
        0,
        &bytesReturned,
        NULL
    );
    
    if (!result) {
        PrintLastError("DeviceIoControl (SET_CONFIG)");
    }
    
    return result;
}

// Get spoof config from driver
BOOL GetSpoofConfig(HANDLE hDevice, PSPOOF_CONFIG Config)
{
    if (hDevice == INVALID_HANDLE_VALUE) return FALSE;
    
    DWORD bytesReturned;
    BOOL result = DeviceIoControl(
        hDevice,
        IOCTL_GET_SPOOF_CONFIG,
        NULL,
        0,
        Config,
        sizeof(SPOOF_CONFIG),
        &bytesReturned,
        NULL
    );
    
    if (!result) {
        PrintLastError("DeviceIoControl (GET_CONFIG)");
    }
    
    return result;
}

// Enable spoofing
BOOL EnableSpoofing(HANDLE hDevice)
{
    if (hDevice == INVALID_HANDLE_VALUE) return FALSE;
    
    DWORD bytesReturned;
    BOOL result = DeviceIoControl(
        hDevice,
        IOCTL_ENABLE_SPOOFING,
        NULL,
        0,
        NULL,
        0,
        &bytesReturned,
        NULL
    );
    
    if (!result) {
        PrintLastError("DeviceIoControl (ENABLE)");
    }
    
    return result;
}

// Disable spoofing
BOOL DisableSpoofing(HANDLE hDevice)
{
    if (hDevice == INVALID_HANDLE_VALUE) return FALSE;
    
    DWORD bytesReturned;
    BOOL result = DeviceIoControl(
        hDevice,
        IOCTL_DISABLE_SPOOFING,
        NULL,
        0,
        NULL,
        0,
        &bytesReturned,
        NULL
    );
    
    if (!result) {
        PrintLastError("DeviceIoControl (DISABLE)");
    }
    
    return result;
}

// Get spoofing status
BOOL GetSpoofingStatus(HANDLE hDevice, PBOOLEAN Enabled)
{
    if (hDevice == INVALID_HANDLE_VALUE) return FALSE;
    
    DWORD bytesReturned;
    BOOL result = DeviceIoControl(
        hDevice,
        IOCTL_GET_STATUS,
        NULL,
        0,
        Enabled,
        sizeof(BOOLEAN),
        &bytesReturned,
        NULL
    );
    
    if (!result) {
        PrintLastError("DeviceIoControl (GET_STATUS)");
    }
    
    return result;
}

// Set process filter
BOOL SetProcessFilter(HANDLE hDevice, PULONG ProcessIds, ULONG Count)
{
    if (hDevice == INVALID_HANDLE_VALUE) return FALSE;
    
    // This would require a custom IOCTL or extend the config structure
    // For simplicity, we'll read the current config and update it
    SPOOF_CONFIG config;
    if (!GetSpoofConfig(hDevice, &config)) {
        return FALSE;
    }
    
    config.EnableProcessFilter = (Count > 0);
    config.ProcessCount = min(Count, 32);
    for (ULONG i = 0; i < config.ProcessCount; i++) {
        config.TargetProcessIds[i] = ProcessIds[i];
    }
    
    return SendSpoofConfig(hDevice, &config);
}

// Install driver
BOOL InstallDriver(LPCWSTR DriverPath)
{
    wprintf(L"Installing driver from: %s\n", DriverPath);
    
    // Check if running as administrator
    if (!IsUserAdministrator()) {
        wprintf(L"Error: Administrator privileges required!\n");
        return FALSE;
    }
    
    // Enable debug privilege
    EnableDebugPrivilege();
    
    // Create service
    SC_HANDLE hService = CreateDriverService(L"HardwareSpoofer", DriverPath);
    if (!hService) {
        return FALSE;
    }
    
    // Start service
    if (!StartDriverService(hService)) {
        CloseServiceHandle(hService);
        return FALSE;
    }
    
    CloseServiceHandle(hService);
    
    // Try to open device
    HANDLE hDevice = OpenDriverDevice(L"\\\\.\\HardwareSpoofer");
    if (hDevice != INVALID_HANDLE_VALUE) {
        CloseDriverDevice(hDevice);
        wprintf(L"Driver device opened successfully\n");
    } else {
        wprintf(L"Warning: Could not open driver device\n");
    }
    
    wprintf(L"Driver installed successfully\n");
    return TRUE;
}

// Uninstall driver
BOOL UninstallDriver(void)
{
    wprintf(L"Uninstalling driver...\n");
    
    // Check if running as administrator
    if (!IsUserAdministrator()) {
        wprintf(L"Error: Administrator privileges required!\n");
        return FALSE;
    }
    
    // Close device if open
    CloseDriverDevice(g_hDevice);
    
    // Delete service
    return DeleteDriverService(L"HardwareSpoofer");
}

// Check if driver is installed
BOOL IsDriverInstalled(void)
{
    SC_HANDLE hService = OpenDriverService(L"HardwareSpoofer");
    if (hService) {
        CloseServiceHandle(hService);
        return TRUE;
    }
    return FALSE;
}

// Check if driver is running
BOOL IsDriverRunning(void)
{
    BOOL result = FALSE;
    SC_HANDLE hService = OpenDriverService(L"HardwareSpoofer");
    
    if (hService) {
        SERVICE_STATUS status;
        if (QueryServiceStatus(hService, &status)) {
            result = (status.dwCurrentState == SERVICE_RUNNING);
        }
        CloseServiceHandle(hService);
    }
    
    return result;
}

// Load driver
BOOL LoadDriver(void)
{
    return StartDriverService(OpenDriverService(L"HardwareSpoofer"));
}

// Unload driver
BOOL UnloadDriver(void)
{
    return StopDriverService(OpenDriverService(L"HardwareSpoofer"));
}

// Print last error
VOID PrintLastError(LPCSTR Function)
{
    DWORD err = GetLastError();
    LPWSTR message = NULL;
    
    FormatMessage(
        FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM,
        NULL,
        err,
        MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
        (LPWSTR)&message,
        0,
        NULL
    );
    
    wprintf(L"%S failed: %s (Error: %d)\n", Function, message ? message : L"Unknown error", err);
    
    if (message) {
        LocalFree(message);
    }
}

// Check if user is administrator
BOOL IsUserAdministrator(void)
{
    BOOL result = FALSE;
    PSID adminGroup = NULL;
    SID_IDENTIFIER_AUTHORITY ntAuthority = SECURITY_NT_AUTHORITY;
    
    if (AllocateAndInitializeSid(
        &ntAuthority,
        2,
        SECURITY_BUILTIN_DOMAIN_RID,
        DOMAIN_ALIAS_RID_ADMINS,
        0, 0, 0, 0, 0, 0,
        &adminGroup
    )) {
        CheckTokenMembership(NULL, adminGroup, &result);
        FreeSid(adminGroup);
    }
    
    return result;
}

// Enable debug privilege
BOOL EnableDebugPrivilege(void)
{
    HANDLE hToken;
    TOKEN_PRIVILEGES tp;
    
    if (!OpenProcessToken(GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, &hToken)) {
        return FALSE;
    }
    
    tp.PrivilegeCount = 1;
    tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;
    
    if (!LookupPrivilegeValue(NULL, SE_DEBUG_NAME, &tp.Privileges[0].Luid)) {
        CloseHandle(hToken);
        return FALSE;
    }
    
    BOOL result = AdjustTokenPrivileges(hToken, FALSE, &tp, sizeof(tp), NULL, NULL);
    CloseHandle(hToken);
    
    return result && (GetLastError() == ERROR_SUCCESS);
}

// Get error message
LPCWSTR GetErrorMessage(DWORD ErrorCode)
{
    static WCHAR buffer[256];
    
    FormatMessage(
        FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
        NULL,
        ErrorCode,
        MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
        buffer,
        sizeof(buffer) / sizeof(WCHAR),
        NULL
    );
    
    return buffer;
}

// Save config to file
BOOL SaveConfigToFile(LPCWSTR FilePath, PSPOOF_CONFIG Config)
{
    HANDLE hFile = CreateFile(
        FilePath,
        GENERIC_WRITE,
        0,
        NULL,
        CREATE_ALWAYS,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );
    
    if (hFile == INVALID_HANDLE_VALUE) {
        PrintLastError("CreateFile (save)");
        return FALSE;
    }
    
    DWORD bytesWritten;
    BOOL result = WriteFile(hFile, Config, sizeof(SPOOF_CONFIG), &bytesWritten, NULL);
    
    CloseHandle(hFile);
    
    if (!result) {
        PrintLastError("WriteFile");
    }
    
    return result;
}

// Load config from file
BOOL LoadConfigFromFile(LPCWSTR FilePath, PSPOOF_CONFIG Config)
{
    HANDLE hFile = CreateFile(
        FilePath,
        GENERIC_READ,
        FILE_SHARE_READ,
        NULL,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );
    
    if (hFile == INVALID_HANDLE_VALUE) {
        PrintLastError("CreateFile (load)");
        return FALSE;
    }
    
    DWORD bytesRead;
    BOOL result = ReadFile(hFile, Config, sizeof(SPOOF_CONFIG), &bytesRead, NULL);
    
    CloseHandle(hFile);
    
    if (!result) {
        PrintLastError("ReadFile");
    }
    
    return result;
}

// Validate config
BOOL ValidateConfig(PSPOOF_CONFIG Config)
{
    if (!Config) return FALSE;
    
    // Validate MAC address format
    if (Config->SpoofMacAddress) {
        int len = wcslen(Config->FakeMacAddress);
        if (len != 17) return FALSE; // XX:XX:XX:XX:XX:XX
        
        for (int i = 0; i < len; i++) {
            if (i % 3 == 2) {
                if (Config->FakeMacAddress[i] != L':') return FALSE;
            } else {
                if (!iswxdigit(Config->FakeMacAddress[i])) return FALSE;
            }
        }
    }
    
    // Validate disk ID format (hex)
    if (Config->SpoofDiskId) {
        int len = wcslen(Config->FakeDiskId);
        if (len != 16 && len != 32) return FALSE;
        
        for (int i = 0; i < len; i++) {
            if (!iswxdigit(Config->FakeDiskId[i])) return FALSE;
        }
    }
    
    // Validate CPU ID format (hex)
    if (Config->SpoofCpuId) {
        int len = wcslen(Config->FakeCpuId);
        if (len != 32) return FALSE;
        
        for (int i = 0; i < len; i++) {
            if (!iswxdigit(Config->FakeCpuId[i])) return FALSE;
        }
    }
    
    return TRUE;
}

// Set default config
VOID SetDefaultConfig(PSPOOF_CONFIG Config)
{
    RtlZeroMemory(Config, sizeof(SPOOF_CONFIG));
    
    // Enable all spoofing by default
    Config->SpoofDiskId = TRUE;
    Config->SpoofMacAddress = TRUE;
    Config->SpoofCpuId = TRUE;
    Config->SpoofBiosInfo = TRUE;
    Config->SpoofGpuInfo = TRUE;
    Config->SpoofRamInfo = TRUE;
    Config->SpoofMotherboard = TRUE;
    Config->SpoofMonitorInfo = TRUE;
    
    // Set default fake values
    wcscpy_s(Config->FakeDiskId, 64, L"1234567890ABCDEF");
    wcscpy_s(Config->FakeMacAddress, 18, L"00:16:3E:12:34:56");
    wcscpy_s(Config->FakeCpuId, 64, L"ABCDEF1234567890ABCDEF1234567890");
    wcscpy_s(Config->FakeBiosVersion, 64, L"American Megatrends 5.12");
    wcscpy_s(Config->FakeGpuName, 128, L"NVIDIA GeForce RTX 3080");
    Config->FakeRamSize = 16384;
    wcscpy_s(Config->FakeMotherboard, 64, L"ASUS PRIME X570-PRO");
    wcscpy_s(Config->FakeMonitorInfo, 128, L"DELL U2719D 2560x1440");
}

// Parse command line
BOOL ParseCommandLine(int argc, wchar_t* argv[], PCOMMAND_OPTIONS Options)
{
    RtlZeroMemory(Options, sizeof(COMMAND_OPTIONS));
    
    if (argc < 2) {
        Options->Help = TRUE;
        return TRUE;
    }
    
    for (int i = 1; i < argc; i++) {
        if (wcscmp(argv[i], L"/install") == 0 || wcscmp(argv[i], L"-install") == 0) {
            Options->Install = TRUE;
            if (i + 1 < argc && argv[i + 1][0] != L'/') {
                wcscpy_s(Options->DriverPath, MAX_PATH, argv[++i]);
            } else {
                wcscpy_s(Options->DriverPath, MAX_PATH, L"HardwareSpoofer.sys");
            }
        }
        else if (wcscmp(argv[i], L"/uninstall") == 0 || wcscmp(argv[i], L"-uninstall") == 0) {
            Options->Uninstall = TRUE;
        }
        else if (wcscmp(argv[i], L"/start") == 0 || wcscmp(argv[i], L"-start") == 0) {
            Options->Start = TRUE;
        }
        else if (wcscmp(argv[i], L"/stop") == 0 || wcscmp(argv[i], L"-stop") == 0) {
            Options->Stop = TRUE;
        }
        else if (wcscmp(argv[i], L"/enable") == 0 || wcscmp(argv[i], L"-enable") == 0) {
            Options->Enable = TRUE;
        }
        else if (wcscmp(argv[i], L"/disable") == 0 || wcscmp(argv[i], L"-disable") == 0) {
            Options->Disable = TRUE;
        }
        else if (wcscmp(argv[i], L"/status") == 0 || wcscmp(argv[i], L"-status") == 0) {
            Options->Status = TRUE;
        }
        else if (wcscmp(argv[i], L"/config") == 0 || wcscmp(argv[i], L"-config") == 0) {
            Options->Config = TRUE;
            if (i + 1 < argc && argv[i + 1][0] != L'/') {
                wcscpy_s(Options->ConfigFile, MAX_PATH, argv[++i]);
            }
        }
        else if (wcscmp(argv[i], L"/help") == 0 || wcscmp(argv[i], L"-help") == 0 || wcscmp(argv[i], L"/?") == 0) {
            Options->Help = TRUE;
        }
        else {
            wprintf(L"Unknown option: %s\n", argv[i]);
            Options->Help = TRUE;
            return FALSE;
        }
    }
    
    return TRUE;
}

// Show usage
VOID ShowUsage(void)
{
    wprintf(L"Hardware Masquerade Driver Loader\n");
    wprintf(L"Usage: loader.exe [options]\n\n");
    wprintf(L"Options:\n");
    wprintf(L"  /install [path]    Install and start driver\n");
    wprintf(L"  /uninstall         Uninstall driver\n");
    wprintf(L"  /start             Start driver service\n");
    wprintf(L"  /stop              Stop driver service\n");
    wprintf(L"  /enable            Enable hardware spoofing\n");
    wprintf(L"  /disable           Disable hardware spoofing\n");
    wprintf(L"  /status            Show driver status\n");
    wprintf(L"  /config [file]     Load config from file\n");
    wprintf(L"  /help              Show this help\n");
}

// Show status
VOID ShowStatus(void)
{
    wprintf(L"=== Hardware Masquerade Status ===\n\n");
    
    wprintf(L"Driver installed: %s\n", IsDriverInstalled() ? L"Yes" : L"No");
    wprintf(L"Driver running: %s\n", IsDriverRunning() ? L"Yes" : L"No");
    
    if (IsDriverRunning()) {
        HANDLE hDevice = OpenDriverDevice(L"\\\\.\\HardwareSpoofer");
        if (hDevice != INVALID_HANDLE_VALUE) {
            BOOLEAN enabled = FALSE;
            if (GetSpoofingStatus(hDevice, &enabled)) {
                wprintf(L"Spoofing enabled: %s\n", enabled ? L"Yes" : L"No");
            }
            
            SPOOF_CONFIG config;
            if (GetSpoofConfig(hDevice, &config)) {
                wprintf(L"\nCurrent Configuration:\n");
                wprintf(L"  Spoof Disk ID: %s\n", config.SpoofDiskId ? L"Yes" : L"No");
                wprintf(L"  Spoof MAC: %s\n", config.SpoofMacAddress ? L"Yes" : L"No");
                wprintf(L"  Spoof CPU ID: %s\n", config.SpoofCpuId ? L"Yes" : L"No");
                wprintf(L"  Spoof BIOS: %s\n", config.SpoofBiosInfo ? L"Yes" : L"No");
                wprintf(L"  Spoof GPU: %s\n", config.SpoofGpuInfo ? L"Yes" : L"No");
                wprintf(L"  Process filter: %s (%lu processes)\n", 
                       config.EnableProcessFilter ? L"Yes" : L"No", config.ProcessCount);
            }
            
            CloseDriverDevice(hDevice);
        }
    }
}

// Main function
int wmain(int argc, wchar_t* argv[])
{
    COMMAND_OPTIONS options;
    
    if (!ParseCommandLine(argc, argv, &options)) {
        return 1;
    }
    
    if (options.Help || argc == 1) {
        ShowUsage();
        return 0;
    }
    
    // Check for administrator privileges for most operations
    if (options.Install || options.Uninstall || options.Start || options.Stop) {
        if (!IsUserAdministrator()) {
            wprintf(L"Error: Administrator privileges required for this operation!\n");
            return 1;
        }
        EnableDebugPrivilege();
    }
    
    // Handle commands
    if (options.Install) {
        if (!InstallDriver(options.DriverPath)) {
            return 1;
        }
    }
    
    if (options.Uninstall) {
        if (!UninstallDriver()) {
            return 1;
        }
    }
    
    if (options.Start) {
        SC_HANDLE hService = OpenDriverService(L"HardwareSpoofer");
        if (hService) {
            StartDriverService(hService);
            CloseServiceHandle(hService);
        } else {
            wprintf(L"Driver not installed\n");
            return 1;
        }
    }
    
    if (options.Stop) {
        SC_HANDLE hService = OpenDriverService(L"HardwareSpoofer");
        if (hService) {
            StopDriverService(hService);
            CloseServiceHandle(hService);
        } else {
            wprintf(L"Driver not installed\n");
            return 1;
        }
    }
    
    // Device operations
    if (options.Enable || options.Disable || options.Config || options.Status) {
        HANDLE hDevice = OpenDriverDevice(L"\\\\.\\HardwareSpoofer");
        if (hDevice == INVALID_HANDLE_VALUE) {
            wprintf(L"Failed to open driver device. Is the driver running?\n");
            return 1;
        }
        
        if (options.Enable) {
            if (EnableSpoofing(hDevice)) {
                wprintf(L"Spoofing enabled\n");
            }
        }
        
        if (options.Disable) {
            if (DisableSpoofing(hDevice)) {
                wprintf(L"Spoofing disabled\n");
            }
        }
        
        if (options.Config) {
            SPOOF_CONFIG config;
            if (LoadConfigFromFile(options.ConfigFile, &config)) {
                if (SendSpoofConfig(hDevice, &config)) {
                    wprintf(L"Configuration loaded from %s\n", options.ConfigFile);
                }
            } else {
                wprintf(L"Failed to load config from %s\n", options.ConfigFile);
            }
        }
        
        if (options.Status) {
            ShowStatus();
        }
        
        CloseDriverDevice(hDevice);
    }
    
    return 0;
}