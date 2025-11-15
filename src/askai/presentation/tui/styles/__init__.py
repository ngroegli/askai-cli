"""
Centralized styling system for the TUI application.
"""

from .theme import Theme, DEFAULT_THEME
from .components import ComponentStyles
from .base_styles import BaseStyles

# Only import styled components if they're available
try:
    from .styled_components import *
    STYLED_COMPONENTS_AVAILABLE = True
except (ImportError, AttributeError):
    STYLED_COMPONENTS_AVAILABLE = False

__all__ = ['Theme', 'DEFAULT_THEME', 'ComponentStyles', 'BaseStyles', 'STYLED_COMPONENTS_AVAILABLE']
