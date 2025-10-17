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
        ListItem = object
        Select = object
        Vertical = object
        Horizontal = object

# Type imports for static analysis
if TYPE_CHECKING:
    from textual.widgets import Button as TextualButton, Input as TextualInput, TextArea as TextualTextArea
    from textual.widgets import Static, ListView, ListItem, Select
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

        def __init__(self, text: str = "", placeholder: str = "", size: str = "default", **kwargs):
            # Add size class if specified
            if size != "default":
                classes = kwargs.get('classes', '')
                if classes:
                    classes += f" {size}"
                else:
                    classes = size
                kwargs['classes'] = classes

            super().__init__(text=text, placeholder=placeholder, **kwargs)


    class LargeTextArea(StyledTextArea):
        """Large text area for long content."""
        def __init__(self, **kwargs):
            super().__init__(size="large", **kwargs)


    class SmallTextArea(StyledTextArea):
        """Small text area for brief content."""
        def __init__(self, **kwargs):
            super().__init__(size="small", **kwargs)


    class ReadOnlyTextArea(StyledTextArea):
        """Read-only text area for displaying content."""
        def __init__(self, text: str = "", **kwargs):
            kwargs['read_only'] = True
            classes = kwargs.get('classes', '')
            classes += " readonly"
            kwargs['classes'] = classes
            super().__init__(text=text, **kwargs)


    class StyledSelect(Select):
        """Select dropdown with predefined styling."""

        def __init__(self, options, **kwargs):
            super().__init__(options, **kwargs)


    class StyledListView(ListView):
        """ListView with predefined styling."""

        def __init__(self, **kwargs):
            super().__init__(**kwargs)


    class StyledStatic(Static):
        """Static text with semantic styling."""

        def __init__(self, renderable: str = "", variant: str = "default", **kwargs):
            # Add variant class
            if variant != "default":
                classes = kwargs.get('classes', '')
                if classes:
                    classes += f" {variant}"
                else:
                    classes = variant
                kwargs['classes'] = classes

            super().__init__(renderable, **kwargs)


    class TitleText(StyledStatic):
        """Title text styling."""
        def __init__(self, text: str, **kwargs):
            super().__init__(text, variant="title", **kwargs)


    class SubtitleText(StyledStatic):
        """Subtitle text styling."""
        def __init__(self, text: str, **kwargs):
            super().__init__(text, variant="subtitle", **kwargs)


    class CaptionText(StyledStatic):
        """Caption/description text styling."""
        def __init__(self, text: str, **kwargs):
            super().__init__(text, variant="caption", **kwargs)


    class ErrorText(StyledStatic):
        """Error message text styling."""
        def __init__(self, text: str, **kwargs):
            super().__init__(text, variant="error-text", **kwargs)


    class SuccessText(StyledStatic):
        """Success message text styling."""
        def __init__(self, text: str, **kwargs):
            super().__init__(text, variant="success-text", **kwargs)


    class WarningText(StyledStatic):
        """Warning message text styling."""
        def __init__(self, text: str, **kwargs):
            super().__init__(text, variant="warning-text", **kwargs)


    class StatusText(StyledStatic):
        """Status indicator text."""
        def __init__(self, text: str, status: str = "loading", **kwargs):
            variant = f"status-{status}"
            super().__init__(text, variant=variant, **kwargs)


    class ButtonGroup(Horizontal):
        """Horizontal container for button groups."""
        def __init__(self, **kwargs):
            classes = kwargs.get('classes', '')
            classes += " button-group"
            kwargs['classes'] = classes
            super().__init__(**kwargs)


    class ButtonRow(Horizontal):
        """Horizontal container for button rows."""
        def __init__(self, **kwargs):
            classes = kwargs.get('classes', '')
            classes += " button-row"
            kwargs['classes'] = classes
            super().__init__(**kwargs)


    class FormField(Vertical):
        """Container for form fields with label and input."""

        def __init__(self, label: str, input_widget, description: str = "", error: str = "", **kwargs):
            super().__init__(**kwargs)
            self.label_text = label
            self.input_widget = input_widget
            self.description_text = description
            self.error_text = error

        def compose(self):
            if self.label_text:
                yield StyledStatic(self.label_text, classes="input-label")

            if self.description_text:
                yield StyledStatic(self.description_text, classes="input-description")

            yield self.input_widget

            if self.error_text:
                yield ErrorText(self.error_text, classes="input-error")


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


# Convenience function to create styled components
def create_button(label: str, variant: str = "primary", icon: str = "", **kwargs):
    """Create a styled button with the specified variant."""
    if not TEXTUAL_AVAILABLE:
        return None

    # Only reference button classes if textual is available
    if 'StyledButton' in globals() and 'PrimaryButton' in globals():
        variant_map = {
            'primary': PrimaryButton,
            'secondary': SecondaryButton,
            'success': SuccessButton,
            'warning': WarningButton,
            'danger': DangerButton,
            'error': DangerButton,
        }

        button_class = variant_map.get(variant, StyledButton)
        return button_class(label, icon=icon, **kwargs)
    return None


def create_input(placeholder: str = "", variant: str = "default", **kwargs):
    """Create a styled input field."""
    if not TEXTUAL_AVAILABLE:
        return None
    # Only reference StyledInput if textual is available
    if 'StyledInput' in globals():
        return StyledInput(placeholder=placeholder, variant=variant, **kwargs)
    return None


def create_textarea(text: str = "", placeholder: str = "", size: str = "default", **kwargs):
    """Create a styled text area."""
    if not TEXTUAL_AVAILABLE:
        return None

    # Only reference text area classes if textual is available
    if 'StyledTextArea' in globals() and 'LargeTextArea' in globals():
        if size == "large":
            return LargeTextArea(text=text, placeholder=placeholder, **kwargs)
        elif size == "small":
            return SmallTextArea(text=text, placeholder=placeholder, **kwargs)
        else:
            return StyledTextArea(text=text, placeholder=placeholder, **kwargs)
    return None


__all__ = [
    'StyledButton', 'PrimaryButton', 'SecondaryButton', 'SuccessButton',
    'WarningButton', 'DangerButton', 'IconButton',
    'StyledInput', 'StyledTextArea', 'LargeTextArea', 'SmallTextArea', 'ReadOnlyTextArea',
    'StyledSelect', 'StyledListView', 'StyledStatic',
    'TitleText', 'SubtitleText', 'CaptionText', 'ErrorText', 'SuccessText', 'WarningText', 'StatusText',
    'ButtonGroup', 'ButtonRow', 'FormField', 'Card',
    'create_button', 'create_input', 'create_textarea'
]
