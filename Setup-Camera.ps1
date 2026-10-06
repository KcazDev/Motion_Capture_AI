$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath '.venv-camera\Scripts\python.exe')) {
    python -m venv .venv-camera
    if ($LASTEXITCODE -ne 0) { throw 'Could not create camera environment.' }
}
& .\.venv-camera\Scripts\python.exe -m pip install -r requirements-camera.txt
if ($LASTEXITCODE -ne 0) { throw 'Camera dependency installation failed.' }
& .\.venv-camera\Scripts\python.exe -m demo.setup_camera
if ($LASTEXITCODE -ne 0) { throw 'Pose model download failed.' }
Write-Host 'Ready. Run .\Start-Camera.ps1 or .\Start-MotionAI.ps1'
