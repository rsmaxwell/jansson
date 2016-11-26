@echo off
setlocal


set REPOSITORY=snapshots
rem REPOSITORY=releases
set PACKAGING=zip
set GROUPID=com.rsmaxwell.jansson.2-9
set ARTIFACTID=jansson-2.9-x86_64-Windows-msvc
set VERSION=0.0.1-SNAPSHOT
rem VERSION=1


set URL=http://www.rsmaxwell.co.uk/nexus/service/local/repositories/%REPOSITORY%/content


@echo on
call mvn dependency:get -DgroupId=%GROUPID:.=/% -DartifactId=%ARTIFACTID% -Dversion=%VERSION% -Dpackaging=%PACKAGING% -DremoteRepositories=%URL%

dir %USERPROFILE%\.m2\repository
