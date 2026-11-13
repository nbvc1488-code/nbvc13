@echo off
setlocal
pushd "%~dp0" || exit /b 1
if exist "game\options.rpy" (
    if exist "game\cache\" rd /s /q "game\cache"
    if exist "game\*.rpyc" del /q "game\*.rpyc"
) else (
    echo CareerGame source directory not found.
    popd
    exit /b 1
)
if exist "game\cache\" goto failed
if exist "game\*.rpyc" goto failed
echo RenPy cache and compiled top-level scripts cleared.
popd
exit /b 0

:failed
echo Could not clear RenPy generated files.
popd
exit /b 1
