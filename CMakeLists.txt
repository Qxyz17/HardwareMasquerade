cmake_minimum_required(VERSION 3.15)
project(HardwareMasquerade)

# 设置 C 标准
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# 查找 WDK
if(NOT DEFINED WDK_ROOT)
    if(DEFINED ENV{WDK_ROOT})
        set(WDK_ROOT $ENV{WDK_ROOT})
    else()
        set(WDK_ROOT "C:/Program Files (x86)/Windows Kits/10")
    endif()
endif()

# 添加驱动
add_executable(HardwareSpoofer driver/HardwareSpoofer.c)

# 设置驱动编译选项
target_compile_options(HardwareSpoofer PRIVATE
    /kernel
    /W4
    /Gs
    /Gz
)

# 设置驱动包含目录
target_include_directories(HardwareSpoofer PRIVATE
    ${WDK_ROOT}/Include/10.0.19041.0/km
    ${WDK_ROOT}/Include/10.0.19041.0/um
    ${WDK_ROOT}/Include/10.0.19041.0/shared
    ${CMAKE_CURRENT_SOURCE_DIR}/common
)

# 设置驱动定义
target_compile_definitions(HardwareSpoofer PRIVATE
    _KERNEL_MODE
    DBG=1
    _UNICODE
    UNICODE
)

# 设置驱动链接选项
target_link_options(HardwareSpoofer PRIVATE
    /subsystem:native
    /driver
    /entry:DriverEntry
)

# 添加加载器
add_executable(loader driver_loader/loader.c)

# 设置加载器编译选项
target_compile_options(loader PRIVATE
    /W4
    /O2
)

# 设置加载器包含目录
target_include_directories(loader PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/common
)

# 设置加载器链接库
target_link_libraries(loader
    advapi32
    user32
)

# 添加服务
add_executable(service service/service.c)

# 设置服务编译选项
target_compile_options(service PRIVATE
    /W4
    /O2
)

# 设置服务包含目录
target_include_directories(service PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/common
)

# 设置服务链接库
target_link_libraries(service
    advapi32
    user32
)