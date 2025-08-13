"""
Console formatter for formatting content for terminal output.
"""

import re
import os
from typing import Optional
import logging
import io
from rich.console import Console
from rich.markdown import Markdown

from .base_formatter import BaseFormatter


class ConsoleFormatter(BaseFormatter):
    """Formatter for terminal/console output with colors and formatting."""

    # ANSI color codes
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'dim': '\033[2m',
        'italic': '\033[3m',
        'underline': '\033[4m',
        'black': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'bg_black': '\033[40m',
        'bg_red': '\033[41m',
        'bg_green': '\033[42m',
        'bg_yellow': '\033[43m',
        'bg_blue': '\033[44m',
        'bg_magenta': '\033[45m',
        'bg_cyan': '\033[46m',
        'bg_white': '\033[47m'
    }

    def __init__(self, use_colors: bool = True, logger: Optional[logging.Logger] = None):
        """Initialize console formatter with color options.

        Args:
            use_colors: Whether to use ANSI color codes in output
            logger: Optional logger for logging messages
        """
        super().__init__(logger)
        self.use_colors = use_colors and self._supports_colors()

    def format(self, content: str, content_type: str = 'text',
              highlight_code: bool = True, **kwargs) -> str:
        """Format content for console output with optional syntax highlighting.

        Args:
            content: Content to format
            content_type: Type of content ('text', 'code', 'json', etc.)
            highlight_code: Whether to highlight code syntax
            kwargs: Additional formatting options

        Returns:
            str: Formatted content for console output
        """
        if not content:
            return ""

        # Apply specific formatting based on content type
        if content_type.lower() in ('code', 'json', 'html', 'css', 'js'):
            formatted = self._format_code(content, content_type.lower(), highlight_code)
        elif content_type.lower() == 'markdown':
            formatted = self._format_markdown(content)
        else:
            # Default text formatting
            formatted = content

        # Apply any custom formatters from kwargs
        for key, value in kwargs.items():
            if key.startswith('format_') and callable(value):
                formatted = value(formatted)

        return str(formatted)

    def _format_code(self, code: str, language: str, highlight: bool = True) -> str:
        """Format code with syntax highlighting if supported.

        Args:
            code: Code content to format
            language: Programming language for highlighting
            highlight: Whether to apply syntax highlighting

        Returns:
            str: Formatted code
        """
        if not highlight or not self.use_colors:
            # Simple code formatting without highlighting
            return self._add_code_frame(code)

        # Basic syntax highlighting using regex patterns
        if language == 'json':
            return self._highlight_json(code)
        elif language in ('js', 'javascript'):
            return self._highlight_js(code)
        elif language == 'html':
            return self._highlight_html(code)
        elif language == 'css':
            return self._highlight_css(code)
        else:
            # Generic code highlighting
            return self._highlight_generic_code(code)

    def _add_code_frame(self, code: str) -> str:
        """Add a frame around code blocks.

        Args:
            code: Code content

        Returns:
            str: Code with frame
        """
        width = min(80, max(len(line) for line in code.split('\n')) + 4)
        horizontal_line = '─' * width if self.use_colors else '-' * width

        if self.use_colors:
            frame_color = self.COLORS['dim'] + self.COLORS['blue']
            reset = self.COLORS['reset']

            framed_code = f"{frame_color}┌{horizontal_line}┐{reset}\n"
            for line in code.split('\n'):
                framed_code += f"{frame_color}│{reset} {line}{' ' * (width - len(line) - 3)}{frame_color}│{reset}\n"
            framed_code += f"{frame_color}└{horizontal_line}┘{reset}"
        else:
            framed_code = f"+{horizontal_line}+\n"
            for line in code.split('\n'):
                framed_code += f"| {line}{' ' * (width - len(line) - 3)}|\n"
            framed_code += f"+{horizontal_line}+"

        return framed_code

    def _format_markdown(self, markdown: str) -> str:
        """Format markdown content for console display using rich.

        Args:
            markdown: Markdown content

        Returns:
            str: Console-formatted markdown
        """
        if not markdown:
            return ""

        if not self.use_colors:
            return markdown

        try:
            # Use rich's Markdown renderer
            string_io = io.StringIO()
            console = Console(file=string_io, highlight=True, width=120)
            md = Markdown(markdown)
            console.print(md)
            return string_io.getvalue()
        except Exception as e:
            if self.logger:
                self.logger.warning("Error formatting markdown with rich: %s", str(e))

            # Fallback to basic formatting
            formatted = markdown

            # Format headings
            formatted = re.sub(
                r'^(#{1,6})\s+(.+?)$',
                lambda m: f"{self.COLORS['bold']}{self.COLORS['cyan']}{m.group(1)} {m.group(2)}{self.COLORS['reset']}",
                formatted,
                flags=re.MULTILINE
            )

            # Format bold text
            formatted = re.sub(
                r'\*\*(.+?)\*\*',
                lambda m: f"{self.COLORS['bold']}{m.group(1)}{self.COLORS['reset']}",
                formatted
            )

            # Format italic text
            formatted = re.sub(
                r'\*(.+?)\*',
                lambda m: f"{self.COLORS['italic']}{m.group(1)}{self.COLORS['reset']}",
                formatted
            )

            # Format code blocks
            formatted = re.sub(
                r'```(\w*)\n(.*?)\n```',
                lambda m: f"{self.COLORS['bg_black']}{self.COLORS['green']}{m.group(2)}{self.COLORS['reset']}",
                formatted,
                flags=re.DOTALL
            )

            # Format inline code
            formatted = re.sub(
                r'`(.+?)`',
                lambda m: f"{self.COLORS['green']}`{m.group(1)}`{self.COLORS['reset']}",
                formatted
            )

            # Format links
            formatted = re.sub(
                r'\[(.+?)\]\((.+?)\)',
                lambda m: f"{self.COLORS['underline']}{self.COLORS['blue']}[{m.group(1)}]"
                          f"({m.group(2)}){self.COLORS['reset']}",
                formatted
            )

            return formatted

    def _highlight_json(self, code: str) -> str:
        """Highlight JSON syntax.

        Args:
            code: JSON content

        Returns:
            str: Highlighted JSON
        """
        if not self.use_colors:
            return self._add_code_frame(code)

        # Highlight key-value pairs
        highlighted = re.sub(
            r'(".*?")(\s*:\s*)(".*?"|\d+\.\d+|\d+|true|false|null)',
            lambda m: f"{self.COLORS['yellow']}{m.group(1)}{self.COLORS['reset']}{m.group(2)}"
                      f"{self._highlight_json_value(m.group(3))}",
            code
        )

        # Highlight structural elements
        highlighted = re.sub(r'(\{|\}|\[|\]|,)', f"{self.COLORS['white']}\\1{self.COLORS['reset']}", highlighted)

        return self._add_code_frame(highlighted)

    def _highlight_json_value(self, value: str) -> str:
        """Helper for JSON value highlighting.

        Args:
            value: JSON value to highlight

        Returns:
            str: Highlighted value
        """
        if value in ('true', 'false', 'null'):
            return f"{self.COLORS['magenta']}{value}{self.COLORS['reset']}"
        elif value.startswith('"'):
            return f"{self.COLORS['green']}{value}{self.COLORS['reset']}"
        else:  # numbers
            return f"{self.COLORS['cyan']}{value}{self.COLORS['reset']}"

    def _highlight_js(self, code: str) -> str:
        """Highlight JavaScript syntax.

        Args:
            code: JavaScript content

        Returns:
            str: Highlighted JavaScript
        """
        if not self.use_colors:
            return self._add_code_frame(code)

        # Keywords
        keywords = (
            r'\b(var|let|const|function|return|if|else|for|while|do|switch|case|'
            r'break|continue|try|catch|finally|throw|new|this|class|extends|'
            r'import|export|async|await|from|of|in)\b'
        )
        highlighted = re.sub(
            keywords,
            f"{self.COLORS['blue']}\\1{self.COLORS['reset']}",
            code
        )

        # Strings
        highlighted = re.sub(
            r'(".*?"|\'.*?\'|`.*?`)',
            f"{self.COLORS['green']}\\1{self.COLORS['reset']}",
            highlighted,
            flags=re.DOTALL
        )

        # Comments
        highlighted = re.sub(
            r'(//.*?$|/\*.*?\*/)',
            f"{self.COLORS['dim']}{self.COLORS['green']}\\1{self.COLORS['reset']}",
            highlighted,
            flags=re.MULTILINE | re.DOTALL
        )

        # Numbers
        highlighted = re.sub(
            r'\b(\d+\.?\d*)\b',
            f"{self.COLORS['cyan']}\\1{self.COLORS['reset']}",
            highlighted
        )

        # Boolean and null
        highlighted = re.sub(
            r'\b(true|false|null|undefined)\b',
            f"{self.COLORS['magenta']}\\1{self.COLORS['reset']}",
            highlighted
        )

        return self._add_code_frame(highlighted)

    def _highlight_html(self, code: str) -> str:
        """Highlight HTML syntax.

        Args:
            code: HTML content

        Returns:
            str: Highlighted HTML
        """
        if not self.use_colors:
            return self._add_code_frame(code)

        # Tags
        highlighted = re.sub(
            r'(</?[a-zA-Z0-9]+)(\s+[^>]*>|>)',
            f"{self.COLORS['magenta']}\\1{self.COLORS['reset']}\\2",
            code
        )

        # Attributes
        highlighted = re.sub(
            r'(\s+)([a-zA-Z0-9_-]+)(="[^"]*")',
            f"\\1{self.COLORS['yellow']}\\2{self.COLORS['reset']}{self.COLORS['green']}\\3{self.COLORS['reset']}",
            highlighted
        )

        # Comments
        highlighted = re.sub(
            r'(<!--.*?-->)',
            f"{self.COLORS['dim']}{self.COLORS['green']}\\1{self.COLORS['reset']}",
            highlighted,
            flags=re.DOTALL
        )

        # Brackets and symbols
        highlighted = re.sub(
            r'(<|>|=|/)',
            f"{self.COLORS['blue']}\\1{self.COLORS['reset']}",
            highlighted
        )

        return self._add_code_frame(highlighted)

    def _highlight_css(self, code: str) -> str:
        """Highlight CSS syntax.

        Args:
            code: CSS content

        Returns:
            str: Highlighted CSS
        """
        if not self.use_colors:
            return self._add_code_frame(code)

        # Selectors
        highlighted = re.sub(
            r'([a-zA-Z0-9\-_. #:]+)(\s*\{)',
            f"{self.COLORS['yellow']}\\1{self.COLORS['reset']}\\2",
            code
        )

        # Properties
        highlighted = re.sub(
            r'(\s+)([a-zA-Z0-9\-]+)(\s*:)',
            f"\\1{self.COLORS['blue']}\\2{self.COLORS['reset']}\\3",
            highlighted
        )

        # Values
        highlighted = re.sub(
            r'(:)(\s*)(.*?)(;|$)',
            f"\\1\\2{self.COLORS['green']}\\3{self.COLORS['reset']}\\4",
            highlighted
        )

        # Comments
        highlighted = re.sub(
            r'(/\*.*?\*/)',
            f"{self.COLORS['dim']}{self.COLORS['green']}\\1{self.COLORS['reset']}",
            highlighted,
            flags=re.DOTALL
        )

        # Brackets and symbols
        highlighted = re.sub(
            r'(\{|\}|;)',
            f"{self.COLORS['magenta']}\\1{self.COLORS['reset']}",
            highlighted
        )

        return self._add_code_frame(highlighted)

    def _highlight_generic_code(self, code: str) -> str:
        """Basic generic code highlighting.

        Args:
            code: Code content

        Returns:
            str: Highlighted code
        """
        if not self.use_colors:
            return self._add_code_frame(code)

        # Simple highlighting for any code type

        # Comments (C-style, Python, and shell)
        highlighted = re.sub(
            r'(//.*?$|#.*?$|/\*.*?\*/)',
            f"{self.COLORS['dim']}{self.COLORS['green']}\\1{self.COLORS['reset']}",
            code,
            flags=re.MULTILINE | re.DOTALL
        )

        # Strings
        highlighted = re.sub(
            r'(".*?"|\'.*?\'|`.*?`)',
            f"{self.COLORS['green']}\\1{self.COLORS['reset']}",
            highlighted,
            flags=re.DOTALL
        )

        # Numbers
        highlighted = re.sub(
            r'\b(\d+\.?\d*)\b',
            f"{self.COLORS['cyan']}\\1{self.COLORS['reset']}",
            highlighted
        )

        # Common keywords across many languages
        keywords = (
            r'\b(function|def|class|if|else|elif|for|while|return|import|'
            r'from|as|try|except|finally|raise|with|const|let|var)\b'
        )
        highlighted = re.sub(
            keywords,
            f"{self.COLORS['blue']}\\1{self.COLORS['reset']}",
            highlighted
        )

        # Boolean and null values across languages
        highlighted = re.sub(
            r'\b(true|false|null|None|TRUE|FALSE|nil|undefined)\b',
            f"{self.COLORS['magenta']}\\1{self.COLORS['reset']}",
            highlighted
        )

        return self._add_code_frame(highlighted)

    def _supports_colors(self) -> bool:
        """Determine if the terminal supports colors.

        Returns:
            bool: True if colors are supported
        """
        # Check if NO_COLOR environment variable is set
        if os.environ.get('NO_COLOR') is not None:
            return False

        # Check if TERM is set to "dumb"
        if os.environ.get('TERM') == 'dumb':
            return False

        # Check for common CI environments that support colors
        if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
            return True

        # Check for TTY
        try:
            return os.isatty(1)  # 1 is stdout
        except (AttributeError, ValueError):
            return False
