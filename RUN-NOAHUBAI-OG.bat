@echo off
setlocal EnableDelayedExpansion
title Noahubai OG + AI Hub Bridge
cd /d "%~dp0"
set ROOT=%CD%

set BRIDGE_PORT=8765
set NOAH_PORT=8000
set NOAH_URL=http://127.0.0.1:%NOAH_PORT%/
set BRIDGE_DIR=%ROOT%\AI HUB oVerk1LL

echo.
echo  Noahubai OG (GitHub library) + AI Hub Bridge
echo  Repo: https://github.com/ezsoftwarez/Noahubai
echo  Root: %ROOT%
echo.

where python >nul 2>&1
if %errorlevel%==0 (set PY=python) else (
  where py >nul 2>&1
  if !errorlevel!==0 (set PY=py) else goto no_python
)

if not exist "%ROOT%\main.py" (
  echo ERROR: main.py not found in %ROOT%
  echo Clone from https://github.com/ezsoftwarez/Noahubai
  pause
  exit /b 1
)

REM --- 1) AI Hub Bridge (auto-start) ---
if exist "%BRIDGE_DIR%\bridge_server.py" (
  echo [1/3] Starting AI Hub Bridge on port %BRIDGE_PORT%...
  start "AI Hub Bridge" /min cmd /k "cd /d \"%BRIDGE_DIR%\" && %PY% bridge_server.py"
  set /a TRIES=0
  :wait_bridge
  timeout /t 1 /nobreak >nul
  powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:%BRIDGE_PORT%/api/bridge/status' -UseBasicParsing -TimeoutSec 2; exit 0 } catch { exit 1 }" >nul 2>&1
  if !errorlevel!==0 goto bridge_ok
  set /a TRIES+=1
  if !TRIES! lss 20 goto wait_bridge
  echo Warning: Bridge slow to start — continuing anyway.
  :bridge_ok
  echo       Bridge ready.
) else (
  echo [skip] AI HUB oVerk1LL not found — Noahubai only.
)

REM --- 2) Noahubai OG app (Windows 7 shell on :8000) ---
echo [2/3] Starting Noahubai OG on port %NOAH_PORT%...
start "Noahubai OG" cmd /k "cd /d \"%ROOT%\" && %PY% main.py"
set /a TRIES=0
:wait_noah
timeout /t 1 /nobreak >nul
powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:%NOAH_PORT%/api/health' -UseBasicParsing -TimeoutSec 2; exit 0 } catch { exit 1 }" >nul 2>&1
if !errorlevel!==0 goto noah_ok
set /a TRIES+=1
if !TRIES! lss 25 goto wait_noah
echo Warning: Noahubai slow to start — opening browser anyway.
:noah_ok
echo       Noahubai ready.

REM --- 3) Open original desktop UI ---
echo [3/3] Opening Noahubai OG desktop...
start "" "%NOAH_URL%"

echo.
echo  Noahubai OG:  %NOAH_URL%
echo  AI Hub Bridge: http://127.0.0.1:%BRIDGE_PORT%/
echo  Keep the Bridge and Noahubai terminal windows open.
echo.
pause
goto :eof

:no_python
echo Python not found. Install Python 3.10+ from https://www.python.org/
pause
exit /b 1
