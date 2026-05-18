param(
    [ValidateSet("install", "test", "verify", "run", "all")]
    [string]$Action = "all"
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $Root "backend"
$FrontendDir = Join-Path $Root "frontend"

$PythonExe = "C:\Users\Shubh\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$NpmCmd = "C:\Program Files\nodejs\npm.cmd"

$PipTarget = Join-Path $Root ".pip-target"
$PipCache = Join-Path $Root ".pip-cache"
$TmpDir = Join-Path $Root ".tmp"
$NpmCache = Join-Path $Root ".npm-cache"

function Initialize-Environment {
    New-Item -ItemType Directory -Force -Path $PipTarget, $PipCache, $TmpDir, $NpmCache | Out-Null
    $env:TMP = $TmpDir
    $env:TEMP = $TmpDir
    $env:PIP_CACHE_DIR = $PipCache
    $env:npm_config_cache = $NpmCache
    $env:PYTHONPATH = "$PipTarget;$BackendDir"
}

function Install-Dependencies {
    Initialize-Environment
    Push-Location $BackendDir
    try {
        & $PythonExe -m pip install --target $PipTarget -r requirements.txt
    } finally {
        Pop-Location
    }

    Push-Location $FrontendDir
    try {
        & $NpmCmd install
    } finally {
        Pop-Location
    }
}

function Run-Tests {
    Initialize-Environment
    Push-Location $BackendDir
    try {
        & $PythonExe -m unittest discover -s tests -v
    } finally {
        Pop-Location
    }

    Push-Location $FrontendDir
    try {
        & $NpmCmd run build
    } finally {
        Pop-Location
    }
}

function Invoke-Verification {
    Initialize-Environment

    $verifyBackendPort = 18000
    $verifyFrontendPort = 15173

    $backendOut = Join-Path $TmpDir "verify-backend-out.log"
    $backendErr = Join-Path $TmpDir "verify-backend-err.log"
    $frontendOut = Join-Path $TmpDir "verify-frontend-out.log"
    $frontendErr = Join-Path $TmpDir "verify-frontend-err.log"

    $backendCmd = "`$env:PYTHONPATH='$PipTarget;$BackendDir'; & '$PythonExe' -m uvicorn app.main:app --host 127.0.0.1 --port $verifyBackendPort"
    $frontendCmd = "`$env:npm_config_cache='$NpmCache'; & '$NpmCmd' run dev -- --host 127.0.0.1 --port $verifyFrontendPort --strictPort"

    $backendProc = $null
    $frontendProc = $null

    try {
        $backendProc = Start-Process -FilePath "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" `
            -ArgumentList "-NoProfile", "-Command", $backendCmd `
            -WorkingDirectory $BackendDir `
            -WindowStyle Hidden `
            -PassThru `
            -RedirectStandardOutput $backendOut `
            -RedirectStandardError $backendErr

        Start-Sleep -Seconds 8
        $health = Invoke-WebRequest "http://127.0.0.1:$verifyBackendPort/health" -UseBasicParsing
        $scenario = Invoke-WebRequest "http://127.0.0.1:$verifyBackendPort/api/scenario" -UseBasicParsing

        $frontendProc = Start-Process -FilePath "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" `
            -ArgumentList "-NoProfile", "-Command", $frontendCmd `
            -WorkingDirectory $FrontendDir `
            -WindowStyle Hidden `
            -PassThru `
            -RedirectStandardOutput $frontendOut `
            -RedirectStandardError $frontendErr

        Start-Sleep -Seconds 10
        $page = Invoke-WebRequest "http://127.0.0.1:$verifyFrontendPort" -UseBasicParsing

        Write-Output "Backend /health: $($health.StatusCode)"
        Write-Output "Backend /api/scenario: $($scenario.StatusCode)"
        Write-Output "Frontend /: $($page.StatusCode)"
    }
    finally {
        if ($backendProc) {
            Stop-Process -Id $backendProc.Id -Force -ErrorAction SilentlyContinue
        }
        if ($frontendProc) {
            Stop-Process -Id $frontendProc.Id -Force -ErrorAction SilentlyContinue
        }
    }
}

function Start-Application {
    Initialize-Environment

    $backendCmd = "`$env:PYTHONPATH='$PipTarget;$BackendDir'; Set-Location '$BackendDir'; & '$PythonExe' -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
    $frontendCmd = "`$env:npm_config_cache='$NpmCache'; Set-Location '$FrontendDir'; & '$NpmCmd' run dev -- --host 127.0.0.1 --port 5173"

    Start-Process -FilePath "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" `
        -ArgumentList "-NoExit", "-Command", $backendCmd `
        -WorkingDirectory $BackendDir

    Start-Process -FilePath "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" `
        -ArgumentList "-NoExit", "-Command", $frontendCmd `
        -WorkingDirectory $FrontendDir

    Write-Host "Backend:  http://127.0.0.1:8000"
    Write-Host "Frontend: http://127.0.0.1:5173"
}

switch ($Action) {
    "install" { Install-Dependencies }
    "test" { Run-Tests }
    "verify" { Invoke-Verification }
    "run" { Start-Application }
    "all" {
        Install-Dependencies
        Run-Tests
        Invoke-Verification
    }
}
