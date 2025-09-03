"""
Automated integration tests for the chat functionality.
"""
from tests.integration.test_base import AutomatedTest
from tests.integration.test_utils import run_cli_command, verify_output_contains


class TestBasicChat(AutomatedTest):
    """Automated test for basic chat interaction with the CLI."""
    
    def run(self):
        """Run the test cases."""
        self._test_basic_chat()
        self._test_basic_chat_with_model()
        self._test_basic_chat_with_json_format()
        self._test_basic_chat_with_model_and_json()
        return self.results
        
    def _test_basic_chat(self):
        """Test a basic chat interaction."""
        # Simple test query about the capital of France
        query = "What's the capital of France?"
        
        # Run the command
        stdout, stderr, return_code = run_cli_command(["-q", query])
        
        # Check if "Paris" appears in the response
        expected_patterns = [
            r"Paris|paris|PARIS",  # Look for Paris in any case
        ]
        
        success, missing = verify_output_contains(stdout, expected_patterns)
        
        # Also check that the command executed without errors
        no_errors = return_code == 0
        
        # Test passes if Paris is mentioned and no errors occurred
        test_success = success and no_errors
        
        self.add_result(
            "basic_chat_interaction",
            test_success,
            "Basic chat correctly answered with Paris" if test_success
            else f"Basic chat failed - Paris not found: {missing}" if not success
            else "Basic chat failed - command returned error",
            {
                "command": f"askai.py -q \"{query}\"",
                "paris_found": success,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors", 
                "return_code": return_code
            }
        )

    def _test_basic_chat_with_model(self):
        """Test a basic chat interaction with specific model."""
        # Simple test query about the capital of France with model specification
        query = "What's the capital of France?"
        model_name = "anthropic/claude-3-haiku"
        
        # Run the command with model specification
        stdout, stderr, return_code = run_cli_command(["-q", query, "-m", model_name])
        
        # Check if "Paris" appears in the response
        expected_patterns = [
            r"Paris|paris|PARIS",  # Look for Paris in any case
        ]
        
        success, missing = verify_output_contains(stdout, expected_patterns)
        
        # Also check that the command executed without errors
        no_errors = return_code == 0
        
        # Test passes if Paris is mentioned and no errors occurred
        test_success = success and no_errors
        
        self.add_result(
            "basic_chat_with_model",
            test_success,
            "Basic chat with model correctly answered with Paris" if test_success
            else f"Basic chat with model failed - Paris not found: {missing}" if not success
            else "Basic chat with model failed - command returned error",
            {
                "command": f"askai.py -q \"{query}\" -m \"{model_name}\"",
                "paris_found": success,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors", 
                "return_code": return_code
            }
        )

    def _test_basic_chat_with_json_format(self):
        """Test a basic chat interaction with JSON output format."""
        # Simple test query about the capital of France with JSON format
        query = "What's the capital of France?"
        
        # Run the command with JSON format
        stdout, stderr, return_code = run_cli_command(["-q", query, "-f", "json"])
        
        # Check if "Paris" appears in the response
        expected_patterns = [
            r"Paris|paris|PARIS",  # Look for Paris in any case
        ]
        
        success, missing = verify_output_contains(stdout, expected_patterns)
        
        # Also check that the command executed without errors
        no_errors = return_code == 0
        
        # Test passes if Paris is mentioned and no errors occurred
        test_success = success and no_errors
        
        self.add_result(
            "basic_chat_with_json",
            test_success,
            "Basic chat with JSON format correctly answered with Paris" if test_success
            else f"Basic chat with JSON format failed - Paris not found: {missing}" if not success
            else "Basic chat with JSON format failed - command returned error",
            {
                "command": f"askai.py -q \"{query}\" -f \"json\"",
                "paris_found": success,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors", 
                "return_code": return_code
            }
        )

    def _test_basic_chat_with_model_and_json(self):
        """Test a basic chat interaction with both model and JSON format."""
        # Simple test query about the capital of France with model and JSON format
        query = "What's the capital of France?"
        model_name = "anthropic/claude-3-haiku"
        
        # Run the command with both model and JSON format
        stdout, stderr, return_code = run_cli_command(["-q", query, "-f", "json", "-m", model_name])
        
        # Check if "Paris" appears in the response
        expected_patterns = [
            r"Paris|paris|PARIS",  # Look for Paris in any case
        ]
        
        success, missing = verify_output_contains(stdout, expected_patterns)
        
        # Also check that the command executed without errors
        no_errors = return_code == 0
        
        # Test passes if Paris is mentioned and no errors occurred
        test_success = success and no_errors
        
        self.add_result(
            "basic_chat_with_model_and_json",
            test_success,
            "Basic chat with model and JSON format correctly answered with Paris" if test_success
            else f"Basic chat with model and JSON format failed - Paris not found: {missing}" if not success
            else "Basic chat with model and JSON format failed - command returned error",
            {
                "command": f"askai.py -q \"{query}\" -f \"json\" -m \"{model_name}\"",
                "paris_found": success,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors", 
                "return_code": return_code
            }
        )
