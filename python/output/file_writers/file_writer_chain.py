"""
Chain of Responsibility coordinator for file writers.
"""

import os
from typing import List, Optional, Dict, Any
from .base_writer import BaseWriter
from .text_writer import TextWriter
from .html_writer import HtmlWriter
from .css_writer import CssWriter
from .js_writer import JsWriter
from .json_writer import JsonWriter
from .markdown_writer import MarkdownWriter


class FileWriterChain:
    """Coordinates multiple file writers using Chain of Responsibility pattern."""

    def __init__(self):
        """Initialize the chain with all available writers."""
        self.writers: List[BaseWriter] = [
            HtmlWriter(),
            CssWriter(),
            JsWriter(),
            JsonWriter(),
            MarkdownWriter(),
            TextWriter()  # TextWriter should be last as it's the fallback
        ]

    def write_file(self, content: str, file_path: str, content_type: str,
                   additional_params: Optional[Dict[str, Any]] = None) -> bool:
        """Write content using the appropriate writer from the chain.

        Args:
            content: Content to write
            file_path: Path where to write the file
            content_type: Type of content (e.g., 'html', 'css', 'js', 'json', 'markdown', 'text')
            additional_params: Additional parameters for the writer

        Returns:
            bool: True if successful, False otherwise
        """
        for writer in self.writers:
            if writer.can_handle(content_type):
                return writer.write(content, file_path, additional_params)

        # This should never happen since TextWriter handles all types
        # But just in case, return False
        return False

    def write_by_extension(self, content: str, file_path: str,
                          additional_params: Optional[Dict[str, Any]] = None) -> bool:
        """Write content based on file extension (compatibility method).

        This method provides compatibility with the old FileWriter interface.
        It determines the content type from the file extension.

        Args:
            content: Content to write
            file_path: Path where to write the file
            additional_params: Additional parameters for the writer

        Returns:
            bool: True if successful, False otherwise
        """
        # Extract extension and map to content type
        extension = os.path.splitext(file_path)[1].lower()

        # Map extensions to content types
        extension_mapping = {
            '.html': 'html',
            '.htm': 'html',
            '.css': 'css',
            '.js': 'js',
            '.json': 'json',
            '.md': 'markdown',
            '.markdown': 'markdown',
            '.txt': 'text',
            '': 'text'  # fallback for files without extension
        }

        content_type = extension_mapping.get(extension, 'text')
        return self.write_file(content, file_path, content_type, additional_params)

    def get_available_types(self) -> List[str]:
        """Get list of all content types that can be handled.

        Returns:
            List[str]: List of supported content types
        """
        types = []
        # Note: TextWriter handles all types as fallback, so we'll check specific ones
        test_types = ['html', 'css', 'js', 'javascript', 'json', 'markdown', 'md', 'text']

        for content_type in test_types:
            for writer in self.writers:
                if writer.can_handle(content_type):
                    if content_type not in types:
                        types.append(content_type)
                    break

        return sorted(types)

    def add_writer(self, writer: BaseWriter, position: Optional[int] = None) -> None:
        """Add a new writer to the chain.

        Args:
            writer: Writer instance to add
            position: Position to insert at (None for before TextWriter)
        """
        if position is None:
            # Insert before TextWriter (which should be last)
            self.writers.insert(-1, writer)
        else:
            self.writers.insert(position, writer)

    def remove_writer(self, writer_class: type) -> bool:
        """Remove a writer of the specified class from the chain.

        Args:
            writer_class: Class of writer to remove

        Returns:
            bool: True if removed, False if not found
        """
        for i, writer in enumerate(self.writers):
            if isinstance(writer, writer_class):
                del self.writers[i]
                return True
        return False
