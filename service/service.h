#pragma once

#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Service configuration
#define SERVICE_NAME             L"HardwareMasquerade"
#define SERVICE_DISPLAY_NAME     L"Hardware Masquerade Service"
#define SERVICE_DESCRIPTION      L"Provides hardware spoofing capabilities"
#define SERVICE_DEPENDENCIES     L""

// Service control codes
#define SERVICE_CONTROL_ENABLE_SPOOFING  128
#define SERVICE_CONTROL_DISABLE_SPOOFING 129
#define SERVICE_CONTROL_GET_STATUS       130

// Service status
typedef enum _SERVICE_STATE {
    SERVICE_STATE_STOPPED,
    SERVICE_STATE_STARTING,
    SERVICE_STATE_RUNNING,
    SERVICE_STATE_STOPPING
} SERVICE_STATE;

// Service configuration structure
typedef struct _SERVICE_CONFIG {
    BOOL AutoStart;
    BOOL EnableSpoofingOnStart;
    WCHAR ConfigFile[MAX_PATH];
    DWORD UpdateInterval;  // milliseconds
} SERVICE_CONFIG, *PSERVICE_CONFIG;

// Service context
typedef struct _SERVICE_CONTEXT {
    SERVICE_STATUS_HANDLE StatusHandle;
    SERVICE_STATUS Status;
    SERVICE_STATE CurrentState;
    HANDLE StopEvent;
    HANDLE UpdateTimer;
    CRITICAL_SECTION ConfigLock;
    SERVICE_CONFIG Config;
    HANDLE DriverHandle;
    BOOL SpoofingEnabled;
} SERVICE_CONTEXT, *PSERVICE_CONTEXT;

// Function prototypes
VOID WINAPI ServiceMain(DWORD argc, LPTSTR* argv);
VOID WINAPI ServiceCtrlHandler(DWORD ctrlCode);
DWORD WINAPI ServiceWorkerThread(LPVOID lpParam);
BOOL InstallService(void);
BOOL UninstallService(void);
BOOL StartService(void);
BOOL StopService(void);
BOOL UpdateServiceStatus(PSERVICE_CONTEXT Context, DWORD CurrentState, DWORD Win32ExitCode, DWORD WaitHint);
BOOL OpenDriver(PSERVICE_CONTEXT Context);
VOID CloseDriver(PSERVICE_CONTEXT Context);
BOOL LoadConfiguration(PSERVICE_CONTEXT Context, LPCWSTR ConfigFile);
BOOL SaveConfiguration(PSERVICE_CONTEXT Context, LPCWSTR ConfigFile);
VOID LogEvent(LPCWSTR Message, WORD Type);