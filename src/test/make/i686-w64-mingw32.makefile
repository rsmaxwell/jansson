
CC = gcc

CFLAGS_BASE = -m64 -Wall -fPIC 
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

INCLUDES = -I $(subst /,\,$(SOURCE_DIR)) \
           -I $(subst /,\,$(BUILD_DIR)/dependances/CUnit/headers/CUnit) \
           -I $(subst /,\,$(BUILD_DIR)/dependances/jansson/headers)

SOURCES = $(wildcard $(SOURCE_DIR)/*.c)

HEADERS = $(subst /,\,$(wildcard $(SOURCE_DIR)/*.h)) \
          $(subst /,\,$(wildcard $(BUILD_DIR)/dependances/CUnit/headers/CUnit/*.h)) \
          $(subst /,\,$(wildcard $(BUILD_DIR)/dependances/jansson/headers/jansson/*.h))

PROGRAM = janssontest

all : $(PROGRAM)

$(PROGRAM): $(SOURCES)  $(HEADERS)
	@echo "BUILD_TYPE = $(BUILD_TYPE)"
	@echo "SOURCE_DIR = $(SOURCE_DIR)"
	@echo "BUILD_DIR = $(BUILD_DIR)"
	$(CC) $(CFLAGS) $(DEFINES) -D_REENTRANT $(INCLUDES) $(LINKFLAGS) -o $(PROGRAM) $(SOURCES)

clean::
	-@rm $(PROGRAM)
