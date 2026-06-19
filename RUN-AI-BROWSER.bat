@echo off
setlocal
cd /d "%~dp0"
title AI Browser (Steamish + AI Assistant)

set PY=python
where py >nul 2>&1 && set PY=py

echo ========================================
echo  AI Browser — Steamish + AI Assistant
echo ========================================
echo.

if not exist "AIBrowser.py" (
  echo ERROR: AIBrowser.py not found
  pause
  exit /b 1
)

if not exist "steamish_browser\main.py" (
  echo ERROR: steamish_browser not found
  pause
  exit /b 1
)

echo Tip: start AI Hub Bridge on :8765 for Brain replies.
echo.

%PY% AIBrowser.py
pause
