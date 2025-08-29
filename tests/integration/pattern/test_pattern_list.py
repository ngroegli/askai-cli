"""
Integration tests for pattern-related CLI commands.
"""
from tests.integration.test_base import AutomatedTest
from tests.integration.test_utils import run_cli_command, verify_output_contains


class TestPatternList(AutomatedTest):
    """Test the CLI pattern listing functionality."""
    
    def run(self):
        """Run the test cases."""
        # Test case 1: Running askai -lp
        self._test_list_patterns()
        
        # Test case 2: Running askai --list-patterns
        self._test_list_patterns_longhand()
        
        return self.results
        
    def _test_list_patterns(self):
        """Test running 'askai -lp'."""
        stdout, stderr, return_code = run_cli_command(["-lp"])
        
        # Define expected patterns in the output
        expected_patterns = [
            r"pattern",  # There should be some reference to patterns
            r"available|Available",  # There should be some indication of availability
        ]
        
        success, missing = verify_output_contains(stdout, expected_patterns)
        
        self.add_result(
            "pattern_list_shorthand",
            success,
            "Pattern list displayed correctly with -lp flag" if success 
            else f"Missing expected content in pattern list output: {missing}",
            {
                "command": "askai.py -lp",
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )
        
    def _test_list_patterns_longhand(self):
        """Test running 'askai --list-patterns'."""
        stdout, stderr, return_code = run_cli_command(["--list-patterns"])
        
        # Define expected patterns in the output
        expected_patterns = [
            r"pattern",  # There should be some reference to patterns
            r"available|Available",  # There should be some indication of availability
        ]
        
        success, missing = verify_output_contains(stdout, expected_patterns)
        
        self.add_result(
            "pattern_list_longhand",
            success,
            "Pattern list displayed correctly with --list-patterns flag" if success 
            else f"Missing expected content in pattern list output: {missing}",
            {
                "command": "askai.py --list-patterns",
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )
