@echo off
setlocal

set ROOT=%USERPROFILE%\git\home\jansson
set SOURCE=%ROOT%\src\main\c
set OUTPUT=%ROOT%\target\output
set DIST=%ROOT%\target\dist
set BUILD_TYPE=debug
set buildLabel=93

set TEST_SOURCE=%ROOT%\src\test\c
set TARGET_TEST=%ROOT%\target\test
set TEST_OUTPUT=%TARGET_TEST%\output
set TEST_RUN=%TARGET_TEST%\run

if NOT exist %TEST_OUTPUT% mkdir %TEST_OUTPUT%

cd %TEST_OUTPUT%

echo on
make -f %TEST_SOURCE%\make\windows_amd64.makefile %*
@echo off

cd %TEST_RUN%


echo JSON_INDENT=4               >  env
echo JSON_COMPACT=0              >> env
echo JSON_INDENT=4               >> env
echo JSON_COMPACT=0              >> env
echo JSON_ENSURE_ASCII=0         >> env
echo JSON_PRESERVE_ORDER=0       >> env
echo JSON_SORT_KEYS=1            >> env
echo JSON_REAL_PRECISION=0       >> env
echo HASHSEED=12345              >> env
echo STRIP=1                     >> env

echo { "id": 1, "name": "fred" } > input

echo on
test-jansson .
@echo off

echo %ERRORLEVEL%


