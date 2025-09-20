# CI/CD Pipeline Documentation

## Overview

The askai-cli project uses GitHub Actions for Continuous Integration (CI) to ensure code quality and functionality. The CI pipeline automatically runs on pull requests and helps maintain high code standards.

## Workflows

### 1. Main CI Pipeline (`ci.yml`)

**Triggers:**
- Pull requests to `main` or `develop` branches
- Pushes to `main` or `develop` branches
- Manual workflow dispatch

**Jobs:**

#### Pylint (Code Quality Analysis)
- **Purpose**: Analyzes Python code for errors, warnings, and style issues
- **Blocking**: ❌ **Critical errors block the pipeline**
- **Non-blocking**: ⚠️ Warnings and conventions are reported but don't block merges
- **Configuration**: Uses `.pylintrc` for project-specific rules
- **Output**: Creates detailed summary in GitHub Actions

#### Unit Tests
- **Purpose**: Runs the complete unit test suite
- **Dependency**: Only runs if Pylint passes (no critical errors)
- **Blocking**: ❌ **Any test failures block the pipeline**
- **Coverage**: All 284+ unit tests must pass
- **Output**: Detailed test results and failure information

#### CI Status Summary
- **Purpose**: Provides overall pipeline status and summary
- **Output**: Complete CI results overview

### 2. Standalone Pylint Analysis (`pylint.yml`)

**Triggers:**
- Manual workflow dispatch
- Weekly schedule (Sundays at 2 AM UTC)

**Purpose**: Detailed Pylint analysis for code quality monitoring outside of PR checks.

## Branch Protection Rules

The CI pipeline enforces the following requirements for pull requests:

### Required Status Checks
- ✅ **Pylint**: Must pass (no critical errors)
- ✅ **Unit Tests**: All tests must pass
- ✅ **CI Status Summary**: Overall pipeline must succeed

### Merge Requirements
1. All CI checks must pass
2. At least one approval from code reviewer (recommended)
3. Branch must be up to date with target branch

## Developer Workflow

### Before Creating a Pull Request

1. **Run Local CI Checks** (recommended):
   ```bash
   ./run_local_ci.sh
   ```
   This runs the same checks as the CI pipeline locally.

2. **Fix Any Issues**:
   - Address Pylint critical errors
   - Fix failing unit tests
   - Consider addressing warnings and conventions

3. **Create Pull Request**:
   - CI will automatically run
   - Check results in the "Actions" tab
   - Address any failures before requesting review

### Understanding CI Results

#### ✅ Success States
- **Green checkmark**: All checks passed, ready for review
- **Pylint passed**: No critical errors found
- **Unit tests passed**: All 284+ tests successful

#### ❌ Failure States
- **Red X**: Critical issues found, PR blocked
- **Pylint failed**: Critical errors must be fixed
- **Unit tests failed**: Broken functionality must be repaired

#### ⚠️ Warning States
- **Yellow warning**: Non-critical issues found
- **Pylint warnings**: Should be addressed but don't block merge
- **Skipped tests**: Previous job failed, tests didn't run

## Local Development

### Setup for Local CI Testing

1. **Ensure virtual environment is active**:
   ```bash
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run local checks**:
   ```bash
   # Run both Pylint and tests
   ./run_local_ci.sh

   # Or run individually:
   ./run_pylint.sh           # Pylint only
   python tests/run_unit_tests.py  # Tests only
   ```

### Understanding Pylint Exit Codes

- `0`: No issues found ✅
- `1`: Fatal message ❌ (blocks CI)
- `2`: Error ❌ (blocks CI)
- `4`: Warning ⚠️ (reported, doesn't block)
- `8`: Refactor suggestion ℹ️ (informational)
- `16`: Convention issue 📝 (informational)
- `32`: Usage error ❌ (blocks CI)

Combinations like `24` (4+8+16) indicate multiple issue types.

## CI Configuration Files

### `.github/workflows/ci.yml`
Main CI pipeline configuration with job dependencies and comprehensive error handling.

### `.github/workflows/pylint.yml`
Standalone Pylint analysis for detailed code quality monitoring.

### `.pylintrc`
Pylint configuration with project-specific rules and disabled checks.

### `run_local_ci.sh`
Local script to run CI checks before pushing code.

## Troubleshooting Common CI Issues

### Pylint Failures
```bash
# Run Pylint locally to see detailed errors
PYTHONPATH=python pylint --rcfile=.pylintrc python/**/*.py

# Focus on critical errors only
PYTHONPATH=python pylint --rcfile=.pylintrc --disable=C,W,R,I --enable=E python/**/*.py
```

### Unit Test Failures
```bash
# Run tests locally with detailed output
python tests/run_unit_tests.py

# Run specific test modules
python -m tests.unit.modules.test_specific_module
```

### Environment Issues
```bash
# Check Python path
echo $PYTHONPATH

# Verify virtual environment
which python
pip list
```

## Status Badges

The README includes CI status badges showing current build status:

- [![CI Status](https://github.com/ngroegli/askai-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/ngroegli/askai-cli/actions/workflows/ci.yml) - Main CI pipeline
- [![Code Quality](https://github.com/ngroegli/askai-cli/actions/workflows/pylint.yml/badge.svg)](https://github.com/ngroegli/askai-cli/actions/workflows/pylint.yml) - Code quality analysis

## Best Practices

1. **Always run local CI checks before pushing**
2. **Address Pylint critical errors immediately**
3. **Ensure all unit tests pass locally**
4. **Consider fixing warnings and conventions for better code quality**
5. **Keep pull requests focused and small for easier review**
6. **Write unit tests for new functionality**
7. **Update documentation when adding features**

## Getting Help

- **CI Pipeline Issues**: Check the Actions tab in GitHub for detailed logs
- **Local Development**: Use `./run_local_ci.sh` to reproduce CI environment
- **Test Failures**: Review test output for specific failure details
- **Pylint Issues**: Use the detailed Pylint workflow for comprehensive analysis
