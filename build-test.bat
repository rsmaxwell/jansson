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

if NOT exist %TEST_OUTPUT% mkdir %TEST_OUTPUT%

cd %TEST_OUTPUT%

echo on
make -f %TEST_SOURCE%\make\windows_amd64.makefile %*



