# Build AI HUB.exe and Setup.exe into <dest>\Setup\
param(
  [string]$DestRoot = "B:\AI HUB oVerk1LL"
)

$ErrorActionPreference = "Stop"
$Repo = Split-Path $PSScriptRoot -Parent
if (-not (Test-Path (Join-Path $Repo "bridge_server.py"))) {
  throw "bridge_server.py not found in $Repo"
}
$SetupDir = Join-Path $DestRoot "Setup"
New-Item -ItemType Directory -Path $SetupDir -Force | Out-Null

$DataArgs = @(
  "--add-data", "$(Join-Path $Repo 'index.html');.",
  "--add-data", "$(Join-Path $Repo 'app.js');.",
  "--add-data", "$(Join-Path $Repo 'js');js",
  "--add-data", "$(Join-Path $Repo 'bridge-data');bridge-data",
  "--add-data", "$(Join-Path $Repo 'pinned-codes');pinned-codes",
  "--add-data", "$(Join-Path $Repo 'RUN-AI-HUB.bat');.",
  "--add-data", "$(Join-Path $Repo 'RUN-AI-SWARM.bat');.",
  "--add-data", "$(Join-Path $Repo 'requirements.txt');."
)

Push-Location $Repo
try {
  python -m PyInstaller --noconfirm --onefile --console --name "AI HUB" --distpath $SetupDir --workpath (Join-Path $Repo "build\pyi-work-hub") --specpath (Join-Path $Repo "build\spec") @DataArgs (Join-Path $Repo "build\ai_hub_main.py")
  python -m PyInstaller --noconfirm --onefile --console --name "Setup" --distpath $SetupDir --workpath (Join-Path $Repo "build\pyi-work-setup") --specpath (Join-Path $Repo "build\spec") (Join-Path $Repo "build\setup_installer.py")
}
finally {
  Pop-Location
}

Write-Host "Built:" (Get-ChildItem $SetupDir -Filter *.exe | ForEach-Object Name)
