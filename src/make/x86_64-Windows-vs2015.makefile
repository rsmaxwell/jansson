
CC = cl
LD = link

CFLAGS_BASE = /c /GS /W2 /Zc:wchar_t /sdl /Zc:inline /fp:precise /WX- /Zc:forScope /RTC1 /Gd /EHsc /nologo /wd4090
CFLAGS_NODEBUG = /MD
CFLAGS_DEBUG = /MDd /Gm /Zi /Od 

DEFINES_BASE = /D_MT /DbuildLabel=$(buildLabel) /D_CRT_SECURE_NO_WARNINGS /D_CRT_SECURE_NO_DEPRECATE /D_CRT_NONSTDC_NO_DEPRECATE /D_CRT_NON_CONFORMING_SWPRINTFS
DEFINES_DEBUG = /D_DEBUG

LINKFLAGS_BASE = /MANIFEST /NXCOMPAT /MACHINE:X64 /INCREMENTAL /SUBSYSTEM:CONSOLE /MANIFESTUAC:"level='asInvoker' uiAccess='false'" /NOLOGO /TLBID:1 
LINKFLAGS_NODEBUG =
LINKFLAGS_DEBUG = /DEBUG 



ifeq ($(BUILD_TYPE),debug)
  DEFINES = $(DEFINES_BASE) $(DEFINES_DEBUG)
  CFLAGS = $(CFLAGS_BASE) $(CFLAGS_DEBUG)
  LINKFLAGS = $(LINKFLAGS_BASE) $(LINKFLAGS_DEBUG)
else
  DEFINES = $(DEFINES_BASE)
  CFLAGS = $(CFLAGS_BASE) $(CFLAGS_NODEBUG)
  LINKFLAGS = $(LINKFLAGS_BASE) $(LINKFLAGS_NODEBUG)
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
	echo $(OUTPUT)\shared\$(LIBRARY_NAME).exp                                                           >> $(LIBRARY_NAME).link
	echo "vcruntime.lib" "kernel32.lib" "user32.lib" "gdi32.lib" "winspool.lib" "comdlg32.lib"          >> $(LIBRARY_NAME).link
	echo "advapi32.lib" "shell32.lib" "ole32.lib" "oleaut32.lib" "uuid.lib" "odbc32.lib" "odbccp32.lib" >> $(LIBRARY_NAME).link
	$(CC) $(CFLAGS) $(DEFINES) $(INCLUDES) $(SOURCES)
	lib -nologo -machine:x64 -out:$(OUTPUT)\shared\$(LIBRARY_NAME).lib -def:$(SOURCE)\$(LIBRARY_NAME).def
	$(LD) $(LINKFLAGS) *.obj @$(LIBRARY_NAME).link -out:$(OUTPUT)\shared\$(LIBRARY_NAME).dll
	lib -nologo -machine:x64 -out:$(OUTPUT)\static\$(LIBRARY_NAME).lib *.obj

clean::
	-del *.exe *.obj *.pdb *.ilk *.link

