
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
HEADERS = $(wildcard $(SOURCE)/*.h) $(OUTPUT)/jansson_config.h $(OUTPUT)/jansson_private_config.h

LIBRARY_NAME = jansson
LIBRARY = $(LIBRARY_NAME).dll

all : $(DIST)/$(LIBRARY)

$(OUTPUT)/jansson_private_config.h : $(SOURCE)/make/windows_amd64.makefile
	echo /* Generated file */  > $(OUTPUT)\jansson_private_config.h
	echo #include ^<stdint.h^> >> $(OUTPUT)\jansson_private_config.h

$(OUTPUT)/jansson_config.h : $(SOURCE)/jansson_config.h.in $(SOURCE)/make/windows_amd64.makefile
	copy $(SOURCE)\jansson_config.h.in  $(OUTPUT)\jansson_config.h
	sed -i 's/@json_inline@/__inline/g'      $(OUTPUT)/jansson_config.h
	sed -i 's/@json_have_long_long@/1/g'     $(OUTPUT)/jansson_config.h
	sed -i 's/@json_have_localeconv@/1/g'    $(OUTPUT)/jansson_config.h

$(DIST)/$(LIBRARY): $(SOURCES) $(HEADERS)
	del $(LIBRARY_NAME).link
	echo $(DIST)\$(LIBRARY_NAME).exp                                              >> $(LIBRARY_NAME).link
	echo msvcrt.lib oldnames.lib kernel32.lib user32.lib advapi32.lib dbghelp.lib >> $(LIBRARY_NAME).link	
	$(CC) $(CFLAGS) $(DEFINES) $(INCLUDES) $(SOURCES)
	lib -nologo -machine:x64 -out:$(DIST)\$(LIBRARY_NAME).lib -def:$(SOURCE)\$(LIBRARY_NAME).def
	$(LD) $(LINKFLAGS) *.obj @$(LIBRARY_NAME).link -out:$(DIST)\$(LIBRARY)

clean::
	-del /q $(OUTPUT)\*
	-rd /s /q $(DIST)

