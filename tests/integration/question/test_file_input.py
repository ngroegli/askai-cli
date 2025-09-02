"""
Tests for file input functionality.
"""
import os
import sys
from tests.integration.test_base import AutomatedTest
from tests.integration.test_utils import run_cli_command, verify_output_contains


class TestFileInput(AutomatedTest):
    """Test file input functionality."""
    
    def run(self):
        """Run the test cases."""
        # Test missing question with file input
        self._test_file_input_missing_question()
        
        # Test valid question with valid file
        self._test_file_input_valid()
        
        # Test valid question but non-existent file
        self._test_file_input_missing_file()
        
        # Test valid file but missing -q flag
        self._test_file_input_missing_q_flag()
        
        return self.results
        
    def _test_file_input_missing_question(self):
        """Test that file input flag is recognized."""
        # Create a temporary test file
        test_file_path = os.path.join(sys.path[0], "tests/test_resources/test.txt") 
    
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
            "file_input_missing_question",
            success and return_code != 0,  # Should fail with error code
            "File input with missing question handled correctly" if success 
            else f"File input with missing question not handled correctly: {missing}",
            {
                "command": f"askai -q -fi {test_file_path}",
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )
                
    def _test_file_input_valid(self):
        """Test file input with valid question and existing file."""
        # Create a temporary test file
        test_file_path = os.path.join(sys.path[0], "tests/test_resources/test.txt") 

        # Run command with file input flag and valid question
        query = "Can you identify the text in this file?"
        stdout, stderr, return_code = run_cli_command(["-q", query, "-fi", test_file_path])
        
        # The command should be recognized
        expected_patterns = [
            r"lorem|Lorem",  # Should see reference to file
            r"ipsum|Ipsum",  # Should see reference to input
        ]
        
        success, missing = verify_output_contains(stdout, expected_patterns)
        
        self.add_result(
            "file_input_valid",
            success and return_code == 0,  # Should succeed
            "File input with valid question processed correctly" if success and return_code == 0
            else f"File input with valid question not processed correctly: {missing}",
            {
                "command": f"askai.py -q \"{query}\" -fi {test_file_path}",
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )
            
                
    def _test_file_input_missing_file(self):
        """Test file input with valid question but non-existent file."""
        # Use a file path that doesn't exist
        test_file_path = os.path.join(sys.path[0], "tests/test_resources/nonexistent_file.txt") 
        
        # Make sure the file doesn't actually exist
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            
        # Run command with file input flag, valid question, but non-existent file
        query = "Summarize this file"
        stdout, stderr, return_code = run_cli_command(["-q", query, "-fi", test_file_path])
        
        # The command shows a warning about the missing file but continues execution
        expected_patterns = [
            r"warning|WARNING",  # Should see a warning message
            r"file|File",        # Should mention file
            r"exist|found",      # Should indicate file not found
        ]
        
        success, missing = verify_output_contains(stdout + stderr, expected_patterns)
        
        self.add_result(
            "file_input_missing_file",
            success,  # Only check for the warning message, don't check return code
            "Non-existent file properly produces warning" if success 
            else f"Non-existent file warning not displayed correctly: {missing}",
            {
                "command": f"askai.py -q \"{query}\" -fi {test_file_path}",
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )
        
    def _test_file_input_missing_q_flag(self):
        """Test file input with valid file but missing -q flag."""
        # Create a temporary test file
        test_file_path = os.path.join(sys.path[0], "tests/test_resources/test.txt") 

        # Run command with file input flag but without -q flag
        stdout, stderr, return_code = run_cli_command(["-fi", test_file_path])
        
        # The command should fail with an error about the missing question
        expected_patterns = [
            r"error|ERROR",       # Should see an error message
            r"question|query|-q", # Should mention needing a question
        ]
        
        success, missing = verify_output_contains(stdout + stderr, expected_patterns)
        
        self.add_result(
            "file_input_missing_q_flag",
            success and return_code != 0,  # Should fail with error code
            "File input with missing -q flag handled correctly" if success and return_code != 0
            else f"File input with missing -q flag not handled correctly: {missing}",
            {
                "command": f"askai.py -fi {test_file_path}",
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )
