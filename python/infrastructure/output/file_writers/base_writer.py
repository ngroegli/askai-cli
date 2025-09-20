"""
Base writer interface for the Chain of Responsibility pattern.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging
import re
from pathlib import Path


class BaseWriter(ABC):
    """Abstract base class for file writers using Chain of Responsibility pattern."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize the base writer.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self._next_writer: Optional['BaseWriter'] = None

    def set_next(self, writer: 'BaseWriter') -> 'BaseWriter':
        """Set the next writer in the chain.

        Args:
            writer: Next writer in the chain

        Returns:
            BaseWriter: The writer that was set as next (for chaining)
        """
        self._next_writer = writer
        return writer

    def handle(self, content: str, file_path: str, content_type: str,
               additional_params: Optional[Dict[str, Any]] = None) -> bool:
        """Handle the write request or pass to next writer.

        Args:
            content: Content to write
            file_path: Path where to write the file
            content_type: Type of content (from pattern output type field)
            additional_params: Additional parameters for specific file types

        Returns:
            bool: True if successful, False otherwise
        """
        if self.can_handle(content_type):
            return self.write(content, file_path, additional_params)
        if self._next_writer:
            return self._next_writer.handle(content, file_path, content_type, additional_params)
        self.logger.warning(f"No writer found for content type: {content_type}")
        return False

    @abstractmethod
    def can_handle(self, content_type: str) -> bool:
        """Check if this writer can handle the given content type.

        Args:
            content_type: Type of content to check

        Returns:
            bool: True if this writer can handle the content type
        """

    @abstractmethod
    def write(self, content: str, file_path: str,
              additional_params: Optional[Dict[str, Any]] = None) -> bool:
        """Write content to file with specific formatting.

        Args:
            content: Content to write
            file_path: Path where to write the file
            additional_params: Additional parameters for specific file types

        Returns:
            bool: True if successful, False otherwise
        """


    def _ensure_directory(self, file_path: str) -> None:
        """Ensure the directory for the file path exists.

        Args:
            file_path: File path to check
        """
        path_obj = Path(file_path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)

    def _clean_content(self, content: str) -> str:
        """Clean content by removing escape characters and code blocks.

        Args:
            content: Content to clean

        Returns:
            str: Cleaned content
        """
        if not isinstance(content, str):
            return str(content)

        # Remove generic code block markers
        content = re.sub(r'^```\w*\s*', '', content)
        content = re.sub(r'\s*```$', '', content)

        # Handle escape sequences
        cleaned = content.replace('\\n', '\n')
        cleaned = cleaned.replace('\\"', '"')
        cleaned = cleaned.replace("\\'", "'")
        cleaned = cleaned.replace('\\\\', '\\')
        cleaned = cleaned.replace('\\t', '\t')
        cleaned = cleaned.replace('\\r', '\r')

        return cleaned

    def _write_file(self, content: str, file_path: str) -> bool:
        """Write content to file with proper error handling.

        Args:
            content: Content to write
            file_path: Path where to write the file

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self._ensure_directory(file_path)

            # Sanitize content
            if content is None:
                content = ""
                self.logger.warning(f"Null content provided for {file_path}, using empty string")

            if not isinstance(content, str):
                content = str(content)
                self.logger.warning("Non-string content converted for %s", file_path)

            # Write the file
            with open(file_path, 'w', encoding='utf-8', errors='replace') as f:
                f.write(content)

            self.logger.info("Content written to %s (%d chars)", file_path, len(content))
            return True

        except Exception as e:
            self.logger.error("Error writing to %s: %s", file_path, str(e))
            return False
