
CC = cl
LD = link

CFLAGS_BASE = -c -W2 -Gs -nologo
CFLAGS_DEBUG = -Zi -Od
LINKFLAGS_BASE = -nod -nologo -dll
LINKFLAGS_DEBUG = -debug
DEFINES_BASE = -DbuildLabel=$(buildLabel) -D_MT -D_DLL -D_CRT_SECURE_NO_WARNINGS -D_CRT_SECURE_NO_DEPRECATE -D_CRT_NONSTDC_NO_DEPRECATE -D_CRT_NON_CONFORMING_SWPRINTFS -DHAVE_CONFIG_H
DEFINES_DEBUG =

ifeq ($(BUILD_TYPE),debug)
  CFLAGS = $(CFLAGS_BASE) $(CFLAGS_DEBUG)
  LINKFLAGS = $(LINKFLAGS_BASE) $(LINKFLAGS_DEBUG)
  DEFINES = $(DEFINES_BASE) $(DEFINES_DEBUG)
else
  CFLAGS = $(CFLAGS_BASE)
  LINKFLAGS = $(LINKFLAGS_BASE)
  DEFINES = $(DEFINES_BASE)
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
	echo msvcrt.lib oldnames.lib kernel32.lib user32.lib advapi32.lib dbghelp.lib >> $(LIBRARY_NAME).link
	$(CC) $(CFLAGS) $(DEFINES) $(INCLUDES) $(SOURCES)
	lib -nologo -machine:x64 -out:$(OUTPUT)\shared\$(LIBRARY_NAME).lib -def:$(SOURCE)\$(LIBRARY_NAME).def
	$(LD) $(LINKFLAGS) *.obj @$(LIBRARY_NAME).link -out:$(OUTPUT)\shared\$(LIBRARY_NAME).dll
	lib -nologo -machine:x64 -out:$(OUTPUT)\static\$(LIBRARY_NAME).lib *.obj

clean::
	-del /q $(OUTPUT)\* 2>nul
	-rd /s /q $(OUTPUT) 2>nul

