#!/bin/bash

# Resolve the directory of the script, even if called via symlink
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate the virtual environment located inside the repo
source "$SCRIPT_DIR/venv/bin/activate"

# Run askai.py using repo-relative path
python3 $SCRIPT_DIR/python/askai.py "$@"