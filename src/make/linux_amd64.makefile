#
# Name:          linux_amd64.makefile
#
# Description: Linux makefile for the Quotas ApiExit 
#
# <N_OCO_COPYRIGHT> 
# Licensed Materials - Property of IBM 
# 04L1830, 5639-B43
# (C) Copyright IBM Corp. 2010,2015
#
# US Government Users Restricted Rights - Use, duplication or       
# disclosure restricted by GSA ADP Schedule Contract with   
# IBM Corp.    
# <NOC_COPYRIGHT>
#

CC = gcc

MQM_INC = $(MQ_INST_DIR)/inc
MQM_LIB = $(MQ_INST_DIR)/lib64
MQM_EXITS = $(MQ_DATA_DIR)/exits64

CFLAGS_BASE = -m64 -Wall -fPIC 
CFLAGS_DEBUG = -g -rdynamic
LINKFLAGS_BASE = -shared -Wl,-rpath=$(MQM_EXITS)
LINKFLAGS_DEBUG =
DEFINES_BASE = -DbuildLabel=$(buildLabel) -DMQ_LIB_DIR=lib64 -DHAVE_CONFIG_H
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

INCLUDES = -I $(SOURCE_DIR) -I $(UTILS_DIR) -I $(UTILS_DIR)/linux_amd64 -I $(JANSSON_DIR)/linux_amd64 -I $(JANSSON_DIR) -I $(MQM_INC)

SOURCES = $(SOURCE_DIR)/QuotasExit.c \
          $(UTILS_DIR)/MqHelper.c $(UTILS_DIR)/Logger.c $(UTILS_DIR)/Utils.c $(UTILS_DIR)/CommonServices.c $(UTILS_DIR)/Account.c $(UTILS_DIR)/Users.c \
          $(UTILS_DIR)/FileLock.c $(UTILS_DIR)/JsonUtils.c $(UTILS_DIR)/Exception.c $(UTILS_DIR)/linux_amd64/Exception2.c $(wildcard $(JANSSON_DIR)/*.c)

HEADERS = $(UTILS_DIR)/MqHelper.h $(UTILS_DIR)/Logger.h $(UTILS_DIR)/Utils.h $(UTILS_DIR)/CommonServices.h $(UTILS_DIR)/Account.h $(UTILS_DIR)/Users.h \
          $(UTILS_DIR)/FileLock.h $(UTILS_DIR)/JsonUtils.h $(UTILS_DIR)/Exception.h $(UTILS_DIR)/linux_amd64/Exception2.h \
          $(JANSSON_DIR)/linux_amd64/jansson_config.h $(wildcard $(JANSSON_DIR)/*.h)

LIBRARY_NAME = QuotasExit
LIBRARY = $(LIBRARY_NAME)
LIBRARY_THREADED = $(LIBRARY_NAME)_r

all : $(LIBRARY) $(LIBRARY_THREADED)

$(LIBRARY_THREADED): $(SOURCES)  $(HEADERS)
	$(CC) $(CFLAGS) $(DEFINES) -D_REENTRANT $(INCLUDES) $(LINKFLAGS) -o $(LIBRARY_THREADED) $(SOURCES) -lmqutl_r
	cp $(LIBRARY_THREADED) $(DIST_DIR)
	cp $(LIBRARY_THREADED) $(MQM_EXITS)

$(LIBRARY): $(SOURCES) $(HEADERS)
	$(CC) $(CFLAGS) $(DEFINES) $(INCLUDES) $(LINKFLAGS) -o $(LIBRARY) $(SOURCES) -lmqutl
	cp $(LIBRARY) $(DIST_DIR)
	cp $(LIBRARY) $(MQM_EXITS)

clean::
	-@rm $(LIBRARY) $(LIBRARY_THREADED)
