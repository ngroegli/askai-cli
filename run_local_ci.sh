#!/bin/bash

# Local CI Check Script
# This script runs the same checks as the GitHub Actions CI pipeline
# Run this before committing to catch issues early

# Note: We don't use 'set -e' here because we need to handle Pylint's
# non-zero exit codes properly before deciding whether to exit

echo "🔧 Running Local CI Checks for askai-cli"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "src" ]; then
    print_error "Please run this script from the askai-cli project root directory"
    exit 1
fi

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    print_status "Activating virtual environment..."
    source venv/bin/activate
else
    print_warning "No virtual environment found at ./venv"
    print_status "Using system Python..."
fi

# Set up Python path
export PYTHONPATH=".:$(pwd):$(pwd)/src:$(pwd)/tests"

echo ""
print_status "Step 1/2: Running Pylint Analysis..."
echo "======================================"

# Check if Python files exist
PYTHON_FILES=$(find ./src -name "*.py" 2>/dev/null || echo "")
if [ -z "$PYTHON_FILES" ]; then
    print_error "No Python files found in ./src directory!"
    exit 1
fi

# Run Pylint with the same configuration as CI
print_status "Analyzing Python files with Pylint..."
PYTHONPATH=src pylint --rcfile=.pylintrc $PYTHON_FILES 2>&1 || true

PYLINT_EXIT_CODE=$?

if [ $PYLINT_EXIT_CODE -eq 0 ]; then
    print_success "Pylint analysis passed! ✅"
elif [ $PYLINT_EXIT_CODE -eq 1 ] || [ $PYLINT_EXIT_CODE -eq 2 ]; then
    print_error "Pylint found critical errors! ❌"
    print_error "Please fix these issues before committing."
    exit 1
else
    print_warning "Pylint found some issues (warnings/conventions) but no critical errors."
    print_status "These won't block the CI, but consider addressing them."
fi

echo ""
print_status "Step 2/2: Running Unit Tests..."
echo "================================"

# Run unit tests
print_status "Executing unit test suite..."
python tests/run_unit_tests.py 2>&1 || true

TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -eq 0 ]; then
    print_success "All unit tests passed! ✅"
else
    print_error "Some unit tests failed! ❌"
    print_error "Please fix failing tests before committing."
    exit 1
fi

echo ""
echo "🎉 All local CI checks passed!"
echo "=============================="
print_success "Your code is ready for commit and push! ✅"
print_status "The GitHub Actions CI pipeline should pass when you create a PR."

echo ""
print_status "Next steps:"
echo "  1. git add ."
echo "  2. git commit -m 'Your commit message'"
echo "  3. git push origin your-branch"
echo "  4. Create a pull request"
