#include <ntddk.h>
#include <wdm.h>
#include <ntstrsafe.h>
#include "..\common\ioctl_codes.h"

// Global variables
PDEVICE_OBJECT g_DeviceObject = NULL;
UNICODE_STRING g_DeviceName;
UNICODE_STRING g_SymbolicLinkName;
SPOOF_CONFIG g_SpoofConfig = {0};
BOOLEAN g_SpoofingEnabled = FALSE;
KGUARDED_MUTEX g_ConfigMutex;

// Function prototypes
DRIVER_INITIALIZE DriverEntry;
DRIVER_UNLOAD DriverUnload;
DRIVER_DISPATCH SpooferCreateClose;
DRIVER_DISPATCH SpooferDeviceControl;

// Registry callback to intercept hardware queries
NTSTATUS RegistryCallback(
    _In_ PVOID CallbackContext,
    _In_opt_ PVOID Argument1,
    _In_opt_ PVOID Argument2
)
{
    UNREFERENCED_PARAMETER(CallbackContext);
    
    if (!g_SpoofingEnabled) {
        return STATUS_SUCCESS;
    }
    
    PREG_POST_OPERATION_INFORMATION PostInfo = (PREG_POST_OPERATION_INFORMATION)Argument1;
    PREG_PRE_OPERATION_INFORMATION PreInfo = (PREG_PRE_OPERATION_INFORMATION)Argument1;
    
    // Check if this is a registry operation we want to intercept
    if (PostInfo && PostInfo->Status == STATUS_SUCCESS) {
        switch (PostInfo->Operation) {
            case RegNtQueryValueKey:
            case RegNtQueryMultipleValueKey:
            {
                // Hardware-related registry keys to spoof
                PCWSTR HardwareKeys[] = {
                    L"MachineGuid",
                    L"HwProfileGuid",
                    L"Identifier",
                    L"ProcessorNameString",
                    L"VideoBiosVersion",
                    L"SystemBiosVersion",
                    L"HardwareInformation"
                };
                
                for (int i = 0; i < sizeof(HardwareKeys)/sizeof(HardwareKeys[0]); i++) {
                    if (wcsstr(PostInfo->KeyName->Buffer, HardwareKeys[i])) {
                        // Modify the registry data
                        // Implementation details for modifying registry query results
                        break;
                    }
                }
                break;
            }
        }
    }
    
    return STATUS_SUCCESS;
}

// System service callback to intercept NtQuerySystemInformation
VOID SystemServiceCallback(
    _In_ PVOID CallbackContext,
    _In_ PVOID Argument1,
    _In_ PVOID Argument2
)
{
    UNREFERENCED_PARAMETER(CallbackContext);
    UNREFERENCED_PARAMETER(Argument2);
    
    if (!g_SpoofingEnabled) {
        return;
    }
    
    PSYSTEM_SERVICE_CALLBACK_INFORMATION ServiceInfo = (PSYSTEM_SERVICE_CALLBACK_INFORMATION)Argument1;
    
    // Intercept NtQuerySystemInformation (syscall number varies by Windows version)
    if (ServiceInfo && ServiceInfo->ServiceNumber == 0x36) { // NtQuerySystemInformation
        // Check if querying system hardware information
        // Modify the returned data to spoof hardware IDs
    }
}

// Device control handler
NTSTATUS SpooferDeviceControl(
    _In_ PDEVICE_OBJECT DeviceObject,
    _In_ PIRP Irp
)
{
    UNREFERENCED_PARAMETER(DeviceObject);
    
    PIO_STACK_LOCATION stack = IoGetCurrentIrpStackLocation(Irp);
    NTSTATUS status = STATUS_SUCCESS;
    ULONG bytesReturned = 0;
    
    switch (stack->Parameters.DeviceIoControl.IoControlCode) {
        case IOCTL_SET_SPOOF_CONFIG:
        {
            if (stack->Parameters.DeviceIoControl.InputBufferLength >= sizeof(SPOOF_CONFIG)) {
                PSPOOF_CONFIG config = (PSPOOF_CONFIG)Irp->AssociatedIrp.SystemBuffer;
                
                KeGuardedMutexAcquire(&g_ConfigMutex);
                RtlCopyMemory(&g_SpoofConfig, config, sizeof(SPOOF_CONFIG));
                KeGuardedMutexRelease(&g_ConfigMutex);
                
                bytesReturned = sizeof(SPOOF_CONFIG);
            } else {
                status = STATUS_BUFFER_TOO_SMALL;
            }
            break;
        }
        
        case IOCTL_GET_SPOOF_CONFIG:
        {
            if (stack->Parameters.DeviceIoControl.OutputBufferLength >= sizeof(SPOOF_CONFIG)) {
                PSPOOF_CONFIG config = (PSPOOF_CONFIG)Irp->AssociatedIrp.SystemBuffer;
                
                KeGuardedMutexAcquire(&g_ConfigMutex);
                RtlCopyMemory(config, &g_SpoofConfig, sizeof(SPOOF_CONFIG));
                KeGuardedMutexRelease(&g_ConfigMutex);
                
                bytesReturned = sizeof(SPOOF_CONFIG);
            } else {
                status = STATUS_BUFFER_TOO_SMALL;
            }
            break;
        }
        
        case IOCTL_ENABLE_SPOOFING:
        {
            g_SpoofingEnabled = TRUE;
            DbgPrint("Hardware Spoofing Enabled\n");
            break;
        }
        
        case IOCTL_DISABLE_SPOOFING:
        {
            g_SpoofingEnabled = FALSE;
            DbgPrint("Hardware Spoofing Disabled\n");
            break;
        }
        
        case IOCTL_GET_STATUS:
        {
            PBOOLEAN statusFlag = (PBOOLEAN)Irp->AssociatedIrp.SystemBuffer;
            *statusFlag = g_SpoofingEnabled;
            bytesReturned = sizeof(BOOLEAN);
            break;
        }
        
        default:
            status = STATUS_INVALID_DEVICE_REQUEST;
            break;
    }
    
    Irp->IoStatus.Status = status;
    Irp->IoStatus.Information = bytesReturned;
    IoCompleteRequest(Irp, IO_NO_INCREMENT);
    
    return status;
}

// Create/Close handler
NTSTATUS SpooferCreateClose(
    _In_ PDEVICE_OBJECT DeviceObject,
    _In_ PIRP Irp
)
{
    UNREFERENCED_PARAMETER(DeviceObject);
    
    Irp->IoStatus.Status = STATUS_SUCCESS;
    Irp->IoStatus.Information = 0;
    IoCompleteRequest(Irp, IO_NO_INCREMENT);
    
    return STATUS_SUCCESS;
}

// Driver entry point
NTSTATUS DriverEntry(
    _In_ PDRIVER_OBJECT DriverObject,
    _In_ PUNICODE_STRING RegistryPath
)
{
    UNREFERENCED_PARAMETER(RegistryPath);
    
    NTSTATUS status;
    
    // Initialize mutex
    KeInitializeGuardedMutex(&g_ConfigMutex);
    
    // Create device name
    RtlInitUnicodeString(&g_DeviceName, L"\\Device\\HardwareSpoofer");
    RtlInitUnicodeString(&g_SymbolicLinkName, L"\\DosDevices\\HardwareSpoofer");
    
    // Create device object
    status = IoCreateDevice(
        DriverObject,
        0,
        &g_DeviceName,
        FILE_DEVICE_UNKNOWN,
        FILE_DEVICE_SECURE_OPEN,
        FALSE,
        &g_DeviceObject
    );
    
    if (!NT_SUCCESS(status)) {
        DbgPrint("Failed to create device: %x\n", status);
        return status;
    }
    
    // Create symbolic link
    status = IoCreateSymbolicLink(&g_SymbolicLinkName, &g_DeviceName);
    if (!NT_SUCCESS(status)) {
        DbgPrint("Failed to create symbolic link: %x\n", status);
        IoDeleteDevice(g_DeviceObject);
        return status;
    }
    
    // Set dispatch routines
    DriverObject->MajorFunction[IRP_MJ_CREATE] = SpooferCreateClose;
    DriverObject->MajorFunction[IRP_MJ_CLOSE] = SpooferCreateClose;
    DriverObject->MajorFunction[IRP_MJ_DEVICE_CONTROL] = SpooferDeviceControl;
    DriverObject->DriverUnload = DriverUnload;
    
    // Register registry callback
    status = CmRegisterCallback(RegistryCallback, NULL, &g_RegistryCookie);
    if (!NT_SUCCESS(status)) {
        DbgPrint("Failed to register registry callback: %x\n", status);
    }
    
    // Register system service callback
    status = KeRegisterServiceCallback(SystemServiceCallback, NULL, &g_ServiceCallbackCookie);
    if (!NT_SUCCESS(status)) {
        DbgPrint("Failed to register service callback: %x\n", status);
    }
    
    // Set device flags
    g_DeviceObject->Flags |= DO_DIRECT_IO;
    g_DeviceObject->Flags &= ~DO_DEVICE_INITIALIZING;
    
    DbgPrint("Hardware Spoofer Driver Loaded Successfully\n");
    
    return STATUS_SUCCESS;
}

// Driver unload routine
VOID DriverUnload(
    _In_ PDRIVER_OBJECT DriverObject
)
{
    // Unregister callbacks
    if (g_RegistryCookie) {
        CmUnRegisterCallback(g_RegistryCookie);
    }
    
    if (g_ServiceCallbackCookie) {
        KeDeregisterServiceCallback(g_ServiceCallbackCookie);
    }
    
    // Delete symbolic link
    IoDeleteSymbolicLink(&g_SymbolicLinkName);
    
    // Delete device
    if (g_DeviceObject) {
        IoDeleteDevice(g_DeviceObject);
    }
    
    DbgPrint("Hardware Spoofer Driver Unloaded\n");
}