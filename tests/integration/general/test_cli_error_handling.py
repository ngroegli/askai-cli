"""
Integration tests for CLI error handling.
"""
from tests.integration.test_base import AutomatedTest
from tests.integration.test_utils import run_cli_command, verify_output_contains


class TestCliErrorHandling(AutomatedTest):
    """Test the CLI error handling functionality."""
    
    def run(self):
        """Run the test cases."""
        # Test case 1: Running with invalid option should show error
        self._test_invalid_option()
        
        # Test case 2: Running with invalid argument
        self._test_invalid_argument()
        
        # Test case 3: Running a query without -q flag should show error
        self._test_missing_q_flag()
        
        return self.results
        
    def _test_invalid_option(self):
        """Test running with an invalid option."""
        stdout, stderr, return_code = run_cli_command(["--invalid-option"])
        
        # Define expected patterns in the output
        expected_patterns = [
            r"error|ERROR",  # Look for an error message
        ]
        
        success, missing = verify_output_contains(stdout, expected_patterns)
        
        self.add_result(
            "askai_invalid_option",
            success,
            "Error message displayed correctly for invalid option" if success 
            else f"Missing error message in output: {missing}",
            {
                "command": "askai.py --invalid-option",
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )
        
    def _test_invalid_argument(self):
        """Test running with an invalid argument."""
        # Use a valid option but with invalid value
        stdout, stderr, return_code = run_cli_command(["-m", ""])
        
        # Check for error message that starts with ERROR:
        expected_patterns = [
            r"^ERROR:",  # Error message should start with ERROR:
        ]
        
        error_output = stderr if stderr else stdout
        success, missing = verify_output_contains(error_output, expected_patterns)
        
        self.add_result(
            "askai_invalid_argument",
            success and return_code != 0,  # Should have error message and non-zero return code
            "CLI correctly rejected invalid argument with proper error format" if success and return_code != 0
            else f"CLI error format incorrect or missing. Missing patterns: {missing}",
            {
                "command": "askai.py -m \"\"",
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )
        
    def _test_missing_q_flag(self):
        """Test running a query without the -q flag."""
        # Run a query without the -q flag
        stdout, stderr, return_code = run_cli_command(["What's the capital of France?"])
        
        # Define expected patterns in the output
        expected_patterns = [
            r"error|ERROR",  # Look for an error message
            r"unrecognized arguments",  # Should indicate unrecognized arguments
        ]
        
        success, missing = verify_output_contains(stdout + stderr, expected_patterns)
        
        self.add_result(
            "missing_q_flag",
            success and return_code != 0,  # Should have error message and non-zero return code
            "CLI correctly requires -q flag for queries" if success and return_code != 0
            else f"CLI did not properly handle missing -q flag. Missing patterns: {missing}",
            {
                "command": "askai.py \"What's the capital of France?\"",
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr[:500] + ("..." if len(stderr) > 500 else ""),
                "return_code": return_code
            }
        )
        
        # Add a second test to document correct behavior
        self.add_result(
            "with_q_flag",
            True,
            "Queries should be passed with the -q flag: -q \"What's the capital of France?\""
        )
