# Setup script for the Architecture Accelerator Framework
# Run this script to create a local virtual environment and install the required dependencies.

$ErrorActionPreference = 'Stop'

# Get the directory of the script and resolve the project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir
$VenvPath = Join-Path $ProjectRoot ".venv"
$RequirementsPath = Join-Path $ProjectRoot "requirements.txt"

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host " Building Architecture Accelerator Workspace" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Python availability
try {
    $pythonVersion = & python --version 2>&1
    Write-Host "[✓] Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[X] Python is not installed or not in your PATH. Please install Python 3.10+." -ForegroundColor Red
    exit 1
}

# Step 2: Create virtual environment
if (-Not (Test-Path $VenvPath)) {
    Write-Host "[-] Creating isolated virtual environment (.venv)..." -ForegroundColor Yellow
    Set-Location $ProjectRoot
    & python -m venv .venv
    Write-Host "[✓] Virtual environment created successfully." -ForegroundColor Green
} else {
    Write-Host "[✓] Virtual environment already exists at $VenvPath." -ForegroundColor Green
}

# Step 3: Install dependencies
if (Test-Path $RequirementsPath) {
    Write-Host "[-] Installing dependencies from requirements.txt..." -ForegroundColor Yellow
    $pipPath = Join-Path $VenvPath "Scripts\pip.exe"
    
    if (-Not (Test-Path $pipPath)) {
        Write-Host "[X] Cannot find pip in the virtual environment. Ensure the virtual environment was created correctly." -ForegroundColor Red
        exit 1
    }
    
    # We use the explicit path to pip inside the virtual environment to ensure 
    # packages do not leak into the global user environment.
    & $pipPath install -r $RequirementsPath
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[✓] Dependencies installed securely into the local environment." -ForegroundColor Green
    } else {
        Write-Host "[X] Failed to install dependencies." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[X] Cannot find requirements.txt in the project root." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host " Setup Complete! You are ready to begin." -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start working, open a terminal in the project root and activate the environment:"
Write-Host "    .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host ""
