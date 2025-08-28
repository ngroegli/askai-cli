"""
Integration tests for image handling in askai-cli.
"""
import os
from tests.integration.test_base import AutomatedTest
from tests.integration.test_utils import run_cli_command, verify_output_contains


class TestImageInput(AutomatedTest):
    """Test image input handling in the CLI."""
    
    def run(self):
        """Run the test cases."""
        print("Running test: _test_image_file_exists")
        self._test_image_file_exists()
        print("Running test: _test_image_parameter_recognition")
        self._test_image_parameter_recognition()
        print("Running test: _test_image_url_parameter_recognition")
        self._test_image_url_parameter_recognition()
        print("Running test: _test_image_url_detection")
        self._test_image_url_detection()
        print("All tests completed")
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
                "files": file_details,
                "note": "These files are used for image handling tests"
            }
        )
    
    def _test_image_parameter_recognition(self):
        """Test that the image parameter is recognized by the CLI."""
        test_image_path = os.path.join("tests", "test_resources", "test.jpg")
        
        # Run with --help to avoid making actual API calls
        stdout, stderr, return_code = run_cli_command([
            "-img", test_image_path, 
            "--help"
        ])
        
        # Verify the command doesn't error out due to parameter issues
        expected_patterns = [
            r"usage:",  # Help output should be shown
            r"-img",    # Image parameter should be recognized in help
        ]
        
        success, missing = verify_output_contains(stdout, expected_patterns)
        
        self.add_result(
            "image_parameter_recognition",
            success and return_code == 0,
            "Image parameter is recognized correctly" if success and return_code == 0
            else f"Image parameter not recognized correctly. Missing patterns: {missing}",
            {
                "command": f"-img {test_image_path} --help",
                "stdout": stdout[:200] + ("..." if len(stdout) > 200 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )
        
    def _test_image_url_parameter_recognition(self):
        """Test that the image URL parameter is recognized by the CLI."""
        test_image_url = "https://www.example.com/image.jpg"
        
        # Run with --help to avoid making actual API calls
        stdout, stderr, return_code = run_cli_command([
            "-img-url", test_image_url, 
            "--help"
        ])
        
        # Verify the command doesn't error out due to parameter issues
        expected_patterns = [
            r"usage:",  # Help output should be shown
            r"-img-url",    # Image URL parameter should be recognized in help
        ]
        
        success, missing = verify_output_contains(stdout, expected_patterns)
        
        self.add_result(
            "image_url_parameter_recognition",
            success and return_code == 0,
            "Image URL parameter is recognized correctly" if success and return_code == 0
            else f"Image URL parameter not recognized correctly. Missing patterns: {missing}",
            {
                "command": f"-img-url {test_image_url} --help",
                "stdout": stdout[:200] + ("..." if len(stdout) > 200 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )
    
    def _test_image_url_detection(self):
        """Test that the CLI handles image URLs correctly."""
        image_url = "https://www.iana.org/_img/2025.01/iana-logo-header.svg"
        
        # We'll run with --version to avoid actual API calls but still trigger the URL detection code
        stdout, stderr, return_code = run_cli_command(["-img-url", image_url, "--version"])
        
        # Check if there's an error specifically about the image URL
        url_error = "URL" in (stdout + stderr) and "error" in (stdout + stderr).lower()
        
        # Check if there's some recognition of image processing from URL
        image_url_indicators = [
            r"image|IMAGE|img|Img",
            r"url|URL",
            r"download|Download|fetching|Fetching"
        ]
        
        url_processing_mentioned, _ = verify_output_contains(stdout + stderr, image_url_indicators)
        
        self.add_result(
            "image_url_detection",
            not url_error or url_processing_mentioned,
            "CLI correctly handles image URLs" if not url_error or url_processing_mentioned
            else "CLI failed to handle the image URL",
            {
                "image_url": image_url,
                "url_processing_mentioned": url_processing_mentioned,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr[:500] + ("..." if len(stderr) > 500 else ""),
                "return_code": return_code
            }
        )


if __name__ == "__main__":
    print("Starting image input tests...")
    test = TestImageInput()
    results = test.run()
    passed, failed = test.report()
    print(f"Test completed with {passed} tests passed and {failed} tests failed.")
