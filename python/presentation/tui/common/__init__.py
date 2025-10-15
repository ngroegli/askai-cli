"""
Common package for shared TUI utilities and imports.
"""

# Import from textual_imports module
from .textual_imports import (
    TEXTUAL_AVAILABLE, TEXTUAL_EXTENDED_AVAILABLE, TEXTUAL_SCREEN_AVAILABLE,
    Static, Button, ListView, ListItem, Label,
    TextArea, Input, Select, ProgressBar,
    Vertical, Horizontal, VerticalScroll,
    Message, ModalScreen, work
)

# Import from utils module
from .utils import (
    update_status_safe, get_widget_safe, StatusMixin
)

# Import from styles module
from .styles import (
    BUTTON_STYLES, PANEL_STYLES, INPUT_STYLES,
    MODAL_STYLES, STATUS_STYLES, COMMON_STYLES
)

__all__ = [
    # Textual imports
    'TEXTUAL_AVAILABLE', 'TEXTUAL_EXTENDED_AVAILABLE', 'TEXTUAL_SCREEN_AVAILABLE',
    'Static', 'Button', 'ListView', 'ListItem', 'Label',
    'TextArea', 'Input', 'Select', 'ProgressBar',
    'Vertical', 'Horizontal', 'VerticalScroll',
    'Message', 'ModalScreen', 'work',
    # Utilities
    'update_status_safe', 'get_widget_safe', 'StatusMixin',
    # Styles
    'BUTTON_STYLES', 'PANEL_STYLES', 'INPUT_STYLES',
    'MODAL_STYLES', 'STATUS_STYLES', 'COMMON_STYLES'
]
