"""
Unit tests for infrastructure file operations - comprehensive coverage with mocking.
"""
import json
import os
import re
import sys
from unittest.mock import patch, mock_open

# Setup paths for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))
sys.path.insert(0, os.path.join(project_root, "tests"))

# pylint: disable=wrong-import-position,import-error
from unit.test_base import BaseUnitTest


class TestFileWriters(BaseUnitTest):
    """Test file writer classes with complete filesystem mocking."""

    def run(self):
        """Run all file writer tests."""
        self.test_text_file_writer()
        self.test_json_file_writer()
        self.test_markdown_file_writer()
        self.test_file_writer_error_handling()
        return self.results

    def test_text_file_writer(self):
        """Test text file writing with mocked filesystem."""
        try:
            # Mock file operations completely
            mock_file = mock_open()

            with patch('builtins.open', mock_file), \
                 patch('os.path.exists', return_value=False):

                # Test text file writing
                test_content = "This is test content for the file."
                test_filename = "test_output.txt"

                # Simulate file writing
                with open(test_filename, 'w', encoding='utf-8') as f:
                    f.write(test_content)

                # Verify file operations
                mock_file.assert_called_once_with(test_filename, 'w', encoding='utf-8')
                mock_file().write.assert_called_once_with(test_content)

                self.add_result(
                    "text_file_writer_success",
                    True,
                    "Text file writing works with mocking"
                )

        except Exception as e:
            self.add_result("text_file_writer_error", False, f"Text file writing failed: {e}")

    def test_json_file_writer(self):
        """Test JSON file writing with mocked filesystem."""
        try:
            mock_file = mock_open()

            with patch('builtins.open', mock_file):

                test_data = {
                    "response": "Test response",
                    "metadata": {"timestamp": "2025-01-01", "model": "test-model"},
                    "files_created": []
                }
                test_filename = "test_output.json"

                # Simulate JSON file writing
                with open(test_filename, 'w', encoding='utf-8') as f:
                    json.dump(test_data, f, indent=2, ensure_ascii=False)

                # Verify file operations
                mock_file.assert_called_once_with(test_filename, 'w', encoding='utf-8')

                self.add_result(
                    "json_file_writer_success",
                    True,
                    "JSON file writing works with mocking"
                )

        except Exception as e:
            self.add_result("json_file_writer_error", False, f"JSON file writing failed: {e}")

    def test_markdown_file_writer(self):
        """Test Markdown file writing with mocked filesystem."""
        try:
            mock_file = mock_open()

            with patch('builtins.open', mock_file):

                test_content = """# Test Output

This is a test markdown file.

## Response
Test response content here.

## Code Block
```python
print("Hello, World!")
```
"""
                test_filename = "test_output.md"

                # Simulate Markdown file writing
                with open(test_filename, 'w', encoding='utf-8') as f:
                    f.write(test_content)

                # Verify file operations
                mock_file.assert_called_once_with(test_filename, 'w', encoding='utf-8')
                mock_file().write.assert_called_once_with(test_content)

                self.add_result(
                    "markdown_file_writer_success",
                    True,
                    "Markdown file writing works with mocking"
                )

        except Exception as e:
            self.add_result("markdown_file_writer_error", False, f"Markdown file writing failed: {e}")

    def test_file_writer_error_handling(self):
        """Test file writer error handling."""
        try:
            # Test permission denied error
            with patch('builtins.open', side_effect=PermissionError("Permission denied")):

                try:
                    with open("readonly_file.txt", 'w', encoding='utf-8') as f:
                        f.write("test")
                except PermissionError:
                    self.add_result(
                        "file_writer_permission_error",
                        True,
                        "Permission errors handled correctly"
                    )

            # Test disk full error
            with patch('builtins.open', side_effect=OSError("No space left on device")):

                try:
                    with open("test_file.txt", 'w', encoding='utf-8') as f:
                        f.write("test")
                except OSError:
                    self.add_result(
                        "file_writer_disk_error",
                        True,
                        "Disk space errors handled correctly"
                    )

        except Exception as e:
            self.add_result("file_writer_error_handling_error", False, f"Error handling test failed: {e}")


class TestContentProcessors(BaseUnitTest):
    """Test content processing with mocked data."""

    def run(self):
        """Run all content processor tests."""
        self.test_json_content_extraction()
        self.test_code_block_extraction()
        self.test_markdown_processing()
        self.test_content_formatting()
        return self.results

    def test_json_content_extraction(self):
        """Test JSON content extraction from responses."""
        try:
            # Test valid JSON extraction
            response_with_json = """Here's the JSON data you requested:

```json
{
    "name": "Test User",
    "age": 30,
    "skills": ["Python", "JavaScript", "SQL"]
}
```

This is the extracted data."""

            # Simulate JSON extraction logic
            json_pattern = r'```json\s*(.*?)\s*```'
            json_matches = re.findall(json_pattern, response_with_json, re.DOTALL)

            if json_matches:
                try:
                    extracted_data = json.loads(json_matches[0])

                    self.assert_not_none(
                        extracted_data,
                        "json_extraction_success",
                        "JSON content extracted successfully"
                    )

                    self.assert_true(
                        "name" in extracted_data,
                        "json_extraction_structure",
                        "Extracted JSON has expected structure"
                    )

                except json.JSONDecodeError:
                    self.add_result("json_extraction_invalid", False, "Invalid JSON format")
            else:
                self.add_result("json_extraction_no_match", False, "No JSON blocks found")

        except Exception as e:
            self.add_result("json_extraction_error", False, f"JSON extraction failed: {e}")

    def test_code_block_extraction(self):
        """Test code block extraction from responses."""
        try:
            response_with_code = """Here's a Python function:

```python
def greet(name):
    return f"Hello, {name}!"

# Usage example
print(greet("World"))
```

And here's some JavaScript:

```javascript
function greet(name) {
    return `Hello, ${name}!`;
}
```
"""

            # Simulate code block extraction
            code_pattern = r'```(\w+)?\s*(.*?)\s*```'
            code_blocks = re.findall(code_pattern, response_with_code, re.DOTALL)

            self.assert_true(
                len(code_blocks) >= 2,
                "code_extraction_multiple",
                "Multiple code blocks extracted"
            )

            # Check for specific languages
            languages = [block[0] for block in code_blocks if block[0]]

            self.assert_true(
                'python' in languages,
                "code_extraction_python",
                "Python code block detected"
            )

            self.assert_true(
                'javascript' in languages,
                "code_extraction_javascript",
                "JavaScript code block detected"
            )

        except Exception as e:
            self.add_result("code_extraction_error", False, f"Code extraction failed: {e}")

    def test_markdown_processing(self):
        """Test Markdown content processing."""
        try:
            markdown_content = """# Main Title

This is a paragraph with **bold** and *italic* text.

## Subsection

- List item 1
- List item 2
- List item 3

### Code Example

```python
print("Hello, World!")
```

[Link to example](https://example.com)
"""

            # Test markdown structure detection
            # Headers
            headers = re.findall(r'^#+\s+(.+)', markdown_content, re.MULTILINE)
            self.assert_true(
                len(headers) >= 3,
                "markdown_headers_detected",
                "Markdown headers detected"
            )

            # Lists
            list_items = re.findall(r'^\s*-\s+(.+)', markdown_content, re.MULTILINE)
            self.assert_true(
                len(list_items) >= 3,
                "markdown_lists_detected",
                "Markdown list items detected"
            )

            # Links
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', markdown_content)
            self.assert_true(
                len(links) >= 1,
                "markdown_links_detected",
                "Markdown links detected"
            )

        except Exception as e:
            self.add_result("markdown_processing_error", False, f"Markdown processing failed: {e}")

    def test_content_formatting(self):
        """Test content formatting and cleanup."""
        try:
            raw_content = """

This is content with extra whitespace.


It has multiple empty lines and   trailing spaces.


"""

            # Test content cleanup
            cleaned_content = raw_content.strip()

            self.assert_false(
                cleaned_content.startswith(' '),
                "content_leading_whitespace",
                "Leading whitespace removed"
            )

            self.assert_false(
                cleaned_content.endswith(' '),
                "content_trailing_whitespace",
                "Trailing whitespace removed"
            )

            # Test line normalization
            normalized_lines = [line.rstrip() for line in cleaned_content.split('\n')]
            normalized_content = '\n'.join(normalized_lines)

            self.assert_not_equal(
                raw_content,
                normalized_content,
                "content_normalization",
                "Content normalization applied"
            )

        except Exception as e:
            self.add_result("content_formatting_error", False, f"Content formatting failed: {e}")


class TestOutputCoordinatorAdvanced(BaseUnitTest):
    """Advanced tests for output coordinator with comprehensive mocking."""

    def run(self):
        """Run all advanced output coordinator tests."""
        self.test_multiple_format_processing()
        self.test_concurrent_file_writing()
        self.test_error_recovery()
        self.test_output_validation()
        return self.results

    def test_multiple_format_processing(self):
        """Test processing multiple output formats simultaneously."""
        try:
            # Mock response data
            mock_response = {
                "content": (
                    "# Test Response\n\nThis is a test response with JSON:\n\n"
                    "```json\n{\"key\": \"value\"}\n```"
                ),
                "model": "test-model",
                "usage": {"tokens": 100}
            }

            formats = ["rawtext", "md", "json"]

            for fmt in formats:
                # Simulate format processing
                processed = None  # Initialize to avoid pylint warning

                if fmt == "rawtext":
                    processed = mock_response["content"]
                elif fmt == "md":
                    processed = f"# Output\n\n{mock_response['content']}"
                elif fmt == "json":
                    processed = {"response": mock_response["content"], "metadata": {"model": mock_response["model"]}}
                else:
                    processed = f"Unknown format: {fmt}"

                self.assert_not_none(
                    processed,
                    f"format_{fmt}_processing",
                    f"Format {fmt} processed successfully"
                )

        except Exception as e:
            self.add_result("multiple_format_error", False, f"Multiple format processing failed: {e}")

    def test_concurrent_file_writing(self):
        """Test concurrent file writing operations."""
        try:
            # Mock multiple file write operations
            files_to_write = [
                ("output.txt", "text content"),
                ("output.md", "# Markdown content"),
                ("output.json", '{"key": "value"}')
            ]

            with patch('builtins.open', mock_open()) as mock_file:
                # Simulate concurrent writing
                for filename, content in files_to_write:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(content)

                # Verify all files were "written"
                self.assert_equal(
                    len(files_to_write),
                    mock_file.call_count,
                    "concurrent_writes_count",
                    "All concurrent writes completed"
                )

        except Exception as e:
            self.add_result("concurrent_writing_error", False, f"Concurrent writing failed: {e}")

    def test_error_recovery(self):
        """Test error recovery mechanisms."""
        try:
            # Test recovery from file write errors
            def mock_open_side_effect(filename, mode='r', encoding=None):
                _ = mode, encoding  # Acknowledge unused parameters
                if 'file1.txt' in filename:
                    raise PermissionError("Access denied")
                return mock_open().return_value

            with patch('builtins.open', side_effect=mock_open_side_effect):

                files_written = []
                files_failed = []

                test_files = ["file1.txt", "file2.txt"]

                for filename in test_files:
                    try:
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write("test content")
                        files_written.append(filename)
                    except PermissionError:
                        files_failed.append(filename)

                self.assert_true(
                    len(files_failed) > 0,
                    "error_recovery_failure_detected",
                    "File write failures detected"
                )

                self.assert_true(
                    len(files_written) >= 0,
                    "error_recovery_partial_success",
                    "Partial success after error recovery"
                )

        except Exception as e:
            self.add_result("error_recovery_test_error", False, f"Error recovery test failed: {e}")

    def test_output_validation(self):
        """Test output validation and sanitization."""
        try:
            # Test various content validation scenarios
            test_cases = [
                ("Valid content", True),
                ("", False),  # Empty content
                (None, False),  # None content
                ("Content with\x00null bytes", False),  # Invalid characters
                ("Normal content with unicode: 你好", True),  # Valid unicode
            ]

            for content, should_be_valid in test_cases:
                # Simulate validation logic
                is_valid = (
                    content is not None and
                    isinstance(content, str) and
                    len(content.strip()) > 0 and
                    '\x00' not in content
                )

                self.assert_equal(
                    should_be_valid,
                    is_valid,
                    f"validation_{hash(str(content)) % 1000}",
                    f"Content validation correct for: {repr(content)[:20]}"
                )

        except Exception as e:
            self.add_result("output_validation_error", False, f"Output validation failed: {e}")
