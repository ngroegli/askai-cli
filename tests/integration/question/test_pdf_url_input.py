"""
Integration tests for PDF URL handling in askai-cli.
"""
from tests.integration.test_base import AutomatedTest
from tests.integration.test_utils import run_cli_command, verify_output_contains, verify_basic_json_format


class TestPdfUrlInput(AutomatedTest):
    """Test PDF URL input handling in the CLI."""

    # Global configurable URLs for testing
    # These should point to publicly accessible PDFs containing Lorem Ipsum text
    TEST_PDF_URLS = {
        "primary": "https://freetestdata.com/wp-content/uploads/2021/09/Free_Test_Data_100KB_PDF.pdf"
    }

    # URL for testing nonexistent/invalid PDFs
    INVALID_PDF_URL = "https://example.com/nonexistent/invalid.pdf"

    def run(self):
        """Run the test cases."""
        self._test_pdf_url_basic()
        self._test_pdf_url_analysis_with_query()
        self._test_pdf_url_analysis_with_json()
        self._test_pdf_url_analysis_with_model()
        self._test_pdf_url_analysis_with_query_and_json()
        self._test_pdf_url_analysis_with_query_and_model()
        self._test_pdf_url_analysis_with_json_and_model()
        self._test_pdf_url_analysis_with_query_model_and_format()
        self._test_missing_pdf_url()
        self._test_invalid_pdf_url()
        return self.results

    def _test_pdf_url_basic(self):
        """Test basic PDF URL analysis without additional parameters."""
        test_pdf_url = self.TEST_PDF_URLS["primary"]

        # Run PDF URL analysis
        stdout, stderr, return_code = run_cli_command(["-pdf-url", test_pdf_url])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM",
        ]

        success, missing = verify_output_contains(stdout, expected_patterns)
        no_errors = return_code == 0
        test_success = success and no_errors

        self.add_result(
            "pdf_url_analysis_basic",
            test_success,
            "PDF URL analysis completed successfully" if test_success
            else f"PDF URL analysis failed - Lorem Ipsum not found: {missing}" if not success
            else "PDF URL analysis failed - command returned error",
            {
                "command": f"askai.py -pdf-url {test_pdf_url}",
                "lorem_ipsum_found": success,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_pdf_url_analysis_with_query(self):
        """Test PDF URL analysis with a specific query."""
        test_pdf_url = self.TEST_PDF_URLS["primary"]
        query = "What is the main content of this PDF document?"

        # Run PDF URL analysis with query
        stdout, stderr, return_code = run_cli_command(["-pdf-url", test_pdf_url, "-q", query])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM",
        ]

        success, missing = verify_output_contains(stdout, expected_patterns)
        no_errors = return_code == 0
        test_success = success and no_errors

        self.add_result(
            "pdf_url_analysis_with_query",
            test_success,
            "PDF URL analysis with query completed successfully" if test_success
            else f"PDF URL analysis with query failed - Lorem Ipsum not found: {missing}" if not success
            else "PDF URL analysis with query failed - command returned error",
            {
                "command": f"askai.py -pdf-url {test_pdf_url} -q \"{query}\"",
                "lorem_ipsum_found": success,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_pdf_url_analysis_with_json(self):
        """Test PDF URL analysis with JSON output format."""
        test_pdf_url = self.TEST_PDF_URLS["primary"]

        # Run PDF URL analysis with JSON format
        stdout, stderr, return_code = run_cli_command(["-pdf-url", test_pdf_url, "-f", "json"])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM|PDF|pdf|document|content|text",
        ]

        lorem_success, lorem_missing = verify_output_contains(stdout, expected_patterns)

        # Check JSON format validation
        json_valid, json_reason = verify_basic_json_format(stdout)

        no_errors = return_code == 0
        test_success = lorem_success and no_errors and json_valid

        self.add_result(
            "pdf_url_analysis_with_json",
            test_success,
            "PDF URL analysis with JSON format completed successfully" if test_success
            else f"PDF URL analysis with JSON format failed - Lorem Ipsum not found: {lorem_missing}" if not lorem_success
            else "PDF URL analysis with JSON format failed - invalid JSON format" if not json_valid
            else "PDF URL analysis with JSON format failed - command returned error",
            {
                "command": f"askai.py -pdf-url {test_pdf_url} -f \"json\"",
                "lorem_ipsum_found": lorem_success,
                "json_valid": json_valid,
                "json_reason": json_reason,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_pdf_url_analysis_with_model(self):
        """Test PDF URL analysis with specific model."""
        test_pdf_url = self.TEST_PDF_URLS["primary"]
        model_name = "anthropic/claude-3-haiku"

        # Run PDF URL analysis with specific model
        stdout, stderr, return_code = run_cli_command(["-pdf-url", test_pdf_url, "-m", model_name])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM|PDF|pdf|document|content|text",
        ]

        success, missing = verify_output_contains(stdout, expected_patterns)
        no_errors = return_code == 0
        test_success = success and no_errors

        self.add_result(
            "pdf_url_analysis_with_model",
            test_success,
            "PDF URL analysis with model completed successfully" if test_success
            else f"PDF URL analysis with model failed - Lorem Ipsum not found: {missing}" if not success
            else "PDF URL analysis with model failed - command returned error",
            {
                "command": f"askai.py -pdf-url {test_pdf_url} -m \"{model_name}\"",
                "lorem_ipsum_found": success,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_pdf_url_analysis_with_query_and_json(self):
        """Test PDF URL analysis with query and JSON format."""
        test_pdf_url = self.TEST_PDF_URLS["primary"]
        query = "Analyze the text content in this PDF document"

        # Run PDF URL analysis with query and JSON format
        stdout, stderr, return_code = run_cli_command(["-pdf-url", test_pdf_url, "-q", query, "-f", "json"])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM|PDF|pdf|document|content|text",
        ]

        lorem_success, lorem_missing = verify_output_contains(stdout, expected_patterns)

        # Check JSON format validation
        json_valid, json_reason = verify_basic_json_format(stdout)

        no_errors = return_code == 0
        test_success = lorem_success and no_errors and json_valid

        self.add_result(
            "pdf_url_analysis_with_query_and_json",
            test_success,
            "PDF URL analysis with query and JSON completed successfully" if test_success
            else f"PDF URL analysis with query and JSON failed - Lorem Ipsum not found: {lorem_missing}" if not lorem_success
            else "PDF URL analysis with query and JSON failed - invalid JSON format" if not json_valid
            else "PDF URL analysis with query and JSON failed - command returned error",
            {
                "command": f"askai.py -pdf-url {test_pdf_url} -q \"{query}\" -f \"json\"",
                "lorem_ipsum_found": lorem_success,
                "json_valid": json_valid,
                "json_reason": json_reason,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_pdf_url_analysis_with_query_and_model(self):
        """Test PDF URL analysis with query and specific model."""
        test_pdf_url = self.TEST_PDF_URLS["primary"]
        query = "What text content do you see in this PDF document?"
        model_name = "anthropic/claude-3-haiku"

        # Run PDF URL analysis with query and model
        stdout, stderr, return_code = run_cli_command(["-pdf-url", test_pdf_url, "-q", query, "-m", model_name])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM|PDF|pdf|document|content|text",
        ]

        success, missing = verify_output_contains(stdout, expected_patterns)
        no_errors = return_code == 0
        test_success = success and no_errors

        self.add_result(
            "pdf_url_analysis_with_query_and_model",
            test_success,
            "PDF URL analysis with query and model completed successfully" if test_success
            else f"PDF URL analysis with query and model failed - Lorem Ipsum not found: {missing}" if not success
            else "PDF URL analysis with query and model failed - command returned error",
            {
                "command": f"askai.py -pdf-url {test_pdf_url} -q \"{query}\" -m \"{model_name}\"",
                "lorem_ipsum_found": success,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_pdf_url_analysis_with_json_and_model(self):
        """Test PDF URL analysis with JSON format and specific model."""
        test_pdf_url = self.TEST_PDF_URLS["primary"]
        model_name = "anthropic/claude-3-haiku"

        # Run PDF URL analysis with JSON format and model
        stdout, stderr, return_code = run_cli_command(["-pdf-url", test_pdf_url, "-f", "json", "-m", model_name])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM|PDF|pdf|document|content|text",
        ]

        lorem_success, lorem_missing = verify_output_contains(stdout, expected_patterns)

        # Check JSON format validation
        json_valid, json_reason = verify_basic_json_format(stdout)

        no_errors = return_code == 0
        test_success = lorem_success and no_errors and json_valid

        self.add_result(
            "pdf_url_analysis_with_json_and_model",
            test_success,
            "PDF URL analysis with JSON and model completed successfully" if test_success
            else f"PDF URL analysis with JSON and model failed - Lorem Ipsum not found: {lorem_missing}" if not lorem_success
            else "PDF URL analysis with JSON and model failed - invalid JSON format" if not json_valid
            else "PDF URL analysis with JSON and model failed - command returned error",
            {
                "command": f"askai.py -pdf-url {test_pdf_url} -f \"json\" -m \"{model_name}\"",
                "lorem_ipsum_found": lorem_success,
                "json_valid": json_valid,
                "json_reason": json_reason,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_pdf_url_analysis_with_query_model_and_format(self):
        """Test PDF URL analysis with all options: query, JSON format, and model."""
        test_pdf_url = self.TEST_PDF_URLS["primary"]
        query = "Analyze all text content in this PDF document"
        model_name = "anthropic/claude-3-haiku"

        # Run PDF URL analysis with all options
        stdout, stderr, return_code = run_cli_command(["-pdf-url", test_pdf_url, "-q", query, "-f", "json", "-m", model_name])

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
            "pdf_url_analysis_with_all_options",
            test_success,
            "PDF URL analysis with all options completed successfully" if test_success
            else f"PDF URL analysis with all options failed - Lorem Ipsum not found: {lorem_missing}" if not lorem_success
            else "PDF URL analysis with all options failed - invalid JSON format" if not json_valid
            else "PDF URL analysis with all options failed - command returned error",
            {
                "command": f"askai.py -pdf-url {test_pdf_url} -q \"{query}\" -f \"json\" -m \"{model_name}\"",
                "lorem_ipsum_found": lorem_success,
                "json_valid": json_valid,
                "json_reason": json_reason,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_missing_pdf_url(self):
        """Test error handling when -pdf-url parameter is provided but URL is missing."""
        # Run command with -pdf-url but no URL argument - should produce an error
        stdout, stderr, return_code = run_cli_command(["-pdf-url"])

        # We expect an error return code or error message indicating missing URL
        has_error = return_code != 0 or "error" in stdout.lower() or "error" in stderr.lower() or "required" in stdout.lower() or "required" in stderr.lower()

        self.add_result(
            "missing_pdf_url_handling",
            has_error,
            "Missing PDF URL properly handled with error" if has_error
            else "Missing PDF URL did not produce expected error response",
            {
                "command": "askai.py -pdf-url",
                "error_detected": has_error,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_invalid_pdf_url(self):
        """Test error handling for invalid/nonexistent PDF URLs."""
        invalid_url = self.INVALID_PDF_URL

        # Run command with invalid PDF URL - should produce an error
        stdout, stderr, return_code = run_cli_command(["-pdf-url", invalid_url])

        # For invalid URLs, we expect either an error return code or error message
        has_error = return_code != 0 or "error" in stdout.lower() or "error" in stderr.lower()

        self.add_result(
            "invalid_pdf_url_handling",
            has_error,
            "Invalid PDF URL properly handled with error" if has_error
            else "Invalid PDF URL did not produce expected error response",
            {
                "command": f"askai.py -pdf-url {invalid_url}",
                "error_detected": has_error,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )
