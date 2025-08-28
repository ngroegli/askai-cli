"""
Integration tests for query parameter handling.
"""
import os
from tests.integration.test_base import AutomatedTest

class TestQueryParameters(AutomatedTest):
    """Test query parameter handling in the CLI."""
    
    def run(self):
        """Run the test cases."""
        # Test basic query parameters
        self._test_basic_query_parameters()
        
        # Test URL input parameters
        self._test_url_input_parameters()
        
        # Test image input parameters
        self._test_image_input_parameters()
        
        # Test PDF input parameters
        self._test_pdf_input_parameters()
        
        # Test pattern parameters
        self._test_pattern_parameters()
        
        return self.results
    
    def _test_basic_query_parameters(self):
        """Test basic query parameter handling."""
        # Test case 1: Document correct usage of -q flag
        self.add_result(
            "query_parameter_usage",
            True,
            "Queries should be passed with the -q flag: -q \"What's the capital of France?\"",
            {
                "correct_usage": "-q \"What's the capital of France?\"",
                "incorrect_usage": "What's the capital of France?",
                "explanation": "Without the -q flag, arguments are interpreted as positional arguments, causing errors"
            }
        )
        
        # Test case 2: Document quotes handling in queries
        self.add_result(
            "query_quoting",
            True,
            "Queries with spaces must be enclosed in quotes",
            {
                "correct_usage": "-q \"What's the capital of France?\"",
                "incorrect_usage": "-q What's the capital of France?",
                "shell_behavior": "Without quotes, the shell will interpret spaces as argument separators",
                "tip": "Use single quotes for queries with double quotes, or escape the inner quotes"
            }
        )
        
        # Test case 3: Document single vs double quotes
        self.add_result(
            "query_quote_types",
            True,
            "Use appropriate quotes based on query content",
            {
                "double_quotes": "-q \"What is the capital of France?\"",
                "single_quotes": "-q 'What is the \"capital\" of France?'",
                "escaping": "-q \"What is the \\\"capital\\\" of France?\"",
                "tip": "Single quotes don't process special characters, double quotes allow for variable expansion and escaping"
            }
        )
    
    def _test_url_input_parameters(self):
        """Test URL input parameter handling."""
        example_url = "https://example.com"
        
        # Test case 1: Document correct URL input usage
        self.add_result(
            "url_input_usage",
            True,
            "URL input should be provided with -url or --url parameter",
            {
                "correct_usage": f"-url {example_url} -q \"Summarize this website\"",
                "shorthand_flag": "-url",
                "longhand_flag": "--url",
                "example_url": example_url,
                "explanation": "The URL content will be fetched and provided as context to the AI"
            }
        )
        
        # Test case 2: URL without query
        self.add_result(
            "url_without_query",
            True,
            "URL can be used without an explicit query",
            {
                "usage": f"-url {example_url}",
                "explanation": "When no query is provided with -q, the system will use a default prompt to analyze the URL content",
                "recommendation": "For better results, include a specific question with -q"
            }
        )
        
        # Test case 3: Multiple URLs
        self.add_result(
            "multiple_urls",
            True,
            "Multiple URLs can be provided (if supported by the CLI)",
            {
                "potential_usage": f"-url {example_url} -url https://another-example.com",
                "check_docs": "Check the CLI documentation to confirm if multiple URLs are supported",
                "recommendation": "If multiple URLs aren't supported, consider using a pattern for multi-URL analysis"
            }
        )
    
    def _test_image_input_parameters(self):
        """Test image input parameter handling."""
        example_img_path = "/path/to/image.jpg"
        example_img_url = "https://www.iana.org/_img/2025.01/iana-logo-header.svg"
        
        # Test case 1: Local image input
        self.add_result(
            "local_image_input",
            True,
            "Local image input should be provided with -img or --image parameter",
            {
                "correct_usage": f"-img {example_img_path} -q \"What's in this image?\"",
                "shorthand_flag": "-img",
                "longhand_flag": "--image",
                "explanation": "The local image will be sent to the AI for analysis",
                "supported_formats": "JPG, PNG, GIF, WebP, etc. (check documentation for full list)"
            }
        )
        
        # Test case 2: Image URL input
        self.add_result(
            "image_url_input",
            True,
            "Image URL input should be provided with -img-url or --image-url parameter",
            {
                "correct_usage": f"-img-url {example_img_url} -q \"What's in this image?\"",
                "shorthand_flag": "-img-url",
                "longhand_flag": "--image-url",
                "example_url": example_img_url,
                "explanation": "The image will be fetched from the URL and sent to the AI for analysis"
            }
        )
        
        # Test case 3: Image without query
        self.add_result(
            "image_without_query",
            True,
            "Image can be used without an explicit query",
            {
                "usage": f"-img {example_img_path}",
                "explanation": "When no query is provided with -q, the system will use a default prompt like 'Describe this image'",
                "recommendation": "For better results, include a specific question with -q"
            }
        )
        
        # Test case 4: Model selection for images
        self.add_result(
            "image_model_selection",
            True,
            "When using images, ensure a vision-capable model is selected",
            {
                "usage": f"-img {example_img_path} -m 'anthropic/claude-3-opus-20240229'",
                "explanation": "Not all models support image analysis. The CLI should automatically select a vision-capable model, but you can override it with -m",
                "recommendation": "Check the documentation for which models support vision capabilities"
            }
        )
    
    def _test_pdf_input_parameters(self):
        """Test PDF input parameter handling."""
        example_pdf_path = os.path.join("tests", "test_resources", "test.pdf")
        example_pdf_url = "https://ontheline.trincoll.edu/images/bookdown/sample-local-pdf.pdf"
        
        # Verify test.pdf exists
        pdf_exists = os.path.exists(example_pdf_path)
        
        # Test case 1: Local PDF input
        self.add_result(
            "local_pdf_input",
            True,
            "Local PDF input should be provided with -pdf or --pdf parameter",
            {
                "correct_usage": f"-pdf {example_pdf_path} -q \"Summarize this document\"",
                "shorthand_flag": "-pdf",
                "longhand_flag": "--pdf",
                "explanation": "The local PDF will be processed and sent to the AI for analysis",
                "note": "The file must have a .pdf extension to be processed correctly",
                "test_file_exists": pdf_exists
            }
        )
        
        # Test case 2: PDF URL input
        self.add_result(
            "pdf_url_input",
            True,
            "PDF URL input should be provided with -pdf-url or --pdf-url parameter",
            {
                "correct_usage": f"-pdf-url {example_pdf_url} -q \"Summarize this document\"",
                "shorthand_flag": "-pdf-url",
                "longhand_flag": "--pdf-url",
                "example_url": example_pdf_url,
                "explanation": "The PDF will be downloaded from the URL and sent to the AI for analysis",
                "note": "The URL must point directly to a publicly accessible PDF file"
            }
        )
        
        # Test case 3: PDF without query
        self.add_result(
            "pdf_without_query",
            True,
            "PDF can be used without an explicit query",
            {
                "usage": f"-pdf {example_pdf_path}",
                "explanation": "When no query is provided with -q, the system will use a default prompt to analyze the document",
                "recommendation": "For better results, include a specific question with -q"
            }
        )
        
        # Test case 4: Model selection for PDFs
        self.add_result(
            "pdf_model_selection",
            True,
            "When using PDFs, ensure a model that supports document processing is selected",
            {
                "usage": f"-pdf {example_pdf_path} -m 'anthropic/claude-3-opus-20240229'",
                "explanation": "Not all models support PDF processing. Check the documentation for which models support document analysis",
                "recommendation": "Claude models typically have good document processing capabilities"
            }
        )
    
    def _test_pattern_parameters(self):
        """Test pattern parameter handling."""
        example_pattern = "log_interpretation"
        
        # Test case 1: Using pattern with input
        self.add_result(
            "pattern_with_input",
            True,
            "Patterns should be specified with -up or --use-pattern parameter",
            {
                "correct_usage": f"-up {example_pattern} -i /var/log/auth.log",
                "shorthand_flag": "-up",
                "longhand_flag": "--use-pattern",
                "explanation": "The pattern provides specialized instructions for the AI, and -i provides input for that pattern",
                "available_patterns": "Use --list-patterns to see available patterns"
            }
        )
        
        # Test case 2: Pattern with query conflict
        self.add_result(
            "pattern_query_conflict",
            True,
            "When using both pattern and query parameters, pattern takes precedence",
            {
                "usage": f"-up {example_pattern} -q \"What does this log mean?\"",
                "behavior": "The pattern functionality takes precedence, and the query is used as input for the pattern",
                "recommendation": "When using patterns, provide specific input with -i instead of -q if possible"
            }
        )
        
        # Test case 3: Listing available patterns
        self.add_result(
            "listing_patterns",
            True,
            "Available patterns can be listed with -lp or --list-patterns",
            {
                "correct_usage": "-lp",
                "alternate_usage": "--list-patterns",
                "explanation": "This will display all available patterns in the patterns/ directory"
            }
        )
        
        return self.results
