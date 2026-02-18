#pragma once

#ifdef __cplusplus
extern "C" {
#endif

#include <windows.h>
#include <winioctl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// 定义 BOOLEAN 如果未定义
#ifndef BOOLEAN
typedef unsigned char BOOLEAN;
#endif

// 包含驱动头文件
#include "../common/ioctl_codes.h"

// 服务管理器函数
SC_HANDLE OpenServiceManager(void);
SC_HANDLE CreateDriverService(LPCWSTR DriverName, LPCWSTR DriverPath);
SC_HANDLE OpenDriverService(LPCWSTR DriverName);
BOOL DeleteDriverService(LPCWSTR DriverName);
BOOL StartDriverService(SC_HANDLE hService);
BOOL StopDriverService(SC_HANDLE hService);
BOOL ControlDriver(SC_HANDLE hService, DWORD ControlCode);

// 驱动通信函数
HANDLE OpenDriverDevice(LPCWSTR DeviceName);
BOOL CloseDriverDevice(HANDLE hDevice);
BOOL SendSpoofConfig(HANDLE hDevice, PSPOOF_CONFIG Config);
BOOL GetSpoofConfig(HANDLE hDevice, PSPOOF_CONFIG Config);
BOOL EnableSpoofing(HANDLE hDevice);
BOOL DisableSpoofing(HANDLE hDevice);
BOOL GetSpoofingStatus(HANDLE hDevice, PBOOLEAN Enabled);
BOOL SetProcessFilter(HANDLE hDevice, PULONG ProcessIds, ULONG Count);

// 安装函数
BOOL InstallDriver(LPCWSTR DriverPath);
BOOL UninstallDriver(void);
BOOL IsDriverInstalled(void);
BOOL IsDriverRunning(void);
BOOL LoadDriver(void);
BOOL UnloadDriver(void);

// 工具函数
VOID PrintLastError(LPCSTR Function);
BOOL IsUserAdministrator(void);
BOOL EnableDebugPrivilege(void);
LPCWSTR GetErrorMessage(DWORD ErrorCode);

// 配置函数
BOOL SaveConfigToFile(LPCWSTR FilePath, PSPOOF_CONFIG Config);
BOOL LoadConfigFromFile(LPCWSTR FilePath, PSPOOF_CONFIG Config);
BOOL ValidateConfig(PSPOOF_CONFIG Config);
VOID SetDefaultConfig(PSPOOF_CONFIG Config);

// 命令行选项
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

#ifdef __cplusplus
}
#endif