
CC = cl
LD = link

CFLAGS_BASE = /c /GS /W2 /Zc:wchar_t /sdl /Zc:inline /fp:precise /WX- /Zc:forScope /RTC1 /Gd /EHsc /nologo /wd4090
CFLAGS_NODEBUG = /MD
CFLAGS_DEBUG = /MDd /Gm /Zi /Od 

DEFINES_BASE = /D_MT /DbuildLabel=$(buildLabel) /D_CRT_SECURE_NO_WARNINGS /D_CRT_SECURE_NO_DEPRECATE /D_CRT_NONSTDC_NO_DEPRECATE /D_CRT_NON_CONFORMING_SWPRINTFS
DEFINES_DEBUG = /D_DEBUG

LINKFLAGS_BASE = /MANIFEST /NXCOMPAT /MACHINE:X64 /INCREMENTAL /SUBSYSTEM:CONSOLE /MANIFESTUAC:"level='asInvoker' uiAccess='false'" /NOLOGO /TLBID:1 /NODEFAULTLIB
LINKFLAGS_NODEBUG =
LINKFLAGS_DEBUG = /DEBUG 



ifeq ($(BUILD_TYPE),debug)
  DEFINES = $(DEFINES_BASE) $(DEFINES_DEBUG)
  CFLAGS = $(CFLAGS_BASE) $(CFLAGS_DEBUG)
  LINKFLAGS = $(LINKFLAGS_BASE) $(LINKFLAGS_DEBUG)
  CRTLIB=libcmtd.lib libvcruntimed.lib libucrtd.lib
else
  DEFINES = $(DEFINES_BASE)
  CFLAGS = $(CFLAGS_BASE) $(CFLAGS_NODEBUG)
  LINKFLAGS = $(LINKFLAGS_BASE) $(LINKFLAGS_NODEBUG)
  CRTLIB=msvcrt.lib vcruntime.lib ucrt.lib
endif


INCLUDES = -I $(SOURCE) -I $(subst /,\,../../source/main/src) -I $(subst /,\,../../dependencies/cunit/include)
SOURCES = $(wildcard $(SOURCE)/*.c)
HEADERS = $(wildcard $(SOURCE)/*.h) $(wildcard ../../dependencies/cunit/include/*.h)

NAME = janssontest

all : $(OUTPUT)/dist/$(PROGRAM)

$(OUTPUT)/dist/$(PROGRAM): $(SOURCES) $(HEADERS)
	-echo $(SOURCES)
	-del $(NAME).link $(NAME).def 1>nul 2>nul
	echo kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib  >> $(NAME).link
	echo shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib       >> $(NAME).link
	echo $(CRTLIB)                                                                 >> $(NAME).link
	echo $(wildcard ../../output/main/static/*.lib)                                >> $(NAME).link
	echo $(wildcard ../../dependencies/cunit/lib/static/*.lib)                     >> $(NAME).link
	$(CC) $(CFLAGS) $(DEFINES) $(INCLUDES) $(SOURCES)
	$(LD) $(LINKFLAGS) *.obj @$(NAME).link -out:$(NAME).exe

clean::
	-del *.exe *.obj *.pdb *.ilk *.link *.manifest *.exp *.lib *.txt 2>nul



