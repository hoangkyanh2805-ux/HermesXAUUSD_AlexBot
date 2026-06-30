# Reset Metabase local H2 database (fixes login "An error occurred")
# Usage: powershell -ExecutionPolicy Bypass -File scripts/reset_metabase.ps1

$ErrorActionPreference = "Stop"
$RunDir = "C:\hermes-metabase"
$DataDir = Join-Path $RunDir "data"
$Jar = Join-Path $RunDir "metabase.jar"
$Java = "C:\Program Files\Microsoft\jdk-21.0.11.10-hotspot\bin\java.exe"

Write-Host "Stopping Metabase (java -jar metabase.jar)..."
Get-CimInstance Win32_Process -Filter "Name='java.exe'" |
    Where-Object { $_.CommandLine -like "*hermes-metabase*metabase.jar*" } |
    ForEach-Object {
        Write-Host "  kill PID $($_.ProcessId)"
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }
Start-Sleep -Seconds 2

if (Test-Path $DataDir) {
    Write-Host "Removing corrupted data: $DataDir"
    Remove-Item -Path (Join-Path $DataDir "*") -Recurse -Force -ErrorAction SilentlyContinue
}

New-Item -ItemType Directory -Force -Path $DataDir | Out-Null

if (-not (Test-Path $Java)) {
    $Java = (Get-Command java -ErrorAction SilentlyContinue).Source
}
if (-not $Java -or -not (Test-Path $Jar)) {
    throw "Java or metabase.jar not found. Run scripts/start_metabase.ps1 first."
}

$env:MB_DB_FILE = Join-Path $DataDir "metabase.db"
Write-Host "Starting fresh Metabase on http://localhost:3000/setup/"
Start-Process -FilePath $Java -ArgumentList "--add-opens","java.base/java.nio=ALL-UNNAMED","-jar",$Jar -WorkingDirectory $RunDir -WindowStyle Minimized

Write-Host "Wait ~60s, then open: http://localhost:3000/setup/"
Write-Host "Create NEW admin account (first-time wizard). Do NOT use /auth/login until setup completes."
