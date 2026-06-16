@echo off
title AI Hub
cd /d "%~dp0"

set PORT=8765
set URL=http://127.0.0.1:%PORT%/index.html#bridge

echo.
echo  AI Hub — starting Bridge server...
echo.

where python >nul 2>&1
if %errorlevel%==0 (
  set PY=python
  goto run_hub
)

where py >nul 2>&1
if %errorlevel%==0 (
  set PY=py
  goto run_hub
)

goto no_python

:run_hub
start /b %PY% "%~dp0bridge_server.py"
echo Waiting for Bridge on port %PORT%...
set /aTRIES=0
:wait_loop
timeout /t 1 /nobreak >nul
powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:%PORT%/api/bridge/status' -UseBasicParsing -TimeoutSec 2; exit ([int]($r.StatusCode -ne 200)) } catch { exit 1 }"
if %errorlevel%==0 goto bridge_ready
set /aTRIES+=1
if %TRIES% lss 15 goto wait_loop
echo Warning: Bridge did not respond in 15s — opening UI anyway.
:bridge_ready
start "" "%URL%"
echo.
echo  AI Hub: %URL%
echo  Bridge MUST run via this window — do not double-click index.html
echo.
echo  - Sidebar: Bridge (first icon)
echo  - Cursor sessions load automatically (Scan all)
echo.
echo  Close this window to stop the server.
pause
goto :eof

:no_python
echo Python not found. Install Python 3, then run this file again.
start "" "%~dp0index.html"
pause
