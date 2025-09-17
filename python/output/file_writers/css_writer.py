"""
CSS writer for handling CSS stylesheets.
"""

import re
from typing import Optional, Dict, Any
from .base_writer import BaseWriter


class CssWriter(BaseWriter):
    """Writer for CSS content."""

    def can_handle(self, content_type: str) -> bool:
        """Check if this writer can handle the content type.

        Args:
            content_type: Type of content to check

        Returns:
            bool: True for CSS type
        """
        return content_type.lower() == 'css'

    def write(self, content: str, file_path: str,
              additional_params: Optional[Dict[str, Any]] = None) -> bool:
        """Write CSS content to file with proper formatting.

        Args:
            content: CSS content to write
            file_path: Path where to write the file
            additional_params: Additional parameters (unused for CSS)

        Returns:
            bool: True if successful, False otherwise
        """
        cleaned_content = self._clean_content(content)
        formatted_content = self._format_css(cleaned_content)

        # Ensure proper file extension
        if not file_path.lower().endswith('.css'):
            file_path += '.css'

        return self._write_file(formatted_content, file_path)

    def _format_css(self, content: str) -> str:
        """Format CSS content with proper structure.

        Args:
            content: CSS content to format

        Returns:
            str: Formatted CSS content
        """
        # Remove CSS code block markers
        content = re.sub(r'^```css\s*', '', content)
        content = re.sub(r'\s*```$', '', content)

        # Clean up content
        content = self._clean_css_content(content)

        # Add CSS header comment
        header = "/*\n * Generated CSS file\n */\n\n"

        return header + content.strip()

    def _clean_css_content(self, content: str) -> str:
        """Clean CSS content of common formatting issues.

        Args:
            content: CSS content to clean

        Returns:
            str: Cleaned CSS content
        """
        lines = content.split('\n')
        fixed_lines = []

        # CSS selectors that commonly follow 'n' when incorrectly processed
        css_selectors = [
            'html', 'body', 'div', 'span', 'a', 'p', 'ul', 'ol', 'li',
            'header', 'footer', 'nav', 'section', 'article', 'aside',
            'main', 'form', 'input', 'button', 'img', 'table', 'tr', 'td', 'th'
        ]

        for line in lines:
            stripped_line = line.strip()

            # Check for 'n' followed by space
            if stripped_line.startswith('n '):
                fixed_lines.append(line[line.find('n')+1:])
            # Check for 'n' followed by CSS selector
            elif stripped_line.startswith('n'):
                found_selector = False
                for selector in css_selectors:
                    if stripped_line.startswith('n' + selector) and (
                        len(stripped_line) == len('n' + selector) or
                        stripped_line[len('n' + selector)] in [' ', '{', '.', '#', ':', '[']
                    ):
                        # It's likely a CSS selector - remove the 'n'
                        fixed_lines.append(line[line.find('n')+1:])
                        found_selector = True
                        break

                if not found_selector:
                    # No CSS selector match, keep the line as is
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

        return '\n'.join(fixed_lines)
