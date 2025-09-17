"""
HTML writer for handling HTML content.
"""

import re
from typing import Optional, Dict, Any
from .base_writer import BaseWriter


class HtmlWriter(BaseWriter):
    """Writer for HTML content."""

    def can_handle(self, content_type: str) -> bool:
        """Check if this writer can handle the content type.

        Args:
            content_type: Type of content to check

        Returns:
            bool: True for HTML type
        """
        return content_type.lower() in ['html', 'htm']

    def write(self, content: str, file_path: str,
              additional_params: Optional[Dict[str, Any]] = None) -> bool:
        """Write HTML content to file with proper structure and references.

        Args:
            content: HTML content to write
            file_path: Path where to write the file
            additional_params: Additional parameters (css_path, js_path)

        Returns:
            bool: True if successful, False otherwise
        """
        additional_params = additional_params or {}

        cleaned_content = self._clean_content(content)
        formatted_content = self._format_html(cleaned_content, additional_params)

        # Ensure proper file extension
        if not file_path.lower().endswith(('.html', '.htm')):
            file_path += '.html'

        return self._write_file(formatted_content, file_path)

    def _format_html(self, content: str, params: Dict[str, Any]) -> str:
        """Format HTML content with proper structure and references.

        Args:
            content: HTML content to format
            params: Additional parameters (css_path, js_path)

        Returns:
            str: Formatted HTML content
        """
        # Remove HTML code block markers
        content = re.sub(r'^```html\s*', '', content)
        content = re.sub(r'\s*```$', '', content)

        # Ensure proper HTML document structure
        if not re.search(r'<html[^>]*>', content, re.IGNORECASE):
            content = self._wrap_in_html_structure(content)

        # Add CSS reference if provided
        css_path = params.get('css_path')
        if css_path:
            content = self._add_css_reference(content, css_path)

        # Add JS reference if provided
        js_path = params.get('js_path')
        if js_path:
            content = self._add_js_reference(content, js_path)

        # Format indentation
        content = self._format_html_indentation(content)

        return content

    def _wrap_in_html_structure(self, content: str) -> str:
        """Wrap content in proper HTML document structure.

        Args:
            content: Content to wrap

        Returns:
            str: Content wrapped in HTML structure
        """
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated Page</title>
</head>
<body>
{content}
</body>
</html>'''

    def _add_css_reference(self, content: str, css_path: str) -> str:
        """Add CSS reference to HTML content.

        Args:
            content: HTML content
            css_path: Path to CSS file

        Returns:
            str: HTML content with CSS reference
        """
        css_filename = css_path.split('/')[-1]
        css_link = f'    <link rel="stylesheet" href="{css_filename}">'

        # Find head section and insert CSS link
        head_end = content.find('</head>')
        if head_end != -1:
            return content[:head_end] + css_link + '\n' + content[head_end:]

        # Fallback: add to beginning if no head section
        return css_link + '\n' + content

    def _add_js_reference(self, content: str, js_path: str) -> str:
        """Add JavaScript reference to HTML content.

        Args:
            content: HTML content
            js_path: Path to JavaScript file

        Returns:
            str: HTML content with JavaScript reference
        """
        js_filename = js_path.split('/')[-1]
        script_tag = f'    <script src="{js_filename}" defer></script>'

        # Find head section and insert script tag
        head_end = content.find('</head>')
        if head_end != -1:
            return content[:head_end] + script_tag + '\n' + content[head_end:]

        # Fallback: add before closing body
        body_end = content.rfind('</body>')
        if body_end != -1:
            return content[:body_end] + script_tag + '\n' + content[body_end:]

        # Last resort: add at end
        return content + '\n' + script_tag

    def _format_html_indentation(self, content: str) -> str:
        """Format HTML content with proper indentation.

        Args:
            content: HTML content to format

        Returns:
            str: Formatted HTML content
        """
        try:
            lines = content.split('\n')
            indented_lines = []
            indent_level = 0

            block_tags = ['html', 'head', 'body', 'div', 'header', 'main', 'footer',
                         'section', 'article', 'nav', 'aside', 'form']

            for line in lines:
                stripped = line.strip()
                if not stripped:
                    indented_lines.append('')
                    continue

                # Check for closing tags
                closing_match = re.match(r'^\s*</([a-zA-Z]+)[^>]*>', stripped)
                if closing_match and closing_match.group(1).lower() in block_tags:
                    indent_level = max(0, indent_level - 1)

                # Add the line with proper indentation
                indented_lines.append('  ' * indent_level + stripped)

                # Check for opening tags
                opening_match = re.match(r'^\s*<([a-zA-Z]+)[^>]*>(?!</)', stripped)
                if opening_match:
                    tag = opening_match.group(1).lower()
                    if tag in block_tags and not stripped.endswith('/>'):
                        indent_level += 1

            return '\n'.join(indented_lines)
        except Exception as e:
            self.logger.debug(f"HTML indentation failed: {str(e)}")
            return content
