
CC = gcc

CFLAGS_BASE = -m32 -Wall -Wno-format-zero-length -Wno-pointer-sign -Wno-unused-variable
CFLAGS_DEBUG = -g

DEFINES_BASE = -DbuildLabel=$(buildLabel) 
DEFINES_DEBUG =

LINKFLAGS_BASE = -v -L/usr/local/lib -L$(DIST)
LINKFLAGS_DEBUG =

ifeq ($(BUILD_TYPE),static)
  DEFINES   = $(DEFINES_BASE)
  CFLAGS    = $(CFLAGS_BASE)
  LINKFLAGS = $(LINKFLAGS_BASE) -Wl,-Bstatic -lcunit -ljansson

else ifeq ($(BUILD_TYPE),static_debug)
  DEFINES   = $(DEFINES_BASE) $(DEFINES_DEBUG)
  CFLAGS    = $(CFLAGS_BASE) $(CFLAGS_DEBUG)
  LINKFLAGS = $(LINKFLAGS_BASE) $(LINKFLAGS_DEBUG) -Wl,-Bstatic -lcunitd -ljansson

else ifeq ($(BUILD_TYPE),dynamic)
  DEFINES   = $(DEFINES_BASE)
  CFLAGS    = $(CFLAGS_BASE)
  LINKFLAGS = $(LINKFLAGS_BASE) -Wl,-Bstatic -lcunit -ljansson

else ifeq ($(BUILD_TYPE),dynamic_debug)
  DEFINES   = $(DEFINES_BASE) $(DEFINES_DEBUG)
  CFLAGS    = $(CFLAGS_BASE) $(CFLAGS_DEBUG)
  LINKFLAGS = $(LINKFLAGS_BASE) $(LINKFLAGS_DEBUG) -Wl,-Bstatic -lcunitd -ljansson

else 
  $(error BUILD_TYPE=$(BUILD_TYPE) is not supported)
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
	$(CC) $(CFLAGS) $(DEFINES) $(INCLUDES) $(LINKFLAGS) -o $(NAME) $(SOURCES)

clean::
	-@rm $(NAME) 1>/dev/null 2>&1
