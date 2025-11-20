"""
Centralized styling system for the TUI application.
"""
from .theme import Theme, DEFAULT_THEME
from .components import ComponentStyles
from .base_styles import BaseStyles

# Define DARK_THEME and BASE_STYLES as empty dicts
# These can be populated by importing modules if needed
DARK_THEME = {}
BASE_STYLES = {}

# Only import styled components if they're available
try:
    from .styled_components import *
    STYLED_COMPONENTS_AVAILABLE = True
except (ImportError, AttributeError):
    STYLED_COMPONENTS_AVAILABLE = False

__all__ = [
    'Theme', 'DEFAULT_THEME', 'ComponentStyles', 'BaseStyles',
    'STYLED_COMPONENTS_AVAILABLE', 'DARK_THEME', 'BASE_STYLES'
]
