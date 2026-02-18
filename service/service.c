#include <windows.h>
#include <stdio.h>

#define SERVICE_NAME "HardwareMasquerade"
#define DISPLAY_NAME "Hardware Masquerade Service"
#define DRIVER_SERVICE_NAME "HardwareSpoofer"

// 全局变量
SERVICE_STATUS g_ServiceStatus = {0};
SERVICE_STATUS_HANDLE g_StatusHandle = NULL;
HANDLE g_StopEvent = NULL;

// 函数声明
void WINAPI ServiceMain(DWORD argc, LPTSTR* argv);
void WINAPI ServiceCtrlHandler(DWORD ctrlCode);
DWORD WINAPI ServiceWorkerThread(LPVOID lpParam);
void InstallService();
void UninstallService();
void StartService();
void StopService();
BOOL IsUserAdmin();

int main(int argc, char* argv[]) {
    printf("========================================\n");
    printf("  Hardware Masquerade Windows Service\n");
    printf("========================================\n\n");

    if (argc > 1) {
        if (strcmp(argv[1], "/install") == 0) {
            InstallService();
        }
        else if (strcmp(argv[1], "/uninstall") == 0) {
            UninstallService();
        }
        else if (strcmp(argv[1], "/start") == 0) {
            StartService();
        }
        else if (strcmp(argv[1], "/stop") == 0) {
            StopService();
        }
        else {
            printf("用法:\n");
            printf("  service.exe /install   - 安装服务\n");
            printf("  service.exe /uninstall - 卸载服务\n");
            printf("  service.exe /start     - 启动服务\n");
            printf("  service.exe /stop      - 停止服务\n");
        }
        return 0;
    }

    // 作为服务运行
    SERVICE_TABLE_ENTRY serviceTable[] = {
        {SERVICE_NAME, (LPSERVICE_MAIN_FUNCTION)ServiceMain},
        {NULL, NULL}
    };

    if (!StartServiceCtrlDispatcher(serviceTable)) {
        printf("无法启动服务控制器，错误: %d\n", GetLastError());
        return 1;
    }

    return 0;
}

// 服务主函数
void WINAPI ServiceMain(DWORD argc, LPTSTR* argv) {
    // 注册服务控制处理器
    g_StatusHandle = RegisterServiceCtrlHandler(
        SERVICE_NAME, 
        ServiceCtrlHandler
    );

    if (!g_StatusHandle) {
        return;
    }

    // 初始化服务状态
    g_ServiceStatus.dwServiceType = SERVICE_WIN32_OWN_PROCESS;
    g_ServiceStatus.dwCurrentState = SERVICE_START_PENDING;
    g_ServiceStatus.dwControlsAccepted = SERVICE_ACCEPT_STOP | SERVICE_ACCEPT_SHUTDOWN;
    g_ServiceStatus.dwWin32ExitCode = NO_ERROR;
    g_ServiceStatus.dwServiceSpecificExitCode = 0;
    g_ServiceStatus.dwCheckPoint = 0;
    g_ServiceStatus.dwWaitHint = 3000;

    SetServiceStatus(g_StatusHandle, &g_ServiceStatus);

    // 创建停止事件
    g_StopEvent = CreateEvent(NULL, TRUE, FALSE, NULL);
    if (!g_StopEvent) {
        g_ServiceStatus.dwCurrentState = SERVICE_STOPPED;
        SetServiceStatus(g_StatusHandle, &g_ServiceStatus);
        return;
    }

    // 更新状态为运行中
    g_ServiceStatus.dwCurrentState = SERVICE_RUNNING;
    SetServiceStatus(g_StatusHandle, &g_ServiceStatus);

    // 创建工作线程
    HANDLE hThread = CreateThread(NULL, 0, ServiceWorkerThread, NULL, 0, NULL);
    
    // 等待停止信号
    WaitForSingleObject(g_StopEvent, INFINITE);

    // 清理
    CloseHandle(g_StopEvent);
    
    g_ServiceStatus.dwCurrentState = SERVICE_STOPPED;
    SetServiceStatus(g_StatusHandle, &g_ServiceStatus);
}

// 服务控制处理器
void WINAPI ServiceCtrlHandler(DWORD ctrlCode) {
    switch (ctrlCode) {
        case SERVICE_CONTROL_STOP:
        case SERVICE_CONTROL_SHUTDOWN:
            g_ServiceStatus.dwCurrentState = SERVICE_STOP_PENDING;
            SetServiceStatus(g_StatusHandle, &g_ServiceStatus);
            SetEvent(g_StopEvent);
            break;
            
        case SERVICE_CONTROL_INTERROGATE:
            SetServiceStatus(g_StatusHandle, &g_ServiceStatus);
            break;
    }
}

// 服务工作线程
DWORD WINAPI ServiceWorkerThread(LPVOID lpParam) {
    // 这里添加实际的服务逻辑
    // 例如：监控驱动状态、日志记录等
    
    while (WaitForSingleObject(g_StopEvent, 5000) == WAIT_TIMEOUT) {
        // 每5秒执行一次检查
        // 可以在这里添加定期任务
    }
    
    return 0;
}

// 安装服务
void InstallService() {
    printf("正在安装 Windows 服务...\n");

    if (!IsUserAdmin()) {
        printf("错误: 需要管理员权限！\n");
        return;
    }

    char modulePath[MAX_PATH];
    GetModuleFileName(NULL, modulePath, MAX_PATH);

    SC_HANDLE hSCManager = OpenSCManager(NULL, NULL, SC_MANAGER_CREATE_SERVICE);
    if (!hSCManager) {
        printf("无法打开服务管理器，错误: %d\n", GetLastError());
        return;
    }

    SC_HANDLE hService = CreateService(
        hSCManager,
        SERVICE_NAME,
        DISPLAY_NAME,
        SERVICE_ALL_ACCESS,
        SERVICE_WIN32_OWN_PROCESS,
        SERVICE_AUTO_START,
        SERVICE_ERROR_NORMAL,
        modulePath,
        NULL, NULL, NULL, NULL, NULL
    );

    if (!hService) {
        DWORD err = GetLastError();
        if (err == ERROR_SERVICE_EXISTS) {
            printf("服务已存在。\n");
        } else {
            printf("无法创建服务，错误: %d\n", err);
        }
    } else {
        printf("服务安装成功！\n");
        
        // 设置服务描述
        SERVICE_DESCRIPTION desc;
        desc.lpDescription = "提供硬件伪装功能的管理服务";
        ChangeServiceConfig2(hService, SERVICE_CONFIG_DESCRIPTION, &desc);
        
        CloseServiceHandle(hService);
    }

    CloseServiceHandle(hSCManager);
}

// 卸载服务
void UninstallService() {
    printf("正在卸载 Windows 服务...\n");

    if (!IsUserAdmin()) {
        printf("错误: 需要管理员权限！\n");
        return;
    }

    SC_HANDLE hSCManager = OpenSCManager(NULL, NULL, SC_MANAGER_ALL_ACCESS);
    if (!hSCManager) {
        printf("无法打开服务管理器，错误: %d\n", GetLastError());
        return;
    }

    SC_HANDLE hService = OpenService(hSCManager, SERVICE_NAME, SERVICE_ALL_ACCESS);
    if (!hService) {
        printf("服务未安装。\n");
        CloseServiceHandle(hSCManager);
        return;
    }

    // 停止服务
    SERVICE_STATUS status;
    if (ControlService(hService, SERVICE_CONTROL_STOP, &status)) {
        printf("服务已停止。\n");
        Sleep(1000);
    }

    // 删除服务
    if (DeleteService(hService)) {
        printf("服务已卸载。\n");
    } else {
        printf("无法卸载服务，错误: %d\n", GetLastError());
    }

    CloseServiceHandle(hService);
    CloseServiceHandle(hSCManager);
}

// 启动服务
void StartService() {
    printf("正在启动服务...\n");

    SC_HANDLE hSCManager = OpenSCManager(NULL, NULL, SC_MANAGER_CONNECT);
    if (!hSCManager) {
        printf("无法打开服务管理器，错误: %d\n", GetLastError());
        return;
    }

    SC_HANDLE hService = OpenService(hSCManager, SERVICE_NAME, SERVICE_START);
    if (!hService) {
        printf("服务未安装。\n");
        CloseServiceHandle(hSCManager);
        return;
    }

    if (StartService(hService, 0, NULL)) {
        printf("服务启动成功！\n");
    } else {
        DWORD err = GetLastError();
        if (err == ERROR_SERVICE_ALREADY_RUNNING) {
            printf("服务已经在运行中。\n");
        } else {
            printf("无法启动服务，错误: %d\n", err);
        }
    }

    CloseServiceHandle(hService);
    CloseServiceHandle(hSCManager);
}

// 停止服务
void StopService() {
    printf("正在停止服务...\n");

    SC_HANDLE hSCManager = OpenSCManager(NULL, NULL, SC_MANAGER_CONNECT);
    if (!hSCManager) {
        printf("无法打开服务管理器，错误: %d\n", GetLastError());
        return;
    }

    SC_HANDLE hService = OpenService(hSCManager, SERVICE_NAME, SERVICE_STOP);
    if (!hService) {
        printf("服务未安装。\n");
        CloseServiceHandle(hSCManager);
        return;
    }

    SERVICE_STATUS status;
    if (ControlService(hService, SERVICE_CONTROL_STOP, &status)) {
        printf("服务已停止。\n");
    } else {
        DWORD err = GetLastError();
        if (err == ERROR_SERVICE_NOT_ACTIVE) {
            printf("服务未在运行。\n");
        } else {
            printf("无法停止服务，错误: %d\n", err);
        }
    }

    CloseServiceHandle(hService);
    CloseServiceHandle(hSCManager);
}

// 检查管理员权限
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