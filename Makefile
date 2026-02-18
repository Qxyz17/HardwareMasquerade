# Makefile for Hardware Masquerade

WDK_ROOT = C:/Program Files (x86)/Windows Kits/10
SDK_VERSION = 10.0.19041.0
VS_TOOLS = C:/Program Files (x86)/Microsoft Visual Studio/2019/Community/VC/Tools/MSVC/14.29.30133

CC = cl.exe
LD = link.exe

CFLAGS = /nologo /O2 /MT /W4 /Gz /kernel
LDFLAGS = /nologo /subsystem:native /driver /entry:DriverEntry

INCLUDES = /I"$(WDK_ROOT)/Include/$(SDK_VERSION)/km" \
           /I"$(WDK_ROOT)/Include/$(SDK_VERSION)/um" \
           /I"$(WDK_ROOT)/Include/$(SDK_VERSION)/shared" \
           /I"common"

DEFINES = /D_KERNEL_MODE /DDBG=1 /DUNICODE /D_UNICODE

LIBS = ntoskrnl.lib hal.lib

all: driver loader service

driver:
    $(CC) $(CFLAGS) $(INCLUDES) $(DEFINES) driver/HardwareSpoofer.c /FeHardwareSpoofer.sys /link $(LDFLAGS) $(LIBS)

loader:
    $(CC) /nologo /O2 /W4 driver_loader/loader.c /Feloader.exe /link advapi32.lib user32.lib

service:
    $(CC) /nologo /O2 /W4 service/service.c /Feservice.exe /link advapi32.lib user32.lib

clean:
    del *.obj *.sys *.exe *.exp *.lib

.PHONY: all driver loader service clean