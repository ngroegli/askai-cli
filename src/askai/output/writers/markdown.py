"""
Markdown writer for handling Markdown content.
"""

import re
from typing import Optional, Dict, Any
from .base import BaseWriter


class MarkdownWriter(BaseWriter):
    """Writer for Markdown content."""

    def can_handle(self, content_type: str) -> bool:
        """Check if this writer can handle the content type.

        Args:
            content_type: Type of content to check

        Returns:
            bool: True for Markdown type
        """
        return content_type.lower() in ['markdown', 'md']

    def write(self, content: str, file_path: str,
              additional_params: Optional[Dict[str, Any]] = None) -> bool:
        """Write Markdown content to file with proper formatting.

        Args:
            content: Markdown content to write
            file_path: Path where to write the file
            additional_params: Additional parameters (unused for Markdown)

        Returns:
            bool: True if successful, False otherwise
        """
        cleaned_content = self._clean_content(content)
        formatted_content = self._format_markdown(cleaned_content)

        # Ensure proper file extension
        if not file_path.lower().endswith(('.md', '.markdown')):
            file_path += '.md'

        return self._write_file(formatted_content, file_path)

    def _format_markdown(self, content: str) -> str:
        """Format Markdown content with proper structure.

        Args:
            content: Markdown content to format

        Returns:
            str: Formatted Markdown content
        """
        # Remove markdown code block markers (for when markdown is in a code block)
        content = re.sub(r'^```(?:md|markdown)\\s*', '', content)
        content = re.sub(r'\\s*```$', '', content)

        # Fix heading spacing
        content = self._fix_heading_spacing(content)

        # Fix list formatting
        content = self._fix_list_formatting(content)

        # Fix code block formatting
        content = self._fix_code_block_formatting(content)

        # Fix link formatting
        content = self._fix_link_formatting(content)

        # Ensure proper line ending
        if not content.endswith('\\n'):
            content += '\\n'

        return content

    def _fix_heading_spacing(self, content: str) -> str:
        """Fix spacing around headings.

        Args:
            content: Markdown content

        Returns:
            str: Content with fixed heading spacing
        """
        # Ensure space after hash marks
        content = re.sub(r'^(#{1,6})([^\\s#])', r'\\1 \\2', content, flags=re.MULTILINE)

        # Ensure blank line before headings (except at start)
        content = re.sub(r'(?<!^)(?<!\\n\\n)(\\n)(#{1,6}\\s)', r'\\n\\n\\2', content)

        # Ensure blank line after headings
        content = re.sub(r'(#{1,6}\\s.*?)\\n(?!\\n)', r'\\1\\n\\n', content)

        return content

    def _fix_list_formatting(self, content: str) -> str:
        """Fix list formatting issues.

        Args:
            content: Markdown content

        Returns:
            str: Content with fixed list formatting
        """
        # Fix bullet list markers
        content = re.sub(r'^\\s*[*+-]\\s*', '- ', content, flags=re.MULTILINE)

        # Fix numbered list formatting
        content = re.sub(r'^\\s*(\\d+)\\.\\s*', r'\\1. ', content, flags=re.MULTILINE)

        # Ensure proper indentation for nested lists
        lines = content.split('\\n')
        for i, line in enumerate(lines):
            if re.match(r'^\\s*[*+-]\\s+', line):
                # Count indentation level
                indent = len(line) - len(line.lstrip())
                proper_indent = (indent // 2) * 2  # Round to even number
                lines[i] = ' ' * proper_indent + '- ' + line.lstrip()[2:]

        return '\\n'.join(lines)

    def _fix_code_block_formatting(self, content: str) -> str:
        """Fix code block formatting.

        Args:
            content: Markdown content

        Returns:
            str: Content with fixed code blocks
        """
        # Ensure proper fenced code block formatting
        content = re.sub(r'^\\s*```(\\w*)\\s*$', r'```\\1', content, flags=re.MULTILINE)

        # Fix inline code formatting
        content = re.sub(r'`([^`]+)`', r'`\\1`', content)

        return content

    def _fix_link_formatting(self, content: str) -> str:
        """Fix link formatting issues.

        Args:
            content: Markdown content

        Returns:
            str: Content with fixed links
        """
        # Fix reference-style links
        content = re.sub(r'\\[([^\\]]+)\\]\\s*\\(([^)]+)\\)', r'[\\1](\\2)', content)

        # Fix image links
        content = re.sub(r'!\\[([^\\]]*)\\]\\s*\\(([^)]+)\\)', r'![\\1](\\2)', content)

        # Ensure proper email links
        content = re.sub(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,})', r'<\\1>', content)

        return content
