@echo off
setlocal
title Doupo App - Start

set "BASE=%~dp0"
set "APP=%BASE%cc-main\cc-main_extracted\doupo-app"

echo ================================================
echo   Doupo App (doupo-cangqiong) One-Click Start
echo   Backend  : http://localhost:3000
echo   Frontend : http://localhost:5173
echo ================================================
echo.

rem ---- 1. Locate project ----
if not exist "%APP%\package.json" (
  echo [X] Project directory not found:
  echo     %APP%
  echo     Please extract cc-main.rar first.
  pause
  exit /b 1
)

rem ---- 2. Check Node.js ----
where node >nul 2>nul
if errorlevel 1 (
  echo [X] Node.js not found. Please install Node.js 22+ from https://nodejs.org/
  pause
  exit /b 1
)
echo [OK] Node.js:
node -v

rem ---- 3. Install dependencies if missing ----
if not exist "%APP%\node_modules" (
  echo [..] First run: installing dependencies, please wait...
  cd /d "%APP%"
  call npm install
  if errorlevel 1 goto :fail
  call npm run install:all
  if errorlevel 1 goto :fail
)

rem ---- 4. Start dev servers ----
echo.
echo [..] Starting backend + frontend...
echo     Close this window to stop the servers.
echo.
cd /d "%APP%"

rem Open browser after a short delay so Vite is ready
start "" cmd /c "timeout /t 6 /nobreak >nul && start http://localhost:5173/"

call npm run dev
goto :eof

:fail
echo.
echo [X] Dependency install failed. Check your network and retry.
pause
exit /b 1
