"""
Consolidated styles for AskAI TUI application.
"""

from rich.style import Style
from textual.widgets import Static, Button, Input

# Core color scheme
PRIMARY = "#0066cc"
SECONDARY = "#00aa66"
ACCENT = "#ff6600"
WARNING = "#ffaa00"
ERROR = "#cc0000"
SUCCESS = "#00aa00"

# Base styles
BASE_STYLES = {
    'primary': Style(color=PRIMARY),
    'secondary': Style(color=SECONDARY),
    'accent': Style(color=ACCENT),
    'warning': Style(color=WARNING),
    'error': Style(color=ERROR),
    'success': Style(color=SUCCESS),
}

# Themes
DARK_THEME = {
    "background": "#1e1e1e",
    "primary": PRIMARY,
    "text": "#ffffff",
    "success": SUCCESS,
    "warning": WARNING,
    "error": ERROR
}


# Styled components
class StyledStatic(Static):
    """Styled Static widget with AskAI theme."""

    def __init__(self, content="", **kwargs):
        super().__init__(content, **kwargs)


class StyledButton(Button):
    """Styled Button widget with AskAI theme."""

    def __init__(self, label="", **kwargs):
        super().__init__(label, **kwargs)


class StyledInput(Input):
    """Styled Input widget with AskAI theme."""

    def __init__(self, placeholder="", **kwargs):
        super().__init__(placeholder=placeholder, **kwargs)

__all__ = ['StyledStatic', 'StyledButton', 'StyledInput', 'DARK_THEME', 'BASE_STYLES']
