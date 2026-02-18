#pragma once

// IOCTL codes for driver communication
#define IOCTL_SPOOFER_BASE CTL_CODE(FILE_DEVICE_UNKNOWN, 0x800, METHOD_BUFFERED, FILE_ANY_ACCESS)

#define IOCTL_SET_SPOOF_CONFIG  CTL_CODE(FILE_DEVICE_UNKNOWN, 0x801, METHOD_BUFFERED, FILE_WRITE_ACCESS)
#define IOCTL_GET_SPOOF_CONFIG  CTL_CODE(FILE_DEVICE_UNKNOWN, 0x802, METHOD_BUFFERED, FILE_READ_ACCESS)
#define IOCTL_ENABLE_SPOOFING   CTL_CODE(FILE_DEVICE_UNKNOWN, 0x803, METHOD_BUFFERED, FILE_WRITE_ACCESS)
#define IOCTL_DISABLE_SPOOFING  CTL_CODE(FILE_DEVICE_UNKNOWN, 0x804, METHOD_BUFFERED, FILE_WRITE_ACCESS)
#define IOCTL_GET_STATUS        CTL_CODE(FILE_DEVICE_UNKNOWN, 0x805, METHOD_BUFFERED, FILE_READ_ACCESS)

// Spoofing configuration structure
typedef struct _SPOOF_CONFIG {
    BOOLEAN SpoofDiskId;
    BOOLEAN SpoofMacAddress;
    BOOLEAN SpoofCpuId;
    BOOLEAN SpoofBiosInfo;
    BOOLEAN SpoofGpuInfo;
    BOOLEAN SpoofRamInfo;
    BOOLEAN SpoofMotherboard;
    BOOLEAN SpoofMonitorInfo;
    
    // Fake data buffers
    WCHAR FakeDiskId[64];
    WCHAR FakeMacAddress[18];
    WCHAR FakeCpuId[64];
    WCHAR FakeBiosVersion[64];
    WCHAR FakeGpuName[128];
    ULONG FakeRamSize;  // in MB
    WCHAR FakeMotherboard[64];
    WCHAR FakeMonitorInfo[128];
    
    // Process filter
    BOOLEAN EnableProcessFilter;
    ULONG TargetProcessIds[32];
    ULONG ProcessCount;
} SPOOF_CONFIG, *PSPOOF_CONFIG;