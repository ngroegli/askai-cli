"""
General utility functions for the AskAI CLI application.
Contains core util handling, command execution, and formatting.
"""

import base64
import itertools
import json
import os
import shlex
import subprocess
import sys
import tempfile
import time
from termcolor import cprint


def tqdm_spinner(stop_event):
    """Displays a rotating spinner using tqdm."""
    # Check if we're running in a test environment
    in_test_env = os.environ.get('ASKAI_TESTING', '').lower() in ('true', '1', 'yes')

    thinking_color = "light_cyan"
    result_color = "green"

    # Skip the spinner animation if we're in a test environment
    if in_test_env:
        # In tests, just wait for the stop event without visual updates
        stop_event.wait()
        return

    # Display initial thinking message
    cprint("AI is thinking", thinking_color, end="", flush=True)

    # Create a spinner using itertools.cycle for the characters
    spinner = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])

    # Continue spinning until stop_event is set
    try:
        while not stop_event.is_set():
            # Clear the line and show spinner with message
            cprint(f"\rAI is thinking {next(spinner)}", thinking_color, end="", flush=True)
            time.sleep(0.1)  # Control the spinner speed

        # Clear the line and show completion message
        cprint(f"\r{' ' * 20}\r", end="", flush=True)  # Clear the spinner line
        cprint("✓ AI response ready", result_color, flush=True)

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        cprint(f"\r{' ' * 20}\r", end="", flush=True)  # Clear the spinner line
        cprint("✗ AI request cancelled", "red", flush=True)
        # Re-raise the KeyboardInterrupt to be handled by the calling code
        raise


def print_error_or_warnings(message, is_warning=False, exit_on_error=True):
    """
    Print error or warning messages to stderr with optional exit.

    Args:
        message (str): The error or warning message to display
        is_warning (bool): If True, treat as warning (yellow), else as error (red)
        exit_on_error (bool): If True, exit with status 1 on errors
    """
    if is_warning:
        cprint(f"⚠ WARNING: {message}", "yellow", file=sys.stderr)
    else:
        cprint(f"✗ ERROR: {message}", "red", file=sys.stderr)
        if exit_on_error:
            sys.exit(1)


def get_piped_input():
    """
    Reads from stdin if data is piped in.

    Returns:
        str or None: The piped input content, or None if no piped data
    """
    try:
        # Check if data is available on stdin without blocking
        if not sys.stdin.isatty():
            # There's piped data available
            piped_input = sys.stdin.read().strip()
            return piped_input if piped_input else None
    except Exception as e:
        print_error_or_warnings(f"Error reading piped input: {e}", is_warning=True, exit_on_error=False)
    return None


def get_file_input(file_path):
    """
    Reads content from a file path.

    Args:
        file_path (str): Path to the file to read

    Returns:
        bytes: The file content as bytes, or None if error
    """
    try:
        if not os.path.exists(file_path):
            print_error_or_warnings(f"File not found: {file_path}")
            return None

        if not os.path.isfile(file_path):
            print_error_or_warnings(f"Path is not a file: {file_path}")
            return None

        # Check if file is readable
        if not os.access(file_path, os.R_OK):
            print_error_or_warnings(f"File is not readable: {file_path}")
            return None

        # Check file size (limit to 100MB for safety)
        file_size = os.path.getsize(file_path)
        max_size = 100 * 1024 * 1024  # 100MB
        if file_size > max_size:
            print_error_or_warnings(f"File too large: {file_path} ({file_size} bytes > {max_size} bytes)")
            return None

        try:
            # Open and read the file in binary mode
            with open(file_path, "rb") as file:
                file_content = file.read()
                # file_content is always bytes when reading in binary mode
                return file_content
        except Exception as read_error:
            print_error_or_warnings(f"Error reading file {file_path}: {read_error}")
            return None

    except Exception as e:
        print_error_or_warnings(f"Error accessing file {file_path}: {e}")
        return None


def build_format_instruction(response_format):
    """
    Build format instruction for AI based on user's format choice.

    Args:
        response_format (str): The desired response format ('rawtext', 'json', 'md')

    Returns:
        str: The format instruction to add to the AI prompt
    """
    if response_format == "json":
        return (
            "\n\nIMPORTANT: Provide your response in valid JSON format only. "
            "Do not include any text before or after the JSON."
        )
    elif response_format == "md":
        return "\n\nIMPORTANT: Format your response using Markdown syntax for better readability."
    else:
        # rawtext (default) - no special formatting instruction needed
        return ""


def encode_file_to_base64(file_path):
    """
    Encode a file to base64 format.

    Args:
        file_path (str): Path to the file to encode

    Returns:
        str or None: Base64 encoded string, or None if error
    """
    try:
        file_content = get_file_input(file_path)
        if file_content is None:
            return None

        # Encode to base64
        encoded_content = base64.b64encode(file_content).decode('utf-8')
        return encoded_content

    except Exception as e:
        print_error_or_warnings(f"Error encoding file to base64: {e}")
        return None


def run_command(command, capture_output=True, shell=False, timeout=30):
    """
    Execute a shell command safely.

    Args:
        command (str or list): The command to execute
        capture_output (bool): Whether to capture stdout/stderr
        shell (bool): Whether to run through shell
        timeout (int): Command timeout in seconds

    Returns:
        tuple: (return_code, stdout, stderr)
    """
    try:
        if isinstance(command, str) and not shell:
            # Split string command into list for safety
            command = shlex.split(command)

        result = subprocess.run(
            command,
            capture_output=capture_output,
            shell=shell,
            timeout=timeout,
            text=True,
            check=False
        )

        stdout = result.stdout if capture_output else ""
        stderr = result.stderr if capture_output else ""

        return result.returncode, stdout, stderr

    except subprocess.TimeoutExpired:
        print_error_or_warnings(f"Command timed out after {timeout} seconds", is_warning=True, exit_on_error=False)
        return -1, "", "Command timed out"
    except Exception as e:
        print_error_or_warnings(f"Error executing command: {e}", is_warning=True, exit_on_error=False)
        return -1, "", str(e)


def safe_json_parse(json_string):
    """
    Safely parse JSON string with error handling.

    Args:
        json_string (str): JSON string to parse

    Returns:
        dict or None: Parsed JSON object, or None if parsing fails
    """
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print_error_or_warnings(f"JSON parsing error: {e}", is_warning=True, exit_on_error=False)
        return None
    except Exception as e:
        print_error_or_warnings(f"Unexpected error parsing JSON: {e}", is_warning=True, exit_on_error=False)
        return None


def format_file_size(size_bytes):
    """
    Format file size in human readable format.

    Args:
        size_bytes (int): Size in bytes

    Returns:
        str: Formatted size string
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024.0 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"


def truncate_string(text, max_length=100, suffix="..."):
    """
    Truncate a string to a maximum length with suffix.

    Args:
        text (str): Text to truncate
        max_length (int): Maximum length including suffix
        suffix (str): Suffix to add when truncating

    Returns:
        str: Truncated string
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def validate_file_extension(file_path, allowed_extensions):
    """
    Validate that a file has an allowed extension.

    Args:
        file_path (str): Path to the file
        allowed_extensions (list): List of allowed extensions (with dots, e.g., ['.jpg', '.png'])

    Returns:
        bool: True if extension is allowed, False otherwise
    """
    if not file_path:
        return False

    file_ext = os.path.splitext(file_path)[1].lower()
    return file_ext in [ext.lower() for ext in allowed_extensions]


def create_temp_file(content, suffix="", prefix="askai_"):
    """
    Create a temporary file with given content.

    Args:
        content (str or bytes): Content to write to the file
        suffix (str): File suffix
        prefix (str): File prefix

    Returns:
        str or None: Path to the created temporary file, or None if error
    """
    try:
        mode = "w" if isinstance(content, str) else "wb"
        encoding = "utf-8" if isinstance(content, str) else None

        with tempfile.NamedTemporaryFile(
            mode=mode,
            delete=False,
            suffix=suffix,
            prefix=prefix,
            encoding=encoding
        ) as temp_file:
            temp_file.write(content)
            return temp_file.name

    except Exception as e:
        print_error_or_warnings(f"Error creating temporary file: {e}", is_warning=True, exit_on_error=False)
        return None


def generate_output_format_template(pattern_outputs):
    """
    Generate output format template based on pattern outputs.

    Args:
        pattern_outputs (list): List of pattern output configurations

    Returns:
        str: Generated format template
    """
    if not pattern_outputs:
        return ""

    try:
        # Build a template based on the expected outputs
        template_parts = []
        template_parts.append("Please structure your response according to the following format:")

        for output in pattern_outputs:
            output_type = getattr(output, 'type', 'unknown')
            output_description = getattr(output, 'description', f'{output_type} output')

            template_parts.append(f"- {output_type.title()}: {output_description}")

        return "\n".join(template_parts)

    except Exception as e:
        print_error_or_warnings(
            f"Error generating output format template: {e}",
            is_warning=True,
            exit_on_error=False
        )

        return ""
