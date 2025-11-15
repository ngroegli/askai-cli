"""
AskAI CLI - AI-powered command line interface for intelligent question processing.

This package provides a comprehensive CLI tool that leverages AI to process questions,
manage patterns, and provide intelligent responses through multiple interfaces including
traditional CLI, TUI, and REST API.
"""

__version__ = "0.1.0"
__author__ = "AskAI Team"
__email__ = "info@askai.com"
__license__ = "MIT"

# Import main components for easy access
from .shared.config.loader import load_config
from .shared.logging import setup_logger, get_logger

__all__ = [
    '__version__',
    '__author__',
    '__email__',
    '__license__',
    'load_config',
    'setup_logger',
    'get_logger',
]
