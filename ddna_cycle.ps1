$ErrorActionPreference = "Stop"

$ROOT = "C:\Users\jacks\OneDrive\Desktop\Digital-DNA"
$ENGINE = Join-Path $ROOT "engine\orchestrator\run_ddna.py"
$ART_LAST = Join-Path $ROOT "artifacts\last_run.json"

Write-Host ""
Write-Host "DDNA ITERATION CYCLE"
Write-Host "Root:" $ROOT
Write-Host ""

Push-Location $ROOT

Write-Host "Running engine..."
python $ENGINE

Write-Host ""
Write-Host "Reading metrics..."

if (Test-Path $ART_LAST) {
    Get-Content $ART_LAST
} else {
    Write-Host "No last_run.json found"
}

Pop-Location

Write-Host ""
Write-Host "Cycle complete."
