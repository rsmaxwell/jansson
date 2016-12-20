
CC = cl
LD = link

CFLAGS_BASE = /c /W2 /nologo
CFLAGS_NORMAL = /MT
CFLAGS_DEBUG = /MTd /Zi /Od

DEFINES_BASE = /D_CRT_SECURE_NO_WARNINGS /D_CRT_SECURE_NO_DEPRECATE /D_CRT_NONSTDC_NO_DEPRECATE /D_CRT_NON_CONFORMING_SWPRINTFS
DEFINES_DEBUG =

LINKFLAGS_BASE = /NODEFAULTLIB /NOLOGO
LINKFLAGS_DEBUG = /DEBUG 


ifeq ($(BUILD_TYPE),debug)
  DEFINES = $(DEFINES_BASE) $(DEFINES_DEBUG)
  CFLAGS = $(CFLAGS_BASE) $(CFLAGS_DEBUG)
  LINKFLAGS = $(LINKFLAGS_BASE) $(LINKFLAGS_DEBUG)
  CRTLIB=msvcrtd.lib
else
  DEFINES = $(DEFINES_BASE)
  CFLAGS = $(CFLAGS_BASE) $(CFLAGS_NORMAL)
  LINKFLAGS = $(LINKFLAGS_BASE)
  CRTLIB=msvcrt.lib
endif


INCLUDES = -I $(SOURCE) -I $(subst /,\,../../dist/include) -I $(subst /,\,../../dependencies/cunit/include)
SOURCES = $(wildcard $(SOURCE)/*.c)
HEADERS = $(wildcard $(SOURCE)/*.h) $(wildcard ../../dependencies/cunit/include/*.h)

NAME = janssontest

all : $(NAME)

$(NAME): $(SOURCES) $(HEADERS)
	-del $(NAME).link $(NAME).def 1>nul 2>nul
	echo kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib  >> $(NAME).link
	echo shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib       >> $(NAME).link
	echo $(CRTLIB)                                                                 >> $(NAME).link
	echo $(wildcard ../../dist/lib/static/*.lib)                                   >> $(NAME).link
	echo $(wildcard ../../dependencies/cunit/lib/static/*.lib)                     >> $(NAME).link
	$(CC) $(CFLAGS) $(DEFINES) $(INCLUDES) $(SOURCES)
	$(LD) $(LINKFLAGS) *.obj @$(NAME).link -out:$(NAME).exe

clean::
	-del /q $(OUTPUT)\* 2>nul


