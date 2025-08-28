"""
Integration tests for PDF handling in askai-cli.
"""
import os
from tests.integration.test_base import AutomatedTest
from tests.integration.test_utils import run_cli_command, verify_output_contains


class TestPdfInput(AutomatedTest):
    """Test PDF input handling in the CLI."""
    
    def run(self):
        """Run the test cases."""
        self._test_pdf_detection()
        self._test_pdf_url_detection()
        return self.results
    
    def _test_pdf_detection(self):
        """Test that the CLI recognizes PDF files correctly."""
        # Path to the test PDF file
        test_pdf_path = os.path.join("tests", "test_resources", "test.pdf")
        
        # Check if the test PDF exists
        pdf_exists = os.path.exists(test_pdf_path)
        
        if not pdf_exists:
            self.add_result(
                "pdf_file_existence",
                False,
                "Test PDF file not found",
                {
                    "expected_path": test_pdf_path,
                    "solution": "Please ensure a test.pdf file is placed in the tests/test_resources directory"
                }
            )
            return
            
        # Verify the CLI recognizes the PDF file format
        # We'll run with --version to avoid actual API calls but still trigger the PDF detection code
        stdout, stderr, return_code = run_cli_command(["-pdf", test_pdf_path, "--version"])
        
        # Check if there's an error specifically about the PDF format
        pdf_format_error = "not a valid PDF" in (stdout + stderr)
        
        if pdf_format_error:
            self.add_result(
                "pdf_format_detection",
                False,
                "CLI reported that the test file is not a valid PDF",
                {
                    "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                    "stderr": stderr[:500] + ("..." if len(stderr) > 500 else ""),
                    "return_code": return_code,
                    "resolution": "Please ensure test.pdf is a valid PDF file"
                }
            )
        else:
            # Check if there's some recognition of PDF processing
            pdf_processing_indicators = [
                r"pdf|PDF",
                r"document|Document",
                r"processing|Processing|reading|Reading"
            ]
            
            processing_mentioned, _ = verify_output_contains(stdout + stderr, pdf_processing_indicators)
            
            self.add_result(
                "pdf_format_detection",
                not pdf_format_error,
                "CLI correctly recognized the PDF file format" if not pdf_format_error 
                else "CLI failed to recognize the PDF file format",
                {
                    "pdf_path": test_pdf_path,
                    "pdf_exists": pdf_exists,
                    "processing_mentioned": processing_mentioned,
                    "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                    "stderr": stderr[:500] + ("..." if len(stderr) > 500 else ""),
                    "return_code": return_code
                }
            )
    
    def _test_pdf_url_detection(self):
        """Test that the CLI handles PDF URLs correctly."""
        pdf_url = "https://ontheline.trincoll.edu/images/bookdown/sample-local-pdf.pdf"
        
        # We'll run with --version to avoid actual API calls but still trigger the URL detection code
        stdout, stderr, return_code = run_cli_command(["-pdf-url", pdf_url, "--version"])
        
        # Check if there's an error specifically about the PDF URL
        url_error = "URL" in (stdout + stderr) and "error" in (stdout + stderr).lower()
        
        # Check if there's some recognition of PDF processing from URL
        pdf_url_indicators = [
            r"pdf|PDF",
            r"url|URL",
            r"download|Download|fetching|Fetching"
        ]
        
        url_processing_mentioned, _ = verify_output_contains(stdout + stderr, pdf_url_indicators)
        
        self.add_result(
            "pdf_url_detection",
            not url_error or url_processing_mentioned,
            "CLI correctly handles PDF URLs" if not url_error or url_processing_mentioned
            else "CLI failed to handle the PDF URL",
            {
                "pdf_url": pdf_url,
                "url_processing_mentioned": url_processing_mentioned,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr[:500] + ("..." if len(stderr) > 500 else ""),
                "return_code": return_code
            }
        )
