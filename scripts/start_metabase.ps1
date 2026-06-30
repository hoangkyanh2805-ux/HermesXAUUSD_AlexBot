# Start Metabase Open Source locally (JAR — no Docker required)
# Windows: JAR must live in a path WITHOUT spaces (Metabase bug).
# Usage: powershell -ExecutionPolicy Bypass -File scripts/start_metabase.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$RepoJar = Join-Path $Root "metabase\metabase.jar"
$RunDir = "C:\hermes-metabase"
$Jar = Join-Path $RunDir "metabase.jar"
$DataDir = Join-Path $RunDir "data"
$JarUrl = "https://downloads.metabase.com/latest/metabase.jar"

New-Item -ItemType Directory -Force -Path $RunDir, $DataDir | Out-Null

if (-not (Test-Path $Jar)) {
    if (Test-Path $RepoJar) {
        Write-Host "Copying metabase.jar to $RunDir (no spaces in path)..."
        Copy-Item $RepoJar $Jar
    } else {
        Write-Host "Downloading metabase.jar (~500MB) to $RunDir..."
        Invoke-WebRequest -Uri $JarUrl -OutFile $Jar -UseBasicParsing
    }
}

$java = Get-Command java -ErrorAction SilentlyContinue
if (-not $java) {
  $candidates = @(
    "C:\Program Files\Microsoft\jdk-21*\bin\java.exe",
    "C:\Program Files\Microsoft\jdk-17*\bin\java.exe",
    "C:\Program Files\Eclipse Adoptium\jdk-17*\bin\java.exe"
  )
  foreach ($pattern in $candidates) {
    $found = Get-ChildItem $pattern -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) { $java = $found.FullName; break }
  }
}
if (-not $java) { throw "Java not found. Install OpenJDK 21 (Metabase requires Java 21+)." }
if ($java -is [System.Management.Automation.CommandInfo]) { $java = $java.Source }

$env:MB_DB_FILE = Join-Path $DataDir "metabase.db"
Write-Host "Starting Metabase on http://localhost:3000"
Write-Host "Data: $DataDir"
Write-Host "Press Ctrl+C to stop."

& $java --add-opens java.base/java.nio=ALL-UNNAMED -jar $Jar
