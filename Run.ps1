$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$pythonCandidates = @(
    (Join-Path $projectRoot '.venv\Scripts\python.exe'),
    (Join-Path (Split-Path $projectRoot -Parent) '.venv\Scripts\python.exe')
)
$pythonExecutable = $pythonCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $pythonExecutable) {
    Write-Error 'Chua co moi truong Python. Xem README.md de cai requirements.txt.'
    exit 1
}
& $pythonExecutable -X utf8 (Join-Path $projectRoot 'Script\Main.py')
exit $LASTEXITCODE
