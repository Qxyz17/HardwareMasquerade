#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <winioctl.h>

// 服务名称
#define SERVICE_NAME "HardwareSpoofer"
#define DISPLAY_NAME "Hardware Masquerade Driver"
#define DRIVER_PATH "C:\\Windows\\System32\\drivers\\HardwareSpoofer.sys"

// 函数声明
void InstallDriver();
void UninstallDriver();
void StartDriver();
void StopDriver();
void ShowStatus();
BOOL IsUserAdmin();
BOOL EnableDebugPrivilege();

int main(int argc, char* argv[]) {
    printf("========================================\n");
    printf("  Hardware Masquerade Driver Loader\n");
    printf("========================================\n\n");

    if (argc < 2) {
        printf("Usage: loader.exe [command]\n\n");
        printf("Commands:\n");
        printf("  install   - Install and start the driver\n");
        printf("  uninstall - Stop and uninstall the driver\n");
        printf("  start     - Start the driver\n");
        printf("  stop      - Stop the driver\n");
        printf("  status    - Show driver status\n");
        printf("  help      - Show this help\n\n");
        return 0;
    }

    // 检查管理员权限（除了 help 和 status）
    if (strcmp(argv[1], "help") != 0 && strcmp(argv[1], "status") != 0) {
        if (!IsUserAdmin()) {
            printf("错误: 需要管理员权限！\n");
            printf("请以管理员身份重新运行。\n");
            return 1;
        }
        EnableDebugPrivilege();
    }

    // 处理命令
    if (strcmp(argv[1], "install") == 0) {
        InstallDriver();
    }
    else if (strcmp(argv[1], "uninstall") == 0) {
        UninstallDriver();
    }
    else if (strcmp(argv[1], "start") == 0) {
        StartDriver();
    }
    else if (strcmp(argv[1], "stop") == 0) {
        StopDriver();
    }
    else if (strcmp(argv[1], "status") == 0) {
        ShowStatus();
    }
    else if (strcmp(argv[1], "help") == 0) {
        // 显示帮助
        printf("Commands:\n");
        printf("  install   - Install and start the driver\n");
        printf("  uninstall - Stop and uninstall the driver\n");
        printf("  start     - Start the driver\n");
        printf("  stop      - Stop the driver\n");
        printf("  status    - Show driver status\n");
        printf("  help      - Show this help\n");
    }
    else {
        printf("未知命令: %s\n", argv[1]);
        printf("使用 'loader.exe help' 查看可用命令\n");
    }

    return 0;
}

// 检查是否为管理员
BOOL IsUserAdmin() {
    BOOL isAdmin = FALSE;
    PSID adminGroup = NULL;
    SID_IDENTIFIER_AUTHORITY ntAuthority = SECURITY_NT_AUTHORITY;

    if (AllocateAndInitializeSid(&ntAuthority, 2, 
        SECURITY_BUILTIN_DOMAIN_RID, DOMAIN_ALIAS_RID_ADMINS,
        0, 0, 0, 0, 0, 0, &adminGroup)) {
        
        CheckTokenMembership(NULL, adminGroup, &isAdmin);
        FreeSid(adminGroup);
    }

    return isAdmin;
}

// 启用调试权限
BOOL EnableDebugPrivilege() {
    HANDLE hToken;
    TOKEN_PRIVILEGES tp;

    if (!OpenProcessToken(GetCurrentProcess(), 
        TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, &hToken)) {
        printf("无法打开进程令牌，错误: %d\n", GetLastError());
        return FALSE;
    }

    tp.PrivilegeCount = 1;
    tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;

    if (!LookupPrivilegeValue(NULL, SE_DEBUG_NAME, &tp.Privileges[0].Luid)) {
        printf("无法查找权限，错误: %d\n", GetLastError());
        CloseHandle(hToken);
        return FALSE;
    }

    BOOL result = AdjustTokenPrivileges(hToken, FALSE, &tp, 
        sizeof(tp), NULL, NULL);
    
    if (!result || GetLastError() != ERROR_SUCCESS) {
        printf("无法调整权限，错误: %d\n", GetLastError());
    }

    CloseHandle(hToken);
    return result;
}

// 安装驱动
void InstallDriver() {
    printf("正在安装驱动...\n");

    SC_HANDLE hSCManager = OpenSCManager(NULL, NULL, 
        SC_MANAGER_CREATE_SERVICE);
    
    if (!hSCManager) {
        printf("无法打开服务管理器，错误: %d\n", GetLastError());
        return;
    }

    // 检查驱动文件是否存在
    if (GetFileAttributes(DRIVER_PATH) == INVALID_FILE_ATTRIBUTES) {
        printf("错误: 驱动文件不存在于 %s\n", DRIVER_PATH);
        printf("请确保 HardwareSpoofer.sys 已复制到系统目录。\n");
        CloseServiceHandle(hSCManager);
        return;
    }

    // 创建服务
    SC_HANDLE hService = CreateService(
        hSCManager,
        SERVICE_NAME,
        DISPLAY_NAME,
        SERVICE_ALL_ACCESS,
        SERVICE_KERNEL_DRIVER,
        SERVICE_DEMAND_START,
        SERVICE_ERROR_NORMAL,
        DRIVER_PATH,
        NULL, NULL, NULL, NULL, NULL
    );

    if (!hService) {
        DWORD err = GetLastError();
        if (err == ERROR_SERVICE_EXISTS) {
            printf("驱动服务已存在，正在打开...\n");
            hService = OpenService(hSCManager, SERVICE_NAME, SERVICE_ALL_ACCESS);
        } else {
            printf("无法创建驱动服务，错误: %d\n", err);
            CloseServiceHandle(hSCManager);
            return;
        }
    }

    if (hService) {
        printf("驱动服务创建成功！\n");
        
        // 启动驱动
        if (StartService(hService, 0, NULL)) {
            printf("驱动启动成功！\n");
        } else {
            DWORD err = GetLastError();
            if (err == ERROR_SERVICE_ALREADY_RUNNING) {
                printf("驱动已经在运行中。\n");
            } else {
                printf("无法启动驱动，错误: %d\n", err);
            }
        }

        CloseServiceHandle(hService);
    }

    CloseServiceHandle(hSCManager);
}

// 卸载驱动
void UninstallDriver() {
    printf("正在卸载驱动...\n");

    SC_HANDLE hSCManager = OpenSCManager(NULL, NULL, SC_MANAGER_ALL_ACCESS);
    if (!hSCManager) {
        printf("无法打开服务管理器，错误: %d\n", GetLastError());
        return;
    }

    SC_HANDLE hService = OpenService(hSCManager, SERVICE_NAME, SERVICE_ALL_ACCESS);
    if (!hService) {
        printf("驱动服务未安装。\n");
        CloseServiceHandle(hSCManager);
        return;
    }

    // 停止驱动
    SERVICE_STATUS status;
    if (ControlService(hService, SERVICE_CONTROL_STOP, &status)) {
        printf("驱动已停止。\n");
        Sleep(1000);
    } else {
        DWORD err = GetLastError();
        if (err != ERROR_SERVICE_NOT_ACTIVE) {
            printf("无法停止驱动，错误: %d\n", err);
        }
    }

    // 删除服务
    if (DeleteService(hService)) {
        printf("驱动服务已删除。\n");
    } else {
        printf("无法删除驱动服务，错误: %d\n", GetLastError());
    }

    CloseServiceHandle(hService);
    CloseServiceHandle(hSCManager);

    // 尝试删除驱动文件
    if (DeleteFile(DRIVER_PATH)) {
        printf("驱动文件已删除。\n");
    } else {
        printf("驱动文件将在重启后删除。\n");
    }
}

// 启动驱动
void StartDriver() {
    printf("正在启动驱动...\n");

    SC_HANDLE hSCManager = OpenSCManager(NULL, NULL, SC_MANAGER_CONNECT);
    if (!hSCManager) {
        printf("无法打开服务管理器，错误: %d\n", GetLastError());
        return;
    }

    SC_HANDLE hService = OpenService(hSCManager, SERVICE_NAME, SERVICE_START);
    if (!hService) {
        printf("驱动服务未安装。\n");
        CloseServiceHandle(hSCManager);
        return;
    }

    if (StartService(hService, 0, NULL)) {
        printf("驱动启动成功！\n");
    } else {
        DWORD err = GetLastError();
        if (err == ERROR_SERVICE_ALREADY_RUNNING) {
            printf("驱动已经在运行中。\n");
        } else {
            printf("无法启动驱动，错误: %d\n", err);
        }
    }

    CloseServiceHandle(hService);
    CloseServiceHandle(hSCManager);
}

// 停止驱动
void StopDriver() {
    printf("正在停止驱动...\n");

    SC_HANDLE hSCManager = OpenSCManager(NULL, NULL, SC_MANAGER_CONNECT);
    if (!hSCManager) {
        printf("无法打开服务管理器，错误: %d\n", GetLastError());
        return;
    }

    SC_HANDLE hService = OpenService(hSCManager, SERVICE_NAME, SERVICE_STOP);
    if (!hService) {
        printf("驱动服务未安装。\n");
        CloseServiceHandle(hSCManager);
        return;
    }

    SERVICE_STATUS status;
    if (ControlService(hService, SERVICE_CONTROL_STOP, &status)) {
        printf("驱动已停止。\n");
    } else {
        DWORD err = GetLastError();
        if (err == ERROR_SERVICE_NOT_ACTIVE) {
            printf("驱动未在运行。\n");
        } else {
            printf("无法停止驱动，错误: %d\n", err);
        }
    }

    CloseServiceHandle(hService);
    CloseServiceHandle(hSCManager);
}

// 显示状态
void ShowStatus() {
    printf("正在检查驱动状态...\n\n");

    SC_HANDLE hSCManager = OpenSCManager(NULL, NULL, SC_MANAGER_CONNECT);
    if (!hSCManager) {
        printf("无法打开服务管理器，错误: %d\n", GetLastError());
        return;
    }

    SC_HANDLE hService = OpenService(hSCManager, SERVICE_NAME, SERVICE_QUERY_STATUS);
    if (!hService) {
        printf("驱动状态: 未安装\n");
        CloseServiceHandle(hSCManager);
        return;
    }

    SERVICE_STATUS status;
    if (QueryServiceStatus(hService, &status)) {
        printf("驱动状态: ");
        switch (status.dwCurrentState) {
            case SERVICE_RUNNING:
                printf("运行中\n");
                break;
            case SERVICE_STOPPED:
                printf("已停止\n");
                break;
            case SERVICE_START_PENDING:
                printf("正在启动\n");
                break;
            case SERVICE_STOP_PENDING:
                printf("正在停止\n");
                break;
            default:
                printf("未知状态 (%d)\n", status.dwCurrentState);
        }

        // 检查驱动文件
        if (GetFileAttributes(DRIVER_PATH) != INVALID_FILE_ATTRIBUTES) {
            printf("驱动文件: 存在 (%s)\n", DRIVER_PATH);
        } else {
            printf("驱动文件: 不存在\n");
        }

    } else {
        printf("无法查询驱动状态，错误: %d\n", GetLastError());
    }

    CloseServiceHandle(hService);
    CloseServiceHandle(hSCManager);
}