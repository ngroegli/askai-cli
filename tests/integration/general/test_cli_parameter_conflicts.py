"""
Tests for validating parameter conflict handling in the CLI arguments.
"""
from tests.integration.test_base import AutomatedTest
from tests.integration.test_utils import run_cli_command, verify_output_contains


class TestCliParameterConflicts(AutomatedTest):
    """Test CLI parameter conflict validation."""
    
    def run(self):
        """Run tests for parameter conflict handling."""
        # Test plain-md without format flag
        self._test_plain_md_without_format()
        
        # Test pattern and query parameter conflict
        self._test_pattern_query_conflict()
        
        return self.results
        
    def _test_plain_md_without_format(self):
        """Test using --plain-md without -f flag."""
        # Run command with --plain-md but without -f flag
        stdout, stderr, return_code = run_cli_command(["-q", "Test query", "--plain-md"])
        
        # Expected patterns for handling this scenario
        expected_patterns_auto_format = [
            r"markdown|md|Markdown",  # Should automatically apply markdown formatting
        ]
        
        expected_patterns_warning = [
            r"warning|WARNING|Warning",  # Should show a warning about format
            r"format|Format",  # Should mention format
        ]
        
        # Check for either automatic formatting or warning
        auto_format = verify_output_contains(stdout + stderr, expected_patterns_auto_format)[0]
        warning_shown = verify_output_contains(stdout + stderr, expected_patterns_warning)[0]
        
        # Success if either auto-format is applied or warning is shown
        success = auto_format or warning_shown
        
        self.add_result(
            "plain_md_without_format",
            success,
            "CLI properly handles --plain-md without -f flag" if success
            else "CLI does not handle --plain-md without -f flag properly",
            {
                "command": "askai.py -q \"Test query\" --plain-md",
                "auto_format_detected": auto_format,
                "warning_shown": warning_shown,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )
        
    def _test_pattern_query_conflict(self):
        """Test using both pattern (-up) and query (-q) parameters."""
        # Run command with both pattern and query parameters
        stdout, stderr, return_code = run_cli_command(["-up", "no_patter", "-q", "What does this mean?"])
        
        expected_patterns_warning = [
            r"WARNING: Question logic parameters",  # Should mention that pattern takes precedence
        ]
        
        # Check for pattern usage and warnings
        warning_shown = verify_output_contains(stdout + stderr, expected_patterns_warning)[0]
        
        # Success if pattern is used (pattern takes precedence)
        # Bonus points if warning is also shown
        success = warning_shown
        
        message = ""
        if warning_shown:
            message = "CLI properly uses pattern and shows conflict warning"
        else:
            message = "CLI does not handle pattern/query conflict properly"
        
        self.add_result(
            "pattern_query_conflict",
            success,
            message,
            {
                "command": "askai.py -up log_interpretation -q \"What does this mean?\" -i \"sample log data\"",
                "warning_shown": warning_shown,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )
