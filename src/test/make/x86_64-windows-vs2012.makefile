
CC = cl
LD = link

CFLAGS_BASE = /c /W2 /nologo

DEFINES_BASE = /D_CRT_SECURE_NO_WARNINGS /D_CRT_SECURE_NO_DEPRECATE /D_CRT_NONSTDC_NO_DEPRECATE /D_CRT_NON_CONFORMING_SWPRINTFS
DEFINES_DEBUG =

LINKFLAGS_BASE = /NODEFAULTLIB /NOLOGO
LINKFLAGS_DEBUG = /DEBUG 

ifeq ($(BUILD_TYPE),static)
  DEFINES   = $(DEFINES_BASE)
  CFLAGS    = $(CFLAGS_BASE) /MT
  LINKFLAGS = $(LINKFLAGS_BASE)
  CRTLIB    = libcmt.lib
  CUNITLIB  = static/libcunit_exe.lib

else ifeq ($(BUILD_TYPE),static_debug)
  DEFINES   = $(DEFINES_BASE) $(DEFINES_DEBUG)
  CFLAGS    = $(CFLAGS_BASE) /MTd /Zi /Od
  LINKFLAGS = $(LINKFLAGS_BASE) $(LINKFLAGS_DEBUG)
  CRTLIB    = libcmtd.lib
  CUNITLIB  = static/libcunitd_exe.lib

else ifeq ($(BUILD_TYPE),dynamic)
  DEFINES   = $(DEFINES_BASE)
  CFLAGS    = $(CFLAGS_BASE) /MD
  LINKFLAGS = $(LINKFLAGS_BASE)
  CRTLIB    = msvcrt.lib
  CUNITLIB  = shared/libcunit.lib

else ifeq ($(BUILD_TYPE),dynamic_debug)
  DEFINES   = $(DEFINES_BASE) $(DEFINES_DEBUG)
  CFLAGS    = $(CFLAGS_BASE) /MDd /Zi /Od
  LINKFLAGS = $(LINKFLAGS_BASE) $(LINKFLAGS_DEBUG)
  CRTLIB    = msvcrtd.lib
  CUNITLIB  = shared/libcunitd.lib

else 
  $(error BUILD_TYPE=$(BUILD_TYPE) is not supported)
endif


INCLUDES = -I $(SOURCE) -I $(subst /,\,../../dist/include) -I $(subst /,\,$(INSTALL)include)
SOURCES = $(wildcard $(SOURCE)/*.c)
HEADERS = $(wildcard $(SOURCE)/*.h) $(wildcard $(INSTALL)include/*.h)

NAME = janssontest

all : $(NAME).exe

$(NAME).exe: $(SOURCES) $(HEADERS)
	@echo SOURCE = $(SOURCE)
	@echo INSTALL = $(INSTALL)
	@echo BUILD_TYPE = $(BUILD_TYPE)
	@echo INCLUDES = $(INCLUDES)
	@echo SOURCES = $(SOURCES)
	@echo HEADERS = $(HEADERS)
	@echo pwd = ${CURDIR}
	-del $(NAME).link $(NAME).def 1>nul 2>nul
	echo kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib  >> $(NAME).link
	echo shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib       >> $(NAME).link
	echo $(CRTLIB)                                                                 >> $(NAME).link
	echo $(wildcard ../../dist/lib/static/*.lib)                                   >> $(NAME).link
	echo $(wildcard $(INSTALL)lib/static/*_exe.lib)                                >> $(NAME).link
	$(CC) $(CFLAGS) $(DEFINES) $(INCLUDES) $(SOURCES)
	$(LD) $(LINKFLAGS) *.obj @$(NAME).link -out:$(NAME).exe

clean::
	-del /q * 2>nul


