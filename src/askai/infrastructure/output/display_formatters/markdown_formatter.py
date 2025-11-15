"""
Markdown formatter for formatting content for markdown output.
"""

import re

from .base_display_formatter import BaseDisplayFormatter


class MarkdownFormatter(BaseDisplayFormatter):
    """Formatter for markdown output with proper syntax."""

    def format(self, content: str, content_type: str = 'text',
              include_language_tag: bool = True, **kwargs) -> str:
        """Format content for markdown output.

        Args:
            content: Content to format
            content_type: Type of content ('text', 'code', 'json', etc.)
            include_language_tag: Whether to include language tag in code blocks
            kwargs: Additional formatting options

        Returns:
            str: Formatted markdown content
        """
        if not content:
            return ""

        # Apply specific formatting based on content type
        if content_type.lower() in ('code', 'json', 'html', 'css', 'js', 'python'):
            # Format as code block with appropriate language tag
            lang_tag = content_type.lower() if include_language_tag else ''
            formatted = self._format_as_code_block(content, lang_tag)
        elif content_type.lower() == 'markdown':
            # Already markdown, just ensure proper formatting
            formatted = self._ensure_valid_markdown(content)
        else:
            # Default text formatting as regular text
            formatted = content

        # Apply any custom formatters from kwargs
        for key, value in kwargs.items():
            if key.startswith('format_') and callable(value):
                formatted = value(formatted)

        return str(formatted)

    def _format_as_code_block(self, code: str, language_tag: str = '') -> str:
        """Format content as markdown code block.

        Args:
            code: Code content
            language_tag: Language identifier for syntax highlighting

        Returns:
            str: Formatted code block
        """
        # Remove existing code block markers if present
        code = re.sub(r'^```.*?\n|```$', '', code, flags=re.MULTILINE)

        # Ensure code doesn't end with blank lines (which would break the code block)
        code = code.rstrip() + '\n'

        # Format as code block with language tag if provided
        return f'```{language_tag}\n{code}```'

    def _ensure_valid_markdown(self, markdown: str) -> str:
        """Ensure markdown is properly formatted.

        Args:
            markdown: Markdown content to validate

        Returns:
            str: Valid markdown content
        """
        # Fix incomplete or broken code blocks
        # Count opening and closing code block markers
        open_markers = len(re.findall(r'```\w*\n', markdown))
        close_markers = len(re.findall(r'\n```', markdown))

        # If they don't match, fix it
        if open_markers > close_markers:
            markdown = markdown + '\n```'
            if self.logger:
                self.logger.info("Added missing closing code block marker")

        # Ensure headers have space after #
        markdown = re.sub(r'^(#+)([^ #])', r'\1 \2', markdown, flags=re.MULTILINE)

        # Ensure blank line before headers
        markdown = re.sub(r'([^\n])\n(#+\s+)', r'\1\n\n\2', markdown)

        # Fix lists to have proper spacing
        markdown = re.sub(r'^([*+-])\s*([^ ])', r'\1 \2', markdown, flags=re.MULTILINE)

        return markdown
