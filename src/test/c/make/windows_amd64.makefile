
CC = cl
LD = link

CFLAGS_BASE = -c -W2 -Gs -nologo
CFLAGS_DEBUG = -Zi -Od 
LINKFLAGS_BASE = -nod -nologo
LINKFLAGS_DEBUG = -debug
DEFINES_BASE = -DbuildLabel=$(buildLabel) -D_MT -D_CRT_SECURE_NO_WARNINGS -D_CRT_SECURE_NO_DEPRECATE -D_CRT_NONSTDC_NO_DEPRECATE -D_CRT_NON_CONFORMING_SWPRINTFS -DHAVE_CONFIG_H
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

INCLUDES = -I $(TEST_SOURCE) -I $(TEST_OUTPUT) -I $(SOURCE) -I $(OUTPUT)

SOURCES = $(wildcard $(TEST_SOURCE)/*.c)
HEADERS = $(wildcard $(TEST_SOURCE)/*.h) $(SOURCE)/jansson.h $(OUTPUT)/jansson_config.h $(OUTPUT)/jansson_private_config.h

PROGRAM_NAME = test-jansson
PROGRAM = $(PROGRAM_NAME).exe

LIBRARY_NAME = jansson
LIBRARY = $(LIBRARY_NAME).dll

all : $(TEST_OUTPUT)/$(PROGRAM)

$(TEST_OUTPUT)/$(PROGRAM): $(SOURCES) $(HEADERS)
	del $(LIBRARY_NAME).link
	echo msvcrt.lib oldnames.lib kernel32.lib user32.lib advapi32.lib dbghelp.lib >> $(PROGRAM_NAME).link
	echo $(DIST)/$(LIBRARY_NAME).lib                                                 >> $(PROGRAM_NAME).link	
	$(CC) $(CFLAGS) $(DEFINES) $(INCLUDES) $(SOURCES)
	lib -nologo -machine:x64 -out:$(LIBRARY_NAME).lib 
	$(LD) $(LINKFLAGS) *.obj @$(PROGRAM_NAME).link -out:$(TEST_OUTPUT)\$(PROGRAM)

clean::
	-del /q $(TEST_OUTPUT)\*


