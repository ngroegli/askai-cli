"""
General utilities and helper functions for the AskAI CLI application.
"""

# Import main functions for backward compatibility
from .helpers import (
    print_error_or_warnings,
    get_piped_input,
    get_file_input,
    encode_file_to_base64,
    build_format_instruction,
    generate_output_format_template,
    capture_command_output,
    tqdm_spinner
)

__all__ = [
    'print_error_or_warnings',
    'get_piped_input',
    'get_file_input',
    'encode_file_to_base64',
    'build_format_instruction',
    'generate_output_format_template',
    'capture_command_output',
    'tqdm_spinner'
]
