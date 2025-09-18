"""
Output handling module for askai-cli.
This module handles all aspects of output processing, extraction, formatting, and writing.
"""

from python.output.output_coordinator import OutputCoordinator
from python.output.file_writers.file_writer_chain import FileWriterChain

__all__ = [
    "OutputCoordinator",
    "FileWriterChain"
]
