#!/usr/bin/env python3

"""Test script to verify content extraction fix."""

import json
import sys
import os

# Add the python directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

from python.output.processors.content_extractor import ContentExtractor

def test_double_escaped_json():
    """Test extracting content from double-escaped JSON like in the log."""

    # This simulates the response structure from the log
    test_response = {
        'content': '{\n  "results": {\n    "explanation": "This command will:\\n- List all files in /var/log directory (-l flag)\\n- Show hidden files (-a flag)\\n- Sort by modification time (-t flag)\\n- Display in long format with permissions and timestamps\\n- Show human-readable file sizes (-h flag)\\n\\nSafety notes:\\n- This is a read-only command\\n- Requires read permissions on /var/log\\n- Safe to run as regular user",\n    "command": "ls -lath /var/log"\n  }\n}',
        'annotations': [],
        'full_response': {'id': 'gen-test'}
    }

    extractor = ContentExtractor()

    print("Testing content extraction...")
    print("Original response content:")
    print(repr(test_response['content']))
    print()

    # Extract structured data
    structured_data = extractor.extract_structured_data(test_response)

    print("Extracted structured data:")
    print(json.dumps(structured_data, indent=2))
    print()

    # Check if explanation and command are found
    if 'explanation' in structured_data and 'command' in structured_data:
        print("✅ SUCCESS: Both 'explanation' and 'command' found!")
        print(f"Command: {structured_data['command']}")
        print(f"Explanation: {structured_data['explanation'][:100]}...")
        return True
    else:
        print("❌ FAILURE: Missing explanation or command")
        print(f"Found keys: {list(structured_data.keys())}")
        return False

if __name__ == "__main__":
    success = test_double_escaped_json()
    sys.exit(0 if success else 1)
