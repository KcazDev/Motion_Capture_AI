param([int]$Camera = 0)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath '.venv-camera\Scripts\python.exe')) { throw 'Run .\Setup-Camera.ps1 first.' }
& .\.venv-camera\Scripts\python.exe -m src.vision.camera --camera $Camera
exit $LASTEXITCODE
