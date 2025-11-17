"""
Integration tests for image URL handling in askai-cli.
"""
from tests.integration.test_base import AutomatedTest
from tests.integration.test_utils import run_cli_command, verify_output_contains, verify_basic_json_format


class TestImageUrlInput(AutomatedTest):
    """Test image URL input handling in the CLI."""

    # Global configurable URLs for testing
    # These should point to publicly accessible images containing Lorem Ipsum text
    TEST_IMAGE_URLS = {
        "png_format": "https://dummyimage.com/600x400/000/fff.png&text=Lorem+Ipsum+Test+Content",
        "jpg_format": "https://dummyimage.com/600x400/000/fff.jpg&text=Lorem+Ipsum+Test+Content"
    }

    # URL for testing nonexistent/invalid images
    INVALID_IMAGE_URL = "https://example.com/nonexistent/invalid.jpg"

    def run(self):
        """Run the test cases."""
        self._test_image_url_basic()
        self._test_image_url_analysis_with_query()
        self._test_image_url_analysis_with_json()
        self._test_image_url_analysis_with_model()
        self._test_image_url_analysis_with_query_and_json()
        self._test_image_url_analysis_with_query_and_model()
        self._test_image_url_analysis_with_json_and_model()
        self._test_image_url_analysis_with_all_options()
        self._test_missing_image_url()
        self._test_invalid_image_url()
        return self.results

    def _test_image_url_basic(self):
        """Test basic image URL analysis without additional parameters."""
        test_image_url = self.TEST_IMAGE_URLS["png_format"]

        # Run image URL analysis
        stdout, stderr, return_code = run_cli_command(["-img-url", test_image_url])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM|image|text|content",
        ]

        success, missing = verify_output_contains(stdout, expected_patterns)
        no_errors = return_code == 0
        test_success = success and no_errors

        self.add_result(
            "image_url_analysis_basic",
            test_success,
            "Image URL analysis completed successfully" if test_success
            else f"Image URL analysis failed - Expected content not found: {missing}" if not success
            else "Image URL analysis failed - command returned error",
            {
                "command": f"askai.py -img-url {test_image_url}",
                "content_found": success,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_image_url_analysis_with_query(self):
        """Test image URL analysis with a specific query."""
        test_image_url = self.TEST_IMAGE_URLS["png_format"]
        query = "What text do you see in this image?"

        # Run image URL analysis with query
        stdout, stderr, return_code = run_cli_command(["-img-url", test_image_url, "-q", query])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM|image|text|content",
        ]

        success, missing = verify_output_contains(stdout, expected_patterns)
        no_errors = return_code == 0
        test_success = success and no_errors

        self.add_result(
            "image_url_analysis_with_query",
            test_success,
            "Image URL analysis with query completed successfully" if test_success
            else f"Image URL analysis with query failed - Expected content not found: {missing}" if not success
            else "Image URL analysis with query failed - command returned error",
            {
                "command": f"askai.py -img-url {test_image_url} -q \"{query}\"",
                "content_found": success,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_image_url_analysis_with_json(self):
        """Test image URL analysis with JSON output format."""
        test_image_url = self.TEST_IMAGE_URLS["png_format"]

        # Run image URL analysis with JSON format
        stdout, stderr, return_code = run_cli_command(["-img-url", test_image_url, "-f", "json"])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM|image|text|content",
        ]

        lorem_success, lorem_missing = verify_output_contains(stdout, expected_patterns)

        # Check JSON format validation
        json_valid, json_reason = verify_basic_json_format(stdout)

        no_errors = return_code == 0
        test_success = lorem_success and no_errors and json_valid

        self.add_result(
            "image_url_analysis_with_json",
            test_success,
            "Image URL analysis with JSON format completed successfully" if test_success
            else f"Image URL analysis with JSON format failed - Expected content not found: {lorem_missing}" if not lorem_success
            else "Image URL analysis with JSON format failed - invalid JSON format" if not json_valid
            else "Image URL analysis with JSON format failed - command returned error",
            {
                "command": f"askai.py -img-url {test_image_url} -f \"json\"",
                "content_found": lorem_success,
                "json_valid": json_valid,
                "json_reason": json_reason,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_image_url_analysis_with_model(self):
        """Test image URL analysis with specific model."""
        test_image_url = self.TEST_IMAGE_URLS["jpg_format"]
        model_name = "anthropic/claude-3-haiku"

        # Run image URL analysis with specific model
        stdout, stderr, return_code = run_cli_command(["-img-url", test_image_url, "-m", model_name])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM|image|text|content",
        ]

        success, missing = verify_output_contains(stdout, expected_patterns)
        no_errors = return_code == 0
        test_success = success and no_errors

        self.add_result(
            "image_url_analysis_with_model",
            test_success,
            "Image URL analysis with model completed successfully" if test_success
            else f"Image URL analysis with model failed - Expected content not found: {missing}" if not success
            else "Image URL analysis with model failed - command returned error",
            {
                "command": f"askai.py -img-url {test_image_url} -m \"{model_name}\"",
                "content_found": success,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_image_url_analysis_with_query_and_json(self):
        """Test image URL analysis with query and JSON format."""
        test_image_url = self.TEST_IMAGE_URLS["jpg_format"]
        query = "Analyze all text content in this image"

        # Run image URL analysis with query and JSON format
        stdout, stderr, return_code = run_cli_command(["-img-url", test_image_url, "-q", query, "-f", "json"])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM|image|text|content",
        ]

        lorem_success, lorem_missing = verify_output_contains(stdout, expected_patterns)

        # Check JSON format validation
        json_valid, json_reason = verify_basic_json_format(stdout)

        no_errors = return_code == 0
        test_success = lorem_success and no_errors and json_valid

        self.add_result(
            "image_url_analysis_with_query_and_json",
            test_success,
            "Image URL analysis with query and JSON completed successfully" if test_success
            else f"Image URL analysis with query and JSON failed - Expected content not found: {lorem_missing}" if not lorem_success
            else "Image URL analysis with query and JSON failed - invalid JSON format" if not json_valid
            else "Image URL analysis with query and JSON failed - command returned error",
            {
                "command": f"askai.py -img-url {test_image_url} -q \"{query}\" -f \"json\"",
                "content_found": lorem_success,
                "json_valid": json_valid,
                "json_reason": json_reason,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_image_url_analysis_with_query_and_model(self):
        """Test image URL analysis with query and specific model."""
        test_image_url = self.TEST_IMAGE_URLS["png_format"]
        query = "What text content do you see in this image?"
        model_name = "anthropic/claude-3-haiku"

        # Run image URL analysis with query and model
        stdout, stderr, return_code = run_cli_command(["-img-url", test_image_url, "-q", query, "-m", model_name])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM|image|text|content",
        ]

        success, missing = verify_output_contains(stdout, expected_patterns)
        no_errors = return_code == 0
        test_success = success and no_errors

        self.add_result(
            "image_url_analysis_with_query_and_model",
            test_success,
            "Image URL analysis with query and model completed successfully" if test_success
            else f"Image URL analysis with query and model failed - Expected content not found: {missing}" if not success
            else "Image URL analysis with query and model failed - command returned error",
            {
                "command": f"askai.py -img-url {test_image_url} -q \"{query}\" -m \"{model_name}\"",
                "content_found": success,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_image_url_analysis_with_json_and_model(self):
        """Test image URL analysis with JSON format and specific model."""
        test_image_url = self.TEST_IMAGE_URLS["jpg_format"]
        model_name = "anthropic/claude-3-haiku"

        # Run image URL analysis with JSON format and model
        stdout, stderr, return_code = run_cli_command(["-img-url", test_image_url, "-f", "json", "-m", model_name])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM|image|text|content",
        ]

        lorem_success, lorem_missing = verify_output_contains(stdout, expected_patterns)

        # Check JSON format validation
        json_valid, json_reason = verify_basic_json_format(stdout)

        no_errors = return_code == 0
        test_success = lorem_success and no_errors and json_valid

        self.add_result(
            "image_url_analysis_with_json_and_model",
            test_success,
            "Image URL analysis with JSON and model completed successfully" if test_success
            else f"Image URL analysis with JSON and model failed - Expected content not found: {lorem_missing}" if not lorem_success
            else "Image URL analysis with JSON and model failed - invalid JSON format" if not json_valid
            else "Image URL analysis with JSON and model failed - command returned error",
            {
                "command": f"askai.py -img-url {test_image_url} -f \"json\" -m \"{model_name}\"",
                "content_found": lorem_success,
                "json_valid": json_valid,
                "json_reason": json_reason,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_image_url_analysis_with_all_options(self):
        """Test image URL analysis with all options: query, JSON format, and model."""
        test_image_url = self.TEST_IMAGE_URLS["png_format"]
        query = "Analyze all text content in this image"
        model_name = "anthropic/claude-3-haiku"

        # Run image URL analysis with all options
        stdout, stderr, return_code = run_cli_command(["-img-url", test_image_url, "-q", query, "-f", "json", "-m", model_name])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM|image|text|content",
        ]

        lorem_success, lorem_missing = verify_output_contains(stdout, expected_patterns)

        # Check JSON format validation
        json_valid, json_reason = verify_basic_json_format(stdout)

        no_errors = return_code == 0
        test_success = lorem_success and no_errors and json_valid

        self.add_result(
            "image_url_analysis_with_all_options",
            test_success,
            "Image URL analysis with all options completed successfully" if test_success
            else f"Image URL analysis with all options failed - Expected content not found: {lorem_missing}" if not lorem_success
            else "Image URL analysis with all options failed - invalid JSON format" if not json_valid
            else "Image URL analysis with all options failed - command returned error",
            {
                "command": f"askai.py -img-url {test_image_url} -q \"{query}\" -f \"json\" -m \"{model_name}\"",
                "content_found": lorem_success,
                "json_valid": json_valid,
                "json_reason": json_reason,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_missing_image_url(self):
        """Test error handling when -img-url parameter is provided but URL is missing."""
        # Run command with -img-url but no URL argument - should produce an error
        stdout, stderr, return_code = run_cli_command(["-img-url"])

        # We expect an error return code or error message indicating missing URL
        has_error = return_code != 0 or "error" in stdout.lower() or "error" in stderr.lower() or "required" in stdout.lower() or "required" in stderr.lower()

        self.add_result(
            "missing_image_url_handling",
            has_error,
            "Missing image URL properly handled with error" if has_error
            else "Missing image URL did not produce expected error response",
            {
                "command": "askai.py -img-url",
                "error_detected": has_error,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_invalid_image_url(self):
        """Test error handling for invalid/nonexistent image URLs."""
        invalid_url = self.INVALID_IMAGE_URL

        # Run command with invalid image URL - should produce an error
        stdout, stderr, return_code = run_cli_command(["-img-url", invalid_url])

        # For invalid URLs, we expect either an error return code or error message
        has_error = return_code != 0 or "error" in stdout.lower() or "error" in stderr.lower()

        self.add_result(
            "invalid_image_url_handling",
            has_error,
            "Invalid image URL properly handled with error" if has_error
            else "Invalid image URL did not produce expected error response",
            {
                "command": f"askai.py -img-url {invalid_url}",
                "error_detected": has_error,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )
