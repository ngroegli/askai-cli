"""
Integration tests for image handling in askai-cli.
"""
import os
from tests.integration.test_base import AutomatedTest
from tests.integration.test_utils import run_cli_command, verify_output_contains, verify_basic_json_format


class TestImageInput(AutomatedTest):
    """Test image input handling in the CLI."""

    def run(self):
        """Run the test cases."""
        self._test_image_file_exists()
        self._test_image_analysis_basic()
        self._test_image_analysis_with_query()
        self._test_image_analysis_with_json()
        self._test_image_analysis_with_model()
        self._test_image_analysis_with_query_and_json()
        self._test_image_analysis_with_query_and_model()
        self._test_image_analysis_with_json_and_model()
        self._test_image_analysis_with_question_format_and_model_options()
        self._test_nonexistent_image()
        return self.results

    def _test_image_file_exists(self):
        """Test that the image test files exist and are accessible."""
        test_files = [
            os.path.join("tests", "test_resources", "test.jpg"),
            os.path.join("tests", "test_resources", "test.png"),
        ]

        all_files_exist = True
        file_details = {}

        for test_file in test_files:
            # Check if file exists
            file_exists = os.path.isfile(test_file)
            all_files_exist = all_files_exist and file_exists

            file_details[test_file] = {
                "exists": file_exists,
                "absolute_path": os.path.abspath(test_file) if file_exists else "N/A"
            }

        self.add_result(
            "image_test_files_exist",
            all_files_exist,
            "All test image files exist and are accessible" if all_files_exist else "Some test image files not found",
            {
                "command": "File existence check",
                "files": file_details,
                "note": "These files are used for image handling tests"
            }
        )

    def _test_image_analysis_basic(self):
        """Test basic image analysis without additional parameters."""
        test_image_path = os.path.join("tests", "test_resources", "test.jpg")

        # Run image analysis without query
        stdout, stderr, return_code = run_cli_command(["-img", test_image_path])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM",
        ]

        success, missing = verify_output_contains(stdout, expected_patterns)
        no_errors = return_code == 0
        test_success = success and no_errors

        self.add_result(
            "image_analysis_basic",
            test_success,
            "Basic image analysis detected Lorem Ipsum text" if test_success
            else f"Basic image analysis failed - Lorem Ipsum not found: {missing}" if not success
            else "Basic image analysis failed - command returned error",
            {
                "command": f"askai.py -img {test_image_path}",
                "lorem_ipsum_found": success,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_image_analysis_with_query(self):
        """Test image analysis with specific query."""
        test_image_path = os.path.join("tests", "test_resources", "test.jpg")
        query = "What text is in this image?"

        # Run image analysis with query
        stdout, stderr, return_code = run_cli_command(["-img", test_image_path, "-q", query])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM",
        ]

        success, missing = verify_output_contains(stdout, expected_patterns)
        no_errors = return_code == 0
        test_success = success and no_errors

        self.add_result(
            "image_analysis_with_query",
            test_success,
            "Image analysis with query detected Lorem Ipsum text" if test_success
            else f"Image analysis with query failed - Lorem Ipsum not found: {missing}" if not success
            else "Image analysis with query failed - command returned error",
            {
                "command": f"askai.py -img {test_image_path} -q \"{query}\"",
                "lorem_ipsum_found": success,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_image_analysis_with_json(self):
        """Test image analysis with JSON output format."""
        test_image_path = os.path.join("tests", "test_resources", "test.jpg")

        # Run image analysis with JSON format
        stdout, stderr, return_code = run_cli_command(["-img", test_image_path, "-f", "json"])

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
            "image_analysis_with_json",
            test_success,
            "Image analysis with JSON format detected Lorem Ipsum text" if test_success
            else f"Image analysis with JSON format failed - Lorem Ipsum not found: {lorem_missing}" if not lorem_success
            else "Image analysis with JSON format failed - invalid JSON format" if not json_valid
            else "Image analysis with JSON format failed - command returned error",
            {
                "command": f"askai.py -img {test_image_path} -f \"json\"",
                "lorem_ipsum_found": lorem_success,
                "json_valid": json_valid,
                "json_reason": json_reason,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_image_analysis_with_model(self):
        """Test image analysis with specific model."""
        test_image_path = os.path.join("tests", "test_resources", "test.png")
        model_name = "anthropic/claude-3-haiku"

        # Run image analysis with specific model
        stdout, stderr, return_code = run_cli_command(["-img", test_image_path, "-m", model_name])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM",
        ]

        success, missing = verify_output_contains(stdout, expected_patterns)
        no_errors = return_code == 0
        test_success = success and no_errors

        self.add_result(
            "image_analysis_with_model",
            test_success,
            "Image analysis with model detected Lorem Ipsum text" if test_success
            else f"Image analysis with model failed - Lorem Ipsum not found: {missing}" if not success
            else "Image analysis with model failed - command returned error",
            {
                "command": f"askai.py -img {test_image_path} -m \"{model_name}\"",
                "lorem_ipsum_found": success,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_image_analysis_with_query_and_json(self):
        """Test image analysis with query and JSON format."""
        test_image_path = os.path.join("tests", "test_resources", "test.jpg")
        query = "Describe the text content in this image"

        # Run image analysis with query and JSON format
        stdout, stderr, return_code = run_cli_command(["-img", test_image_path, "-q", query, "-f", "json"])

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
            "image_analysis_with_query_and_json",
            test_success,
            "Image analysis with query and JSON detected Lorem Ipsum text" if test_success
            else f"Image analysis with query and JSON failed - Lorem Ipsum not found: {lorem_missing}" if not lorem_success
            else "Image analysis with query and JSON failed - invalid JSON format" if not json_valid
            else "Image analysis with query and JSON failed - command returned error",
            {
                "command": f"askai.py -img {test_image_path} -q \"{query}\" -f \"json\"",
                "lorem_ipsum_found": lorem_success,
                "json_valid": json_valid,
                "json_reason": json_reason,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_image_analysis_with_query_and_model(self):
        """Test image analysis with query and specific model."""
        test_image_path = os.path.join("tests", "test_resources", "test.png")
        query = "What text is in this image?"
        model_name = "anthropic/claude-3-haiku"

        # Run image analysis with query and model
        stdout, stderr, return_code = run_cli_command(["-img", test_image_path, "-q", query, "-m", model_name])

        # Check if Lorem Ipsum is detected
        expected_patterns = [
            r"[Ll]orem\s+[Ii]psum|Lorem|lorem|LOREM|Ipsum|ipsum|IPSUM",
        ]

        success, missing = verify_output_contains(stdout, expected_patterns)
        no_errors = return_code == 0
        test_success = success and no_errors

        self.add_result(
            "image_analysis_with_query_and_model",
            test_success,
            "Image analysis with query and model detected Lorem Ipsum text" if test_success
            else f"Image analysis with query and model failed - Lorem Ipsum not found: {missing}" if not success
            else "Image analysis with query and model failed - command returned error",
            {
                "command": f"askai.py -img {test_image_path} -q \"{query}\" -m \"{model_name}\"",
                "lorem_ipsum_found": success,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_image_analysis_with_json_and_model(self):
        """Test image analysis with JSON format and specific model."""
        test_image_path = os.path.join("tests", "test_resources", "test.jpg")
        model_name = "anthropic/claude-3-haiku"

        # Run image analysis with JSON format and model
        stdout, stderr, return_code = run_cli_command(["-img", test_image_path, "-f", "json", "-m", model_name])

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
            "image_analysis_with_json_and_model",
            test_success,
            "Image analysis with JSON and model detected Lorem Ipsum text" if test_success
            else f"Image analysis with JSON and model failed - Lorem Ipsum not found: {lorem_missing}" if not lorem_success
            else "Image analysis with JSON and model failed - invalid JSON format" if not json_valid
            else "Image analysis with JSON and model failed - command returned error",
            {
                "command": f"askai.py -img {test_image_path} -f \"json\" -m \"{model_name}\"",
                "lorem_ipsum_found": lorem_success,
                "json_valid": json_valid,
                "json_reason": json_reason,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_image_analysis_with_question_format_and_model_options(self):
        """Test image analysis with all options: query, JSON format, and model."""
        test_image_path = os.path.join("tests", "test_resources", "test.png")
        query = "Analyze all text content in this image"
        model_name = "anthropic/claude-3-haiku"

        # Run image analysis with all options
        stdout, stderr, return_code = run_cli_command(["-img", test_image_path, "-q", query, "-f", "json", "-m", model_name])

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
            "image_analysis_with_all_options",
            test_success,
            "Image analysis with all options detected Lorem Ipsum text" if test_success
            else f"Image analysis with all options failed - Lorem Ipsum not found: {lorem_missing}" if not lorem_success
            else "Image analysis with all options failed - invalid JSON format" if not json_valid
            else "Image analysis with all options failed - command returned error",
            {
                "command": f"askai.py -img {test_image_path} -q \"{query}\" -f \"json\" -m \"{model_name}\"",
                "lorem_ipsum_found": lorem_success,
                "json_valid": json_valid,
                "json_reason": json_reason,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_nonexistent_image(self):
        """Test error handling for nonexistent image files."""
        nonexistent_path = os.path.join("tests", "test_resources", "nonexistent.jpg")

        # Run command with nonexistent image - should produce an error
        stdout, stderr, return_code = run_cli_command(["-img", nonexistent_path])

        # Check for appropriate error messages
        error_patterns = [
            r"[Ee]rror|[Ff]ile not found|[Nn]o such file|[Dd]oes not exist",
        ]

        error_found, missing = verify_output_contains(stdout + stderr, error_patterns)
        error_return_code = return_code != 0
        test_success = error_found or error_return_code

        self.add_result(
            "nonexistent_image_error",
            test_success,
            "Nonexistent image properly handled with error" if test_success
            else f"Nonexistent image not handled properly - no error detected: {missing}",
            {
                "command": f"askai.py -img {nonexistent_path}",
                "error_found": error_found,
                "error_return_code": error_return_code,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr[:500] + ("..." if len(stderr) > 500 else ""),
                "return_code": return_code
            }
        )
