@echo off
REM Launcher for Model Fusion Demo (PowerShell / cmd)
REM Usage: go         - starts both frontend and backend
REM        go front   - starts frontend only
REM        go back    - starts backend only

set "GITBASH=C:\Program Files\Git\bin\bash.exe"
if not exist "%GITBASH%" (
    echo Git Bash not found at %GITBASH%
    exit /b 1
)

if "%~1"=="front" (
    "%GITBASH%" "%~dp0scripts\start-frontend.sh"
) else if "%~1"=="back" (
    "%GITBASH%" "%~dp0scripts\start-backend.sh"
) else (
    "%GITBASH%" "%~dp0scripts\start-app.sh"
)
