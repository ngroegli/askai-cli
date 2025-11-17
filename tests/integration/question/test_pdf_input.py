"""
Integration tests for PDF handling in askai-cli.
"""
import os
from tests.integration.test_base import AutomatedTest
from tests.integration.test_utils import run_cli_command, verify_output_contains, verify_basic_json_format


class TestPdfInput(AutomatedTest):
    """Test PDF input handling in the CLI."""

    def run(self):
        """Run the test cases."""
        self._test_pdf_file_exists()
        self._test_pdf_analysis_basic()
        self._test_pdf_analysis_with_query()
        self._test_pdf_analysis_with_json()
        self._test_pdf_analysis_with_model()
        self._test_pdf_analysis_with_query_and_json()
        self._test_pdf_analysis_with_query_and_model()
        self._test_pdf_analysis_with_json_and_model()
        self._test_pdf_analysis_with_query_model_and_format()
        self._test_nonexistent_pdf()
        return self.results

    def _test_pdf_file_exists(self):
        """Test that the PDF test file exists and is accessible."""
        test_file = os.path.join("tests", "test_resources", "test.pdf")

        file_exists = os.path.isfile(test_file)
        file_details = {
            test_file: {
                "exists": file_exists,
                "absolute_path": os.path.abspath(test_file) if file_exists else "N/A"
            }
        }

        self.add_result(
            "pdf_test_file_exists",
            file_exists,
            "Test PDF file exists and is accessible" if file_exists else "Test PDF file not found",
            {
                "command": "File existence check",
                "file": file_details,
                "note": "This file is used for PDF handling tests"
            }
        )

    def _test_pdf_analysis_basic(self):
        """Test basic PDF analysis without additional parameters."""
        test_pdf_path = os.path.join("tests", "test_resources", "test.pdf")

        # Run PDF analysis without query
        stdout, stderr, return_code = run_cli_command(["-pdf", test_pdf_path])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM",
        ]

        success, missing = verify_output_contains(stdout, expected_patterns)
        no_errors = return_code == 0
        test_success = success and no_errors

        self.add_result(
            "pdf_analysis_basic",
            test_success,
            "Basic PDF analysis detected Lorem Ipsum text" if test_success
            else f"Basic PDF analysis failed - Lorem Ipsum not found: {missing}" if not success
            else "Basic PDF analysis failed - command returned error",
            {
                "command": f"askai.py -pdf {test_pdf_path}",
                "lorem_ipsum_found": success,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_pdf_analysis_with_query(self):
        """Test PDF analysis with specific query."""
        test_pdf_path = os.path.join("tests", "test_resources", "test.pdf")
        query = "What text content do you see in this PDF document?"

        # Run PDF analysis with query
        stdout, stderr, return_code = run_cli_command(["-pdf", test_pdf_path, "-q", query])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM",
        ]

        success, missing = verify_output_contains(stdout, expected_patterns)
        no_errors = return_code == 0
        test_success = success and no_errors

        self.add_result(
            "pdf_analysis_with_query",
            test_success,
            "PDF analysis with query detected Lorem Ipsum text" if test_success
            else f"PDF analysis with query failed - Lorem Ipsum not found: {missing}" if not success
            else "PDF analysis with query failed - command returned error",
            {
                "command": f"askai.py -pdf {test_pdf_path} -q \"{query}\"",
                "lorem_ipsum_found": success,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_pdf_analysis_with_json(self):
        """Test PDF analysis with JSON output format."""
        test_pdf_path = os.path.join("tests", "test_resources", "test.pdf")

        # Run PDF analysis with JSON format
        stdout, stderr, return_code = run_cli_command(["-pdf", test_pdf_path, "-f", "json"])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM",
        ]

        lorem_success, lorem_missing = verify_output_contains(stdout, expected_patterns)

        # Check JSON format validation
        json_valid, json_reason = verify_basic_json_format(stdout)

        no_errors = return_code == 0
        test_success = lorem_success and no_errors and json_valid

        self.add_result(
            "pdf_analysis_with_json",
            test_success,
            "PDF analysis with JSON format detected Lorem Ipsum text" if test_success
            else f"PDF analysis with JSON format failed - Lorem Ipsum not found: {lorem_missing}" if not lorem_success
            else "PDF analysis with JSON format failed - invalid JSON format" if not json_valid
            else "PDF analysis with JSON format failed - command returned error",
            {
                "command": f"askai.py -pdf {test_pdf_path} -f \"json\"",
                "lorem_ipsum_found": lorem_success,
                "json_valid": json_valid,
                "json_reason": json_reason,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_pdf_analysis_with_model(self):
        """Test PDF analysis with specific model."""
        test_pdf_path = os.path.join("tests", "test_resources", "test.pdf")
        model_name = "anthropic/claude-3-haiku"

        # Run PDF analysis with specific model
        stdout, stderr, return_code = run_cli_command(["-pdf", test_pdf_path, "-m", model_name])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM",
        ]

        success, missing = verify_output_contains(stdout, expected_patterns)
        no_errors = return_code == 0
        test_success = success and no_errors

        self.add_result(
            "pdf_analysis_with_model",
            test_success,
            "PDF analysis with model detected Lorem Ipsum text" if test_success
            else f"PDF analysis with model failed - Lorem Ipsum not found: {missing}" if not success
            else "PDF analysis with model failed - command returned error",
            {
                "command": f"askai.py -pdf {test_pdf_path} -m \"{model_name}\"",
                "lorem_ipsum_found": success,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_pdf_analysis_with_query_and_json(self):
        """Test PDF analysis with query and JSON format."""
        test_pdf_path = os.path.join("tests", "test_resources", "test.pdf")
        query = "Analyze the text content in this PDF document"

        # Run PDF analysis with query and JSON format
        stdout, stderr, return_code = run_cli_command(["-pdf", test_pdf_path, "-q", query, "-f", "json"])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM",
        ]

        lorem_success, lorem_missing = verify_output_contains(stdout, expected_patterns)

        # Check JSON format validation
        json_valid, json_reason = verify_basic_json_format(stdout)

        no_errors = return_code == 0
        test_success = lorem_success and no_errors and json_valid

        self.add_result(
            "pdf_analysis_with_query_and_json",
            test_success,
            "PDF analysis with query and JSON detected Lorem Ipsum text" if test_success
            else f"PDF analysis with query and JSON failed - Lorem Ipsum not found: {lorem_missing}" if not lorem_success
            else "PDF analysis with query and JSON failed - invalid JSON format" if not json_valid
            else "PDF analysis with query and JSON failed - command returned error",
            {
                "command": f"askai.py -pdf {test_pdf_path} -q \"{query}\" -f \"json\"",
                "lorem_ipsum_found": lorem_success,
                "json_valid": json_valid,
                "json_reason": json_reason,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_pdf_analysis_with_query_and_model(self):
        """Test PDF analysis with query and specific model."""
        test_pdf_path = os.path.join("tests", "test_resources", "test.pdf")
        query = "What text content do you see in this PDF document?"
        model_name = "anthropic/claude-3-haiku"

        # Run PDF analysis with query and model
        stdout, stderr, return_code = run_cli_command(["-pdf", test_pdf_path, "-q", query, "-m", model_name])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM",
        ]

        success, missing = verify_output_contains(stdout, expected_patterns)
        no_errors = return_code == 0
        test_success = success and no_errors

        self.add_result(
            "pdf_analysis_with_query_and_model",
            test_success,
            "PDF analysis with query and model detected Lorem Ipsum text" if test_success
            else f"PDF analysis with query and model failed - Lorem Ipsum not found: {missing}" if not success
            else "PDF analysis with query and model failed - command returned error",
            {
                "command": f"askai.py -pdf {test_pdf_path} -q \"{query}\" -m \"{model_name}\"",
                "lorem_ipsum_found": success,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_pdf_analysis_with_json_and_model(self):
        """Test PDF analysis with JSON format and specific model."""
        test_pdf_path = os.path.join("tests", "test_resources", "test.pdf")
        model_name = "anthropic/claude-3-haiku"

        # Run PDF analysis with JSON format and model
        stdout, stderr, return_code = run_cli_command(["-pdf", test_pdf_path, "-f", "json", "-m", model_name])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM",
        ]

        lorem_success, lorem_missing = verify_output_contains(stdout, expected_patterns)

        # Check JSON format validation
        json_valid, json_reason = verify_basic_json_format(stdout)

        no_errors = return_code == 0
        test_success = lorem_success and no_errors and json_valid

        self.add_result(
            "pdf_analysis_with_json_and_model",
            test_success,
            "PDF analysis with JSON and model detected Lorem Ipsum text" if test_success
            else f"PDF analysis with JSON and model failed - Lorem Ipsum not found: {lorem_missing}" if not lorem_success
            else "PDF analysis with JSON and model failed - invalid JSON format" if not json_valid
            else "PDF analysis with JSON and model failed - command returned error",
            {
                "command": f"askai.py -pdf {test_pdf_path} -f \"json\" -m \"{model_name}\"",
                "lorem_ipsum_found": lorem_success,
                "json_valid": json_valid,
                "json_reason": json_reason,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_pdf_analysis_with_query_model_and_format(self):
        """Test PDF analysis with all options: query, JSON format, and model."""
        test_pdf_path = os.path.join("tests", "test_resources", "test.pdf")
        query = "Analyze all text content in this PDF document"
        model_name = "anthropic/claude-3-haiku"

        # Run PDF analysis with all options
        stdout, stderr, return_code = run_cli_command(["-pdf", test_pdf_path, "-q", query, "-f", "json", "-m", model_name])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM",
        ]

        lorem_success, lorem_missing = verify_output_contains(stdout, expected_patterns)

        # Check JSON format validation
        json_valid, json_reason = verify_basic_json_format(stdout)

        no_errors = return_code == 0
        test_success = lorem_success and no_errors and json_valid

        self.add_result(
            "pdf_analysis_with_all_options",
            test_success,
            "PDF analysis with all options detected Lorem Ipsum text" if test_success
            else f"PDF analysis with all options failed - Lorem Ipsum not found: {lorem_missing}" if not lorem_success
            else "PDF analysis with all options failed - invalid JSON format" if not json_valid
            else "PDF analysis with all options failed - command returned error",
            {
                "command": f"askai.py -pdf {test_pdf_path} -q \"{query}\" -f \"json\" -m \"{model_name}\"",
                "lorem_ipsum_found": lorem_success,
                "json_valid": json_valid,
                "json_reason": json_reason,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_nonexistent_pdf(self):
        """Test error handling for nonexistent PDF files."""
        nonexistent_path = os.path.join("tests", "test_resources", "nonexistent.pdf")

        # Run command with nonexistent PDF - should produce an error
        stdout, stderr, return_code = run_cli_command(["-pdf", nonexistent_path])

        # Check for appropriate error messages
        error_patterns = [
            r"WARNING|[Ff]ile not found|[Nn]o such file|[Dd]oes not exist",
        ]

        error_found, missing = verify_output_contains(stdout + stderr, error_patterns)
        error_return_code = return_code != 0
        test_success = error_found or error_return_code

        self.add_result(
            "nonexistent_pdf_error",
            test_success,
            "Nonexistent PDF properly handled with error" if test_success
            else f"Nonexistent PDF not handled properly - no error detected: {missing}",
            {
                "command": f"askai.py -pdf {nonexistent_path}",
                "error_found": error_found,
                "error_return_code": error_return_code,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr[:500] + ("..." if len(stderr) > 500 else ""),
                "return_code": return_code
            }
        )
