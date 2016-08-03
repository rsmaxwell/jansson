@echo off
setlocal

set ROOT=%USERPROFILE%\git\home\jansson
set SOURCE=%ROOT%\src\main\c
set OUTPUT=%ROOT%\target\output
set DIST=%ROOT%\target\dist
set BUILD_TYPE=standard
set buildLabel=93

set TEST_SOURCE=%ROOT%\src\test\c
set TEST_RESOURCES=%ROOT%\src\test\resources

set TARGET_TEST=%ROOT%\target\test
set TEST_OUTPUT=%TARGET_TEST%\output
set TEST_RUN=%TARGET_TEST%\run




if NOT exist %TEST_RUN% mkdir %TEST_RUN%

cd %TEST_RUN%
copy %DIST%\*.dll >nul
copy %TEST_OUTPUT%\*.exe >nul
copy %TEST_RESOURCES%\* >nul

set PROGRAM=devenv /debugexe %TEST_RUN%\test-jansson.exe --strip .
set PROGRAM=test-jansson --strip .

echo on
%PROGRAM% --strip .
@echo off
if errorlevel 1 (
   echo ExitCode is %errorlevel%
   exit /b %errorlevel%
)



