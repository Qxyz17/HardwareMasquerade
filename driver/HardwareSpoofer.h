#pragma once

#include <ntddk.h>
#include <wdm.h>
#include <ntstrsafe.h>
#include <initguid.h>

// Device names
#define DEVICE_NAME L"\\Device\\HardwareSpoofer"
#define SYMBOLIC_LINK_NAME L"\\DosDevices\\HardwareSpoofer"

// Pool tags
#define SPOOFER_POOL_TAG 'FOOPS'

// IOCTL codes (defined in ioctl_codes.h)
#include "..\common\ioctl_codes.h"

// Registry keys to monitor
#define REGISTRY_HARDWARE_PATH L"\\Registry\\Machine\\HARDWARE"
#define REGISTRY_SYSTEM_PATH L"\\Registry\\Machine\\SYSTEM"
#define REGISTRY_CRYPTO_PATH L"\\Registry\\Machine\\SOFTWARE\\Microsoft\\Cryptography"
#define REGISTRY_DEVICE_PATH L"\\Registry\\Machine\\HARDWARE\\DEVICEMAP"

// Hardware-related registry values
#define REG_VALUE_MACHINE_GUID L"MachineGuid"
#define REG_VALUE_HW_PROFILE_GUID L"HwProfileGuid"
#define REG_VALUE_PROCESSOR_NAME L"ProcessorNameString"
#define REG_VALUE_VIDEO_BIOS L"VideoBiosVersion"
#define REG_VALUE_SYSTEM_BIOS L"SystemBiosVersion"
#define REG_VALUE_IDENTIFIER L"Identifier"

// Function prototypes
DRIVER_INITIALIZE DriverEntry;
DRIVER_UNLOAD DriverUnload;
DRIVER_DISPATCH SpooferCreateClose;
DRIVER_DISPATCH SpooferDeviceControl;

// Callback functions
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

VOID ImageLoadCallback(
    _In_ PUNICODE_STRING FullImageName,
    _In_ HANDLE ProcessId,
    _In_ PIMAGE_INFO ImageInfo
);

VOID SystemServiceCallback(
    _In_ PVOID CallbackContext,
    _In_ PVOID Argument1,
    _In_ PVOID Argument2
);

// Spoofing functions
NTSTATUS SpoofRegistryQuery(
    _In_ PVOID PreInfo,
    _In_opt_ PVOID PostInfo
);

NTSTATUS SpoofSystemInformation(
    _In_ PVOID ServiceInfo
);

NTSTATUS SpoofDeviceIoControl(
    _In_ PDEVICE_OBJECT DeviceObject,
    _In_ PIRP Irp
);

// Helper functions
BOOLEAN ShouldSpoofProcess(_In_ HANDLE ProcessId);
VOID GenerateFakeData(_Inout_ PSPOOF_CONFIG Config);
NTSTATUS ModifyRegistryData(
    _In_ PVOID Data,
    _In_ ULONG DataSize,
    _In_ PCWSTR ValueName
);

// Driver context structure
typedef struct _DRIVER_CONTEXT {
    LARGE_INTEGER RegistrationCookie;
    PVOID ProcessCallbackHandle;
    PVOID ImageCallbackHandle;
    PVOID ServiceCallbackHandle;
    FAST_MUTEX ConfigMutex;
    SPOOF_CONFIG CurrentConfig;
    BOOLEAN SpoofingEnabled;
    LIST_ENTRY ActiveSessions;
    ULONG SessionCount;
} DRIVER_CONTEXT, *PDRIVER_CONTEXT;

// Session tracking structure
typedef struct _SPOOF_SESSION {
    LIST_ENTRY ListEntry;
    HANDLE ProcessId;
    LARGE_INTEGER StartTime;
    SPOOF_CONFIG SessionConfig;
    ULONG ReferenceCount;
} SPOOF_SESSION, *PSPOOF_SESSION;