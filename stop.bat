@echo off
setlocal
title Doupo App - Stop

echo Stopping Doupo App servers (ports 3000 / 5173)...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr /r ":3000 .*LISTENING :5173 .*LISTENING"') do taskkill /pid %%p /f 2>nul
taskkill /im node.exe /f 2>nul
echo Done.
timeout /t 3 /nobreak >nul
