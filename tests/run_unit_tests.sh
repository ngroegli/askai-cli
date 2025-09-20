#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory to ensure relative paths work
cd "$SCRIPT_DIR"

# Run the unit tests with Python from the virtual environment
VENV_PYTHON="../venv/bin/python"

if [ -f "$VENV_PYTHON" ]; then
    echo "Running unit tests with virtual environment Python..."
    $VENV_PYTHON run_unit_tests.py "$@"
else
    echo "Virtual environment not found, trying system Python..."
    python3 run_unit_tests.py "$@"
fi
