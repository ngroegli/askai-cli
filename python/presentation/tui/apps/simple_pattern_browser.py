"""
Simple and robust pattern browser for quick listing and selection.
"""

from typing import Optional, TYPE_CHECKING

try:
    from textual.app import App
    from textual.widgets import Header, Footer, Static, ListView, ListItem, Label
    from textual.binding import Binding
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    if not TYPE_CHECKING:
        App = object
        Header = object
        Footer = object
        Static = object
        ListView = object
        ListItem = object
        Label = object
        Binding = object

# Type imports for static analysis
if TYPE_CHECKING:
    from textual.app import App
    from textual.widgets import Header, Footer, Static, ListView, ListItem, Label
    from textual.binding import Binding


if TEXTUAL_AVAILABLE:
    class SimplePatternBrowser(App):
        """Simple pattern browser for listing and quick selection."""

        CSS = """
        ListView {
            height: 1fr;
        }

        .pattern-item {
            padding: 1;
        }

        .pattern-name {
            text-style: bold;
        }

        .pattern-description {
            color: $text-muted;
        }
        """

        BINDINGS = [
            Binding("q", "quit", "Quit"),
            Binding("escape", "quit", "Quit"),
            Binding("enter", "select", "Select"),
        ]

        def __init__(self, pattern_manager, **kwargs):
            super().__init__(**kwargs)
            self.pattern_manager = pattern_manager
            self.patterns = []
            self.selected_pattern = None

        def compose(self):
            """Compose the application UI."""
            yield Header()
            yield Static("Pattern Browser - Use arrow keys to navigate, Enter to select, Q to quit",
                        classes="help-text")

            # Create empty list view - will populate after mounting
            yield ListView(id="pattern-list")
            yield Footer()

        def on_mount(self):
            """Called after the widget is mounted."""
            self.load_and_populate_patterns()

        def load_and_populate_patterns(self):
            """Load patterns and populate the list view."""
            # Load patterns from the pattern manager
            self.load_patterns()

            # Get the list view and populate it
            pattern_list = self.query_one("#pattern-list", ListView)

            for i, pattern in enumerate(self.patterns):
                name = pattern.get('name', 'Unknown')
                description = pattern.get('description', '')
                source = pattern.get('source', 'unknown')

                # Create list item with pattern info
                item_text = f"[bold]{name}[/bold] ({source})"
                if description:
                    item_text += f"\n  {description}"

                pattern_list.append(ListItem(Label(item_text), name=str(i)))

        def load_patterns(self):
            """Load patterns from the pattern manager."""
            try:
                self.patterns = self.pattern_manager.list_patterns()
                if not self.patterns:
                    self.patterns = [{'name': 'No patterns found', 'description': '', 'source': 'system'}]
            except Exception as e:
                self.patterns = [{'name': f'Error loading patterns: {e}', 'description': '', 'source': 'error'}]

        def on_list_view_selected(self, event: ListView.Selected):
            """Handle pattern selection."""
            if event.list_view.id == "pattern-list":
                try:
                    if event.item.name:
                        index = int(event.item.name)
                        if 0 <= index < len(self.patterns):
                            self.selected_pattern = self.patterns[index]
                            self.action_select()
                except (ValueError, IndexError):
                    pass

        def action_select(self):
            """Select the current pattern and exit."""
            if self.selected_pattern and self.selected_pattern.get('name') != 'No patterns found':
                self.exit(self.selected_pattern)
            else:
                self.exit(None)

        async def action_quit(self):
            """Quit the application."""
            self.exit(None)


def run_simple_pattern_browser(pattern_manager) -> Optional[dict]:
    """
    Run the simple pattern browser and return the selected pattern.
    """
    if not TEXTUAL_AVAILABLE:
        return None

    try:
        app = SimplePatternBrowser(pattern_manager)
        result = app.run()
        return result
    except Exception:
        # If TUI fails, return None to trigger fallback
        return None


__all__ = ['SimplePatternBrowser', 'run_simple_pattern_browser']
