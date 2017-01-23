
CC = gcc

CFLAGS_BASE = -m64 -Wall -Wno-format-zero-length -Wno-pointer-sign -Wno-unused-variable
CFLAGS_DEBUG = -g -rdynamic
LINKFLAGS_BASE = -shared 
LINKFLAGS_DEBUG =
DEFINES_BASE = -DbuildLabel=$(buildLabel) 
DEFINES_DEBUG = -DCLOUD_DEBUG

ifeq ($(BUILD_TYPE),debug)
  CFLAGS = $(CFLAGS_BASE) $(CFLAGS_DEBUG)
  LINKFLAGS = $(LINKFLAGS_BASE) $(LINKFLAGS_DEBUG)
  DEFINES = $(DEFINES_BASE) $(DEFINES_DEBUG)
else
  CFLAGS = $(CFLAGS_BASE)
  LINKFLAGS = $(LINKFLAGS_BASE)
  DEFINES = $(DEFINES_BASE)
endif   

INCLUDES = -I $(SOURCE) -I $(DIST)/include -I $(INSTALL)include

SOURCES = $(wildcard $(SOURCE)/*.c)

HEADERS = $(wildcard $(SOURCE)/*.h) 


NAME = janssontest

all : $(NAME)

$(NAME): $(SOURCES) $(HEADERS)
	@echo BUILD_TYPE = $(BUILD_TYPE)
	@echo SOURCE = $(SOURCE)
	@echo DIST = $(DIST)
	@echo INSTALL = $(INSTALL)
	@echo INCLUDES = $(INCLUDES)
	@echo SOURCES = $(SOURCES)
	@echo HEADERS = $(HEADERS)
	@echo pwd = ${CURDIR}
	$(CC) $(CFLAGS) $(DEFINES) -D_REENTRANT $(INCLUDES) $(LINKFLAGS) -o $(NAME) $(SOURCES)

clean::
	-@rm $(NAME) 1>/dev/null 2>&1
