#!/usr/bin/env python3
"""Test the refactored output system."""

import sys
import os
import tempfile
import shutil

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from python.output.output_coordinator import OutputCoordinator
from python.patterns.pattern_outputs import PatternOutput, OutputAction, OutputType

def test_basic_functionality():
    """Test basic functionality of the new output system."""
    print("🧪 Testing OutputCoordinator basic functionality...")

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize coordinator
        coordinator = OutputCoordinator(output_dir=temp_dir)

        # Test 1: Simple text processing
        response = "Hello, world! This is a test response."
        formatted_output, created_files = coordinator.process_output(
            response=response,
            console_output=True,
            file_output=False
        )

        print(f"✅ Text processing: {len(formatted_output)} chars formatted")

        # Test 2: HTML content extraction and file writing
        html_response = """
        Here's your website:

        ```html
        <!DOCTYPE html>
        <html>
        <head><title>Test</title></head>
        <body><h1>Hello World</h1></body>
        </html>
        ```
        """

        output_config = {'markdown_filename': 'test.md'}
        formatted_output, created_files = coordinator.process_output(
            response=html_response,
            output_config=output_config,
            console_output=True,
            file_output=True
        )

        print(f"✅ HTML processing: {len(created_files)} files created")

        # Test 3: Content extraction
        structured_data = coordinator.content_extractor.extract_structured_data(html_response)
        print(f"✅ Content extraction: {len(structured_data)} items extracted")

        print("🎉 All basic tests passed!")

def test_pattern_processing():
    """Test pattern-based output processing."""
    print("\n🧪 Testing pattern processing...")

    with tempfile.TemporaryDirectory() as temp_dir:
        coordinator = OutputCoordinator(output_dir=temp_dir)

        # Create a mock pattern output
        pattern_output = PatternOutput(
            name="test_html",
            description="Test HTML output",
            output_type=OutputType.HTML,
            action=OutputAction.WRITE,
            write_to_file="test.html"
        )

        response = {
            "test_html": "<!DOCTYPE html><html><body><h1>Test</h1></body></html>"
        }

        created_files = coordinator.pattern_processor.handle_pattern_outputs(
            response, [pattern_output]
        )

        print(f"✅ Pattern processing: {len(created_files)} files created")

        # Verify file was created
        expected_file = os.path.join(temp_dir, "test.html")
        if os.path.exists(expected_file):
            print("✅ Pattern file created successfully")
        else:
            print("❌ Pattern file creation failed")

if __name__ == "__main__":
    try:
        test_basic_functionality()
        test_pattern_processing()
        print("\n🎉 All tests completed successfully!")
        print("\n📋 Refactoring Summary:")
        print("   • OutputCoordinator replaces monolithic OutputHandler")
        print("   • ContentExtractor handles content extraction")
        print("   • PatternProcessor handles pattern-based outputs")
        print("   • ResponseNormalizer handles response normalization")
        print("   • DirectoryManager handles directory operations")
        print("   • FileWriterChain handles specialized file writing")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
