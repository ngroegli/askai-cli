"""
AskAI CLI - AI-powered command line interface for intelligent question processing.

This package provides a comprehensive CLI tool that leverages AI to process questions,
manage patterns, and provide intelligent responses through multiple interfaces including
traditional CLI, TUI, and REST API.
"""

# Import version from centralized location
from ._version import __version__, get_version, get_version_info, get_full_version

__author__ = "AskAI Team"
__email__ = "info@askai.com"
__license__ = "MIT"

# Import main components for easy access
from .utils.config import load_config
from .utils.logging import setup_logger, get_logger

__all__ = [
    '__version__',
    '__author__',
    '__email__',
    '__license__',
    'get_version',
    'get_version_info',
    'get_full_version',
    'load_config',
    'setup_logger',
    'get_logger',
]
