@echo off
setlocal
cd /d "%~dp0"
set ROOT=%CD%
set LAUNCHER=%ROOT%\RUN-NOAHUBAI-OG.bat
set DESKTOP=%USERPROFILE%\Desktop
set LINK=%DESKTOP%\Noahubai OG.lnk

echo Creating desktop shortcut for Noahubai OG...
echo   Target: %LAUNCHER%
echo   Desktop: %DESKTOP%
echo.

if not exist "%LAUNCHER%" (
  echo ERROR: RUN-NOAHUBAI-OG.bat not found. Run from repo root.
  pause
  exit /b 1
)

powershell -NoProfile -Command ^
  "$Wsh = New-Object -ComObject WScript.Shell; ^
   $S = $Wsh.CreateShortcut('%LINK%'); ^
   $S.TargetPath = '%LAUNCHER%'; ^
   $S.WorkingDirectory = '%ROOT%'; ^
   $S.WindowStyle = 1; ^
   $S.Description = 'Noahubai OG from GitHub — auto-starts AI Hub Bridge'; ^
   $S.Save()"

if exist "%LINK%" (
  echo.
  echo SUCCESS: Desktop shortcut created:
  echo   %LINK%
  echo.
  echo Double-click "Noahubai OG" on your desktop to launch.
) else (
  echo.
  echo Could not create shortcut. Try running as normal user on Windows 10+.
)

pause
