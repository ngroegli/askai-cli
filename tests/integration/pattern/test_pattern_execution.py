"""
Dynamic integration tests for all patterns in askai-cli.
"""
import os
import json
from tests.integration.test_base import AutomatedTest
from tests.integration.test_utils import run_cli_command, verify_output_contains


class TestPatternExecution(AutomatedTest):
    """Test execution of all patterns with dynamic configuration."""

    def __init__(self):
        super().__init__()
        self.config_file = os.path.join("tests", "test_resources", "test_pattern_config.json")
        self.patterns_config = self._load_pattern_config()

    def _load_pattern_config(self):
        """Load pattern configuration from JSON file."""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config.get('patterns', [])
        except Exception as e:
            self.add_result(
                "config_load_error",
                False,
                f"Failed to load pattern configuration: {str(e)}",
                {"config_file": self.config_file, "error": str(e)}
            )
            return []

    def run(self):
        """Run all pattern tests dynamically."""
        if not self.patterns_config:
            self.add_result(
                "no_patterns_configured",
                False,
                "No patterns found in configuration file",
                {"config_file": self.config_file}
            )
            return self.results

        # Test that configuration is loaded
        self.add_result(
            "pattern_config_loaded",
            True,
            f"Successfully loaded {len(self.patterns_config)} pattern configurations",
            {
                "config_file": self.config_file,
                "pattern_count": len(self.patterns_config),
                "patterns": [p['name'] for p in self.patterns_config]
            }
        )

        # Test that all configured patterns are available in CLI
        self._test_pattern_list_contains_configured_patterns()

        # Run each pattern test
        for pattern_config in self.patterns_config:
            self._test_pattern_execution(pattern_config)

        return self.results

    def _test_pattern_execution(self, pattern_config):
        """Test execution of a single pattern."""
        pattern_name = pattern_config.get('name', 'unknown')
        description = pattern_config.get('description', 'No description provided')
        pattern_input = pattern_config.get('input', '')
        expected_patterns = pattern_config.get('expected_patterns', [])

        if not pattern_input:
            self.add_result(
                f"pattern_{pattern_name}_no_input",
                False,
                f"No input configured for pattern {pattern_name}",
                {"pattern": pattern_name, "description": description}
            )
            return

        if not expected_patterns:
            self.add_result(
                f"pattern_{pattern_name}_no_expectations",
                False,
                f"No expected patterns configured for pattern {pattern_name}",
                {"pattern": pattern_name, "description": description}
            )
            return

        # Execute the pattern with input and auto-decline follow-ups
        cmd_args = ["-up", pattern_name, "-pi", json.dumps(pattern_input)]

        # Provide input to decline any follow-up questions
        input_text = "n\n" * 10  # Provide multiple "n" responses for any follow-up questions

        try:
            stdout, stderr, return_code = run_cli_command(cmd_args, input_text=input_text)

            # Check if command executed successfully
            command_success = return_code == 0

            # Check if expected patterns are found in output
            patterns_found = []
            patterns_missing = []

            for pattern_group in expected_patterns:
                # Each pattern group is separated by | for OR logic
                # Check both stdout and stderr for patterns
                combined_output = stdout + "\n" + stderr
                found, missing = verify_output_contains(combined_output, [pattern_group])
                if found:
                    patterns_found.append(pattern_group)
                else:
                    patterns_missing.extend(missing)

            # Test is successful if command runs and at least some expected patterns are found
            pattern_success = len(patterns_found) > 0
            overall_success = command_success and pattern_success

            # Determine the appropriate message
            if overall_success:
                message = f"Pattern {pattern_name} executed successfully with expected content"
            elif not command_success:
                message = f"Pattern {pattern_name} failed to execute (return code: {return_code})"
            else:
                message = f"Pattern {pattern_name} executed but missing expected patterns: {patterns_missing}"

            self.add_result(
                f"pattern_{pattern_name}_execution",
                overall_success,
                message,
                {
                    "pattern": pattern_name,
                    "description": description,
                    "command": f"askai.py -up {pattern_name} -pi '{json.dumps(pattern_input)[:50]}...'",
                    "command_success": command_success,
                    "pattern_success": pattern_success,
                    "patterns_found": patterns_found,
                    "patterns_missing": patterns_missing[:3],  # Limit to first 3 missing
                    "return_code": return_code,
                    "stdout_preview": stdout[:300] + ("..." if len(stdout) > 300 else ""),
                    "stderr": stderr[:200] + ("..." if len(stderr) > 200 else "") if stderr else "No errors"
                }
            )

        except Exception as e:
            self.add_result(
                f"pattern_{pattern_name}_execution",
                False,
                f"Pattern {pattern_name} execution failed with exception: {str(e)}",
                {
                    "pattern": pattern_name,
                    "description": description,
                    "command": f"askai.py -up {pattern_name} -pi '{json.dumps(pattern_input)[:50]}...'",
                    "exception": str(e),
                    "error_type": type(e).__name__
                }
            )

    def _test_pattern_list_contains_configured_patterns(self):
        """Test that all configured patterns exist in the CLI pattern list."""
        try:
            # Get list of available patterns
            stdout, stderr, return_code = run_cli_command(["-lp"])

            if return_code != 0:
                self.add_result(
                    "pattern_list_availability",
                    False,
                    "Failed to retrieve pattern list from CLI",
                    {"return_code": return_code, "stderr": stderr}
                )
                return

            # Check if each configured pattern is in the list
            configured_names = [p['name'] for p in self.patterns_config]
            patterns_found = []
            patterns_missing = []

            for pattern_name in configured_names:
                if pattern_name in stdout:
                    patterns_found.append(pattern_name)
                else:
                    patterns_missing.append(pattern_name)

            all_found = len(patterns_missing) == 0

            self.add_result(
                "pattern_list_contains_configured",
                all_found,
                f"All {len(configured_names)} configured patterns found in CLI" if all_found
                else f"Missing {len(patterns_missing)} configured patterns from CLI",
                {
                    "configured_patterns": configured_names,
                    "patterns_found": patterns_found,
                    "patterns_missing": patterns_missing,
                    "total_configured": len(configured_names)
                }
            )

        except Exception as e:
            self.add_result(
                "pattern_list_availability",
                False,
                f"Exception while checking pattern list: {str(e)}",
                {"exception": str(e), "error_type": type(e).__name__}
            )
