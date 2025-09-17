"""
Text writer for handling plain text and unknown content types.
"""

from typing import Optional, Dict, Any
from .base_writer import BaseWriter


class TextWriter(BaseWriter):
    """Writer for plain text content and fallback for unknown types."""

    def can_handle(self, content_type: str) -> bool:
        """Check if this writer can handle the content type.

        Args:
            content_type: Type of content to check

        Returns:
            bool: True for text type or any unknown type (fallback)
        """
        return content_type.lower() in ['text', 'txt', 'plain'] or True  # Fallback writer

    def write(self, content: str, file_path: str,
              additional_params: Optional[Dict[str, Any]] = None) -> bool:
        """Write plain text content to file.

        Args:
            content: Content to write
            file_path: Path where to write the file
            additional_params: Additional parameters (unused for text)

        Returns:
            bool: True if successful, False otherwise
        """
        cleaned_content = self._clean_content(content)

        # Ensure proper file extension for text files
        if not file_path.lower().endswith(('.txt', '.text')):
            file_path += '.txt'

        return self._write_file(cleaned_content, file_path)
