@echo off
cd /d "%~dp0"
echo DEMOCORE OS — starting dev server...
if not exist node_modules (
  echo npm install...
  call npm install
  if errorlevel 1 exit /b 1
)
echo npm run dev — keep this window open
call npm run dev
