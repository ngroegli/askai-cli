"""Utility functions for TUI components."""

import os
import sys
from typing import Dict, Any, Optional

try:
    import textual
    TEXTUAL_AVAILABLE = True
except ImportError:
    textual = None
    TEXTUAL_AVAILABLE = False


def get_terminal_size() -> tuple[int, int]:
    """Get terminal dimensions (width, height)."""
    try:
        size = os.get_terminal_size()
        return size.columns, size.lines
    except OSError:
        return 80, 24  # Default fallback


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to fit within specified length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    size = float(size_bytes)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def get_theme_colors() -> Dict[str, str]:
    """Get color scheme based on environment and preferences."""
    theme = os.environ.get('ASKAI_TUI_THEME', 'dark').lower()

    if theme == 'light':
        return {
            'primary': '#0066cc',
            'secondary': '#666666',
            'success': '#28a745',
            'warning': '#ffc107',
            'error': '#dc3545',
            'background': '#ffffff',
            'surface': '#f8f9fa',
            'text': '#212529',
        }
    else:  # dark theme (default)
        return {
            'primary': '#3b82f6',
            'secondary': '#6b7280',
            'success': '#10b981',
            'warning': '#f59e0b',
            'error': '#ef4444',
            'background': '#1f2937',
            'surface': '#374151',
            'text': '#f9fafb',
        }


def is_pattern_file(filename: str) -> bool:
    """Check if filename appears to be a pattern file."""
    return filename.endswith('.md') and not filename.startswith('_')


def is_chat_file(filename: str) -> bool:
    """Check if filename appears to be a chat file."""
    return filename.endswith('.json')


def safe_import_textual() -> Optional[Any]:
    """Safely import textual with error handling."""
    return textual if TEXTUAL_AVAILABLE else None


__all__ = [
    'get_terminal_size',
    'truncate_text',
    'format_file_size',
    'get_theme_colors',
    'is_pattern_file',
    'is_chat_file',
    'safe_import_textual'
]
