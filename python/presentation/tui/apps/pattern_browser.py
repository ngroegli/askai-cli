"""
Interactive pattern browser using Textual TUI framework.
Professional two-panel design matching the model browser blueprint.

Provides a modern interface for browsing, searching, and selecting patterns
with real-time preview, filtering, and advanced navigation capabilities.
"""

from typing import Optional, List, TYPE_CHECKING

# Safe imports with fallbacks
try:
    from textual.app import App, ComposeResult
    from textual.containers import Horizontal, Vertical, Container
    from textual.widgets import (
        Header, Footer, Input, ListItem, ListView,
        Label, Static, RichLog, Button
    )
    from textual.binding import Binding
    TEXTUAL_AVAILABLE = True
except ImportError:
    # Fallback classes for when textual is not available
    TEXTUAL_AVAILABLE = False
    if not TYPE_CHECKING:
        App = object
        ComposeResult = None
        Horizontal = object
        Vertical = object
        Container = object
        Header = object
        Footer = object
        Input = object
        Static = object
        ListItem = object
        ListView = object
        Label = object
        Binding = object
        RichLog = object
        Button = object

# Type imports for static analysis
if TYPE_CHECKING:
    from textual.app import App, ComposeResult
    from textual.containers import Horizontal, Vertical, Container
    from textual.widgets import (
        Header, Footer, Input, Static, ListItem, ListView,
        Label, RichLog
    )
    from textual.binding import Binding

# Import styled components
try:
    from ..styles.styled_components import StyledButton, StyledStatic, StyledInput
    STYLES_AVAILABLE = True
except ImportError:
    STYLES_AVAILABLE = False
    if not TYPE_CHECKING:
        # Use base textual widgets when styled components not available
        try:
            from textual.widgets import Button as StyledButton, Static as StyledStatic, Input as StyledInput
        except ImportError:
            StyledButton = object
            StyledStatic = object
            StyledInput = object


class PatternItem:
    """Represents a pattern with metadata."""

    def __init__(self, name: str, path: str, description: str = "", category: str = ""):
        self.name = name
        self.path = path
        self.description = description
        self.category = category
        self.content: Optional[str] = None

    def load_content(self) -> str:
        """Load pattern content from file."""
        if self.content is None:
            try:
                with open(self.path, 'r', encoding='utf-8') as f:
                    self.content = f.read()
            except Exception as e:
                self.content = f"Error loading pattern: {e}"
        return self.content

    def get_preview(self, max_lines: int = 10) -> str:
        """Get a preview of the pattern content."""
        content = self.load_content()
        lines = content.split('\n')
        if len(lines) <= max_lines:
            return content
        return '\n'.join(lines[:max_lines]) + '\n...'


if TEXTUAL_AVAILABLE:
    class PatternBrowserApp(App):
        """Pattern browser with professional two-panel design matching model browser."""

        CSS = """
        .pattern-browser-container {
            height: 1fr;
            padding: 1;
        }

        .pattern-list-panel {
            width: 1fr;
            border: round #00FFFF;
            padding: 2;
            margin-right: 2;
            background: $surface;
            height: 1fr;
        }

        .pattern-details-panel {
            width: 2fr;
            border: round #00FFFF;
            padding: 2;
            background: $surface;
            height: 1fr;
        }

        .pattern-list {
            height: 1fr;
            border: solid #87CEEB;
            background: $background;
            margin-bottom: 1;
        }

        .pattern-details-content {
            height: 1fr;
            border: solid #87CEEB;
            margin-top: 0;
            padding: 1;
            background: $background;
            overflow-x: hidden;
            overflow-y: auto;
        }

        .filter-input {
            margin: 0;
            height: 3;
            border: solid #87CEEB;
        }

        .filter-input:focus {
            border: solid #87CEEB;
        }

        .status-caption {
            color: #87CEEB;
            background: transparent;
            height: 1;
            padding: 0 1;
            text-align: left;
            text-style: dim;
            margin-bottom: 0;
        }

        .success-text {
            color: $success;
        }

        .error-text {
            color: $error;
        }

        .loading-text {
            color: $accent;
            text-style: italic;
        }

        .panel-title {
            text-style: bold;
            color: $primary;
            text-align: center;
            margin-bottom: 0;
            background: $background;
            padding: 0 1;
            border: solid #87CEEB;
        }

        .button-container {
            height: auto;
            padding: 0;
            margin-top: 0;
            background: $surface;
            border: solid #87CEEB;
            text-align: center;
        }

        RichLog {
            overflow-x: hidden;
            overflow-y: auto;
        }

        ListView {
            overflow-x: hidden;
            overflow-y: auto;
            height: 1fr;
        }

        .pattern-list {
            max-height: 80%;
        }

        /* Pattern list items */
        .pattern-item {
            text-overflow: ellipsis;
        }

        /* Button styling to ensure proper colors */
        Button, StyledButton {
            width: 10;
            height: 3;
            align: center middle;
            text-align: center;
            background: $primary;
            color: $text;
            border: solid $primary;
        }

        Button:hover, StyledButton:hover {
            background: $primary 80%;
            border: solid $primary 80%;
        }

        Button:focus, StyledButton:focus {
            border: thick #00FFFF;
        }

        Button.primary:hover, Button.secondary:hover,
        StyledButton.primary:hover, StyledButton.secondary:hover {
            background: $primary 80%;
        }

        Button.primary:focus, Button.secondary:focus,
        StyledButton.primary:focus, StyledButton.secondary:focus {
            border: thick #00FFFF;
        }

        /* Override syntax highlighting for numbers */
        .tok-m, .tok-mf, .tok-mi, .tok-mo {
            color: #00FFFF !important;
        }

        /* Number literal styling */
        Number {
            color: #00FFFF;
        }

        /* Status caption number override */
        .status-caption Number, .status-caption .tok-m, .status-caption .tok-mi {
            color: #00FFFF !important;
        }
        """

        BINDINGS = [
            Binding("ctrl+q", "quit", "Quit"),
            Binding("ctrl+c", "quit", "Quit"),
            Binding("escape", "quit", "Quit"),
            Binding("r", "refresh", "Refresh", show=True),
            Binding("/", "focus_search", "Search", show=True),
            Binding("enter", "select_pattern", "Select", show=True),
        ]

        def __init__(self, pattern_manager, **kwargs):
            super().__init__(**kwargs)
            self.pattern_manager = pattern_manager
            self.patterns: List[PatternItem] = []
            self.filtered_patterns: List[PatternItem] = []
            self.selected_pattern: Optional[PatternItem] = None
            self.pattern_index_map = {}  # Maps list item index to pattern data

        def compose(self) -> ComposeResult:
            """Create child widgets for the app."""
            yield Header(show_clock=True)

            with Container(classes="pattern-browser-container"):
                with Horizontal():
                    # Left panel - pattern list, filter, and buttons
                    with Vertical(classes="pattern-list-panel"):
                        yield StyledStatic("Pattern Browser", classes="panel-title")
                        yield StyledInput(
                            placeholder="Filter patterns (e.g., analysis, generation, cli)...",
                            id="pattern-filter",
                            classes="filter-input"
                        )

                        # Status as small caption above the list
                        yield Static("[cyan]Patterns: Loading...[/cyan]", id="status", classes="status-caption")

                        yield ListView(id="pattern-list", classes="pattern-list")

                        # Buttons moved to left panel
                        with Horizontal(classes="button-container"):
                            yield StyledButton("Refresh", id="refresh-patterns", variant="primary")
                            yield StyledButton("Back", id="back-button", variant="primary")

                    # Right panel - pattern details (full height)
                    with Vertical(classes="pattern-details-panel"):
                        yield StyledStatic("Pattern Details", classes="panel-title")
                        yield RichLog(
                            id="pattern-details",
                            classes="pattern-details-content",
                            auto_scroll=False,
                            markup=True,
                            wrap=True
                        )

            yield Footer()

        async def on_mount(self) -> None:
            """Initialize the screen when mounted."""
            await self.load_patterns()
            # Display initial guidance message
            details_widget = self.query_one("#pattern-details", RichLog)
            details_widget.write("[dim cyan]Select a pattern from the list to view details[/dim cyan]")

        async def action_refresh(self) -> None:
            """Refresh pattern data."""
            await self.load_patterns()

        async def action_focus_search(self) -> None:
            """Focus the filter input."""
            filter_input = self.query_one("#pattern-filter", Input)
            filter_input.focus()

        async def action_select_pattern(self) -> None:
            """Select the currently highlighted pattern."""
            pattern_list = self.query_one("#pattern-list", ListView)
            if pattern_list.highlighted_child:
                # Get the highlighted index and trigger selection manually
                selected_index = pattern_list.index
                pattern_data = self.pattern_index_map.get(selected_index)
                if pattern_data:
                    self.selected_pattern = pattern_data
                    await self.display_pattern_details()
                    self.exit(self.selected_pattern)

        async def load_patterns(self) -> None:
            """Load available patterns from the pattern manager."""
            try:
                status_widget = self.query_one("#status", Static)
                status_widget.update("[cyan]Patterns: Loading...[/cyan]")
                status_widget.add_class("loading-text")

                # Get patterns from the pattern manager
                pattern_data = self.pattern_manager.list_patterns()
                self.patterns = []

                for pattern_info in pattern_data:
                    name = pattern_info.get('name', 'Unknown')
                    path = pattern_info.get('path', '')
                    description = pattern_info.get('description', '')
                    category = pattern_info.get('category', 'private' if 'private' in path else 'built-in')

                    pattern = PatternItem(
                        name=name,
                        path=path,
                        description=description,
                        category=category
                    )
                    self.patterns.append(pattern)

                self.filtered_patterns = self.patterns.copy()
                await self.populate_pattern_list()

                status_widget.remove_class("loading-text")
                status_widget.add_class("success-text")
                total_count = len(self.patterns)
                status_widget.update(f"[cyan]Patterns: {total_count} of {total_count}[/cyan]")

                # Also call update_status to ensure consistency
                self.update_status()

            except Exception as e:
                status_widget = self.query_one("#status", Static)
                status_widget.remove_class("loading-text")
                status_widget.add_class("error-text")
                status_widget.update(f"[red]Error loading patterns: {str(e)}[/red]")

        async def populate_pattern_list(self) -> None:
            """Populate the pattern list with filtered patterns."""
            pattern_list = self.query_one("#pattern-list", ListView)
            await pattern_list.clear()
            self.pattern_index_map.clear()

            for index, pattern in enumerate(self.filtered_patterns):
                pattern_name = pattern.name
                pattern_category = pattern.category

                # Create a display name that fits well in the list
                display_name = pattern_name
                if pattern_category:
                    display_name += f"\n({pattern_category})"

                if pattern.description:
                    # Add truncated description for better overview
                    desc = pattern.description
                    if len(desc) > 60:
                        desc = desc[:57] + "..."
                    display_name += f"\n{desc}"

                list_item = ListItem(Label(display_name), classes="pattern-item")
                self.pattern_index_map[index] = pattern
                await pattern_list.append(list_item)

            # Update status to show current filter state
            self.update_status()

        async def on_input_changed(self, event: Input.Changed) -> None:
            """Handle filter input changes."""
            if event.input.id == "pattern-filter":
                filter_text = event.value.lower()

                if not filter_text:
                    self.filtered_patterns = self.patterns.copy()
                else:
                    self.filtered_patterns = [
                        pattern for pattern in self.patterns
                        if (filter_text in pattern.name.lower() or
                            filter_text in pattern.description.lower() or
                            filter_text in pattern.category.lower())
                    ]

                await self.populate_pattern_list()

        def update_status(self) -> None:
            """Update the status widget with current pattern count."""
            try:
                status_widget = self.query_one("#status", Static)
                if self.filtered_patterns:
                    # Use Rich markup for entire text to avoid syntax highlighting
                    filtered_count = len(self.filtered_patterns)
                    total_count = len(self.patterns)
                    text = f"[cyan]Patterns: {filtered_count} of {total_count}[/cyan]"
                    status_widget.update(text)
                    status_widget.remove_class("error-text")
                    status_widget.add_class("success-text")
                else:
                    text = "[cyan]No patterns match your filter[/cyan]"
                    status_widget.update(text)
                    status_widget.remove_class("success-text")
                    status_widget.add_class("error-text")
            except Exception as e:
                # Debug: print any errors
                print(f"Status update error: {e}")

        async def on_list_view_selected(self, event: ListView.Selected) -> None:
            """Handle pattern selection."""
            if event.list_view.id == "pattern-list":
                try:
                    selected_index = event.list_view.index
                    pattern_data = self.pattern_index_map.get(selected_index)
                    if pattern_data:
                        self.selected_pattern = pattern_data
                        await self.display_pattern_details()
                except Exception as e:
                    print(f"Selection error: {e}")

        async def display_pattern_details(self) -> None:
            """Display detailed information about the selected pattern."""
            if not self.selected_pattern:
                return

            try:
                details_widget = self.query_one("#pattern-details", RichLog)
                details_widget.clear()

                pattern = self.selected_pattern

                # Pattern header with styling
                details_widget.write(f"[bold cyan]{pattern.name}[/bold cyan]")
                details_widget.write("")

                # Pattern metadata
                if pattern.category:
                    details_widget.write(f"[dim]Category:[/dim] [cyan]{pattern.category}[/cyan]")

                if pattern.description:
                    details_widget.write(f"[dim]Description:[/dim] {pattern.description}")

                if pattern.path:
                    details_widget.write(f"[dim]Path:[/dim] [cyan]{pattern.path}[/cyan]")

                details_widget.write("")
                details_widget.write("[dim]" + "─" * 50 + "[/dim]")
                details_widget.write("")

                # Pattern content preview
                details_widget.write("[bold]Pattern Content:[/bold]")
                details_widget.write("")

                try:
                    content = pattern.load_content()
                    # Limit content display to prevent overwhelming
                    lines = content.split('\n')
                    if len(lines) > 100:
                        content = '\n'.join(lines[:100]) + '\n\n[dim]... (content truncated)[/dim]'

                    details_widget.write(content)
                except Exception as e:
                    details_widget.write(f"[red]Error loading pattern content: {str(e)}[/red]")

            except Exception as e:
                print(f"Error displaying pattern details: {e}")

        async def action_quit(self) -> None:
            """Quit the application."""
            self.exit(None)


def run_pattern_browser(pattern_manager) -> Optional[PatternItem]:
    """
    Run the pattern browser TUI and return the selected pattern.

    Args:
        pattern_manager: The pattern manager instance

    Returns:
        Selected PatternItem or None if cancelled
    """
    if not TEXTUAL_AVAILABLE:
        return pattern_browser_fallback(pattern_manager)

    app = PatternBrowserApp(pattern_manager)
    result = app.run()
    return result


# Fallback function for when Textual is not available
def pattern_browser_fallback(pattern_manager):
    """Fallback pattern browser using simple CLI."""
    print("Textual TUI not available, falling back to simple interface...")
    patterns = pattern_manager.list_patterns()

    if not patterns:
        print("No patterns found.")
        return None

    print("\nAvailable patterns:")
    for i, pattern in enumerate(patterns, 1):
        name = pattern.get('name', 'Unknown')
        description = pattern.get('description', '')
        print(f"{i}. {name}")
        if description:
            print(f"   {description}")

    try:
        choice = input(f"\nSelect pattern (1-{len(patterns)}) or press Enter to cancel: ").strip()
        if not choice:
            return None

        index = int(choice) - 1
        if 0 <= index < len(patterns):
            pattern_data = patterns[index]
            return PatternItem(
                name=pattern_data.get('name', 'Unknown'),
                path=pattern_data.get('path', ''),
                description=pattern_data.get('description', ''),
                category=pattern_data.get('category', '')
            )
        else:
            print("Invalid selection.")
            return None
    except (ValueError, KeyboardInterrupt):
        print("\nCancelled.")
        return None


__all__ = ['PatternBrowserApp', 'PatternItem', 'run_pattern_browser', 'pattern_browser_fallback']
