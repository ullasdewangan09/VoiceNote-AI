# VoiceNote AI — Start Backend
# Run this from the project root: .\scripts\start_backend.ps1

$rootDir = Split-Path -Parent $PSScriptRoot
$venvUvicorn = Join-Path $rootDir "venv\Scripts\uvicorn.exe"
$backendDir = Join-Path $rootDir "backend"

Write-Host ""
Write-Host "  VoiceNote AI — Backend" -ForegroundColor Cyan
Write-Host "  FastAPI + faster-whisper on http://localhost:8000" -ForegroundColor Gray
Write-Host "  Swagger UI: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host ""

& $venvUvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir $backendDir
