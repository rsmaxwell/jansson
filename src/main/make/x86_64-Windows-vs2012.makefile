
CC = cl
LD = link

CFLAGS_BASE = /c /W2 /nologo /wd4090
CFLAGS_DEBUG = /Zi /Od

DEFINES_BASE = /DHAVE_CONFIG_H /D_CRT_SECURE_NO_WARNINGS /D_CRT_SECURE_NO_DEPRECATE /D_CRT_NONSTDC_NO_DEPRECATE /D_CRT_NON_CONFORMING_SWPRINTFS
DEFINES_DEBUG =

LINKFLAGS_BASE = /NODEFAULTLIB /NOLOGO /DLL
LINKFLAGS_DEBUG = /DEBUG 

ifeq ($(BUILD_TYPE),static)
  DEFINES   = $(DEFINES_BASE)
  CFLAGS    = $(CFLAGS_BASE) /MT
  LINKFLAGS = $(LINKFLAGS_BASE)
  CRTLIB    = libcmt.lib

else ifeq ($(BUILD_TYPE),static_debug)
  DEFINES   = $(DEFINES_BASE) $(DEFINES_DEBUG)
  CFLAGS    = $(CFLAGS_BASE) $(CFLAGS_DEBUG) /MTd
  LINKFLAGS = $(LINKFLAGS_BASE) $(LINKFLAGS_DEBUG)
  CRTLIB    = libcmtd.lib

else ifeq ($(BUILD_TYPE),dynamic)
  DEFINES   = $(DEFINES_BASE)
  CFLAGS    = $(CFLAGS_BASE) /MD
  LINKFLAGS = $(LINKFLAGS_BASE)
  CRTLIB    = msvcrt.lib

else ifeq ($(BUILD_TYPE),dynamic_debug)
  DEFINES   = $(DEFINES_BASE) $(DEFINES_DEBUG)
  CFLAGS    = $(CFLAGS_BASE) $(CFLAGS_DEBUG) /MDd
  LINKFLAGS = $(LINKFLAGS_BASE) $(LINKFLAGS_DEBUG)
  CRTLIB    = msvcrtd.lib

else 
  $(error BUILD_TYPE=$(BUILD_TYPE) is not supported)
endif


INCLUDES = -I $(SOURCE) -I $(subst /,\,$(DIST)/include) -I $(subst /,\,$(INSTALL)/include)
SOURCES = $(wildcard $(SOURCE)/*.c)
HEADERS = $(wildcard $(SOURCE)/*.h)

NAME = jansson

all : shared\$(NAME).dll static\$(NAME).lib

shared\$(NAME).dll static\$(NAME).lib: $(SOURCES) $(HEADERS)
	@echo SOURCES = $(SOURCES)
	@echo HEADERS = $(HEADERS)
	@echo INSTALL = $(INSTALL)
	@echo BUILD_TYPE = $(BUILD_TYPE)
	@echo pwd = ${CURDIR}
	-mkdir shared 2>nul
	-mkdir static 2>nul
	-del $(NAME).link $(NAME).def 1>nul 2>nul
	echo shared\$(NAME).exp                                                        >> $(NAME).link
	echo oldnames.lib kernel32.lib user32.lib advapi32.lib dbghelp.lib             >> $(NAME).link
	echo $(CRTLIB)                                                                 >> $(NAME).link
	echo $(wildcard $(INSTALL)lib/static/*.lib)                                    >> $(NAME).link
	$(CC) $(CFLAGS) $(DEFINES) $(INCLUDES) $(SOURCES)
	lib -nologo -machine:x64 -out:shared\$(NAME).lib -def:$(SOURCE)\$(NAME).def
	$(LD) $(LINKFLAGS) *.obj @$(NAME).link -out:shared\$(NAME).dll
	lib -nologo -machine:x64 -out:static\$(NAME).lib *.obj

clean::
	-del /q * 2>nul
	-rd /q /s shared 2>nul
	-rd /q /s static 2>nul

