"""
Logger module for AskAI CLI application.

Configures application-wide logging with JSON formatting,
log rotation, and configurable log levels.
"""
import logging
import os
import json
from typing import Dict, Any
from logging.handlers import RotatingFileHandler

# Constants for logger configuration
LOGGER_NAME = 'askai'
DEFAULT_LOG_PATH = '~/.askai/askai.log'
DEFAULT_LOG_LEVEL = 'INFO'
DEFAULT_LOG_ROTATION = 5
MAX_LOG_SIZE_MB = 5
MAX_LOG_SIZE_BYTES = MAX_LOG_SIZE_MB * 1024 * 1024
JSON_LOG_FORMAT = '{"timestamp": "%(asctime)s", "log_level": "%(levelname)s", "log_entry": %(message)s}'


def get_log_level(level_name: str) -> int:
    """Convert string log level to logging constant.

    Args:
        level_name: String representation of log level (e.g., 'INFO', 'DEBUG')

    Returns:
        int: Logging level constant
    """
    return getattr(logging, level_name.upper(), logging.INFO)


def create_log_directory(log_path: str) -> None:
    """Create directory for log file if it doesn't exist.

    Args:
        log_path: Path where log file will be stored
    """
    log_dir = os.path.dirname(log_path)
    os.makedirs(log_dir, exist_ok=True)


def setup_logger(config: Dict[str, Any], debug: bool = False) -> logging.Logger:
    """Set up and configure the application logger.

    Args:
        config: Configuration dictionary containing logging settings
        debug: Flag to enable debug mode (overrides config log level)

    Returns:
        logging.Logger: Configured logger instance

    Configuration options:
        - enable_logging: bool (default: True)
        - log_path: str (default: ~/.askai/askai.log)
        - log_level: str (default: INFO)
        - log_rotation: int (default: 5)
    """
    # Return dummy logger if logging is disabled
    if not config.get('enable_logging', True):
        return logging.getLogger(LOGGER_NAME)

    # Configure logging parameters
    log_path = os.path.expanduser(config.get('log_path', DEFAULT_LOG_PATH))
    log_level = get_log_level(config.get('log_level', DEFAULT_LOG_LEVEL))
    log_rotation = config.get('log_rotation', DEFAULT_LOG_ROTATION)

    # Ensure log directory exists
    create_log_directory(log_path)

    # Set up logger
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(log_level)

    # Override log level if debug mode is enabled
    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug(json.dumps({"log_message": "Debug mode activated via CLI"}))

    # Configure rotating file handler
    handler = RotatingFileHandler(
        log_path,
        maxBytes=MAX_LOG_SIZE_BYTES,
        backupCount=log_rotation
    )

    # Set up JSON formatter
    formatter = logging.Formatter(JSON_LOG_FORMAT)
    handler.setFormatter(formatter)

    # Add handler if not already present
    if not logger.handlers:
        logger.addHandler(handler)

    return logger


def get_logger() -> logging.Logger:
    """Get the configured application logger instance.

    Returns:
        logging.Logger: The existing logger instance, or creates a basic one if not configured

    Note:
        This function returns the logger that was previously configured with setup_logger().
        If no logger was configured, it returns a basic logger with the application name.
    """
    return logging.getLogger(LOGGER_NAME)
