@echo off
setlocal
cd /d "%~dp0.."
set ROOT=%CD%

echo ========================================
echo  DEMOCORE OS + NOAHUBAI + AI Hub
echo ========================================
echo Root: %ROOT%
echo.

REM --- NOAHUBAI (port 8000) ---
if exist "%ROOT%\main.py" (
  echo Starting NOAHUBAI on :8000...
  start "NOAHUBAI" cmd /k "cd /d \"%ROOT%\" && python main.py"
  timeout /t 2 /nobreak >nul
) else (
  echo [skip] main.py not found — NOAHUBAI not started
)

REM --- AI Hub Bridge (port 8765) ---
if exist "%ROOT%\AI HUB oVerk1LL\bridge_server.py" (
  echo Starting AI Hub Bridge on :8765...
  start "AI Hub" cmd /k "cd /d \"%ROOT%\AI HUB oVerk1LL\" && python bridge_server.py"
  timeout /t 2 /nobreak >nul
) else (
  echo [skip] AI HUB oVerk1LL not found
)

REM --- OS Bridge / WinBridge (port 9778) ---
if exist "%ROOT%\WinBridge.py" (
  echo Starting WinBridge OS Bridge on :9778...
  start "WinBridge" cmd /k "cd /d \"%ROOT%\" && python WinBridge.py --no-ui"
  timeout /t 2 /nobreak >nul
) else (
  echo [skip] WinBridge.py not found
)

REM --- DEMOCORE OS web shell (port 5173) ---
cd /d "%~dp0"
echo Starting DEMOCORE OS on :5173...
if not exist node_modules (
  echo npm install...
  call npm install
  if errorlevel 1 exit /b 1
)
start "DEMOCORE OS" cmd /k "cd /d \"%~dp0\" && npm run dev"
timeout /t 3 /nobreak >nul
start http://127.0.0.1:5173/

echo.
echo All services starting. Keep the terminal windows open.
echo   DEMOCORE OS  -> http://127.0.0.1:5173
echo   NOAHUBAI     -> http://127.0.0.1:8000
echo   AI Hub       -> http://127.0.0.1:8765
echo   OS Bridge    -> http://127.0.0.1:9778
pause
