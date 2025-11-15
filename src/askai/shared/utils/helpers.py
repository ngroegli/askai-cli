"""
General utility functions for the AskAI CLI application.
Contains core util            # Open and read the file in binary mode
            with open(file_path, "rb") as file:
                file_content = file.read()
                # file_content is always bytes when reading in binary mode
                return file_contentdling, command execution, and formatting.
"""

import os
import sys
import itertools
import time
import subprocess
import base64
import json
from tqdm import tqdm
from termcolor import colored, cprint


def tqdm_spinner(stop_event):
    """Displays a rotating spinner using tqdm."""
    # Check if we're running in a test environment
    in_test_env = os.environ.get('ASKAI_TESTING', '').lower() in ('true', '1', 'yes')

    thinking_color = "light_cyan"
    result_color = "green"

    # Skip the spinner animation if we're in a test environment
    if in_test_env:
        # For tests, don't wait in a blocking loop, just return immediately
        # The test runner will handle the stop_event through other mechanisms
        return

    with tqdm(total=1, bar_format="{desc} {bar}", leave=False) as pbar:
        spinner_cycle = itertools.cycle(['|', '/', '-', '\\'])
        while not stop_event.is_set():
            pbar.set_description_str(colored(f"Thinking {next(spinner_cycle)}", thinking_color))
            time.sleep(0.1)
        pbar.close()
        cprint("HERE THE RESULT:", result_color)


def get_piped_input():
    """Reads piped stdin input, if available."""
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return None


def get_file_input(file_path):
    """Reads content from a file if it exists."""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    print_error_or_warnings(f"File {file_path} does not exist.", warning_only=True)
    return None


def encode_file_to_base64(file_path):
    """
    Reads any file and encodes it to base64.

    Args:
        file_path: Path to the file

    Returns:
        str: Base64 encoded string or None if file doesn't exist
    """
    # Check if file exists at the provided path
    if os.path.exists(file_path):
        try:
            # Check if the file is readable
            if not os.access(file_path, os.R_OK):
                print_error_or_warnings(f"No read permissions for file: {file_path}")
                return None

            # Get file size to verify it's not empty
            file_size = os.path.getsize(file_path)
            if not file_size:
                print_error_or_warnings(f"File is empty: {file_path}", warning_only=True)
                return None

            # Open and read the file in binary mode
            with open(file_path, "rb") as file:
                file_content = file.read()
                # file_content is always bytes when reading in binary mode

                # Encode the file content to base64
                encoded_string = base64.b64encode(file_content).decode('utf-8')

                # Ensure there are no whitespace, newlines or invalid chars
                encoded_string = ''.join(c for c in encoded_string if c.isalnum() or c in '+/=')

                # Verify we actually got an encoded string and it's valid
                if encoded_string:
                    # Validate that it's a proper base64 string
                    try:
                        # Try to decode to verify it's valid base64
                        test_decode = base64.b64decode(encoded_string)
                        # Make sure we can encode it back to the same string
                        test_reencode = base64.b64encode(test_decode).decode('utf-8')
                        if test_reencode != encoded_string:
                            print_error_or_warnings(
                                "Base64 re-encode test failed, may be an encoding issue",
                                warning_only=True
                            )
                        return encoded_string
                    except (ValueError, TypeError) as e:
                        print_error_or_warnings(f"Generated invalid base64 string: {str(e)}")
                        return None
                else:
                    print_error_or_warnings(f"Failed to encode file to base64: {file_path}")
                    return None
        except PermissionError:
            print_error_or_warnings(f"Permission denied when reading file: {file_path}")
            return None
        except (IOError, OSError, ValueError) as e:
            print_error_or_warnings(f"Error encoding file: {file_path} - {str(e)}")
            return None
    else:
        print_error_or_warnings(f"File does not exist at path: {file_path}", warning_only=True)
        # Try to resolve relative paths
        cwd = os.getcwd()
        potential_path = os.path.join(cwd, file_path)
        if os.path.exists(potential_path):
            print(f"Found file at absolute path, trying again: {potential_path}")
            return encode_file_to_base64(potential_path)
    return None


def build_format_instruction(format_type):
    """Returns AI instruction based on the desired response format."""
    return {
        "rawtext": "Please provide your response as plain text.",
        "md": "Please format the response as GitHub-flavored Markdown.",
        "json": "Please respond with a valid JSON structure containing your answer."
    }.get(format_type, "Please provide your response as plain text.")


def generate_output_format_template(pattern_outputs):
    """Generates a dynamic output format template based on pattern output definitions.

    Args:
        pattern_outputs: List of PatternOutput objects

    Returns:
        str: JSON format instruction template
    """
    if not pattern_outputs:
        return None

    # Create a template that matches the defined outputs
    result_fields = {}

    # Add each output to the result fields
    for output in pattern_outputs:
        # Get a sample value based on the output type
        if output.example:
            # Use the full example as provided
            example_value = output.example
        else:
            # Generate placeholder based on type
            if output.output_type.value == "text":
                example_value = f"sample text for {output.name}"
            elif output.output_type.value == "markdown":
                example_value = (
                    f"# Sample markdown for {output.name}\n\n"
                    "This is an example of markdown content."
                )
            elif output.output_type.value == "json":
                example_value = {"key": f"sample value for {output.name}"}
            elif output.output_type.value == "html":
                example_value = f"<div>Sample HTML for {output.name}</div>"
            elif output.output_type.value == "code":
                example_value = (
                    f"# Sample code for {output.name}\n"
                    "def example():\n"
                    "    return 'example'"
                )
            else:
                example_value = f"Sample content for {output.name}"

        # Add to result fields - ensure it's included no matter what the output action is
        result_fields[output.name] = example_value

    # Create the full template structure
    template = {
        "results": result_fields
    }

    # Convert to formatted JSON string with consistent indentation
    template_json = json.dumps(template, indent=2, ensure_ascii=False)

    # Build a comprehensive instruction with the template
    instruction = f"""**CRITICAL FORMATTING REQUIREMENT**

Your response MUST follow this exact JSON format without any deviations or additional text:


{template_json}


Where:
"""

    # Add detailed descriptions for each field
    for output in pattern_outputs:
        instruction += f"- `{output.name}`: {output.description}\n"

    # Add additional formatting requirements
    instruction += """
⚠️ CRITICAL FORMATTING REQUIREMENTS ⚠️

1. Use the EXACT field names specified above in your response.
2. The JSON object MUST have 'results' as its top-level field.
3. Do not include any additional fields or nested objects not present in the template.
4. All required fields MUST be present exactly as shown.
5. Make sure the JSON is valid and correctly formatted.
6. DO NOT wrap your response in markdown code blocks or use triple backticks (```).
7. DO NOT use any markdown formatting around your JSON response.
8. RETURN ONLY THE RAW JSON OBJECT - nothing else before or after.
9. DO NOT use \\n```json\\n as start for the response field content.

This is not a suggestion - this is a strict formatting requirement that must be followed exactly.
"""

    return instruction


def capture_command_output(command):
    """Run a shell command and capture output, return stdout as string."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)
    if result.returncode:
        raise subprocess.SubprocessError(f"Command failed: {result.stderr}")
    return result.stdout


def print_error_or_warnings(text, warning_only=False):
    """
    Print error or warning messages with appropriate background colors.

    Args:
        text: The message to print
        warning_only: If True, print a warning (yellow background), otherwise print an error (red background)
    """
    if warning_only:
        # Yellow background for warnings
        cprint(f"WARNING: {text}", "black", "on_yellow")
    else:
        # Red background for errors
        cprint(f"ERROR: {text}", "white", "on_red")
