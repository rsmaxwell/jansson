@echo off
setlocal


set URL=http://www.rsmaxwell.co.uk/nexus/service/local/metadata/repositories/snapshots/content/com/rsmaxwell/jannson/2-9/x86_64-Windows-msvc/

@echo on

curl -v --request DELETE  --user "%MAXWELLHOUSE_ADMIN_USER%:%MAXWELLHOUSE_ADMIN_PASS%"  %URL%
