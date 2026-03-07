#!/bin/bash
# Setup script for the Architecture Accelerator Framework
# Run this script to create a local virtual environment and install dependencies on Linux/macOS.

set -e

# Get the absolute path to the project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PATH="$PROJECT_ROOT/.venv"
REQUIREMENTS_PATH="$PROJECT_ROOT/requirements.txt"

echo -e "\033[0;36m=============================================\033[0m"
echo -e "\033[0;36m Building Architecture Accelerator Workspace \033[0m"
echo -e "\033[0;36m=============================================\033[0m"
echo ""

# Step 1: Check Python availability (prefer python3)
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo -e "\033[0;31m[X] Python is not installed or not in your PATH. Please install Python 3.10+.\033[0m"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version)
echo -e "\033[0;32m[✓] Found Python: $PYTHON_VERSION\033[0m"

# Step 2: Create virtual environment
if [ ! -d "$VENV_PATH" ]; then
    echo -e "\033[0;33m[-] Creating isolated virtual environment (.venv)...\033[0m"
    cd "$PROJECT_ROOT"
    $PYTHON_CMD -m venv .venv
    echo -e "\033[0;32m[✓] Virtual environment created successfully.\033[0m"
else
    echo -e "\033[0;32m[✓] Virtual environment already exists at $VENV_PATH.\033[0m"
fi

# Step 3: Install dependencies
if [ -f "$REQUIREMENTS_PATH" ]; then
    echo -e "\033[0;33m[-] Installing dependencies from requirements.txt...\033[0m"
    
    # Path to pip inside the virtual environment for Linux/macOS
    PIP_PATH="$VENV_PATH/bin/pip"
    
    if [ ! -f "$PIP_PATH" ]; then
        echo -e "\033[0;31m[X] Cannot find pip in the virtual environment. Ensure the virtual environment was created correctly.\033[0m"
        exit 1
    fi
    
    # Install dependencies securely inside the local environment
    "$PIP_PATH" install -r "$REQUIREMENTS_PATH"
    
    if [ $? -eq 0 ]; then
        echo -e "\033[0;32m[✓] Dependencies installed securely into the local environment.\033[0m"
    else
        echo -e "\033[0;31m[X] Failed to install dependencies.\033[0m"
        exit 1
    fi
else
    echo -e "\033[0;31m[X] Cannot find requirements.txt in the project root.\033[0m"
    exit 1
fi

echo ""
echo -e "\033[0;36m=============================================\033[0m"
echo -e "\033[0;36m Setup Complete! You are ready to begin.     \033[0m"
echo -e "\033[0;36m=============================================\033[0m"
echo ""
echo "To start working, open a terminal in the project root and activate the environment:"
echo -e "\033[0;33m    source .venv/bin/activate\033[0m"
echo ""
