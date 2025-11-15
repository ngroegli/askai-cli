"""
JavaScript writer for handling JavaScript code.
"""

import re
from typing import Optional, Dict, Any
from .base_writer import BaseWriter


class JsWriter(BaseWriter):
    """Writer for JavaScript content."""

    def can_handle(self, content_type: str) -> bool:
        """Check if this writer can handle the content type.

        Args:
            content_type: Type of content to check

        Returns:
            bool: True for JavaScript type
        """
        return content_type.lower() in ['js', 'javascript']

    def write(self, content: str, file_path: str,
              additional_params: Optional[Dict[str, Any]] = None) -> bool:
        """Write JavaScript content to file with proper formatting.

        Args:
            content: JavaScript content to write
            file_path: Path where to write the file
            additional_params: Additional parameters (unused for JS)

        Returns:
            bool: True if successful, False otherwise
        """
        cleaned_content = self._clean_content(content)
        formatted_content = self._format_js(cleaned_content)

        # Ensure proper file extension
        if not file_path.lower().endswith('.js'):
            file_path += '.js'

        return self._write_file(formatted_content, file_path)

    def _format_js(self, content: str) -> str:
        """Format JavaScript content with proper structure.

        Args:
            content: JavaScript content to format

        Returns:
            str: Formatted JavaScript content
        """
        # Remove JavaScript code block markers
        content = re.sub(r'^```(?:js|javascript)\s*', '', content)
        content = re.sub(r'\s*```$', '', content)

        # Remove script tags if present
        content = re.sub(r'<script[^>]*>(.*?)</script>', r'\\1',
                        content, flags=re.DOTALL | re.IGNORECASE)

        # Clean up common formatting issues
        content = self._clean_js_formatting(content)

        # Add use strict if not present
        if not re.search(r"'use strict'|\"use strict\"", content):
            content = "'use strict';\n\n" + content
            self.logger.info("Added 'use strict' directive")

        # Wrap in DOMContentLoaded if needed
        content = self._wrap_dom_ready_if_needed(content)

        return content

    def _clean_js_formatting(self, content: str) -> str:
        """Clean JavaScript formatting issues.

        Args:
            content: JavaScript content to clean

        Returns:
            str: Cleaned JavaScript content
        """
        # Ensure semicolons at the end of statements
        content = re.sub(r'(\\w+|\\)|\\]|\\})\\s*$', r'\\1;', content, flags=re.MULTILINE)

        # Fix missing semicolons before line breaks
        content = re.sub(r'(\\w+|\\)|\\]|\\})\\s*\\n', r'\\1;\\n', content)

        # Remove duplicate semicolons
        content = re.sub(r';\\s*;', r';', content)

        # Remove semicolons after blocks
        content = re.sub(r'\\}\\s*;', r'}', content)

        return content

    def _wrap_dom_ready_if_needed(self, content: str) -> str:
        """Wrap content in DOMContentLoaded if it interacts with DOM.

        Args:
            content: JavaScript content

        Returns:
            str: Potentially wrapped JavaScript content
        """
        # Check if content interacts with DOM
        has_dom_methods = re.search(
            r'document\\.getElementById|document\\.querySelector|document\\.getElement',
            content, re.IGNORECASE
        )
        has_dom_loaded = re.search(r'DOMContentLoaded', content, re.IGNORECASE)

        if has_dom_methods and not has_dom_loaded:
            # Check if already wrapped in a function or event listener
            if not re.search(r'^\\s*\\(\\s*function|window\\.onload|addEventListener', content.lstrip()):
                # Wrap in DOMContentLoaded
                indented_content = self._indent_code(content)
                content = (
                    "document.addEventListener('DOMContentLoaded', function() {\\n" +
                    indented_content +
                    "\\n});"
                )
                self.logger.info("Added DOMContentLoaded wrapper for DOM interactions")

        return content

    def _indent_code(self, code: str, spaces: int = 2) -> str:
        """Indent code by the specified number of spaces.

        Args:
            code: Code to indent
            spaces: Number of spaces for indentation

        Returns:
            str: Indented code
        """
        indent = ' ' * spaces
        return indent + code.replace('\\n', '\\n' + indent)
