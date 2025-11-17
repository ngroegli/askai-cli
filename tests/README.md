````markdown
# Integration Tests for askai-cli

This directory contains integration tests for the askai command-line interface.

## Test Structure

- `run_integration_tests.py` - Main entry point for running tests
- `integration/` - Contains all integration test modules
  - `test_utils.py` - Common utility functions for testing
  - `test_base.py` - Base classes for automated and semi-automated tests
  - `general/` - Tests for general CLI functionality
    - `test_cli_help.py` - Tests for CLI help functionality
    - `test_cli_error_handling.py` - Tests for error handling
    - `test_cli_openrouter.py` - Tests for OpenRouter API integration
  - `question/` - Tests for question-asking functionality
    - `test_basic_chat.py` - Tests for basic chat functionality
    - `test_persistent_chat.py` - Tests for persistent chat
    - `test_file_input.py` - Tests for file input
    - `test_url_input.py` - Tests for URL input
  - `pattern/` - Tests for pattern functionality
    - `test_pattern_list.py` - Tests for pattern listing
    - `test_pattern_view.py` - Tests for pattern viewing

## Running Tests

### Using the Makefile

To run all integration tests:

```bash
make test-integration
```

To run only automated tests:

```bash
make test-integration-automated
```

To run only semi-automated tests:

```bash
make test-integration-semi
```

To run tests from a specific category:

```bash
make test-integration-general
make test-integration-question
make test-integration-pattern
```

To run a specific test:

```bash
make test-integration-general_testclihelp
```

To list all available tests:

```bash
make list-tests
```

### Using Python Directly

You can also run tests directly with Python:

```bash
python tests/run_integration_tests.py
```

With command-line options:

```bash
# Run a specific test
python tests/run_integration_tests.py --test general_testclihelp

# Run only automated tests
python tests/run_integration_tests.py --automated-only

# Run only semi-automated tests
python tests/run_integration_tests.py --semi-automated-only

# Run tests from a specific category
python tests/run_integration_tests.py --category general

# List all available tests
python tests/run_integration_tests.py --list
```

## Adding New Tests

To add new tests:

1. Create a new test module in the `tests/integration/` directory
2. Extend either `AutomatedTest` or `SemiAutomatedTest` based on the test type
3. Implement the `run()` method to perform the test
4. Add your test class to the `tests` dictionary in `run_integration_tests.py`

### Example:

```python
from tests.integration.test_base import AutomatedTest
from tests.integration.test_utils import run_cli_command, verify_output_contains

class TestMyFeature(AutomatedTest):
    """Test a specific feature of askai-cli."""
    
    def run(self):
        """Run the test cases."""
        # Implement your test cases
        # ...
        return self.results
```

## Types of Tests

### Automated Tests

Fully automated tests that require no user interaction. These tests should have 
clear pass/fail criteria that can be determined programmatically.

### Semi-automated Tests

Tests that require some user interaction or manual validation. These are useful for
testing features where the output needs human verification or where input from the
user is required during the test.
