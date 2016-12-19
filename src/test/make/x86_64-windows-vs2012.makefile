
CC = cl
LD = link

CFLAGS_BASE = -c -GS -W2 -Zc:wchar_t -sdl -Zc:inline -fp:precise -WX- -Zc:forScope -RTC1 -Gd -EHsc -nologo -wd4090
CFLAGS_NORMAL = -MD
CFLAGS_DEBUG = -MDd -Gm -Zi -Od

DEFINES_BASE = -D_MT -DbuildLabel=$(buildLabel) -D_CRT_SECURE_NO_WARNINGS -D_CRT_SECURE_NO_DEPRECATE -D_CRT_NONSTDC_NO_DEPRECATE -D_CRT_NON_CONFORMING_SWPRINTFS
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

INCLUDES = -I $(SOURCE) -I $(subst /,\,../dependencies/cunit/include) -I $(subst /,\,../dependencies/jansson/include)
SOURCES = $(wildcard $(SOURCE)/*.c)
HEADERS = $(wildcard $(SOURCE)/*.h) $(wildcard ../dependencies/cunit/include/*.h)  $(wildcard ../dependencies/jansson/include/*.h)

NAME = janssontest

all : $(OUTPUT)/$(NAME).exe

$(OUTPUT)/$(NAME).exe: $(SOURCES) $(HEADERS)
	del $(NAME).link $(NAME).def 1>nul 2>nul
	echo ucrt.lib oldnames.lib kernel32.lib user32.lib advapi32.lib dbghelp.lib >> $(NAME).link
	echo $(wildcard ../dependencies/cunit/lib/static/*.lib)                     >> $(NAME).link
	echo $(wildcard ../dependencies/jansson/lib/static/*.lib)                   >> $(NAME).link
	$(CC) $(CFLAGS) $(DEFINES) $(INCLUDES) $(SOURCES)
	$(LD) $(LINKFLAGS) *.obj @$(NAME).link -out:$(NAME).exe
	mkdir $(subst /,\,../dist/bin)
	copy $(NAME).exe $(subst /,\,../dist/bin)

clean::
	-del /q $(OUTPUT)\* 2>nul

