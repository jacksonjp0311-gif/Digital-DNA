# ============================================================
# DIGITAL-DNA — STABLE RECURSIVE LOOP DRIVER
# ============================================================

$ROOT = "C:\Users\jacks\OneDrive\Desktop\Digital-DNA"
$ART  = Join-Path $ROOT "artifacts"
$HIST = Join-Path $ART  "history"

New-Item -ItemType Directory -Force -Path $HIST | Out-Null

cd $ROOT

Write-Host ""
Write-Host "DIGITAL-DNA RECURSIVE CYCLE"
Write-Host ""

python engine\orchestrator\run_ddna.py

$last = Join-Path $ART "last_run.json"
if (!(Test-Path $last)) {
    Write-Host "No run output found."
    exit
}

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$dest  = Join-Path $HIST "run_$stamp.json"
Copy-Item $last $dest

Write-Host ""
Write-Host "Snapshot saved:" $dest
Write-Host ""

$files = Get-ChildItem $HIST | Sort-Object Name

if ($files.Count -lt 2) {
    Write-Host "Baseline established."
    exit
}

$a = Get-Content $files[-2].FullName | ConvertFrom-Json
$b = Get-Content $files[-1].FullName | ConvertFrom-Json

$delta = [float]$b.stability - [float]$a.stability

Write-Host "Previous stability:" $a.stability
Write-Host "Current  stability:" $b.stability
Write-Host "Delta:" $delta
