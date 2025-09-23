"""
Base component for tab content in the TUI interface.
"""

from typing import TYPE_CHECKING

try:
    from textual.widgets import Static
    from textual.containers import Vertical
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    if not TYPE_CHECKING:
        Static = object
        Vertical = object

if TYPE_CHECKING:
    from textual.widgets import Static
    from textual.containers import Vertical


class BaseTabComponent(Vertical):
    """Base class for tab components with common functionality."""

    def __init__(self, title: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title
        self._is_initialized = False

    def compose(self):
        """Compose the basic tab structure - override in subclasses."""
        yield Static(self.title, classes="panel-title")

    async def on_mount(self) -> None:
        """Called when the component is mounted."""
        if not self._is_initialized:
            await self.initialize()
            self._is_initialized = True

    async def initialize(self) -> None:
        """Initialize the component - override in subclasses."""

    async def refresh_content(self) -> None:
        """Refresh the component content - override in subclasses."""
