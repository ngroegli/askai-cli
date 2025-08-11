"""
Output handling module for askai-cli.
This module handles all aspects of output processing, extraction, formatting, and writing.
"""

from .common import unescape_string, looks_like_command
from .output_handler import OutputHandler
from .file_writer import FileWriter

__all__ = [
    "OutputHandler",
    "FileWriter",
    "unescape_string",
    "looks_like_command"
]
