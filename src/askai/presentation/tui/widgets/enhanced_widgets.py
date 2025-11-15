"""
TUI Widgets for AskAI CLI.
Custom widgets for enhanced user experience including credit display,
model information, and enhanced browsing capabilities.
"""

import re
from typing import Optional, List, Dict, Any, TYPE_CHECKING

try:
    from textual.widgets import Static, ListView, ListItem, Label, DataTable
    from textual.containers import Container
    from textual.reactive import reactive
    from textual.screen import ModalScreen
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    if not TYPE_CHECKING:
        Container = object
        Static = object
        ListView = object
        ListItem = object
        Label = object
        DataTable = object
        ModalScreen = object

        def reactive(x):
            """Simple fallback for reactive."""
            return x

    ComposeResult = Any

# Type imports for static analysis
if TYPE_CHECKING:
    from textual.containers import Container
    from textual.widgets import Static, ListView, ListItem, Label, DataTable
    from textual.screen import ModalScreen
    from textual.reactive import reactive


if TEXTUAL_AVAILABLE:
    class CreditDisplayWidget(Container):
        """Widget for displaying OpenRouter credit information."""

        credits = reactive(0.0)
        refresh_enabled = reactive(True)

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.credit_info = {}

        def compose(self):
            """Compose the credit display widget."""
            yield Static("Credit Information", classes="widget-title")
            yield Static(id="credit-balance")
            yield Static(id="credit-usage")
            yield Static(id="credit-limits")

        def update_credits(self, credit_info: Dict[str, Any]):
            """Update credit information display."""
            self.credit_info = credit_info

            balance = credit_info.get('balance', 0.0)
            usage_today = credit_info.get('usage_today', 0.0)
            limit_daily = credit_info.get('limit_daily', 0.0)

            self.credits = balance

            # Update display elements
            balance_widget = self.query_one("#credit-balance", Static)
            usage_widget = self.query_one("#credit-usage", Static)
            limits_widget = self.query_one("#credit-limits", Static)

            balance_widget.update(f"Balance: ${balance:.4f}")
            usage_widget.update(f"Today's Usage: ${usage_today:.4f}")
            limits_widget.update(f"Daily Limit: ${limit_daily:.4f}")


    class ModelInfoWidget(Container):
        """Widget for displaying detailed model information."""

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.model_info = {}

        def compose(self):
            """Compose the model info widget."""
            yield Static("Model Information", classes="widget-title")
            yield DataTable(id="model-details")

        def update_model_info(self, model_info: Dict[str, Any]):
            """Update model information display."""
            self.model_info = model_info

            table = self.query_one("#model-details", DataTable)
            table.clear(columns=True)
            table.add_columns("Property", "Value")

            # Add model details
            for key, value in model_info.items():
                table.add_row(key.replace('_', ' ').title(), str(value))


    class EnhancedListView(ListView):
        """Enhanced ListView with search highlighting and preview."""

        search_term = reactive("")
        preview_enabled = reactive(True)

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.original_items = []

        def set_items(self, items: List[Dict[str, Any]]):
            """Set the list items and store originals for filtering."""
            self.original_items = items
            self.refresh_items()

        def refresh_items(self):
            """Refresh the list with current search term."""
            self.clear()

            for i, item in enumerate(self.original_items):
                name = item.get('name', 'Unknown')
                description = item.get('description', '')

                # Apply search filter
                if self.search_term and (
                    self.search_term.lower() not in name.lower() and
                    self.search_term.lower() not in description.lower()
                ):
                    continue

                # Create highlighted text if search term exists
                if self.search_term:
                    name = self._highlight_search_term(name, self.search_term)
                    description = self._highlight_search_term(description, self.search_term)

                item_text = f"[bold]{name}[/bold]"
                if description:
                    item_text += f"\n  {description[:100]}..."

                self.append(ListItem(Label(item_text), name=str(i)))

        def _highlight_search_term(self, text: str, search_term: str) -> str:
            """Highlight search term in text."""
            if not search_term:
                return text

            # Simple highlighting - in a real implementation, you might use more sophisticated highlighting
            pattern = re.compile(re.escape(search_term), re.IGNORECASE)
            return pattern.sub(f"[yellow]{search_term}[/yellow]", text)

        def filter_items(self, search_term: str):
            """Filter items based on search term."""
            self.search_term = search_term
            self.refresh_items()


    class PatternPreviewModal(ModalScreen):
        """Modal screen for previewing pattern details."""

        def __init__(self, pattern_data: Dict[str, Any], **kwargs):
            super().__init__(**kwargs)
            self.pattern_data = pattern_data

        def compose(self):
            """Compose the pattern preview modal."""
            with Container(id="preview-dialog"):
                yield Static(f"Pattern: {self.pattern_data.get('name', 'Unknown')}", classes="preview-title")
                yield Static(self.pattern_data.get('description', 'No description'), classes="preview-description")

                # Show pattern inputs
                inputs = self.pattern_data.get('inputs', [])
                if inputs:
                    yield Static("Required Inputs:", classes="preview-section")
                    for inp in inputs:
                        input_name = inp.get('name', 'Unknown')
                        input_desc = inp.get('description', '')
                        input_required = inp.get('required', False)
                        required_text = " (required)" if input_required else " (optional)"
                        yield Static(f"  • {input_name}: {input_desc}{required_text}", classes="preview-item")

                # Show pattern outputs
                outputs = self.pattern_data.get('outputs', [])
                if outputs:
                    yield Static("Outputs:", classes="preview-section")
                    for out in outputs:
                        output_name = out.get('name', 'Unknown')
                        output_desc = out.get('description', '')
                        yield Static(f"  • {output_name}: {output_desc}", classes="preview-item")

        CSS = """
        #preview-dialog {
            width: 80%;
            height: 80%;
            background: $surface;
            border: thick #00FFFF;
            padding: 2;
        }

        .preview-title {
            text-style: bold;
            color: $primary;
            margin-bottom: 1;
        }

        .preview-description {
            margin-bottom: 2;
        }

        .preview-section {
            text-style: bold;
            margin: 1 0;
        }

        .preview-item {
            margin-left: 2;
        }
        """


    class ProgressWidget(Container):
        """Widget for showing progress and status information."""

        progress = reactive(0)
        status_text = reactive("Ready")

        def compose(self):
            """Compose the progress widget."""
            yield Static(id="status-text")
            yield Static(id="progress-bar")

        def watch_status_text(self, new_status: str):
            """Update status text when it changes."""
            status_widget = self.query_one("#status-text", Static)
            status_widget.update(new_status)

        def watch_progress(self, new_progress: int):
            """Update progress bar when progress changes."""
            progress_widget = self.query_one("#progress-bar", Static)

            # Create a simple text-based progress bar
            bar_width = 40
            filled = int((new_progress / 100) * bar_width)
            progress_bar = "█" * filled + "░" * (bar_width - filled)
            progress_widget.update(f"[{progress_bar}] {new_progress}%")

        def set_status(self, status: str, progress: Optional[int] = None):
            """Set status and optionally progress."""
            self.status_text = status
            if progress is not None:
                self.progress = progress


__all__ = [
    'CreditDisplayWidget',
    'ModelInfoWidget',
    'EnhancedListView',
    'PatternPreviewModal',
    'ProgressWidget'
]
