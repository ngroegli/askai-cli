#!/bin/bash

# Resolve the directory of the script, even if called via symlink
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate the virtual environment located inside the repo
source "$SCRIPT_DIR/venv/bin/activate"

# Set Python path to include both the root directory and the src directory
export PYTHONPATH="$SCRIPT_DIR:$SCRIPT_DIR/src:$PYTHONPATH"

# Install the package in development mode if needed
if [ ! -f "$SCRIPT_DIR/.dev_installed" ]; then
  pip install -e "$SCRIPT_DIR" >/dev/null 2>&1 && touch "$SCRIPT_DIR/.dev_installed"
fi

# Run askai.py using repo-relative path
cd "$SCRIPT_DIR"
python3 "$SCRIPT_DIR/src/askai/askai.py" "$@"