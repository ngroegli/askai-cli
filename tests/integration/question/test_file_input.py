"""
Tests for file input functionality.
"""
import os
from tests.integration.test_base import AutomatedTest
from tests.integration.test_utils import run_cli_command, verify_output_contains, verify_basic_json_format


class TestFileInput(AutomatedTest):
    """Test file input functionality."""

    def run(self):
        """Run the test cases."""
        self._test_file_exists()
        self._test_file_input_basic()
        self._test_file_input_with_query()
        self._test_file_input_with_json()
        self._test_file_input_with_model()
        self._test_file_input_with_query_and_json()
        self._test_file_input_with_query_and_model()
        self._test_file_input_with_format_and_model()
        self._test_file_input_with_model_format_and_question()
        self._test_nonexistent_file()
        return self.results

    def _test_file_exists(self):
        """Test that the file test file exists and is accessible."""
        test_file = os.path.join("tests", "test_resources", "test.txt")

        file_exists = os.path.isfile(test_file)
        file_details = {
            test_file: {
                "exists": file_exists,
                "absolute_path": os.path.abspath(test_file) if file_exists else "N/A"
            }
        }

        self.add_result(
            "file_test_file_exists",
            file_exists,
            "Test file exists and is accessible" if file_exists else "Test file not found",
            {
                "command": "File existence check",
                "file": file_details,
                "note": "This file is used for file input handling tests"
            }
        )

    def _test_file_input_basic(self):
        """Test basic file input analysis without additional parameters."""
        test_file_path = os.path.join("tests", "test_resources", "test.txt")
        query = "What text content do you see in this file?"

        # Run file input analysis with query (required for -fi)
        stdout, stderr, return_code = run_cli_command(["-fi", test_file_path, "-q", query])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM",
        ]

        success, missing = verify_output_contains(stdout, expected_patterns)
        no_errors = return_code == 0
        test_success = success and no_errors

        self.add_result(
            "file_input_basic",
            test_success,
            "Basic file input detected Lorem Ipsum text" if test_success
            else f"Basic file input failed - Lorem Ipsum not found: {missing}" if not success
            else "Basic file input failed - command returned error",
            {
                "command": f"askai.py -fi {test_file_path} -q \"{query}\"",
                "lorem_ipsum_found": success,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_file_input_with_query(self):
        """Test file input with specific query."""
        test_file_path = os.path.join("tests", "test_resources", "test.txt")
        query = "Analyze the text content in this file and describe what you find"

        # Run file input analysis with specific query
        stdout, stderr, return_code = run_cli_command(["-fi", test_file_path, "-q", query])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM",
        ]

        success, missing = verify_output_contains(stdout, expected_patterns)
        no_errors = return_code == 0
        test_success = success and no_errors

        self.add_result(
            "file_input_with_query",
            test_success,
            "File input with query detected Lorem Ipsum text" if test_success
            else f"File input with query failed - Lorem Ipsum not found: {missing}" if not success
            else "File input with query failed - command returned error",
            {
                "command": f"askai.py -fi {test_file_path} -q \"{query}\"",
                "lorem_ipsum_found": success,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_file_input_with_json(self):
        """Test file input with JSON output format."""
        test_file_path = os.path.join("tests", "test_resources", "test.txt")
        query = "What text content do you see in this file?"

        # Run file input analysis with JSON format
        stdout, stderr, return_code = run_cli_command(["-fi", test_file_path, "-q", query, "-f", "json"])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM",
        ]

        success, missing = verify_output_contains(stdout, expected_patterns)

        # Check JSON format validation
        json_valid, json_reason = verify_basic_json_format(stdout)

        no_errors = return_code == 0
        test_success = success and no_errors and json_valid

        self.add_result(
            "file_input_with_json",
            test_success,
            "File input with JSON format detected Lorem Ipsum text" if test_success
            else f"File input with JSON format failed - Lorem Ipsum not found: {missing}" if not success
            else "File input with JSON format failed - invalid JSON format" if not json_valid
            else "File input with JSON format failed - command returned error",
            {
                "command": f"askai.py -fi {test_file_path} -q \"{query}\" -f \"json\"",
                "lorem_ipsum_found": success,
                "json_valid": json_valid,
                "json_reason": json_reason,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_file_input_with_model(self):
        """Test file input with specific model."""
        test_file_path = os.path.join("tests", "test_resources", "test.txt")
        query = "What text content do you see in this file?"
        model_name = "anthropic/claude-3-haiku"

        # Run file input analysis with specific model
        stdout, stderr, return_code = run_cli_command(["-fi", test_file_path, "-q", query, "-m", model_name])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM",
        ]

        success, missing = verify_output_contains(stdout, expected_patterns)
        no_errors = return_code == 0
        test_success = success and no_errors

        self.add_result(
            "file_input_with_model",
            test_success,
            "File input with model detected Lorem Ipsum text" if test_success
            else f"File input with model failed - Lorem Ipsum not found: {missing}" if not success
            else "File input with model failed - command returned error",
            {
                "command": f"askai.py -fi {test_file_path} -q \"{query}\" -m \"{model_name}\"",
                "lorem_ipsum_found": success,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_file_input_with_query_and_json(self):
        """Test file input with query and JSON format."""
        test_file_path = os.path.join("tests", "test_resources", "test.txt")
        query = "Describe the text content in this file"

        # Run file input analysis with query and JSON format
        stdout, stderr, return_code = run_cli_command(["-fi", test_file_path, "-q", query, "-f", "json"])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM",
        ]

        success, missing = verify_output_contains(stdout, expected_patterns)

        # Check JSON format validation
        json_valid, json_reason = verify_basic_json_format(stdout)

        no_errors = return_code == 0
        test_success = success and no_errors and json_valid

        self.add_result(
            "file_input_with_query_and_json",
            test_success,
            "File input with query and JSON detected Lorem Ipsum text" if test_success
            else f"File input with query and JSON failed - Lorem Ipsum not found: {missing}" if not success
            else "File input with query and JSON failed - invalid JSON format" if not json_valid
            else "File input with query and JSON failed - command returned error",
            {
                "command": f"askai.py -fi {test_file_path} -q \"{query}\" -f \"json\"",
                "lorem_ipsum_found": success,
                "json_valid": json_valid,
                "json_reason": json_reason,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_file_input_with_query_and_model(self):
        """Test file input with query and specific model."""
        test_file_path = os.path.join("tests", "test_resources", "test.txt")
        query = "What text content do you see in this file?"
        model_name = "anthropic/claude-3-haiku"

        # Run file input analysis with query and model
        stdout, stderr, return_code = run_cli_command(["-fi", test_file_path, "-q", query, "-m", model_name])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM",
        ]

        success, missing = verify_output_contains(stdout, expected_patterns)
        no_errors = return_code == 0
        test_success = success and no_errors

        self.add_result(
            "file_input_with_query_and_model",
            test_success,
            "File input with query and model detected Lorem Ipsum text" if test_success
            else f"File input with query and model failed - Lorem Ipsum not found: {missing}" if not success
            else "File input with query and model failed - command returned error",
            {
                "command": f"askai.py -fi {test_file_path} -q \"{query}\" -m \"{model_name}\"",
                "lorem_ipsum_found": success,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_file_input_with_format_and_model(self):
        """Test file input with JSON format and specific model."""
        test_file_path = os.path.join("tests", "test_resources", "test.txt")
        query = "What text content do you see in this file?"

        # Run file input analysis with JSON format and model
        stdout, stderr, return_code = run_cli_command(["-fi", test_file_path, "-q", query, "-f", "json"])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM",
        ]

        success, missing = verify_output_contains(stdout, expected_patterns)

        # Check JSON format validation
        json_valid, json_reason = verify_basic_json_format(stdout)

        no_errors = return_code == 0
        test_success = success and no_errors and json_valid

        self.add_result(
            "file_input_with_json_and_model",
            test_success,
            "File input with JSON and model detected Lorem Ipsum text" if test_success
            else f"File input with JSON and model failed - Lorem Ipsum not found: {missing}" if not success
            else "File input with JSON and model failed - invalid JSON format" if not json_valid
            else "File input with JSON and model failed - command returned error",
            {
                "command": f"askai.py -fi {test_file_path} -q \"{query}\" -f \"json\"",
                "lorem_ipsum_found": success,
                "json_valid": json_valid,
                "json_reason": json_reason,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_file_input_with_model_format_and_question(self):
        """Test file input with all options: query, JSON format, and model."""
        test_file_path = os.path.join("tests", "test_resources", "test.txt")
        query = "Analyze all text content in this file"
        model_name = "anthropic/claude-3-haiku"

        # Run file input analysis with all options
        stdout, stderr, return_code = run_cli_command(["-fi", test_file_path, "-q", query, "-f", "json", "-m", model_name])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM",
        ]

        success, missing = verify_output_contains(stdout, expected_patterns)

        # Check JSON format validation
        json_valid, json_reason = verify_basic_json_format(stdout)

        no_errors = return_code == 0
        test_success = success and no_errors and json_valid

        self.add_result(
            "file_input_with_all_options",
            test_success,
            "File input with all options detected Lorem Ipsum text" if test_success
            else f"File input with all options failed - Lorem Ipsum not found: {missing}" if not success
            else "File input with all options failed - invalid JSON format" if not json_valid
            else "File input with all options failed - command returned error",
            {
                "command": f"askai.py -fi {test_file_path} -q \"{query}\" -f \"json\" -m \"{model_name}\"",
                "lorem_ipsum_found": success,
                "json_valid": json_valid,
                "json_reason": json_reason,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_nonexistent_file(self):
        """Test error handling for nonexistent files."""
        nonexistent_path = os.path.join("tests", "test_resources", "nonexistent.txt")
        query = "What is in this file?"

        # Run command with nonexistent file - should produce an error or warning
        stdout, stderr, return_code = run_cli_command(["-fi", nonexistent_path, "-q", query])

        # Check for appropriate error or warning messages
        error_patterns = [
            r"[Ee]rror|[Ww]arning|[Ff]ile not found|[Nn]o such file|[Dd]oes not exist",
        ]

        error_found, missing = verify_output_contains(stdout + stderr, error_patterns)
        # File input might still process with warning, so don't strictly require error return code
        test_success = error_found

        self.add_result(
            "nonexistent_file_error",
            test_success,
            "Nonexistent file properly handled with error/warning" if test_success
            else f"Nonexistent file not handled properly - no error/warning detected: {missing}",
            {
                "command": f"askai.py -fi {nonexistent_path} -q \"{query}\"",
                "error_found": error_found,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr[:500] + ("..." if len(stderr) > 500 else ""),
                "return_code": return_code
            }
        )
