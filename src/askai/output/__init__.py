"""
Output handling for AskAI CLI.

This package provides comprehensive output formatting, writing, and processing
capabilities for AI responses and pattern executions.
"""

from .coordinator import OutputCoordinator
from .formatters import MarkdownFormatter, TerminalFormatter
from .writers import FileWriterChain

__all__ = [
    'OutputCoordinator',
    'MarkdownFormatter',
    'TerminalFormatter',
    'FileWriterChain'
]
