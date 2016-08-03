@echo off
setlocal

set ROOT=%USERPROFILE%\git\home\jansson
set SOURCE=%ROOT%\src\main\c
set OUTPUT=%ROOT%\target\output
set DIST=%ROOT%\target\dist
set BUILD_TYPE=standard
set buildLabel=93

if NOT exist %OUTPUT% mkdir %OUTPUT%
if NOT exist %DIST%   mkdir %DIST%

cd %OUTPUT%

echo on
make -f %SOURCE%\make\windows_amd64.makefile %*


