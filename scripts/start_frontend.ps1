# VoiceNote AI — Start Frontend
# Run this from the project root: .\scripts\start_frontend.ps1

$rootDir = Split-Path -Parent $PSScriptRoot
$frontendDir = Join-Path $rootDir "frontend"

Write-Host ""
Write-Host "  VoiceNote AI — Frontend" -ForegroundColor Cyan  
Write-Host "  Vite + React on http://localhost:5173" -ForegroundColor Gray
Write-Host ""

Set-Location $frontendDir
npm run dev
