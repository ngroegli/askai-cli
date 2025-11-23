"""
Base class for display formatters.
"""

from abc import ABC, abstractmethod
from typing import Optional
import logging


class BaseDisplayFormatter(ABC):  # pylint: disable=too-few-public-methods
    """Base class for formatters that format content for different display outputs."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize formatter with optional logger.

        Args:
            logger: Optional logger for logging messages
        """
        self.logger = logger

    @abstractmethod
    def format(self, content: str, **kwargs) -> str:
        """Format content according to specific display rules.

        Args:
            content: Content to format
            kwargs: Additional formatting options

        Returns:
            str: Formatted content
        """

    def _apply_custom_formatters(self, content: str, **kwargs) -> str:
        """Apply custom formatter functions from kwargs.

        Args:
            content: Content to format
            kwargs: May contain custom formatter functions prefixed with 'format_'

        Returns:
            str: Content after applying custom formatters
        """
        formatted = content
        for key, value in kwargs.items():
            if key.startswith('format_') and callable(value):
                formatted = str(value(formatted))
        return formatted

    def _truncate_content(self, content: str, max_length: int = 1000,
                         ellipsis: str = "...\n[content truncated]") -> str:
        """Truncate content if it exceeds maximum length.

        Args:
            content: Content to truncate
            max_length: Maximum length before truncation
            ellipsis: Text to append when truncating

        Returns:
            str: Truncated content if needed, original otherwise
        """
        if len(content) > max_length:
            truncated = content[:max_length] + ellipsis
            if self.logger:
                self.logger.info("Content truncated from %d to %d characters", len(content), max_length)
            return truncated
        return content
