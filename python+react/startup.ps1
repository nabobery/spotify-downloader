<#
.SYNOPSIS
    Starts backend and frontend development servers with virtual environment support
.DESCRIPTION
    This script:
    - Checks for required tools
    - Activates Python virtual environment
    - Starts backend and frontend servers
    - Provides flexibility in execution
.EXAMPLE
    .\start-dev.ps1                  # Runs normally
    .\start-dev.ps1 -NoFrontend      # Skips frontend
    .\start-dev.ps1 -NoBackend       # Skips backend
#>
param (
    [switch]$NoFrontend = $false,
    [switch]$NoBackend = $false
)

# Ensure script stops on first error
$ErrorActionPreference = 'Stop'

# Paths (modify these to match your project structure)
$BackendPath = ".\backend"
$FrontendPath = ".\frontend"
$VenvPath = "$BackendPath\venv"

# Function to check if a command exists
function Test-CommandExists {
    param ($command)
    $oldPreference = $ErrorActionPreference
    $ErrorActionPreference = 'stop'
    try { if (Get-Command $command) { return $true } }
    catch { return $false }
    finally { $ErrorActionPreference = $oldPreference }
}

# Function to start backend
function Start-Backend {
    # Ensure virtual environment exists
    if (-not (Test-Path $VenvPath)) {
        Write-Host "Virtual environment not found. Please create it first." -ForegroundColor Red
        return $false
    }

    # Activate virtual environment and run
    $env:PYTHONPATH = $BackendPath
    $venvActivate = Join-Path $VenvPath "Scripts\Activate.ps1"

    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "& '$venvActivate'; cd '$BackendPath'; python app.py"
    ) -WindowStyle Normal

    return $true
}

# Function to start frontend
function Start-Frontend {
    if (-not (Test-Path "$FrontendPath\package.json")) {
        Write-Host "Frontend package.json not found." -ForegroundColor Red
        return $false
    }

    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "cd '$FrontendPath'; npm run dev"
    ) -WindowStyle Normal

    return $true
}

# Main execution
try {
    # Validate required tools
    if (-not (Test-CommandExists python)) {
        throw "Python is not installed or not in PATH"
    }

    if (-not (Test-CommandExists npm)) {
        throw "NPM is not installed or not in PATH"
    }

    # Start servers based on parameters
    $backendStarted = $true
    $frontendStarted = $true

    if (-not $NoBackend) {
        $backendStarted = Start-Backend
    }

    if (-not $NoFrontend) {
        $frontendStarted = Start-Frontend
    }

    # Provide summary
    if ($backendStarted -and $frontendStarted) {
        Write-Host "Development environment started successfully!" -ForegroundColor Green
    } else {
        Write-Host "Some services failed to start." -ForegroundColor Yellow
    }
}
catch {
    Write-Host "Error: $_" -ForegroundColor Red
}
