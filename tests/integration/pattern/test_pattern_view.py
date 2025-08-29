"""
Integration tests for pattern view functionality.
"""
from tests.integration.test_base import AutomatedTest
from tests.integration.test_utils import run_cli_command, verify_output_contains


class TestPatternView(AutomatedTest):
    """Test the pattern view functionality."""
    
    def run(self):
        """Run the test cases."""
        # Test case: Running askai -vp pattern_id
        self._test_view_pattern()
        
        return self.results
        
    def _test_view_pattern(self):
        """Test running 'askai -vp data_visualization'."""
        # Using a pattern that should exist in the default installation
        stdout, stderr, return_code = run_cli_command(["-vp", "data_visualization"])
        
        # Define expected patterns in the output
        expected_patterns = [
            r"name|Name",  # Should show pattern name
            r"description|Description",  # Should show pattern description
            r"data.visualization|Data.Visualization",  # Pattern specific content
        ]
        
        success, missing = verify_output_contains(stdout, expected_patterns)
        
        self.add_result(
            "view_pattern",
            success,
            "Pattern details displayed correctly" if success 
            else f"Missing expected content in pattern view: {missing}",
            {
                "command": "askai.py -vp data_visualization",
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )
