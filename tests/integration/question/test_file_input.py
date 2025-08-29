"""
Tests for file input functionality.
"""
import os
from tests.integration.test_base import AutomatedTest
from tests.integration.test_utils import run_cli_command, verify_output_contains


class TestFileInput(AutomatedTest):
    """Test file input functionality."""
    
    def run(self):
        """Run the test cases."""
        # Test file input flag recognition
        self._test_file_input_flag()
        
        return self.results
        
    def _test_file_input_flag(self):
        """Test that file input flag is recognized."""
        # Create a temporary test file
        test_file_path = os.path.join(os.getcwd(), "test_file_input.txt") 
        try:
            # Create a simple test file
            with open(test_file_path, "w", encoding="utf-8") as f:
                f.write("This is a test file for integration testing.")
            
            # Run command with file input flag but no question
            # This should result in a structured error about needing a question
            stdout, stderr, return_code = run_cli_command(["-q", "-fi", test_file_path])
            
            # The command should fail with an error message about needing a question
            expected_patterns = [
                r"error|ERROR",  # Should see an error message
                r"question|query",  # Should mention needing a question
            ]
            
            success, missing = verify_output_contains(stdout + stderr, expected_patterns)
            
            self.add_result(
                "file_input_flag_recognition",
                success and return_code != 0,  # Should fail with error code
                "File input flag recognized correctly" if success 
                else f"File input flag not handled correctly: {missing}",
                {
                    "command": f"askai.py -q -fi {test_file_path}",
                    "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                    "stderr": stderr if stderr else "No errors",
                    "return_code": return_code
                }
            )
            
        finally:
            # Clean up the test file
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
