"""
Base component for tab content in the TUI interface.
"""

try:
    from textual.widgets import Static
    from textual.containers import Vertical
except ImportError:
    # Fallback for when textual is not available
    class Static:
        """Fallback Static widget."""
        def __init__(self, text="", **kwargs):  # pylint: disable=unused-argument
            self.text = text
    class Vertical:
        """Fallback Vertical container."""
        def __init__(self, **kwargs):  # pylint: disable=unused-argument
            pass


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
