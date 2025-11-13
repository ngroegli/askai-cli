# Test Environment Setup Guide

## Prerequisites

- Python 3.8 or higher
- `python3-venv` package (on Debian/Ubuntu: `sudo apt install python3-venv`)

## Quick Setup

### 1. Create Virtual Environment

```bash
# From project root
python3 -m venv venv
```

### 2. Activate Virtual Environment

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Tests

```bash
# Run integration tests
./tests/run_integration_tests.sh

# Run unit tests
./tests/run_unit_tests.sh
```

## Troubleshooting

### "externally-managed-environment" Error

This happens on newer Python installations. Always use a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### "python: command not found"

Use `python3` instead:

```bash
python3 tests/run_integration_tests.py
```

### Virtual Environment Issues

If your virtual environment is corrupted:

```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Test Categories

- **Unit Tests**: Fast, isolated component tests
- **Integration Tests**: Full system tests with real components
  - `--automated-only`: No user interaction required
  - `--semi-automated-only`: Requires user interaction
  - `--category general`: Basic functionality tests
  - `--category question`: Question processing tests
  - `--category pattern`: Pattern validation tests