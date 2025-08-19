#!/bin/bash

# Resolve the directory of the script, even if called via symlink
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate the virtual environment located inside the repo
source "$SCRIPT_DIR/venv/bin/activate"

# Set Python path to include the root directory to fix import issues
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Run askai.py using repo-relative path
cd "$SCRIPT_DIR"
python3 "$SCRIPT_DIR/python/askai.py" "$@"