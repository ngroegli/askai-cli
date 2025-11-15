"""
Reusable UI components with built-in styling.
"""

from typing import TYPE_CHECKING

try:
    from textual.widgets import Button as TextualButton, Input as TextualInput, TextArea as TextualTextArea
    from textual.widgets import Static, ListView, Select
    from textual.containers import Vertical, Horizontal
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    if not TYPE_CHECKING:
        TextualButton = object
        TextualInput = object
        TextualTextArea = object
        Static = object
        ListView = object
        Select = object
        Vertical = object
        Horizontal = object

# Type imports for static analysis
if TYPE_CHECKING:
    from textual.widgets import Button as TextualButton, Input as TextualInput, TextArea as TextualTextArea
    from textual.widgets import Static, ListView, Select
    from textual.containers import Vertical, Horizontal


if TEXTUAL_AVAILABLE:

    class StyledButton(TextualButton):
        """Button with predefined styling classes."""

        def __init__(self, label: str, variant: str = "default", icon: str = "", **kwargs):
            # Add variant class to existing classes
            classes = kwargs.get('classes', '')
            if classes:
                classes += f" {variant}"
            else:
                classes = variant
            kwargs['classes'] = classes

            # Add icon to label if provided
            if icon:
                label = f"{icon} {label}"

            super().__init__(label, **kwargs)


    class PrimaryButton(StyledButton):
        """Primary action button."""
        def __init__(self, label: str, **kwargs):
            super().__init__(label, variant="primary", **kwargs)


    class SecondaryButton(StyledButton):
        """Secondary action button."""
        def __init__(self, label: str, **kwargs):
            super().__init__(label, variant="secondary", **kwargs)


    class SuccessButton(StyledButton):
        """Success/confirm action button."""
        def __init__(self, label: str, **kwargs):
            super().__init__(label, variant="success", **kwargs)


    class WarningButton(StyledButton):
        """Warning action button."""
        def __init__(self, label: str, **kwargs):
            super().__init__(label, variant="warning", **kwargs)


    class DangerButton(StyledButton):
        """Danger/delete action button."""
        def __init__(self, label: str, **kwargs):
            super().__init__(label, variant="error", **kwargs)


    class IconButton(StyledButton):
        """Small icon-only button."""
        def __init__(self, icon: str, variant: str = "default", **kwargs):
            classes = kwargs.get('classes', '')
            classes += " icon"
            kwargs['classes'] = classes
            super().__init__(icon, variant=variant, **kwargs)


    class StyledInput(TextualInput):
        """Input field with predefined styling."""

        def __init__(self, placeholder: str = "", variant: str = "default", **kwargs):
            # Add variant class if not default
            if variant != "default":
                classes = kwargs.get('classes', '')
                if classes:
                    classes += f" {variant}"
                else:
                    classes = variant
                kwargs['classes'] = classes

            super().__init__(placeholder=placeholder, **kwargs)


    class StyledTextArea(TextualTextArea):
        """TextArea with predefined styling."""

        def __init__(self, text: str = "", variant: str = "default", **kwargs):
            # Add variant class if not default
            if variant != "default":
                classes = kwargs.get('classes', '')
                if classes:
                    classes += f" {variant}"
                else:
                    classes = variant
                kwargs['classes'] = classes

            super().__init__(text=text, **kwargs)


    class LargeTextArea(StyledTextArea):
        """Large text area for extensive content."""
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)


    class SmallTextArea(StyledTextArea):
        """Small text area for brief content."""
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)


    class ReadOnlyTextArea(StyledTextArea):
        """Read-only text area for display purposes."""
        def __init__(self, *args, **kwargs):
            kwargs['read_only'] = True
            super().__init__(*args, **kwargs)


    class StyledSelect(Select):
        """Select dropdown with styling."""

        def __init__(self, **kwargs):
            super().__init__(**kwargs)


    class StyledListView(ListView):
        """ListView with styling."""

        def __init__(self, **kwargs):
            super().__init__(**kwargs)


    class StyledStatic(Static):
        """Static text with predefined styling classes."""

        def __init__(self, text: str = "", variant: str = "default", **kwargs):
            # Add variant class if not default
            if variant != "default":
                classes = kwargs.get('classes', '')
                if classes:
                    classes += f" {variant}"
                else:
                    classes = variant
                kwargs['classes'] = classes

            super().__init__(text, **kwargs)


    class TitleText(StyledStatic):
        """Large title text."""
        def __init__(self, text: str, **kwargs):
            super().__init__(text, variant="title", **kwargs)


    class SubtitleText(StyledStatic):
        """Medium subtitle text."""
        def __init__(self, text: str, **kwargs):
            super().__init__(text, variant="subtitle", **kwargs)


    class CaptionText(StyledStatic):
        """Small caption text."""
        def __init__(self, text: str, **kwargs):
            super().__init__(text, variant="caption", **kwargs)


    class ErrorText(StyledStatic):
        """Red error text."""
        def __init__(self, text: str, **kwargs):
            super().__init__(text, variant="error", **kwargs)


    class SuccessText(StyledStatic):
        """Green success text."""
        def __init__(self, text: str, **kwargs):
            super().__init__(text, variant="success", **kwargs)


    class WarningText(StyledStatic):
        """Yellow warning text."""
        def __init__(self, text: str, **kwargs):
            super().__init__(text, variant="warning", **kwargs)


    class StatusText(StyledStatic):
        """Muted status text."""
        def __init__(self, text: str, **kwargs):
            super().__init__(text, variant="status", **kwargs)


    class ButtonGroup(Horizontal):
        """Group of buttons in a horizontal layout."""
        def __init__(self, **kwargs):
            classes = kwargs.get('classes', '')
            classes += " button-group"
            kwargs['classes'] = classes
            super().__init__(**kwargs)


    class ButtonRow(Horizontal):
        """Row of buttons with standard spacing."""
        def __init__(self, **kwargs):
            classes = kwargs.get('classes', '')
            classes += " button-row"
            kwargs['classes'] = classes
            super().__init__(**kwargs)


    class FormField(Vertical):
        """Vertical form field container."""
        def __init__(self, label: str = "", **kwargs):
            classes = kwargs.get('classes', '')
            classes += " form-field"
            kwargs['classes'] = classes
            super().__init__(**kwargs)

            self.field_label = label

        def compose(self):
            if self.field_label:
                yield StyledStatic(self.field_label, variant="label")


    class Card(Vertical):
        """Card container with border and padding."""
        def __init__(self, title: str = "", **kwargs):
            classes = kwargs.get('classes', '')
            classes += " border p-2"
            kwargs['classes'] = classes
            super().__init__(**kwargs)
            self.card_title = title

        def compose(self):
            if self.card_title:
                yield TitleText(self.card_title)


# Convenience functions to create styled components
def create_button(label: str, variant: str = "primary", icon: str = "", **kwargs):
    """Create a styled button with the specified variant."""
    if not TEXTUAL_AVAILABLE:
        return None

    # Get classes from global scope to avoid E0606 errors
    primary_button = globals().get('PrimaryButton')
    secondary_button = globals().get('SecondaryButton')
    success_button = globals().get('SuccessButton')
    warning_button = globals().get('WarningButton')
    danger_button = globals().get('DangerButton')
    styled_button = globals().get('StyledButton')

    variant_map = {
        'primary': primary_button,
        'secondary': secondary_button,
        'success': success_button,
        'warning': warning_button,
        'danger': danger_button,
        'error': danger_button,
    }

    button_class = variant_map.get(variant, styled_button)
    if button_class:
        return button_class(label, icon=icon, **kwargs)
    return None


def create_input(placeholder: str = "", variant: str = "default", **kwargs):
    """Create a styled input field."""
    if not TEXTUAL_AVAILABLE:
        return None

    styled_input = globals().get('StyledInput')
    if styled_input:
        return styled_input(placeholder=placeholder, variant=variant, **kwargs)
    return None


def create_textarea(text: str = "", placeholder: str = "", size: str = "default", **kwargs):
    """Create a styled text area."""
    if not TEXTUAL_AVAILABLE:
        return None

    # Get classes from global scope to avoid E0606 errors
    large_textarea = globals().get('LargeTextArea')
    small_textarea = globals().get('SmallTextArea')
    styled_textarea = globals().get('StyledTextArea')

    if size == "large" and large_textarea:
        return large_textarea(text=text, placeholder=placeholder, **kwargs)
    if size == "small" and small_textarea:
        return small_textarea(text=text, placeholder=placeholder, **kwargs)
    if styled_textarea:
        return styled_textarea(text=text, placeholder=placeholder, **kwargs)
    return None


__all__ = [
    'StyledButton', 'PrimaryButton', 'SecondaryButton', 'SuccessButton',
    'WarningButton', 'DangerButton', 'IconButton',
    'StyledInput', 'StyledTextArea', 'LargeTextArea', 'SmallTextArea', 'ReadOnlyTextArea',
    'StyledSelect', 'StyledListView', 'StyledStatic',
    'TitleText', 'SubtitleText', 'CaptionText',
    'ErrorText', 'SuccessText', 'WarningText', 'StatusText',
    'ButtonGroup', 'ButtonRow', 'FormField', 'Card',
    'create_button', 'create_input', 'create_textarea'
]
