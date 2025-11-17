#!/bin/bash

# AskAI CLI Version
VERSION="1.2.1"

# Resolve the directory of the script, even if called via symlink
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set Python path to include the src directory for package imports
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"

# Change to project directory
cd "$SCRIPT_DIR"

# Use Python from virtual environment if available, otherwise system Python
if [ -f "$SCRIPT_DIR/venv/bin/python3" ]; then
    PYTHON_CMD="$SCRIPT_DIR/venv/bin/python3"
elif [ -f "$SCRIPT_DIR/venv/bin/python" ]; then
    PYTHON_CMD="$SCRIPT_DIR/venv/bin/python"
else
    PYTHON_CMD="python3"
fi

# Debug output (uncomment for debugging)
# echo "SCRIPT_DIR: $SCRIPT_DIR"
# echo "PYTHONPATH: $PYTHONPATH"
# echo "PYTHON_CMD: $PYTHON_CMD"

# Run main.py with explicit paths
exec "$PYTHON_CMD" "$SCRIPT_DIR/src/askai/main.py" "$@"