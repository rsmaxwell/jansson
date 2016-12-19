
CC = cl
LD = link


CFLAGS_BASE = -c -GS -W2 -Zc:wchar_t -sdl -Zc:inline -fp:precise -WX- -Zc:forScope -RTC1 -Gd -EHsc -nologo -wd4090
CFLAGS_NORMAL = -MD
CFLAGS_DEBUG = -MDd -Gm -Zi -Od

DEFINES_BASE = -D_MT -D_DLL -DbuildLabel=$(buildLabel) -D_CRT_SECURE_NO_WARNINGS -D_CRT_SECURE_NO_DEPRECATE -D_CRT_NONSTDC_NO_DEPRECATE -D_CRT_NON_CONFORMING_SWPRINTFS -DHAVE_CONFIG_H
DEFINES_DEBUG = -D_DEBUG

LINKFLAGS_BASE = /MACHINE:X64 /SUBSYSTEM:CONSOLE /NOLOGO
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

NAME = jansson

all : $(OUTPUT)\shared\$(NAME).dll $(OUTPUT)\static\$(NAME).lib

$(OUTPUT)\shared\$(NAME).dll $(OUTPUT)\static\$(NAME).lib: $(SOURCES) $(HEADERS)
	-mkdir $(OUTPUT)\shared 2>nul
	-mkdir $(OUTPUT)\static 2>nul
	-del $(NAME).link 2>nul
	echo $(OUTPUT)\shared\$(NAME).exp                                             >> $(NAME).link
	echo msvcrt.lib oldnames.lib kernel32.lib user32.lib advapi32.lib dbghelp.lib >> $(NAME).link
	$(CC) $(CFLAGS) $(DEFINES) $(INCLUDES) $(SOURCES)
	lib -nologo -machine:x64 -out:$(OUTPUT)\shared\$(NAME).lib -def:$(SOURCE)\$(NAME).def
	$(LD) $(LINKFLAGS) *.obj @$(NAME).link -out:$(OUTPUT)\shared\$(NAME).dll
	lib -nologo -machine:x64 -out:$(OUTPUT)\static\$(NAME).lib *.obj

clean::
	-del /q $(OUTPUT)\* 2>nul


