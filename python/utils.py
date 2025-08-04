"""
General utility functions for the AskAI CLI application.
Contains core utilities for input handling, command execution, and formatting.
"""

import os
import sys
import itertools
import time
import subprocess
import base64
from tqdm import tqdm
from termcolor import colored, cprint


def tqdm_spinner(stop_event):
    """Displays a rotating spinner using tqdm."""
    thinking_color = "light_cyan"
    result_color = "green"

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
        with open(file_path, "r") as f:
            return f.read()
    print(f"File {file_path} does not exist.")
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
                print(f"Error: No read permissions for file: {file_path}")
                return None
                
            # Get file size to verify it's not empty
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                print(f"Warning: File is empty: {file_path}")
                return None
                
            # Open and read the file in binary mode
            with open(file_path, "rb") as file:
                file_content = file.read()
                
                # Ensure it's actually binary data
                if not isinstance(file_content, bytes):
                    file_content = file_content.encode('utf-8')
                
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
                            print(f"Warning: Base64 re-encode test failed, may be an encoding issue")
                        return encoded_string
                    except Exception as e:
                        print(f"Error: Generated invalid base64 string: {str(e)}")
                        return None
                else:
                    print(f"Error: Failed to encode file to base64: {file_path}")
                    return None
        except PermissionError as e:
            print(f"Error: Permission denied when reading file: {file_path}")
            return None
        except Exception as e:
            print(f"Error encoding file: {file_path} - {str(e)}")
            return None
    else:
        print(f"File does not exist at path: {file_path}")
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


def capture_command_output(command):
    """Run a shell command and capture output, return stdout as string."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Command failed: {result.stderr}")
    return result.stdout


def print_error_or_warnings(text, warning_only=False):
    """Print error or warning messages with appropriate colors."""
    color = "red"
    if warning_only:
        color = "light_yellow"
    cprint(text, color)
    