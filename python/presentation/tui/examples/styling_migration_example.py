"""
Example: How to refactor an existing TUI app to use modular styling.
This demonstrates the before/after approach for implementing best practices.
"""

# === BEFORE: Scattered CSS and inline styling ===

class OldTUIApp(App):
    """Example of poor styling practices - DON'T DO THIS"""

    CSS = """
    /* Scattered, duplicate styles in every component */
    Button {
        margin: 1;
        background: $primary;
        color: $text;
        text-style: bold;
    }

    Button.warning {
        background: $warning;
    }

    Button.error {
        background: $error;
    }

    .my-title {
        text-style: bold;
        color: $primary;
        text-align: center;
        margin: 1;
    }

    .my-subtitle {
        text-style: bold;
        margin: 1 0;
    }

    .my-input {
        height: 8;
        margin: 1 0;
        border: solid $accent;
    }

    .my-status {
        color: $accent;
        text-style: italic;
        text-align: center;
    }

    .my-button-group {
        align: center middle;
        height: auto;
        margin: 1 0;
    }
    """

    def compose(self):
        # Manual CSS classes everywhere
        yield Static("My Application", classes="my-title")
        yield Static("Enter your information", classes="my-subtitle")
        yield TextArea(placeholder="Type here...", classes="my-input")
        yield Static("Ready", classes="my-status")

        with Horizontal(classes="my-button-group"):
            yield Button("Save", variant="primary")
            yield Button("Delete", variant="error")
            yield Button("Cancel", variant="warning")


# === AFTER: Modular styling with reusable components ===

from ..styles import DEFAULT_THEME
from ..styles.styled_components import (
    TitleText, SubtitleText, StatusText,
    PrimaryButton, DangerButton, WarningButton,
    create_textarea, ButtonGroup
)

class ModernTUIApp(App):
    """Example of good styling practices - DO THIS"""

    # Use centralized CSS - no scattered styles!
    CSS = DEFAULT_THEME.get_complete_css()

    def compose(self):
        # Semantic components with automatic styling
        yield TitleText("My Application")
        yield SubtitleText("Enter your information")
        yield create_textarea(placeholder="Type here...", classes="question-input")
        yield StatusText("Ready", status="success")

        # Reusable container with styled buttons
        with ButtonGroup():
            yield PrimaryButton("Save")
            yield DangerButton("Delete")
            yield WarningButton("Cancel")


# === COMPARISON: Benefits of the modular approach ===

"""
BEFORE (Bad):
- CSS scattered across 20+ files
- Duplicate button styles everywhere
- Inconsistent spacing and colors
- Hard to maintain and update
- Manual class management
- No component reuse

AFTER (Good):
- Single CSS source of truth
- Consistent button styling
- Semantic component names
- Easy to maintain and update
- Automatic class management
- High component reuse

MAINTENANCE EXAMPLE:
To change all button colors:

Bad way: Update CSS in 20+ files
Good way: Update one CSS rule in theme.py
"""

# === PRACTICAL MIGRATION STEPS ===

def migrate_existing_app():
    """Step-by-step migration guide."""

    # Step 1: Install the modular styling system
    from ..styles import DEFAULT_THEME

    # Step 2: Replace inline CSS with centralized CSS
    # OLD: CSS = "Button { margin: 1; }"
    # NEW: CSS = DEFAULT_THEME.get_complete_css()

    # Step 3: Replace manual components with styled components
    # OLD: yield Static("Title", classes="my-title")
    # NEW: yield TitleText("Title")

    # Step 4: Use semantic button variants
    # OLD: yield Button("Save", variant="primary")
    # NEW: yield PrimaryButton("Save")

    # Step 5: Use utility containers
    # OLD: with Horizontal(classes="button-container"):
    # NEW: with ButtonGroup():

    # Step 6: Add app-specific styles if needed
    additional_css = """
    .special-widget {
        border: thick $accent;
        background: $surface;
    }
    """
    # CSS = DEFAULT_THEME.get_app_css(additional_css)


# === REAL-WORLD EXAMPLE: Tabbed TUI Refactoring ===

# BEFORE: Original tabbed_tui_app.py (simplified)
class OriginalTabbedApp(App):
    CSS = """
    TabbedContent { background: $surface; }
    TabPane { padding: 1; }
    #question-input { height: 8; margin: 1 0; }
    #format-select { width: 60%; margin: 1; }
    #status { color: $accent; text-style: italic; height: 2; text-align: center; }
    Button { margin: 1; }
    .title { text-style: bold; color: $primary; text-align: center; margin: 1; }
    .center-content { text-align: center; color: $text-muted; margin: 2; }
    /* ... 50+ more lines of CSS ... */
    """

    def compose(self):
        with TabPane("Question Builder"):
            yield Static("Ask questions with AI assistance", classes="title")
            yield Static("Type your question below:")
            yield TextArea(placeholder="Enter your question here...", id="question-input")
            yield Static("Select output format:")
            yield Select(options=formats, id="format-select")
            yield Static("", id="status")
            with Horizontal():
                yield Button("Execute Question", id="execute", variant="success")
                yield Button("Clear", id="clear", variant="warning")


# AFTER: Using modular styling system
class RefactoredTabbedApp(App):
    # Single line replaces 50+ lines of scattered CSS!
    CSS = DEFAULT_THEME.get_complete_css()

    def compose(self):
        with TabPane("Question Builder", classes="tab-content"):
            # Semantic components replace manual styling
            yield TitleText("Ask questions with AI assistance")
            yield CaptionText("Type your question below:")
            yield create_textarea(placeholder="Enter your question here...", classes="question-input")
            yield CaptionText("Select output format:")
            yield StyledSelect(options=formats, classes="format-select")
            yield StatusText("", id="status", classes="question-status")

            # Semantic button container and buttons
            with ButtonGroup():
                yield SuccessButton("Execute Question", id="execute")
                yield WarningButton("Clear", id="clear")


# === BENEFITS DEMONSTRATED ===

benefits = {
    "Lines of CSS": "Before: 50+ lines per app | After: 1 line per app",
    "Button consistency": "Before: Manual styling each time | After: Automatic consistency",
    "Maintenance": "Before: Update 20+ files | After: Update 1 file",
    "Reusability": "Before: Copy/paste CSS | After: Import components",
    "Readability": "Before: CSS classes everywhere | After: Semantic component names",
    "Flexibility": "Before: Hard to customize | After: Easy theme switching",
    "Best practices": "Before: Inline styles | After: Separation of concerns"
}

print("🎯 Modular Styling Benefits:")
for benefit, comparison in benefits.items():
    print(f"   • {benefit}: {comparison}")
