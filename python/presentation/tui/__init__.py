"""
TUI (Terminal User Interface) components for AskAI using Textual framework.

This module provides modern, interactive terminal interfaces for pattern management,
chat browsing, and other AskAI features. It gracefully falls back to the traditional
CLI interface when Textual is unavailable or the terminal is incompatible.
"""

import os
import sys

try:
    import textual
    TEXTUAL_AVAILABLE = True
    # Store reference to avoid unused import warning
    _TEXTUAL_MODULE = textual
except ImportError:
    TEXTUAL_AVAILABLE = False
    _TEXTUAL_MODULE = None


def is_tui_available() -> bool:
    """Check if TUI can be used in the current environment."""
    if not TEXTUAL_AVAILABLE:
        return False

    # Check if we're in a terminal
    if not os.isatty(sys.stdout.fileno()):
        return False

    # Check environment variable override
    if os.environ.get('ASKAI_NO_TUI', '').lower() in ['1', 'true']:
        return False

    # Check terminal capabilities
    term = os.environ.get('TERM', '')
    if term in ['dumb', '']:
        return False

    return True


def get_tui_config() -> dict:
    """Get TUI configuration settings."""
    return {
        'theme': os.environ.get('ASKAI_TUI_THEME', 'dark'),
        'keybindings': {
            'search': ['ctrl+f', '/'],
            'quit': ['ctrl+q', 'q'],
            'select': ['enter'],
            'back': ['escape'],
        },
        'features': {
            'live_preview': True,
            'fuzzy_search': True,
            'syntax_highlighting': True,
        }
    }


__all__ = ['is_tui_available', 'get_tui_config']
