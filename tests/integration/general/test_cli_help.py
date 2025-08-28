"""
Integration tests for the askai CLI help functionality.
"""
from tests.integration.test_base import AutomatedTest
from tests.integration.test_utils import run_cli_command, verify_output_contains


class TestCliHelp(AutomatedTest):
    """Test the CLI help functionality."""
    
    def run(self):
        """Run the test cases."""
        # Test case 1: Running askai without arguments should show help
        self._test_askai_no_args()
        
        # Test case 2: Running askai -h
        self._test_askai_h_flag()
        
        # Test case 3: Running askai --help
        self._test_askai_help_flag()
        
        return self.results
        
    def _test_askai_no_args(self):
        """Test running askai with no arguments."""
        stdout, stderr, return_code = run_cli_command([])
        
        # Define expected patterns in the help output
        expected_patterns = [
            r"usage:",
            r"askai",
            r"options:"
        ]
        
        success, missing = verify_output_contains(stdout, expected_patterns)
        
        self.add_result(
            "askai_no_args",
            success,
            "Help information displayed correctly when running with no arguments" if success 
            else f"Missing expected content in help output: {missing}",
            {
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )
        
    def _test_askai_h_flag(self):
        """Test running askai -h."""
        stdout, stderr, return_code = run_cli_command(["-h"])
        
        # Define expected patterns in the help output
        expected_patterns = [
            r"usage:",
            r"askai",
            r"options:",
            r"-h, --help"
        ]
        
        success, missing = verify_output_contains(stdout, expected_patterns)
        
        self.add_result(
            "askai_h_flag",
            success,
            "Help information displayed correctly with -h flag" if success 
            else f"Missing expected content in help output: {missing}",
            {
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )
        
    def _test_askai_help_flag(self):
        """Test running askai --help."""
        stdout, stderr, return_code = run_cli_command(["--help"])
        
        # Define expected patterns in the help output
        expected_patterns = [
            r"usage:",
            r"askai",
            r"options:",
            r"-h, --help"
        ]
        
        success, missing = verify_output_contains(stdout, expected_patterns)
        
        self.add_result(
            "askai_help_flag",
            success,
            "Help information displayed correctly with --help flag" if success 
            else f"Missing expected content in help output: {missing}",
            {
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )
