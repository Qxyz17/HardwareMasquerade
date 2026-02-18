#pragma once

#include <windows.h>
#include <winioctl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

// Service manager functions
SC_HANDLE OpenServiceManager(void);
SC_HANDLE CreateDriverService(LPCWSTR DriverName, LPCWSTR DriverPath);
SC_HANDLE OpenDriverService(LPCWSTR DriverName);
BOOL DeleteDriverService(LPCWSTR DriverName);
BOOL StartDriverService(SC_HANDLE hService);
BOOL StopDriverService(SC_HANDLE hService);
BOOL ControlDriver(SC_HANDLE hService, DWORD ControlCode);

// Driver communication functions
HANDLE OpenDriverDevice(LPCWSTR DeviceName);
BOOL CloseDriverDevice(HANDLE hDevice);
BOOL SendSpoofConfig(HANDLE hDevice, PSPOOF_CONFIG Config);
BOOL GetSpoofConfig(HANDLE hDevice, PSPOOF_CONFIG Config);
BOOL EnableSpoofing(HANDLE hDevice);
BOOL DisableSpoofing(HANDLE hDevice);
BOOL GetSpoofingStatus(HANDLE hDevice, PBOOLEAN Enabled);
BOOL SetProcessFilter(HANDLE hDevice, PULONG ProcessIds, ULONG Count);

// Installation functions
BOOL InstallDriver(LPCWSTR DriverPath);
BOOL UninstallDriver(void);
BOOL IsDriverInstalled(void);
BOOL IsDriverRunning(void);
BOOL LoadDriver(void);
BOOL UnloadDriver(void);

// Utility functions
VOID PrintLastError(LPCSTR Function);
BOOL IsUserAdministrator(void);
BOOL EnableDebugPrivilege(void);
LPCWSTR GetErrorMessage(DWORD ErrorCode);

// Configuration functions
BOOL SaveConfigToFile(LPCWSTR FilePath, PSPOOF_CONFIG Config);
BOOL LoadConfigFromFile(LPCWSTR FilePath, PSPOOF_CONFIG Config);
BOOL ValidateConfig(PSPOOF_CONFIG Config);
VOID SetDefaultConfig(PSPOOF_CONFIG Config);

// Command line parsing
typedef struct _COMMAND_OPTIONS {
    BOOL Install;
    BOOL Uninstall;
    BOOL Start;
    BOOL Stop;
    BOOL Enable;
    BOOL Disable;
    BOOL Status;
    BOOL Config;
    BOOL Help;
    WCHAR ConfigFile[MAX_PATH];
    WCHAR DriverPath[MAX_PATH];
} COMMAND_OPTIONS, *PCOMMAND_OPTIONS;

BOOL ParseCommandLine(int argc, wchar_t* argv[], PCOMMAND_OPTIONS Options);
VOID ShowUsage(void);
VOID ShowStatus(void);