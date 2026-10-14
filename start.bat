@echo off
cd /d "%~dp0"
set PORT=51467

rem 専用ポート51467が既にリッスンされているか確認（すでに起動中ならそのまま開く）
netstat -ano | findstr /C:":%PORT%" > nul
if %errorlevel% equ 0 goto OPEN_HTTP

rem Pythonの実行コマンドを特定
set PY_CMD=
where python > nul 2>&1 && set PY_CMD=python
if "%PY_CMD%"=="" where py > nul 2>&1 && set PY_CMD=py
if "%PY_CMD%"=="" where python3 > nul 2>&1 && set PY_CMD=python3

if not "%PY_CMD%"=="" (
    start "CustomLabelStudio-Server-51467" /min %PY_CMD% server.py
    ping 127.0.0.1 -n 2 > nul
    goto OPEN_HTTP
)

rem Pythonが見つからない場合は直接HTMLを開く
start "" "index.html"
exit

:OPEN_HTTP
start "" "http://localhost:%PORT%"
exit