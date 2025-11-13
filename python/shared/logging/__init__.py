"""
Logging infrastructure for the AskAI CLI application.
"""
import logging

# Import main functions for backward compatibility
from .setup import setup_logger, LOGGER_NAME

def get_logger() -> logging.Logger:
    """Get the application logger instance.

    This returns the same logger instance used throughout the application.
    The logger should be initialized first using setup_logger().

    Returns:
        logging.Logger: The application logger instance
    """
    return logging.getLogger(LOGGER_NAME)

__all__ = ['setup_logger', 'get_logger', 'LOGGER_NAME']
