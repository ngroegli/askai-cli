"""
Logging infrastructure for the AskAI CLI application.
"""

# Import main functions for backward compatibility
from .setup import setup_logger, get_logger

__all__ = ['setup_logger', 'get_logger']
