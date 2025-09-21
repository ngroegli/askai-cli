"""
Interactive pattern browser using Textual TUI framework.

Provides a modern interface for browsing, searching, and selecting patterns
with real-time preview, filtering, and advanced navigation capabilities.
"""

import os
from typing import Optional, List, Any
from pathlib import Path

# Safe imports with fallbacks
try:
    from textual.app import App, ComposeResult
    from textual.containers import Horizontal, Vertical
    from textual.widgets import (
        Header, Footer, Input, Static, ListItem, ListView,
        Button, Label, ScrollableContainer
    )
    from textual.binding import Binding
    from textual.message import Message
    from textual.reactive import reactive
    TEXTUAL_AVAILABLE = True
except ImportError:
    # Fallback classes for when textual is not available
    TEXTUAL_AVAILABLE = False
    App = object
    ComposeResult = None


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
    class PatternPreview(ScrollableContainer):
        """Widget for displaying pattern content preview."""

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.pattern: Optional[PatternItem] = None

        def update_preview(self, pattern: Optional[PatternItem]):
            """Update the preview with new pattern content."""
            self.pattern = pattern
            self.remove_children()

            if pattern is None:
                self.mount(Static("Select a pattern to preview", classes="preview-placeholder"))
            else:
                # Show pattern metadata
                self.mount(Static(f"Pattern: {pattern.name}", classes="preview-title"))
                if pattern.description:
                    self.mount(Static(f"Description: {pattern.description}", classes="preview-description"))
                self.mount(Static("─" * 50, classes="preview-separator"))

                # Show content
                content = pattern.get_preview(50)  # Show more lines in preview
                self.mount(Static(content, classes="preview-content"))


    class PatternList(ListView):
        """Custom ListView for patterns with search functionality."""

        def __init__(self, patterns: List[PatternItem], **kwargs):
            super().__init__(**kwargs)
            self.all_patterns = patterns
            self.filtered_patterns = patterns.copy()
            self.populate_list()

        def populate_list(self):
            """Populate the list with current filtered patterns."""
            self.clear()
            for pattern in self.filtered_patterns:
                label = f"{pattern.name}"
                if pattern.category:
                    label += f" ({pattern.category})"
                self.append(ListItem(Label(label), name=pattern.name))

        def filter_patterns(self, search_term: str):
            """Filter patterns based on search term."""
            search_term = search_term.lower().strip()
            if not search_term:
                self.filtered_patterns = self.all_patterns.copy()
            else:
                self.filtered_patterns = [
                    pattern for pattern in self.all_patterns
                    if (search_term in pattern.name.lower() or
                        search_term in pattern.description.lower() or
                        search_term in pattern.category.lower())
                ]
            self.populate_list()

        def get_selected_pattern(self) -> Optional[PatternItem]:
            """Get the currently selected pattern."""
            if self.index is None or self.index >= len(self.filtered_patterns):
                return None
            return self.filtered_patterns[self.index]


    class PatternBrowser(App):
        """Main application for browsing patterns."""

        CSS = """
        Screen {
            layout: horizontal;
        }

        #sidebar {
            width: 50%;
            border-right: thick $surface;
        }

        #preview {
            width: 50%;
            padding: 1;
        }

        #search {
            margin: 1;
        }

        .preview-title {
            text-style: bold;
            color: $primary;
        }

        .preview-description {
            color: $secondary;
            margin-bottom: 1;
        }

        .preview-separator {
            color: $surface;
            margin-bottom: 1;
        }

        .preview-content {
            margin-top: 1;
        }

        .preview-placeholder {
            color: $secondary;
            text-align: center;
            margin-top: 5;
        }
        """

        BINDINGS = [
            Binding("ctrl+q", "quit", "Quit"),
            Binding("ctrl+c", "quit", "Quit"),
            Binding("escape", "quit", "Quit"),
            Binding("ctrl+f", "focus_search", "Search"),
            Binding("/", "focus_search", "Search"),
            Binding("enter", "select_pattern", "Select"),
            Binding("ctrl+p", "toggle_preview", "Toggle Preview"),
        ]

        def __init__(self, pattern_manager, **kwargs):
            super().__init__(**kwargs)
            self.pattern_manager = pattern_manager
            self.patterns: List[PatternItem] = []
            self.selected_pattern: Optional[PatternItem] = None
            self.preview_visible = True

        def compose(self) -> ComposeResult:
            """Compose the application layout."""
            yield Header(show_clock=True)

            # Load patterns
            self.load_patterns()

            with Horizontal():
                with Vertical(id="sidebar"):
                    yield Input(placeholder="Search patterns...", id="search")
                    yield PatternList(self.patterns, id="pattern-list")

                yield PatternPreview(id="preview")

            yield Footer()

        def load_patterns(self):
            """Load patterns from the pattern manager."""
            try:
                # Get patterns from the pattern manager
                pattern_data = self.pattern_manager.list_patterns()

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

            except Exception as e:
                # Fallback for testing or when pattern manager is not available
                self.patterns = [
                    PatternItem(
                        name="example_pattern",
                        path="/tmp/example.md",
                        description="Example pattern for testing",
                        category="built-in"
                    )
                ]

        def on_mount(self):
            """Called when the app is mounted."""
            search_input = self.query_one("#search", Input)
            search_input.focus()

        def on_input_changed(self, event: Input.Changed):
            """Handle search input changes."""
            if event.input.id == "search":
                pattern_list = self.query_one("#pattern-list", PatternList)
                pattern_list.filter_patterns(event.value)

        def on_list_view_selected(self, event: ListView.Selected):
            """Handle pattern selection."""
            if event.list_view.id == "pattern-list":
                pattern_list = self.query_one("#pattern-list", PatternList)
                selected_pattern = pattern_list.get_selected_pattern()

                if selected_pattern:
                    self.selected_pattern = selected_pattern
                    preview = self.query_one("#preview", PatternPreview)
                    preview.update_preview(selected_pattern)

        def action_focus_search(self):
            """Focus the search input."""
            search_input = self.query_one("#search", Input)
            search_input.focus()

        def action_select_pattern(self):
            """Select the current pattern and exit."""
            if self.selected_pattern:
                self.exit(self.selected_pattern)
            else:
                # If no pattern selected, try to select the first one
                pattern_list = self.query_one("#pattern-list", PatternList)
                if pattern_list.filtered_patterns:
                    self.exit(pattern_list.filtered_patterns[0])

        def action_toggle_preview(self):
            """Toggle preview pane visibility."""
            preview = self.query_one("#preview")
            self.preview_visible = not self.preview_visible
            if self.preview_visible:
                preview.display = True
            else:
                preview.display = False

        def action_quit(self):
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
        return None

    app = PatternBrowser(pattern_manager)
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


__all__ = ['PatternBrowser', 'PatternItem', 'run_pattern_browser', 'pattern_browser_fallback']
