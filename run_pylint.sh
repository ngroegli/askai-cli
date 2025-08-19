#!/bin/bash

# This script runs pylint with the same configuration as GitHub Actions

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Ensure we're in the project root directory
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "Running full pylint check (shows all issues)..."
PYTHONPATH=python pylint --rcfile=pylintrc $(find ./python -name "*.py" | xargs) || echo "Pylint found issues but continuing to show all warnings and errors"

echo -e "\n\n======================= CRITICAL ERRORS ONLY ========================\n"
echo "Checking for critical errors (these will fail the build in GitHub)..."
PYTHONPATH=python pylint --rcfile=pylintrc --disable=C,W,R --enable=E --fail-under=10.0 $(find ./python -name "*.py" | xargs)
CRITICAL_ERROR_STATUS=$?
if [ $CRITICAL_ERROR_STATUS -ne 0 ]; then
    echo "Critical errors found! These will cause the GitHub workflow to fail."
else
    echo "No critical errors found. GitHub workflow will pass this check."
fi

echo -e "\n\n======================= WARNINGS ONLY ========================\n"
echo "Checking for warnings..."
WARNINGS=$(PYTHONPATH=python pylint --rcfile=pylintrc --disable=C,E,R --enable=W --msg-template="{path}:{line}:{column}: {msg_id}: {msg} ({symbol})" $(find ./python -name "*.py" | xargs))
if [ -n "$WARNINGS" ]; then
    echo "Warnings found:"
    echo "$WARNINGS"
else
    echo "No warnings found."
fi

echo -e "\n\nSummary:"
if [ $CRITICAL_ERROR_STATUS -ne 0 ]; then
    echo "❌ Critical errors detected - GitHub CI will fail"
else
    echo "✅ No critical errors detected - GitHub CI should pass this check"
fi
