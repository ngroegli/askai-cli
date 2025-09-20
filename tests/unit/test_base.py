"""
Base classes and utilities for unit tests.
"""
from unittest.mock import Mock
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod


class TestResult:
    """Represents a single test result."""

    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.message = ""
        self.details = {}

    def set_passed(self, message: str = "Test passed"):
        """Mark the test as passed."""
        self.passed = True
        self.message = message

    def set_failed(self, message: str = "Test failed"):
        """Mark the test as failed."""
        self.passed = False
        self.message = message

    def add_detail(self, key: str, value: Any):
        """Add a detail to the test result."""
        self.details[key] = value

    def __str__(self):
        """String representation of the test result."""
        status = "PASS" if self.passed else "FAIL"

        # ANSI color codes
        GREEN = "\033[92m"  # Bright green
        RED = "\033[91m"    # Bright red
        RESET = "\033[0m"   # Reset color

        # Color the status
        if self.passed:
            colored_status = f"{GREEN}{status}{RESET}"
        else:
            colored_status = f"{RED}{status}{RESET}"

        result_str = f"{self.name}: {colored_status} - {self.message}"

        # Add details if present
        if self.details:
            result_str += "\n  Details:"
            for key, value in self.details.items():
                result_str += f"\n    {key}: {value}"

        return result_str


class BaseUnitTest(ABC):
    """Base class for all unit tests."""

    def __init__(self):
        self.name = self.__class__.__name__
        self.results = []
        self._setup_mocks()

    def _setup_mocks(self):
        """Setup common mocks used across tests."""
        self.mock_logger = Mock()
        self.mock_config = {
            'openrouter_api_key': 'test-key',
            'model': 'test-model',
            'askai_dir': '/tmp/test-askai',
            'patterns_dir': '/tmp/test-patterns'
        }

    @abstractmethod
    def run(self) -> List[TestResult]:
        """Run the test and return results."""

    def add_result(self, test_name: str, passed: bool, message: str, details: Optional[Dict[str, Any]] = None):
        """Add a test result."""
        result = TestResult(test_name)
        if passed:
            result.set_passed(message)
        else:
            result.set_failed(message)

        if details:
            for k, v in details.items():
                result.add_detail(k, v)

        self.results.append(result)
        return result

    def assert_equal(self, expected, actual, test_name: str, message: str = ""):
        """Assert that expected equals actual."""
        passed = expected == actual
        details = {
            "expected": expected,
            "actual": actual,
            "match": passed
        }

        if passed:
            self.add_result(test_name, True, message or "Values match", details)
        else:
            self.add_result(test_name, False,
                          message or "Values do not match", details)
        return passed

    def assert_not_equal(self, expected, actual, test_name: str, message: str = ""):
        """Assert that expected does not equal actual."""
        passed = expected != actual
        details = {
            "expected_not": expected,
            "actual": actual,
            "different": passed
        }

        if passed:
            self.add_result(test_name, True, message or "Values differ as expected", details)
        else:
            self.add_result(test_name, False,
                          message or "Values should not be equal", details)
        return passed

    def assert_true(self, value, test_name: str, message: str = ""):
        """Assert that value is True."""
        passed = bool(value) is True
        details = {
            "value": value,
            "is_true": passed
        }

        if passed:
            self.add_result(test_name, True, message or "Value is True", details)
        else:
            self.add_result(test_name, False,
                          message or f"Value is not True: {value}", details)
        return passed

    def assert_false(self, value, test_name: str, message: str = ""):
        """Assert that value is False."""
        passed = bool(value) is False
        details = {
            "value": value,
            "is_false": passed
        }

        if passed:
            self.add_result(test_name, True, message or "Value is False", details)
        else:
            self.add_result(test_name, False,
                          message or f"Value is not False: {value}", details)
        return passed

    def assert_contains(self, container, item, test_name: str, message: str = ""):
        """Assert that container contains item."""
        passed = item in container
        details = {
            "container": container,
            "item": item,
            "contains": passed
        }

        if passed:
            self.add_result(test_name, True, message or "Item found in container", details)
        else:
            self.add_result(test_name, False,
                          message or "Item not found in container", details)
        return passed

    def assert_in(self, item, container, test_name: str, message: str = ""):
        """Assert that item is in container (alias for assert_contains with swapped parameters)."""
        passed = item in container
        details = {
            "item": item,
            "container": container,
            "in_container": passed
        }

        if passed:
            self.add_result(test_name, True, message or "Item found in container", details)
        else:
            self.add_result(test_name, False,
                          message or "Item not found in container", details)
        return passed

    def assert_not_none(self, value, test_name: str, message: str = ""):
        """Assert that value is not None."""
        passed = value is not None
        details = {
            "value": value,
            "is_not_none": passed
        }

        if passed:
            self.add_result(test_name, True, message or "Value is not None", details)
        else:
            self.add_result(test_name, False,
                          message or "Value is None", details)
        return passed

    def assert_raises(self, exception_class, callable_obj, test_name: str, message: str = ""):
        """Assert that calling callable_obj raises exception_class."""
        try:
            callable_obj()
            self.add_result(test_name, False,
                          message or f"Expected {exception_class.__name__} but no exception was raised")
            return False
        except exception_class:
            self.add_result(test_name, True,
                          message or f"Correctly raised {exception_class.__name__}")
            return True
        except Exception as e:
            self.add_result(test_name, False,
                          message or f"Expected {exception_class.__name__} but got {type(e).__name__}: {e}")
            return False

    def report(self):
        """Report the results of the test."""
        print(f"\n{'=' * 70}")
        print(f"Unit Test: {self.name}")
        print(f"{'=' * 70}")

        for result in self.results:
            print(result)
            print("-" * 70)

        # Summary with color formatting
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)

        # ANSI color codes
        GREEN = "\033[92m"  # Bright green
        RED = "\033[91m"    # Bright red
        RESET = "\033[0m"   # Reset color

        # Determine the color formatting based on test results
        if passed > 0 and failed == 0:
            # All tests passed - everything in green
            print(f"\nSummary: {GREEN}{passed} passed{RESET}, {GREEN}{failed} failed{RESET}")
        elif passed == 0 and failed > 0:
            # All tests failed - both numbers in red
            print(f"\nSummary: {RED}{passed} passed{RESET}, {RED}{failed} failed{RESET}")
        else:
            # Mixed results - passed in green, failed in red
            print(f"\nSummary: {GREEN}{passed} passed{RESET}, {RED}{failed} failed{RESET}")

        return passed, failed


class MockMixin:
    """Mixin class providing common mock utilities."""

    def mock_file_system(self):
        """Create mock file system operations."""
        return {
            'os.path.exists': Mock(return_value=True),
            'os.path.isfile': Mock(return_value=True),
            'os.path.isdir': Mock(return_value=True),
            'open': Mock(),
            'json.load': Mock(),
            'json.dump': Mock()
        }

    def mock_http_response(self, status_code=200, json_data=None, text=""):
        """Create a mock HTTP response."""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.json.return_value = json_data or {}
        mock_response.text = text
        return mock_response

    def mock_ai_response(self, content="Test AI response"):
        """Create a mock AI response."""
        return {
            'content': content,
            'model': 'test-model',
            'usage': {'tokens': 100}
        }
