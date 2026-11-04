param(
    [switch]$Rebuild
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$LocalDir = Join-Path $Root ".local"
$PgData = Join-Path $LocalDir "pgdata"
$PgPort = 5433

$pgVersionDirs = Get-ChildItem "C:\Program Files\PostgreSQL" -Directory -ErrorAction SilentlyContinue |
    Where-Object { Test-Path (Join-Path $_.FullName "bin\pg_ctl.exe") } |
    Sort-Object Name -Descending
if (-not $pgVersionDirs) {
    throw "PostgreSQL was not found. Install PostgreSQL 17 or newer and retry."
}
$PgBin = Join-Path $pgVersionDirs[0].FullName "bin"
$PgVersion = $pgVersionDirs[0].Name

$majorVersion = $null
$versionFile = Join-Path $PgData "PG_VERSION"
if (Test-Path $versionFile) {
    $majorVersion = (Get-Content $versionFile -Raw).Trim()
}
if ($majorVersion -and $majorVersion -ne $PgVersion) {
    $backup = Join-Path $LocalDir ("pgdata-v" + $majorVersion + "-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
    Write-Host "Moving PostgreSQL $majorVersion data to $backup before PostgreSQL $PgVersion initialization."
    Move-Item $PgData $backup
    $majorVersion = $null
}

New-Item -ItemType Directory -Force $LocalDir | Out-Null

if (-not $majorVersion) {
    Write-Host "1/3  Initializing local PostgreSQL $PgVersion"
    $passwordFile = Join-Path ([System.IO.Path]::GetTempPath()) ("queueless-pg-" + [guid]::NewGuid() + ".txt")
    try {
        Set-Content -NoNewline -Path $passwordFile -Value "postgres"
        & (Join-Path $PgBin "initdb.exe") -D $PgData -U postgres --pwfile=$passwordFile `
            --auth-local=scram-sha-256 --auth-host=scram-sha-256 --encoding=UTF8 --no-locale
        if ($LASTEXITCODE -ne 0) { throw "PostgreSQL initialization failed." }
    } finally {
        Remove-Item $passwordFile -Force -ErrorAction SilentlyContinue
    }
}

$statusOutput = & (Join-Path $PgBin "pg_ctl.exe") -D $PgData status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Starting PostgreSQL on localhost:$PgPort"
    & (Join-Path $PgBin "pg_ctl.exe") -D $PgData -l (Join-Path $LocalDir "postgres.log") -w `
        -o "-p $PgPort -c listen_addresses=localhost -c max_connections=150" start
    if ($LASTEXITCODE -ne 0) { throw "PostgreSQL failed to start." }
} else {
    Write-Host "PostgreSQL is already running on localhost:$PgPort"
}

for ($attempt = 1; $attempt -le 30; $attempt++) {
    & (Join-Path $PgBin "pg_isready.exe") -h localhost -p $PgPort -U postgres | Out-Null
    if ($LASTEXITCODE -eq 0) { break }
    Start-Sleep -Milliseconds 500
}

$env:PGPASSWORD = "postgres"
$psql = Join-Path $PgBin "psql.exe"
$adminArgs = @("-h", "localhost", "-p", "$PgPort", "-U", "postgres", "-d", "postgres", "-v", "ON_ERROR_STOP=1", "-q")

$roleExists = (& $psql @adminArgs -tAc "SELECT 1 FROM pg_roles WHERE rolname = 'queueless'" | Out-String).Trim()
if ($roleExists -ne "1") {
    & $psql @adminArgs -c "CREATE ROLE queueless LOGIN PASSWORD 'queueless'"
}

foreach ($database in @("queueless", "queueless_test")) {
    $databaseExists = (& $psql @adminArgs -tAc "SELECT 1 FROM pg_database WHERE datname = '$database'" | Out-String).Trim()
    if ($databaseExists -ne "1") {
        & $psql @adminArgs -c "CREATE DATABASE $database OWNER queueless"
    }
}

Set-Location $Root
$jar = Join-Path $Root "backend\target\queueless.jar"
if ($Rebuild -or -not (Test-Path $jar)) {
    Write-Host "2/3  Building frontend and backend"
    Push-Location (Join-Path $Root "frontend")
    npm ci --no-audit --no-fund
    if ($LASTEXITCODE -ne 0) { throw "Frontend dependency installation failed." }
    npm run build
    if ($LASTEXITCODE -ne 0) { throw "Frontend build failed." }
    Pop-Location

    Push-Location (Join-Path $Root "backend")
    .\mvnw.cmd -q -B -DskipTests package
    if ($LASTEXITCODE -ne 0) { throw "Backend build failed." }
    Pop-Location
} else {
    Write-Host "2/3  Using the existing build (run with -Rebuild after code changes)"
}

Write-Host "3/3  Starting QueueLess at http://localhost:8080"
Write-Host "     Demo password: Password123!"
java -jar $jar --spring.profiles.active=dev
