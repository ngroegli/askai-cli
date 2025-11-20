"""
Utilities package for AskAI CLI.

This package contains shared utilities, configuration management,
logging setup, and helper functions used across the application.
"""

from .config import load_config
from .logging import setup_logger, get_logger
from .helpers import (
    print_error_or_warnings,
    tqdm_spinner,
    get_piped_input,
    get_file_input,
    build_format_instruction,
    encode_file_to_base64,
    run_command,
    safe_json_parse,
    format_file_size,
    truncate_string,
    validate_file_extension,
    create_temp_file,
    generate_output_format_template
)

__all__ = [
    'load_config',
    'setup_logger',
    'get_logger',
    'print_error_or_warnings',
    'tqdm_spinner',
    'get_piped_input',
    'get_file_input',
    'build_format_instruction',
    'encode_file_to_base64',
    'run_command',
    'safe_json_parse',
    'format_file_size',
    'truncate_string',
    'validate_file_extension',
    'create_temp_file',
    'generate_output_format_template'
]
