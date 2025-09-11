"""
Tests for URL input functionality.

I do not too many of these tests because URL inputs can be expensive
"""
from tests.integration.test_base import AutomatedTest
from tests.integration.test_utils import run_cli_command, verify_output_contains


class TestUrlInput(AutomatedTest):
    """Test URL input functionality."""

    def run(self):
        """Run the test cases."""
        # Test URL input flag recognition
        self._test_url_input_flag()

        return self.results

    def _test_url_input_flag(self):
        """Test that URL input flag is recognized."""
        # Use a reliable test URL
        test_url = "https://example.com"

        # Run command with URL flag but no question
        # This should result in a structured error or specific behavior
        stdout, stderr, return_code = run_cli_command(["-url", test_url])

        # Two possibilities: either a specific error about needing a question,
        # or it attempts to summarize the URL (which might require API keys)
        expected_patterns_error = [
            r"error|ERROR",  # Error message
            r"question|query",  # Should mention needing a question
        ]

        expected_patterns_attempt = [
            r"url|URL|website",  # Reference to URL processing
            r"example\.com",  # The URL being processed
        ]

        # Check for either possibility
        error_match = verify_output_contains(stdout + stderr, expected_patterns_error)[0]
        attempt_match = verify_output_contains(stdout, expected_patterns_attempt)[0]

        # Command is handled correctly if either condition is met
        success = error_match or attempt_match

        self.add_result(
            "url_input_flag_recognition",
            success,
            "URL input flag recognized correctly" if success
            else "URL input flag not handled correctly",
            {
                "command": "askai.py -url https://example.com",
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )
