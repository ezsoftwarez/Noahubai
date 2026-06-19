@echo off
setlocal
cd /d "%~dp0"
title WinBridge OS Bridge

set PORT=9778
set PY=python
where py >nul 2>&1 && set PY=py

echo ========================================
echo  WinBridge — OS Bridge (port %PORT%)
echo ========================================
echo Repo: %CD%
echo.

if not exist "WinBridge.py" (
  echo ERROR: WinBridge.py not found in %CD%
  pause
  exit /b 1
)

echo Starting WinBridge API + desktop UI...
start "WinBridge" cmd /k "cd /d \"%CD%\" && %PY% WinBridge.py"

timeout /t 2 /nobreak >nul

powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:%PORT%/api/os-bridge/status' -UseBasicParsing -TimeoutSec 3; exit 0 } catch { exit 1 }" >nul 2>&1
if %errorlevel%==0 (
  echo WinBridge is online: http://127.0.0.1:%PORT%/
) else (
  echo WinBridge starting... check the WinBridge terminal window.
)

echo.
echo Use DEMOCORE OS Bridge app or this UI to load files and folders.
pause
