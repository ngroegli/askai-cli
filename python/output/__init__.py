"""
Output handling module for askai-cli.
This module handles all aspects of output processing, extraction, formatting, and writing.
"""

from python.output.common import unescape_string, looks_like_command
from python.output.output_handler import OutputHandler
from python.output.file_writers.file_writer_chain import FileWriterChain

__all__ = [
    "OutputHandler",
    "FileWriterChain",
    "unescape_string",
    "looks_like_command"
]
