
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
  LINKFLAGS = $(LINKFLAGS_BASE) $(LINKFLAGS_DEBUG)
  DEFINES = $(DEFINES_BASE) $(DEFINES_DEBUG)
else
  CFLAGS = $(CFLAGS_BASE)
  LINKFLAGS = $(LINKFLAGS_BASE)
  DEFINES = $(DEFINES_BASE)
endif

INCLUDES = -I $(SOURCE_DIR) -I $(subst /,\,../dependencies/cunit/include) -I $(subst /,\,../dependencies/jansson/include)

SOURCES = $(wildcard $(SOURCE_DIR)/*.c)

HEADERS = $(wildcard $(SOURCE_DIR)/*.h) $(wildcard ../dependencies/cunit/include/*.h)  $(wildcard ../dependencies/jansson/include/*.h)

PROGRAM_NAME = jansson-test
PROGRAM = $(PROGRAM_NAME).exe

all : $(BUILD_DIR)/dist/$(PROGRAM)

$(BUILD_DIR)/dist/$(PROGRAM): $(SOURCES) $(HEADERS)	
	echo $(INCLUDES)
	echo $(SOURCE_DIR)/*.c
	del $(PROGRAM_NAME).link $(PROGRAM_NAME).def 1>nul 2>nul
	echo ucrt.lib oldnames.lib kernel32.lib user32.lib advapi32.lib dbghelp.lib >> $(PROGRAM_NAME).link
	echo $(wildcard ../dependencies/cunit/lib/static/*.lib) >> $(PROGRAM_NAME).link
	echo $(wildcard ../dependencies/jansson/lib/static/*.lib) >> $(PROGRAM_NAME).link
	$(CC) $(CFLAGS) $(DEFINES) $(INCLUDES) $(SOURCES)
	$(LD) $(LINKFLAGS) *.obj @$(PROGRAM_NAME).link -out:$(PROGRAM)
	mkdir $(subst /,\,../dist/bin)
	copy $(PROGRAM) $(subst /,\,../dist/bin)

clean::
	-del *.exe *.obj *.pdb *.ilk *.link

