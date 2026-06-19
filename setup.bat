@echo off
REM Noahubai Installation Batch Script for Windows
REM This script handles the installation of Noahubai on Windows systems

setlocal enabledelayedexpansion

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                              ║
echo ║                   ^🤖 NOAHUBAI INSTALLATION WIZARD ^🤖                         ║
echo ║                                                                              ║
echo ║          Unified AI with Memory, Issues, and Auto-Fixing                    ║
echo ║                                                                              ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo    Please install Python 3.10+ from https://www.python.org/
    echo    Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✅ Python found: 
for /f "tokens=*" %%i in ('python --version') do echo    %%i
echo.

REM Get installation directory
if "%LOCALAPPDATA%"=="" (
    set INSTALL_DIR=%USERPROFILE%\Noahubai
) else (
    set INSTALL_DIR=%LOCALAPPDATA%\Noahubai
)

echo 📁 Installation Directory:
echo    %INSTALL_DIR%
echo.

set /p CUSTOM_PATH="Use custom path? (leave blank for default): "
if not "%CUSTOM_PATH%"=="" (
    set INSTALL_DIR=%CUSTOM_PATH%
)

echo Creating installation directory...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
cd /d "%INSTALL_DIR%"

echo.
echo 🔧 Creating Virtual Environment...
python -m venv venv
if errorlevel 1 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment created

echo.
echo 📦 Installing Dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip -q
if exist "%~dp0requirements.txt" (
    pip install -r "%~dp0requirements.txt" -q
) else (
    echo ⚠️  requirements.txt not found, installing core dependencies...
    pip install fastapi uvicorn pydantic python-multipart -q
)
echo ✅ Dependencies installed

echo.
echo 📋 Copying Application Files...
if exist "%~dp0core" xcopy "%~dp0core" "%INSTALL_DIR%\core" /E /I /Y >nul
if exist "%~dp0agents" xcopy "%~dp0agents" "%INSTALL_DIR%\agents" /E /I /Y >nul
if exist "%~dp0backend" xcopy "%~dp0backend" "%INSTALL_DIR%\backend" /E /I /Y >nul
if exist "%~dp0main.py" copy "%~dp0main.py" "%INSTALL_DIR%\main.py" >nul
echo ✅ Application files copied

echo.
echo 🔗 Creating Shortcuts...

REM Create run batch file (OG + Bridge)
if exist "%~dp0RUN-NOAHUBAI-OG.bat" (
    copy "%~dp0RUN-NOAHUBAI-OG.bat" "%INSTALL_DIR%\RUN-NOAHUBAI-OG.bat" >nul
    echo ✓ Copied RUN-NOAHUBAI-OG.bat
) else (
    (
        echo @echo off
        echo cd /d "%INSTALL_DIR%"
        echo call venv\Scripts\activate.bat
        echo python main.py %%*
        echo pause
    ) > "%INSTALL_DIR%\run_noahubai.bat"
    echo ✓ Created run_noahubai.bat
)

REM Create desktop shortcut — Noahubai OG + auto Bridge
set SHORTCUT_SCRIPT=%~dp0CREATE-NOAHUBAI-DESKTOP-SHORTCUT.bat
if exist "%~dp0RUN-NOAHUBAI-OG.bat" (
    powershell -NoProfile -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Noahubai OG.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\RUN-NOAHUBAI-OG.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Noahubai OG from GitHub — auto-starts AI Hub Bridge'; $Shortcut.Save()" 2>nul
) else (
    powershell -NoProfile -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Noahubai.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\run_noahubai.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()" 2>nul
)
if exist "%USERPROFILE%\Desktop\Noahubai OG.lnk" (
    echo ✓ Created desktop shortcut: Noahubai OG
) else if exist "%USERPROFILE%\Desktop\Noahubai.lnk" (
    echo ✓ Created desktop shortcut: Noahubai
) else (
    echo ⚠️  Could not create desktop shortcut (requires Windows 10+)
)

echo.
echo ⚙️  Creating Configuration Files...
(
    echo # Noahubai Configuration
    echo # Generated: %date% %time%
    echo.
    echo HOST=0.0.0.0
    echo PORT=8000
    echo DEBUG=false
    echo LOG_LEVEL=INFO
) > "%INSTALL_DIR%\.env"
echo ✓ Created .env file

echo.
echo ════════════════════════════════════════════════════════════════════════════════
echo ✅ NOAHUBAI INSTALLATION COMPLETED SUCCESSFULLY!
echo ════════════════════════════════════════════════════════════════════════════════
echo.
echo 📁 Installation Directory: %INSTALL_DIR%
echo.
echo 🚀 Quick Start:
echo    1. Run: %INSTALL_DIR%\run_noahubai.bat
echo    2. Open browser: http://localhost:8000
echo    3. Check the dashboard for agent status
echo.
echo 📖 Documentation:
echo    API Docs: http://localhost:8000/docs
echo.
echo ════════════════════════════════════════════════════════════════════════════════
echo.

set /p START_NOW="Start Noahubai now? (Y/n): "
if /i not "%START_NOW%"=="n" (
    echo.
    echo 🚀 Starting Noahubai...
    echo.
    call "%INSTALL_DIR%\run_noahubai.bat"
)

pause
