#include "service.h"

// Global service context
static SERVICE_CONTEXT g_ServiceContext = {0};

// Service main entry point
VOID WINAPI ServiceMain(DWORD argc, LPTSTR* argv)
{
    UNREFERENCED_PARAMETER(argc);
    UNREFERENCED_PARAMETER(argv);
    
    // Initialize context
    RtlZeroMemory(&g_ServiceContext, sizeof(SERVICE_CONTEXT));
    g_ServiceContext.StatusHandle = RegisterServiceCtrlHandler(SERVICE_NAME, ServiceCtrlHandler);
    
    if (!g_ServiceContext.StatusHandle) {
        LogEvent(L"Failed to register service control handler", EVENTLOG_ERROR_TYPE);
        return;
    }
    
    // Initialize critical section
    InitializeCriticalSection(&g_ServiceContext.ConfigLock);
    
    // Create stop event
    g_ServiceContext.StopEvent = CreateEvent(NULL, TRUE, FALSE, NULL);
    if (!g_ServiceContext.StopEvent) {
        LogEvent(L"Failed to create stop event", EVENTLOG_ERROR_TYPE);
        return;
    }
    
    // Set initial service status
    g_ServiceContext.Status.dwServiceType = SERVICE_WIN32_OWN_PROCESS;
    g_ServiceContext.Status.dwCurrentState = SERVICE_START_PENDING;
    g_ServiceContext.Status.dwControlsAccepted = SERVICE_ACCEPT_STOP | SERVICE_ACCEPT_SHUTDOWN | 
                                                 SERVICE_ACCEPT_POWEREVENT | SERVICE_ACCEPT_SESSIONCHANGE;
    g_ServiceContext.Status.dwWin32ExitCode = NO_ERROR;
    g_ServiceContext.Status.dwServiceSpecificExitCode = 0;
    g_ServiceContext.Status.dwCheckPoint = 0;
    g_ServiceContext.Status.dwWaitHint = 3000;
    
    if (!UpdateServiceStatus(&g_ServiceContext, SERVICE_START_PENDING, NO_ERROR, 3000)) {
        LogEvent(L"Failed to update service status", EVENTLOG_ERROR_TYPE);
        return;
    }
    
    // Load configuration
    LoadConfiguration(&g_ServiceContext, L"spoofer.ini");
    
    // Open driver
    if (!OpenDriver(&g_ServiceContext)) {
        LogEvent(L"Failed to open driver, spoofing will be unavailable", EVENTLOG_WARNING_TYPE);
    }
    
    // Enable spoofing if configured
    if (g_ServiceContext.Config.EnableSpoofingOnStart && g_ServiceContext.DriverHandle) {
        // Enable spoofing
        DWORD bytesReturned;
        DeviceIoControl(g_ServiceContext.DriverHandle, IOCTL_ENABLE_SPOOFING, 
                       NULL, 0, NULL, 0, &bytesReturned, NULL);
        g_ServiceContext.SpoofingEnabled = TRUE;
    }
    
    // Create worker thread
    HANDLE hThread = CreateThread(NULL, 0, ServiceWorkerThread, &g_ServiceContext, 0, NULL);
    if (!hThread) {
        LogEvent(L"Failed to create worker thread", EVENTLOG_ERROR_TYPE);
        UpdateServiceStatus(&g_ServiceContext, SERVICE_STOPPED, GetLastError(), 0);
        return;
    }
    
    // Service is now running
    UpdateServiceStatus(&g_ServiceContext, SERVICE_RUNNING, NO_ERROR, 0);
    
    // Wait for stop event
    WaitForSingleObject(g_ServiceContext.StopEvent, INFINITE);
    
    // Cleanup
    UpdateServiceStatus(&g_ServiceContext, SERVICE_STOP_PENDING, NO_ERROR, 5000);
    
    // Disable spoofing
    if (g_ServiceContext.DriverHandle) {
        DWORD bytesReturned;
        DeviceIoControl(g_ServiceContext.DriverHandle, IOCTL_DISABLE_SPOOFING,
                       NULL, 0, NULL, 0, &bytesReturned, NULL);
        CloseDriver(&g_ServiceContext);
    }
    
    // Wait for worker thread to finish
    WaitForSingleObject(hThread, 5000);
    CloseHandle(hThread);
    
    // Clean up resources
    CloseHandle(g_ServiceContext.StopEvent);
    DeleteCriticalSection(&g_ServiceContext.ConfigLock);
    
    // Final status update
    UpdateServiceStatus(&g_ServiceContext, SERVICE_STOPPED, NO_ERROR, 0);
    
    LogEvent(L"Service stopped", EVENTLOG_INFORMATION_TYPE);
}

// Service control handler
VOID WINAPI ServiceCtrlHandler(DWORD ctrlCode)
{
    switch (ctrlCode) {
        case SERVICE_CONTROL_STOP:
        case SERVICE_CONTROL_SHUTDOWN:
            LogEvent(L"Stop request received", EVENTLOG_INFORMATION_TYPE);
            UpdateServiceStatus(&g_ServiceContext, SERVICE_STOP_PENDING, NO_ERROR, 5000);
            SetEvent(g_ServiceContext.StopEvent);
            break;
            
        case SERVICE_CONTROL_PAUSE:
            // Pause spoofing
            if (g_ServiceContext.DriverHandle) {
                DWORD bytesReturned;
                DeviceIoControl(g_ServiceContext.DriverHandle, IOCTL_DISABLE_SPOOFING,
                               NULL, 0, NULL, 0, &bytesReturned, NULL);
                g_ServiceContext.SpoofingEnabled = FALSE;
            }
            UpdateServiceStatus(&g_ServiceContext, SERVICE_PAUSED, NO_ERROR, 0);
            break;
            
        case SERVICE_CONTROL_CONTINUE:
            // Resume spoofing
            if (g_ServiceContext.DriverHandle && g_ServiceContext.Config.EnableSpoofingOnStart) {
                DWORD bytesReturned;
                DeviceIoControl(g_ServiceContext.DriverHandle, IOCTL_ENABLE_SPOOFING,
                               NULL, 0, NULL, 0, &bytesReturned, NULL);
                g_ServiceContext.SpoofingEnabled = TRUE;
            }
            UpdateServiceStatus(&g_ServiceContext, SERVICE_RUNNING, NO_ERROR, 0);
            break;
            
        case SERVICE_CONTROL_INTERROGATE:
            // Return current status
            break;
            
        case SERVICE_CONTROL_ENABLE_SPOOFING:
            if (g_ServiceContext.DriverHandle) {
                DWORD bytesReturned;
                DeviceIoControl(g_ServiceContext.DriverHandle, IOCTL_ENABLE_SPOOFING,
                               NULL, 0, NULL, 0, &bytesReturned, NULL);
                g_ServiceContext.SpoofingEnabled = TRUE;
                LogEvent(L"Spoofing enabled via control code", EVENTLOG_INFORMATION_TYPE);
            }
            break;
            
        case SERVICE_CONTROL_DISABLE_SPOOFING:
            if (g_ServiceContext.DriverHandle) {
                DWORD bytesReturned;
                DeviceIoControl(g_ServiceContext.DriverHandle, IOCTL_DISABLE_SPOOFING,
                               NULL, 0, NULL, 0, &bytesReturned, NULL);
                g_ServiceContext.SpoofingEnabled = FALSE;
                LogEvent(L"Spoofing disabled via control code", EVENTLOG_INFORMATION_TYPE);
            }
            break;
            
        case SERVICE_CONTROL_GET_STATUS:
            // Return status through some mechanism
            break;
            
        default:
            break;
    }
    
    UpdateServiceStatus(&g_ServiceContext, g_ServiceContext.Status.dwCurrentState, NO_ERROR, 0);
}

// Service worker thread
DWORD WINAPI ServiceWorkerThread(LPVOID lpParam)
{
    PSERVICE_CONTEXT Context = (PSERVICE_CONTEXT)lpParam;
    
    LogEvent(L"Service worker thread started", EVENTLOG_INFORMATION_TYPE);
    
    while (WaitForSingleObject(Context->StopEvent, Context->Config.UpdateInterval) == WAIT_TIMEOUT) {
        // Periodic tasks
        EnterCriticalSection(&Context->ConfigLock);
        
        // Check driver connection
        if (Context->DriverHandle == INVALID_HANDLE_VALUE || Context->DriverHandle == NULL) {
            OpenDriver(Context);
        }
        
        // Update configuration if needed
        // ...
        
        LeaveCriticalSection(&Context->ConfigLock);
    }
    
    LogEvent(L"Service worker thread stopping", EVENTLOG_INFORMATION_TYPE);
    return 0;
}

// Update service status
BOOL UpdateServiceStatus(PSERVICE_CONTEXT Context, DWORD CurrentState, DWORD Win32ExitCode, DWORD WaitHint)
{
    if (!Context || !Context->StatusHandle) {
        return FALSE;
    }
    
    Context->Status.dwCurrentState = CurrentState;
    Context->Status.dwWin32ExitCode = Win32ExitCode;
    Context->Status.dwWaitHint = WaitHint;
    
    if (CurrentState == SERVICE_START_PENDING) {
        Context->Status.dwControlsAccepted = 0;
    } else {
        Context->Status.dwControlsAccepted = SERVICE_ACCEPT_STOP | SERVICE_ACCEPT_SHUTDOWN;
    }
    
    if (CurrentState == SERVICE_RUNNING || CurrentState == SERVICE_STOPPED) {
        Context->Status.dwCheckPoint = 0;
    } else {
        Context->Status.dwCheckPoint++;
    }
    
    return SetServiceStatus(Context->StatusHandle, &Context->Status);
}

// Install service
BOOL InstallService(void)
{
    SC_HANDLE hSCManager = OpenSCManager(NULL, NULL, SC_MANAGER_CREATE_SERVICE);
    if (!hSCManager) {
        LogEvent(L"Failed to open Service Control Manager", EVENTLOG_ERROR_TYPE);
        return FALSE;
    }
    
    // Get current module path
    WCHAR modulePath[MAX_PATH];
    GetModuleFileName(NULL, modulePath, MAX_PATH);
    
    // Create service
    SC_HANDLE hService = CreateService(
        hSCManager,
        SERVICE_NAME,
        SERVICE_DISPLAY_NAME,
        SERVICE_ALL_ACCESS,
        SERVICE_WIN32_OWN_PROCESS,
        SERVICE_AUTO_START,
        SERVICE_ERROR_NORMAL,
        modulePath,
        NULL,
        NULL,
        SERVICE_DEPENDENCIES,
        NULL,
        NULL
    );
    
    if (!hService) {
        DWORD err = GetLastError();
        if (err == ERROR_SERVICE_EXISTS) {
            LogEvent(L"Service already exists", EVENTLOG_WARNING_TYPE);
        } else {
            LogEvent(L"Failed to create service", EVENTLOG_ERROR_TYPE);
            CloseServiceHandle(hSCManager);
            return FALSE;
        }
    } else {
        // Set service description
        SERVICE_DESCRIPTION desc;
        desc.lpDescription = (LPWSTR)SERVICE_DESCRIPTION;
        ChangeServiceConfig2(hService, SERVICE_CONFIG_DESCRIPTION, &desc);
        
        CloseServiceHandle(hService);
        LogEvent(L"Service installed successfully", EVENTLOG_INFORMATION_TYPE);
    }
    
    CloseServiceHandle(hSCManager);
    return TRUE;
}

// Uninstall service
BOOL UninstallService(void)
{
    BOOL result = FALSE;
    
    SC_HANDLE hSCManager = OpenSCManager(NULL, NULL, SC_MANAGER_ALL_ACCESS);
    if (!hSCManager) {
        LogEvent(L"Failed to open Service Control Manager", EVENTLOG_ERROR_TYPE);
        return FALSE;
    }
    
    SC_HANDLE hService = OpenService(hSCManager, SERVICE_NAME, SERVICE_ALL_ACCESS);
    if (hService) {
        // Stop service if running
        SERVICE_STATUS status;
        ControlService(hService, SERVICE_CONTROL_STOP, &status);
        
        // Delete service
        if (DeleteService(hService)) {
            LogEvent(L"Service uninstalled successfully", EVENTLOG_INFORMATION_TYPE);
            result = TRUE;
        } else {
            LogEvent(L"Failed to delete service", EVENTLOG_ERROR_TYPE);
        }
        
        CloseServiceHandle(hService);
    } else {
        LogEvent(L"Service not found", EVENTLOG_WARNING_TYPE);
    }
    
    CloseServiceHandle(hSCManager);
    return result;
}

// Start service
BOOL StartService(void)
{
    SC_HANDLE hSCManager = OpenSCManager(NULL, NULL, SC_MANAGER_CONNECT);
    if (!hSCManager) {
        return FALSE;
    }
    
    SC_HANDLE hService = OpenService(hSCManager, SERVICE_NAME, SERVICE_START);
    if (!hService) {
        CloseServiceHandle(hSCManager);
        return FALSE;
    }
    
    BOOL result = StartService(hService, 0, NULL);
    
    CloseServiceHandle(hService);
    CloseServiceHandle(hSCManager);
    
    return result;
}

// Stop service
BOOL StopService(void)
{
    SC_HANDLE hSCManager = OpenSCManager(NULL, NULL, SC_MANAGER_CONNECT);
    if (!hSCManager) {
        return FALSE;
    }
    
    SC_HANDLE hService = OpenService(hSCManager, SERVICE_NAME, SERVICE_STOP | SERVICE_QUERY_STATUS);
    if (!hService) {
        CloseServiceHandle(hSCManager);
        return FALSE;
    }
    
    SERVICE_STATUS status;
    BOOL result = ControlService(hService, SERVICE_CONTROL_STOP, &status);
    
    CloseServiceHandle(hService);
    CloseServiceHandle(hSCManager);
    
    return result;
}

// Open driver
BOOL OpenDriver(PSERVICE_CONTEXT Context)
{
    if (!Context) return FALSE;
    
    Context->DriverHandle = CreateFile(
        L"\\\\.\\HardwareSpoofer",
        GENERIC_READ | GENERIC_WRITE,
        0,
        NULL,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );
    
    if (Context->DriverHandle == INVALID_HANDLE_VALUE) {
        return FALSE;
    }
    
    return TRUE;
}

// Close driver
VOID CloseDriver(PSERVICE_CONTEXT Context)
{
    if (Context && Context->DriverHandle != INVALID_HANDLE_VALUE) {
        CloseHandle(Context->DriverHandle);
        Context->DriverHandle = INVALID_HANDLE_VALUE;
    }
}

// Load configuration
BOOL LoadConfiguration(PSERVICE_CONTEXT Context, LPCWSTR ConfigFile)
{
    if (!Context) return FALSE;
    
    // Set defaults
    Context->Config.AutoStart = TRUE;
    Context->Config.EnableSpoofingOnStart = TRUE;
    Context->Config.UpdateInterval = 5000;
    wcscpy_s(Context->Config.ConfigFile, MAX_PATH, ConfigFile);
    
    // Try to read from INI file
    if (GetFileAttributes(ConfigFile) != INVALID_FILE_ATTRIBUTES) {
        // Read settings from INI file
        // This would require GetPrivateProfileInt/GetPrivateProfileString
    }
    
    return TRUE;
}

// Save configuration
BOOL SaveConfiguration(PSERVICE_CONTEXT Context, LPCWSTR ConfigFile)
{
    if (!Context || !ConfigFile) return FALSE;
    
    // Save settings to INI file
    // This would require WritePrivateProfileString
    
    return TRUE;
}

// Log event to Windows Event Log
VOID LogEvent(LPCWSTR Message, WORD Type)
{
    HANDLE hEventSource = RegisterEventSource(NULL, SERVICE_NAME);
    if (hEventSource) {
        ReportEvent(hEventSource, Type, 0, 0, NULL, 1, 0, &Message, NULL);
        DeregisterEventSource(hEventSource);
    }
    
    // Also output to debugger
    OutputDebugString(Message);
    OutputDebugString(L"\n");
}

// Main entry point
int wmain(int argc, wchar_t* argv[])
{
    if (argc > 1) {
        if (wcscmp(argv[1], L"/install") == 0) {
            return InstallService() ? 0 : 1;
        }
        else if (wcscmp(argv[1], L"/uninstall") == 0) {
            return UninstallService() ? 0 : 1;
        }
        else if (wcscmp(argv[1], L"/start") == 0) {
            return StartService() ? 0 : 1;
        }
        else if (wcscmp(argv[1], L"/stop") == 0) {
            return StopService() ? 0 : 1;
        }
        else {
            wprintf(L"Usage: %s [/install | /uninstall | /start | /stop]\n", argv[0]);
            return 1;
        }
    }
    
    // Run as service
    SERVICE_TABLE_ENTRY serviceTable[] = {
        {SERVICE_NAME, ServiceMain},
        {NULL, NULL}
    };
    
    if (!StartServiceCtrlDispatcher(serviceTable)) {
        LogEvent(L"Failed to start service control dispatcher", EVENTLOG_ERROR_TYPE);
        return 1;
    }
    
    return 0;
}