@echo off
setlocal
cd /d "%~dp0"
set PORT=51467

:: 1. Check if server is already running on port 51467
netstat -ano | findstr ":%PORT%" >nul 2>&1
if not errorlevel 1 goto OPEN_HTTP

:: 2. Find Python executable
set "PY_CMD="
where python >nul 2>&1 && set "PY_CMD=python"
if not defined PY_CMD (
    where py >nul 2>&1 && set "PY_CMD=py"
)

:: 3. Launch Python server if available
if defined PY_CMD (
    start "CustomLabelStudio-Server" /min %PY_CMD% "%~dp0server.py"
    ping 127.0.0.1 -n 2 >nul
)

:: 4. Verify if port is listening now
netstat -ano | findstr ":%PORT%" >nul 2>&1
if not errorlevel 1 goto OPEN_HTTP

:: 5. Failsafe: If server did not start, open index.html directly
start "" "%~dp0index.html"
exit /b 0

:OPEN_HTTP
start "" "http://localhost:%PORT%/"
exit /b 0