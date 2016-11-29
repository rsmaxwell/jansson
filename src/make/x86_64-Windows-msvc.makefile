
CC = cl
LD = link


CFLAGS_BASE = -c -GS -W2 -Zc:wchar_t -sdl -Zc:inline -fp:precise -WX- -Zc:forScope -RTC1 -Gd -EHsc -nologo -wd4090
CFLAGS_NORMAL = -MD
CFLAGS_DEBUG = -MDd -Gm -Zi -Od 

DEFINES_BASE = -D_MT -D_DLL -DbuildLabel=$(buildLabel) -D_CRT_SECURE_NO_WARNINGS -D_CRT_SECURE_NO_DEPRECATE -D_CRT_NONSTDC_NO_DEPRECATE -D_CRT_NON_CONFORMING_SWPRINTFS -DHAVE_CONFIG_H
DEFINES_DEBUG = -D_DEBUG

LINKFLAGS_BASE = /NXCOMPAT /DYNAMICBASE /MACHINE:X64 /SUBSYSTEM:CONSOLE /NOLOGO /DLL
LINKFLAGS_DEBUG = /DEBUG 


ifeq ($(BUILD_TYPE),debug)
  CFLAGS = $(CFLAGS_BASE) $(CFLAGS_DEBUG)
  DEFINES = $(DEFINES_BASE) $(DEFINES_DEBUG)
  LINKFLAGS = $(LINKFLAGS_BASE) $(LINKFLAGS_DEBUG)
else
  CFLAGS = $(CFLAGS_BASE) $(CFLAGS_NORMAL)
  DEFINES = $(DEFINES_BASE)
  LINKFLAGS = $(LINKFLAGS_BASE)
endif

INCLUDES = -I $(SOURCE) -I $(OUTPUT)

SOURCES = $(wildcard $(SOURCE)/*.c)
HEADERS = $(wildcard $(SOURCE)/*.h)

LIBRARY_NAME = jansson

all : $(OUTPUT)\shared\$(LIBRARY_NAME).dll $(OUTPUT)\static\$(LIBRARY_NAME).lib

$(OUTPUT)\shared\$(LIBRARY_NAME).dll $(OUTPUT)\static\$(LIBRARY_NAME).lib: $(SOURCES) $(HEADERS)
	-mkdir $(OUTPUT)\shared 2>nul
	-mkdir $(OUTPUT)\static 2>nul
	-del $(LIBRARY_NAME).link 2>nul
	echo $(OUTPUT)\shared\$(LIBRARY_NAME).exp                                     >> $(LIBRARY_NAME).link
	echo "ucrt.lib" "vcruntime.lib" "kernel32.lib" "user32.lib" "gdi32.lib" "winspool.lib" "comdlg32.lib" "advapi32.lib" "shell32.lib" "ole32.lib" "oleaut32.lib" "uuid.lib" "odbc32.lib" "odbccp32.lib" >> $(LIBRARY_NAME).link
	$(CC) $(CFLAGS) $(DEFINES) $(INCLUDES) $(SOURCES)
	lib -nologo -machine:x64 -out:$(OUTPUT)\shared\$(LIBRARY_NAME).lib -def:$(SOURCE)\$(LIBRARY_NAME).def
	$(LD) $(LINKFLAGS) *.obj @$(LIBRARY_NAME).link -out:$(OUTPUT)\shared\$(LIBRARY_NAME).dll
	lib -nologo -machine:x64 -out:$(OUTPUT)\static\$(LIBRARY_NAME).lib *.obj

clean::
	-del /q $(OUTPUT)\* 2>nul
	-rd /s /q $(OUTPUT) 2>nul


