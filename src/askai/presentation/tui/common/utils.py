"""
Common utility functions for TUI components.
"""

from .textual_imports import Static


def update_status_safe(component, status_id: str, message: str) -> None:
    """
    Safely update a status display widget.

    Args:
        component: The component containing the status widget
        status_id: The ID of the status widget (e.g., "#status-display")
        message: The message to display
    """
    try:
        status_display = component.query_one(status_id, Static)
        status_display.update(message)
    except Exception:
        pass  # Widget not available yet


def get_widget_safe(component, widget_id: str, widget_type):
    """
    Safely get a widget by ID.

    Args:
        component: The component containing the widget
        widget_id: The ID of the widget
        widget_type: The expected widget type

    Returns:
        The widget if found, None otherwise
    """
    try:
        return component.query_one(widget_id, widget_type)
    except Exception:
        return None


class StatusMixin:
    """
    Mixin class to provide common status update functionality.
    """

    def update_status(self, message: str) -> None:
        """Update the status display."""
        update_status_safe(self, "#status-display", message)


__all__ = ['update_status_safe', 'get_widget_safe', 'StatusMixin']
