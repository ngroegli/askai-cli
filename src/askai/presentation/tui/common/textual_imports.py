"""
Common textual imports and availability checking for TUI components.
This module centralizes the import logic to reduce code duplication.
"""

from typing import TYPE_CHECKING

# Base textual imports that most components need
try:
    from textual.widgets import Static, Button, ListView, ListItem, Label
    from textual.containers import Vertical, Horizontal
    from textual.message import Message
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    if not TYPE_CHECKING:
        Static = object
        Button = object
        ListView = object
        ListItem = object
        Label = object
        Vertical = object
        Horizontal = object
        Message = object

# Extended imports for more complex components
try:
    from textual.widgets import TextArea, Input, Select, ProgressBar
    from textual.containers import VerticalScroll
    TEXTUAL_EXTENDED_AVAILABLE = True
except ImportError:
    TEXTUAL_EXTENDED_AVAILABLE = False
    if not TYPE_CHECKING:
        TextArea = object
        Input = object
        Select = object
        ProgressBar = object
        VerticalScroll = object

# Screen-related imports
try:
    from textual.screen import ModalScreen
    from textual import work
    TEXTUAL_SCREEN_AVAILABLE = True
except ImportError:
    TEXTUAL_SCREEN_AVAILABLE = False
    if not TYPE_CHECKING:
        ModalScreen = object

        def work(f):
            """Simple passthrough decorator."""
            return f

if TYPE_CHECKING:
    from textual.widgets import (
        Static, Button, ListView, ListItem, Label,
        TextArea, Input, Select, ProgressBar
    )
    from textual.containers import Vertical, Horizontal, VerticalScroll
    from textual.message import Message
    from textual.screen import ModalScreen

__all__ = [
    'TEXTUAL_AVAILABLE', 'TEXTUAL_EXTENDED_AVAILABLE', 'TEXTUAL_SCREEN_AVAILABLE',
    'Static', 'Button', 'ListView', 'ListItem', 'Label',
    'TextArea', 'Input', 'Select', 'ProgressBar',
    'Vertical', 'Horizontal', 'VerticalScroll',
    'Message', 'ModalScreen', 'work'
]
