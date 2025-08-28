#!/bin/bash

# Activate the virtual environment if it exists
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Virtual environment not found. Installing dependencies directly..."
    pip install -r requirements.txt
fi

# Run the tests
python tests/run_integration_tests.py "$@"
