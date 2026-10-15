$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not $env:AURUM_API_TOKEN -or $env:AURUM_API_TOKEN.Length -lt 32) {
    Write-Host "Set AURUM_API_TOKEN to a private random secret of at least 32 characters first." -ForegroundColor Yellow
    Write-Host 'Example for this PowerShell session: $env:AURUM_API_TOKEN = [guid]::NewGuid().ToString() + [guid]::NewGuid().ToString()'
    exit 1
}
if (-not $env:AURUM_SYMBOL) { $env:AURUM_SYMBOL = "XAUUSD" }
if (-not $env:AURUM_ALLOWED_ORIGINS) { $env:AURUM_ALLOWED_ORIGINS = "https://novaos-original.github.io" }

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    py -3 -m venv .venv
}
& ".venv\Scripts\python.exe" -m pip install --upgrade pip
& ".venv\Scripts\python.exe" -m pip install -r requirements.txt
Write-Host "Starting READ-ONLY MT5 bridge at http://127.0.0.1:8765" -ForegroundColor Green
Write-Host "Keep MT5 open and signed in to a DEMO account. Press Ctrl+C to stop."
& ".venv\Scripts\python.exe" -m uvicorn app:app --host 127.0.0.1 --port 8765
