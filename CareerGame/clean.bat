@echo off
chcp 65001 >nul
cd /d "%~dp0"
if exist game\cache rd /s /q game\cache
del /q game\*.rpyc 2>nul
echo.
echo Cache and .rpyc files deleted.
echo.
pause