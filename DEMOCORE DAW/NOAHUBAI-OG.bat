@echo off
REM Launch original Noahubai from repo root (parent folder) + AI Hub Bridge
cd /d "%~dp0.."
if exist "%~dp0..\RUN-NOAHUBAI-OG.bat" (
  call "%~dp0..\RUN-NOAHUBAI-OG.bat"
) else (
  echo RUN-NOAHUBAI-OG.bat not found in parent folder.
  echo Expected repo layout:
  echo   DEMOCORE DAW\
  echo   main.py
  echo   RUN-NOAHUBAI-OG.bat
  pause
)
