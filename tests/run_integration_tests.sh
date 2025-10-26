#!/bin/bash

# Go to project root
cd "$(dirname "$0")/.."

# Check if virtual environment exists
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
    PYTHON_CMD="python"
elif [ -d ".venv" ] && [ -f ".venv/bin/activate" ]; then
    echo "Activating virtual environment (.venv)..."
    source .venv/bin/activate
    PYTHON_CMD="python"
else
    echo "Virtual environment not found. Please create one first:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    echo ""
    echo "Attempting to use system python3..."
    PYTHON_CMD="python3"

    # Check if python3 is available
    if ! command -v python3 &> /dev/null; then
        echo "Error: python3 not found. Please install Python 3."
        exit 1
    fi
fi

# Run the tests
echo "Running integration tests..."
$PYTHON_CMD tests/run_integration_tests.py "$@"
