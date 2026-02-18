#pragma once

#include <ntddk.h>
#include <wdm.h>
#include <ntstrsafe.h>

// 定义 BOOLEAN 如果未定义
#ifndef BOOLEAN
typedef unsigned char BOOLEAN;
#endif

// 定义 UNICODE_STRING 如果未定义
#ifndef UNICODE_STRING
typedef struct _UNICODE_STRING {
    USHORT Length;
    USHORT MaximumLength;
    PWSTR  Buffer;
} UNICODE_STRING;
#endif

// 设备名称
#define DEVICE_NAME L"\\Device\\HardwareSpoofer"
#define SYMBOLIC_LINK_NAME L"\\DosDevices\\HardwareSpoofer"

// 内存池标签
#define SPOOFER_POOL_TAG 'fooS'

// IOCTL 代码定义
#define IOCTL_SPOOFER_BASE CTL_CODE(FILE_DEVICE_UNKNOWN, 0x800, METHOD_BUFFERED, FILE_ANY_ACCESS)
#define IOCTL_SET_SPOOF_CONFIG  CTL_CODE(FILE_DEVICE_UNKNOWN, 0x801, METHOD_BUFFERED, FILE_WRITE_ACCESS)
#define IOCTL_GET_SPOOF_CONFIG  CTL_CODE(FILE_DEVICE_UNKNOWN, 0x802, METHOD_BUFFERED, FILE_READ_ACCESS)
#define IOCTL_ENABLE_SPOOFING   CTL_CODE(FILE_DEVICE_UNKNOWN, 0x803, METHOD_BUFFERED, FILE_WRITE_ACCESS)
#define IOCTL_DISABLE_SPOOFING  CTL_CODE(FILE_DEVICE_UNKNOWN, 0x804, METHOD_BUFFERED, FILE_WRITE_ACCESS)
#define IOCTL_GET_STATUS        CTL_CODE(FILE_DEVICE_UNKNOWN, 0x805, METHOD_BUFFERED, FILE_READ_ACCESS)

// 注册表路径
#define REGISTRY_HARDWARE_PATH L"\\Registry\\Machine\\HARDWARE"
#define REGISTRY_SYSTEM_PATH L"\\Registry\\Machine\\SYSTEM"
#define REGISTRY_CRYPTO_PATH L"\\Registry\\Machine\\SOFTWARE\\Microsoft\\Cryptography"

// 注册表值名称
#define REG_VALUE_MACHINE_GUID L"MachineGuid"
#define REG_VALUE_HW_PROFILE_GUID L"HwProfileGuid"
#define REG_VALUE_PROCESSOR_NAME L"ProcessorNameString"
#define REG_VALUE_VIDEO_BIOS L"VideoBiosVersion"
#define REG_VALUE_SYSTEM_BIOS L"SystemBiosVersion"

// 欺骗配置结构
typedef struct _SPOOF_CONFIG {
    BOOLEAN SpoofDiskId;
    BOOLEAN SpoofMacAddress;
    BOOLEAN SpoofCpuId;
    BOOLEAN SpoofBiosInfo;
    BOOLEAN SpoofGpuInfo;
    BOOLEAN SpoofRamInfo;
    BOOLEAN SpoofMotherboard;
    BOOLEAN SpoofMonitorInfo;
    
    // 伪造数据缓冲区
    WCHAR FakeDiskId[64];
    WCHAR FakeMacAddress[18];
    WCHAR FakeCpuId[64];
    WCHAR FakeBiosVersion[64];
    WCHAR FakeGpuName[128];
    ULONG FakeRamSize;
    WCHAR FakeMotherboard[64];
    WCHAR FakeMonitorInfo[128];
    
    // 进程过滤
    BOOLEAN EnableProcessFilter;
    ULONG TargetProcessIds[32];
    ULONG ProcessCount;
} SPOOF_CONFIG, *PSPOOF_CONFIG;

// 驱动上下文结构
typedef struct _DRIVER_CONTEXT {
    LARGE_INTEGER RegistrationCookie;
    PVOID ProcessCallbackHandle;
    PVOID ImageCallbackHandle;
    FAST_MUTEX ConfigMutex;
    SPOOF_CONFIG CurrentConfig;
    BOOLEAN SpoofingEnabled;
    LIST_ENTRY ActiveSessions;
    ULONG SessionCount;
} DRIVER_CONTEXT, *PDRIVER_CONTEXT;

// 函数原型
DRIVER_INITIALIZE DriverEntry;
DRIVER_UNLOAD DriverUnload;
DRIVER_DISPATCH SpooferCreateClose;
DRIVER_DISPATCH SpooferDeviceControl;

NTSTATUS RegistryCallback(
    _In_ PVOID CallbackContext,
    _In_opt_ PVOID Argument1,
    _In_opt_ PVOID Argument2
);

VOID ProcessCallback(
    _In_ HANDLE ParentId,
    _In_ HANDLE ProcessId,
    _In_ BOOLEAN Create
);

BOOLEAN ShouldSpoofProcess(_In_ HANDLE ProcessId);
NTSTATUS SpoofRegistryQuery(_In_ PVOID PreInfo, _In_opt_ PVOID PostInfo);
VOID GenerateFakeData(_Inout_ PSPOOF_CONFIG Config);