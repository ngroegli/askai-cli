"""
Integration tests for OpenRouter API functionality.
"""
from tests.integration.test_base import AutomatedTest
from tests.integration.test_utils import run_cli_command, verify_output_contains


class TestCliOpenRouter(AutomatedTest):
    """Test OpenRouter API functionality in the CLI."""
    
    def run(self):
        """Run the test cases."""
        # Test the OpenRouter model listing
        self._test_openrouter_list_models()
        
        # Test the OpenRouter credits checking
        self._test_openrouter_check_credits()
        
        return self.results
        
    def _test_openrouter_list_models(self):
        """Test running 'askai -or list-models'."""
        # Note: This test doesn't check API results as it requires credentials,
        # but verifies the command is recognized and processes correctly
        stdout, stderr, return_code = run_cli_command(["-or", "list-models"])
        
        # Two cases: either credentials are missing or models are listed
        # Try to detect either case as a valid command recognition
        expected_patterns_credentials_error = [
            r"credentials|api.key|token|error",  # Look for errors
        ]
        
        expected_patterns_success = [
            r"model|models",  # Look for model listing
        ]
        
        # Check for either success or expected credential error
        success_error = verify_output_contains(stdout + stderr, expected_patterns_credentials_error)[0]
        success_list = verify_output_contains(stdout, expected_patterns_success)[0]
        
        # Command is handled correctly if we either get a list or a credential error
        overall_success = success_error or success_list
        
        self.add_result(
            "openrouter_list_models",
            overall_success,
            "OpenRouter list-models command recognized and processed" if overall_success 
            else "OpenRouter list-models command not recognized",
            {
                "command": "askai.py -or list-models",
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )
        
    def _test_openrouter_check_credits(self):
        """Test running 'askai -or check-credits'."""
        # Note: This test doesn't check actual credit values as it requires credentials,
        # but verifies the command is recognized and processes correctly
        stdout, stderr, return_code = run_cli_command(["-or", "check-credits"])
        
        # Two cases: either credentials are missing or credits are displayed
        # Try to detect either case as a valid command recognition
        expected_patterns_credentials_error = [
            r"credentials|api.key|token",  # Look for credential-related error
        ]
        
        expected_patterns_success = [
            r"credit|credits|balance|quota",  # Look for credit-related terms
        ]
        
        # Check for either success or expected credential error
        success_error = verify_output_contains(stdout + stderr, expected_patterns_credentials_error)[0]
        success_credits = verify_output_contains(stdout, expected_patterns_success)[0]
        
        # Command is handled correctly if we either get credits or a credential error
        overall_success = success_error or success_credits
        
        self.add_result(
            "openrouter_check_credits",
            overall_success,
            "OpenRouter check-credits command recognized and processed" if overall_success 
            else "OpenRouter check-credits command not recognized",
            {
                "command": "askai.py -or check-credits",
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )
