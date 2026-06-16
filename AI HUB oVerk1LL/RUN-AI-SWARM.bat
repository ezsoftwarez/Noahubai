@echo off
title AI Swarm — Cursor Pro+
cd /d "%~dp0"

echo AI Swarm (PyQt6) — desktop orchestration UI
echo Requires: Python 3.11+ and pip install -r requirements.txt
echo.

where py >nul 2>&1
if %errorlevel%==0 (
  set PY=py
) else (
  where python >nul 2>&1
  if %errorlevel%==0 (set PY=python) else (
    echo Python not found. Install Python 3.11+ from https://python.org
    pause
    exit /b 1
  )
)

%PY% -c "import PyQt6" 2>nul
if %errorlevel% neq 0 (
  echo Installing dependencies...
  %PY% -m pip install -r "%~dp0requirements.txt"
)

%PY% "%~dp0ai_swarm.py"
pause
