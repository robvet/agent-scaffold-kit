#!/bin/bash
# Start the Python backend server

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$SRC_DIR")"
VENV_DIR="$PROJECT_ROOT/.venv"

# Detect OS: Windows uses Scripts/, Unix uses bin/
if [ -f "$VENV_DIR/Scripts/activate" ]; then
    VENV_PATH="$VENV_DIR/Scripts/activate"
    PYTHON_CMD="$VENV_DIR/Scripts/python.exe"
else
    VENV_PATH="$VENV_DIR/bin/activate"
    PYTHON_CMD="$VENV_DIR/bin/python"
fi

# Always activate this project's virtual environment to avoid cross-project contamination.
if [ -f "$VENV_PATH" ]; then
    if [ -n "$VIRTUAL_ENV" ] && [ "$VIRTUAL_ENV" != "$VENV_DIR" ]; then
        if type deactivate >/dev/null 2>&1; then
            deactivate || true
        fi
    fi
    echo -e "\033[32mActivating virtual environment...\033[0m"
    source "$VENV_PATH"
else
    echo -e "\033[31mVirtual environment not found at $VENV_PATH\033[0m"
    echo -e "\033[33mPlease create a virtual environment first: python -m venv .venv\033[0m"
    exit 1
fi

echo -e "\033[36mStarting FastAPI backend on http://localhost:8010 ...\033[0m"
cd "$SRC_DIR"

# Kill any existing process on port 8010
echo -e "\033[33mStopping any existing backend server...\033[0m"
if command -v lsof &> /dev/null; then
    # Unix/Mac
    lsof -ti:8010 | xargs -r kill -9 2>/dev/null || true
elif command -v netstat &> /dev/null; then
    # Windows (Git Bash) - use netstat and taskkill
    pid=$(netstat -ano | awk -v p="8010" 'BEGIN{IGNORECASE=1} $0 ~ ":"p" " && /LISTENING/ {print $5}' | head -n 1 | tr -d '\r')
    if [ -n "$pid" ] && [ "$pid" != "0" ]; then
        taskkill //F //PID "$pid" > /dev/null 2>&1 || true
    fi
fi
sleep 1

# Run the FastAPI server
"$PYTHON_CMD" -m uvicorn app.main:app --host 127.0.0.1 --port 8010
