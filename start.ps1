# iflow-mcp-catalog — SOTA startup (Windows): clear ports, backend, Vite, open browser
$ErrorActionPreference = "Stop"
$BackendPort = 10809
$FrontendPort = 10808
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

function Stop-ListenersOnPort {
    param([int]$Port)
    $conns = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    foreach ($c in $conns) {
        Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}

Set-Location $Root
Stop-ListenersOnPort -Port $BackendPort
Stop-ListenersOnPort -Port $FrontendPort

if (-not (Test-Path "$Root\.venv\Scripts\python.exe")) {
    Write-Host "Create venv: py -3.12 -m venv .venv ; .\.venv\Scripts\pip install -e ."
    exit 1
}

$py = "$Root\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    Write-Host "Missing $py"
    exit 1
}

Start-Process -FilePath $py -ArgumentList @(
    "-m", "uvicorn", "iflow_mcp_catalog.webapp_backend:app",
    "--host", "127.0.0.1", "--port", "$BackendPort"
) -WindowStyle Hidden

Set-Location "$Root\webapp"
if (-not (Test-Path "node_modules")) {
    npm install
}

Start-Sleep -Seconds 2
Start-Process "http://127.0.0.1:$FrontendPort/"
npm run dev
