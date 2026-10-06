param([int]$Camera = 0, [ValidateSet('left','right')][string]$Side = 'left', [switch]$Voice)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath '.venv-camera\Scripts\python.exe')) { throw 'Run .\Setup-Camera.ps1 first.' }
$demoArguments = @('-m', 'demo.stacking_assessment', '--camera', "$Camera", '--side', $Side)
if ($Voice) { $demoArguments += '--voice' }
& .\.venv-camera\Scripts\python.exe @demoArguments
exit $LASTEXITCODE
