@echo off
cd /d "%~dp0"
rem Pythonやポートを一切使用せず、既定のブラウザで直接アプリを開きます
start "" "index.html"
exit