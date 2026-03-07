#!/bin/bash
# Start both frontend and backend

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

# Check if virtual environment exists
if [ ! -f "$VENV_PATH" ]; then
    echo -e "\033[31mVirtual environment not found at $VENV_PATH\033[0m"
    echo -e "\033[33mPlease create a virtual environment first: python -m venv .venv\033[0m"
    exit 1
fi

# Always activate this project's virtual environment in this shell.
if [ -n "$VIRTUAL_ENV" ] && [ "$VIRTUAL_ENV" != "$VENV_DIR" ]; then
    if type deactivate >/dev/null 2>&1; then
        deactivate || true
    fi
fi
echo -e "\033[32mActivating virtual environment...\033[0m"
source "$VENV_PATH"

echo -e "\033[36mStarting Model Fusion Demo...\033[0m"
echo ""

# Kill any existing processes on ports 8010 and 8501
echo -e "\033[33mStopping any existing servers...\033[0m"
if command -v lsof &> /dev/null; then
    # Unix/Mac
    lsof -ti:8010 | xargs -r kill -9 2>/dev/null || true
    lsof -ti:8501 | xargs -r kill -9 2>/dev/null || true
elif command -v netstat &> /dev/null; then
    # Windows (Git Bash) - use netstat and taskkill
    for port in 8010 8501; do
        pid=$(netstat -ano | awk -v p="$port" 'BEGIN{IGNORECASE=1} $0 ~ ":"p" " && /LISTENING/ {print $5}' | head -n 1 | tr -d '\r')
        if [ -n "$pid" ] && [ "$pid" != "0" ]; then
            taskkill //F //PID "$pid" > /dev/null 2>&1 || true
        fi
    done
fi
sleep 1

# Start backend in background
echo -e "\033[32mStarting FastAPI backend on http://localhost:8010 ...\033[0m"
(cd "$SRC_DIR" && "$PYTHON_CMD" -m uvicorn app.main:app --host 127.0.0.1 --port 8010) &
BACKEND_PID=$!

# Give backend a moment to initialize
sleep 2

# Start frontend in background
echo -e "\033[32mStarting frontend (Streamlit)...\033[0m"
(cd "$SRC_DIR/ui" && "$PYTHON_CMD" -m streamlit run streamlit_app.py) &
FRONTEND_PID=$!

echo ""
echo -e "\033[36mBoth servers starting...\033[0m"
echo -e "\033[33m  Backend:  http://localhost:8010 (FastAPI)\033[0m"
echo -e "\033[33m  Frontend: http://localhost:8501 (Streamlit)\033[0m"
echo ""
echo -e "\033[90mPress Ctrl+C to stop both servers...\033[0m"

# Wait for both processes and handle Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
