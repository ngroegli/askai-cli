#!/bin/bash

# This script runs pylint checks with the same severity-based output as GitHub Actions

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Ensure we're in the project root directory
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set PYTHONPATH to match GitHub Actions
export PYTHONPATH=src:$SCRIPT_DIR
echo "Using PYTHONPATH: $PYTHONPATH"

# Extract disabled warnings from .pylintrc to apply consistently
DISABLED_CHECKS=$(grep -oP '^disable=\K.*' .pylintrc)
echo "Applying disabled warnings from .pylintrc: $DISABLED_CHECKS"

# Make sure there are Python files to analyze
PYTHON_FILES=$(find ./src -name "*.py" | xargs)
if [ -z "$PYTHON_FILES" ]; then
    echo "No Python files found to analyze! Check the paths and file structure."
    exit 0
fi

echo -e "\n\n======================================================================"
echo "                  FULL PYLINT OUTPUT                            "
echo "======================================================================"
# Run pylint using the project's configuration file with full output
# No need for extra --disable flags, as .pylintrc is already used
PYTHONPATH=src pylint --rcfile=.pylintrc $PYTHON_FILES || echo "Pylint check failed but we're continuing to see all errors categorized by severity"
echo -e "\n\n"

# 1. Check for critical errors (error category)
echo -e "======================================================================"
echo "                  CRITICAL ERRORS (E)                            "
echo "                These will block merging                         "
echo "======================================================================"
CRITICAL_ERRORS=$(PYTHONPATH=src pylint --rcfile=.pylintrc --disable=C,W,R,I --enable=E --disable=$DISABLED_CHECKS --msg-template="{path}:{line}:{column}: [{msg_id}({symbol}), {category}] {msg}" $PYTHON_FILES 2>&1 || echo "")
CRITICAL_EXIT_CODE=${PIPESTATUS[0]}

if [ -n "$CRITICAL_ERRORS" ]; then
    echo -e "\033[31m$CRITICAL_ERRORS\033[0m"  # Red text for errors
else
    echo -e "\033[32mNo critical errors found.\033[0m"  # Green text
fi

# 2. Check for warnings
echo -e "\n\n======================================================================"
echo "                  WARNINGS (W)                                  "
echo "      These should be addressed but won't block merging         "
echo "======================================================================"
WARNINGS=$(PYTHONPATH=src pylint --rcfile=.pylintrc --disable=C,E,R,I --enable=W --disable=$DISABLED_CHECKS --msg-template="{path}:{line}:{column}: [{msg_id}({symbol}), {category}] {msg}" $PYTHON_FILES 2>&1 || echo "")

if [ -n "$WARNINGS" ]; then
    echo -e "\033[33m$WARNINGS\033[0m"  # Yellow text for warnings
else
    echo -e "\033[32mNo warnings found.\033[0m"  # Green text
fi

# 3. Check for refactoring suggestions
echo -e "\n\n======================================================================"
echo "                  REFACTORING SUGGESTIONS (R)                    "
echo "           Recommendations to improve code quality               "
echo "======================================================================"
REFACTORING=$(PYTHONPATH=src pylint --rcfile=.pylintrc --disable=C,E,W,I --enable=R --disable=$DISABLED_CHECKS --msg-template="{path}:{line}:{column}: [{msg_id}({symbol}), {category}] {msg}" $PYTHON_FILES 2>&1 || echo "")

if [ -n "$REFACTORING" ]; then
    echo -e "\033[36m$REFACTORING\033[0m"  # Cyan text for refactoring
else
    echo -e "\033[32mNo refactoring suggestions found.\033[0m"  # Green text
fi

# 4. Check for convention violations
echo -e "\n\n======================================================================"
echo "                  CONVENTION ISSUES (C)                         "
echo "                      Style suggestions                         "
echo "======================================================================"
CONVENTIONS=$(PYTHONPATH=src pylint --rcfile=.pylintrc --disable=E,W,R,I --enable=C --disable=$DISABLED_CHECKS --msg-template="{path}:{line}:{column}: [{msg_id}({symbol}), {category}] {msg}" $PYTHON_FILES 2>&1 || echo "")

if [ -n "$CONVENTIONS" ]; then
    echo -e "\033[35m$CONVENTIONS\033[0m"  # Magenta text for conventions
else
    echo -e "\033[32mNo convention issues found.\033[0m"  # Green text
fi

# 5. Check for info messages
echo -e "\n\n======================================================================"
echo "                  INFORMATION (I)                               "
echo "                    Additional info                             "
echo "======================================================================"
INFORMATION=$(PYTHONPATH=src pylint --rcfile=.pylintrc --disable=E,W,R,C --enable=I --disable=$DISABLED_CHECKS --msg-template="{path}:{line}:{column}: [{msg_id}({symbol}), {category}] {msg}" $PYTHON_FILES 2>&1 || echo "")

if [ -n "$INFORMATION" ]; then
    echo -e "\033[34m$INFORMATION\033[0m"  # Blue text for info
else
    echo -e "\033[32mNo information messages found.\033[0m"  # Green text
fi

# Summary
echo -e "\n\n======================================================================"
echo "                          SUMMARY                               "
echo "======================================================================"

if [ $CRITICAL_EXIT_CODE -eq 4 ]; then
    echo "Exit code 4 detected (no files found or config issue). This is not a critical error."
    echo -e "\033[32mGitHub workflow would PASS.\033[0m"
elif [ $CRITICAL_EXIT_CODE -ne 0 ]; then
    echo -e "\033[31mCritical errors found. GitHub workflow would FAIL.\033[0m"
else
    echo -e "\033[32mNo critical errors found. GitHub workflow would PASS.\033[0m"
fi

# Exit with the same code that would be used in CI
if [ $CRITICAL_EXIT_CODE -eq 4 ]; then
    exit 0
else
    exit $CRITICAL_EXIT_CODE
fi
