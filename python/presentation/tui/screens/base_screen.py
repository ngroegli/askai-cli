"""Base screen class with global bindings and consistent styling."""

from textual.screen import Screen
from textual.binding import Binding


class BaseScreen(Screen):
    """Base screen class with consistent global bindings."""

    # Global bindings that should be available in all screens
    BINDINGS = [
        Binding("escape", "back", "Back", show=True, priority=True),
        Binding("ctrl+q", "quit", "Quit", show=True, priority=True),
        Binding("f1", "help", "Help", show=True),
        Binding("ctrl+r", "refresh", "Refresh", show=False),
        Binding("ctrl+f", "focus_search", "Search", show=False),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def action_back(self) -> None:
        """Go back to the previous screen."""
        self.app.pop_screen()

    async def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    async def action_help(self) -> None:
        """Show help information."""
        help_text = self.get_help_text()
        self.notify(help_text, severity="information")

    async def action_refresh(self) -> None:
        """Refresh screen data - override in subclasses."""
        self.notify("Refresh not implemented for this screen", severity="warning")

    async def action_focus_search(self) -> None:
        """Focus search/filter input - override in subclasses."""

    def get_help_text(self) -> str:
        """Get help text for this screen - override in subclasses."""
        return """
Global Controls:
• Escape - Go back to previous screen
• Ctrl+Q - Quit application
• F1 - Show this help
• Ctrl+R - Refresh data
• Ctrl+F - Focus search/filter
        """.strip()
