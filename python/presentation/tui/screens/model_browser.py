"""Model browser screen for the TUI."""

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal, Container
from textual.widgets import Header, Footer, Static, Input, ListView, ListItem, Label, RichLog
from textual.binding import Binding

from python.presentation.tui.styles.styled_components import StyledButton, StyledStatic, StyledInput
from python.presentation.tui.screens.base_screen import BaseScreen


class ModelBrowserScreen(BaseScreen):
    """Screen for browsing and filtering OpenRouter models."""

    BINDINGS = BaseScreen.BINDINGS + [
        Binding("r", "refresh", "Refresh", show=True),
        Binding("/", "focus_search", "Search", show=True),
        Binding("enter", "select_model", "Select", show=True),
    ]

    CSS = """
        .model-browser-container {
            height: 1fr;
            padding: 2;
        }

        .model-list-panel {
            width: 1fr;
            border: round #00FFFF;
            padding: 2;
            margin-right: 2;
            background: $surface;
        }

        .model-details-panel {
            width: 2fr;
            border: round #00FFFF;
            padding: 2;
            background: $surface;
        }

        .model-list {
            height: 1fr;
            border: solid #87CEEB;
            background: $background;
        }

        .model-details-content {
            height: 1fr;
            border: solid #87CEEB;
            margin-top: 1;
            margin-bottom: 2;
            padding: 1;
            background: $background;
            overflow-x: hidden;
            overflow-y: auto;
        }

        .filter-input {
            margin: 1 0;
            height: 3;
            border: solid #87CEEB;
        }

        .filter-input:focus {
            border: solid #00FFFF;
        }

        .status-text {
            color: $text-muted;
            text-align: center;
            height: 3;
            padding: 1;
            background: $surface;
            border: solid #008B8B;
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
            margin-bottom: 1;
            background: $background;
            padding: 1 2;
            border: solid #87CEEB;
        }

        .button-container {
            height: auto;
            padding: 1;
            margin-top: 1;
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
        }

        /* Model list items */
        .model-item {
            text-overflow: ellipsis;
        }

        /* Button styling to ensure proper colors */
        Button.primary, Button.secondary {
            background: $primary;
            color: $text;
            border: none;
            text-style: bold;
            width: 12;
            height: 3;
            margin: 1;
        }

        Button.primary:hover, Button.secondary:hover {
            background: $primary 80%;
        }

        Button.primary:focus, Button.secondary:focus {
            border: thick #00FFFF;
        }
    """

    def __init__(self):
        super().__init__()
        self.models = []
        self.filtered_models = []
        self.selected_model = None
        self.model_index_map = {}  # Maps list item index to model data

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)

        with Container(classes="model-browser-container"):
            with Horizontal():
                # Left panel - model list and filter
                with Vertical(classes="model-list-panel"):
                    yield StyledStatic("Model Browser", classes="panel-title")
                    yield StyledInput(
                        placeholder="Filter models (e.g., gpt, claude, llama)...",
                        id="model-filter",
                        classes="filter-input"
                    )
                    yield ListView(id="model-list", classes="model-list")
                    yield StyledStatic("Loading models...", id="status", classes="status-text")

                # Right panel - model details
                with Vertical(classes="model-details-panel"):
                    yield StyledStatic("Model Details", classes="panel-title")
                    yield RichLog(
                        id="model-details",
                        classes="model-details-content",
                        auto_scroll=False,
                        markup=True,
                        wrap=True
                    )

            with Horizontal(classes="button-container"):
                yield StyledButton("Refresh", id="refresh-models", variant="primary")
                yield StyledButton("Back", id="back-button", variant="primary")

        yield Footer()

    async def on_mount(self) -> None:
        """Initialize the screen when mounted."""
        await self.load_models()
        # Display initial guidance message
        details_widget = self.query_one("#model-details", RichLog)
        details_widget.write("[dim cyan]Select a model from the list to view details[/dim cyan]")

    async def action_refresh(self) -> None:
        """Refresh model data."""
        await self.load_models()

    async def action_focus_search(self) -> None:
        """Focus the filter input."""
        filter_input = self.query_one("#model-filter", Input)
        filter_input.focus()

    async def action_select_model(self) -> None:
        """Select the currently highlighted model."""
        model_list = self.query_one("#model-list", ListView)
        if model_list.highlighted_child:
            # Get the highlighted index and trigger selection manually
            selected_index = model_list.index
            model_data = self.model_index_map.get(selected_index)
            if model_data:
                self.selected_model = model_data
                await self.display_model_details()

    async def load_models(self) -> None:
        """Load available models from OpenRouter."""
        try:
            status_widget = self.query_one("#status", Static)
            status_widget.update("[cyan]Loading models...[/cyan]")
            status_widget.add_class("loading-text")

            # Import and create OpenRouter client
            from python.modules.ai.openrouter_client import OpenRouterClient

            client = OpenRouterClient()
            self.models = client.get_available_models()
            self.filtered_models = self.models.copy()

            await self.populate_model_list()

            status_widget.remove_class("loading-text")
            status_widget.add_class("success-text")
            status_widget.update(f"[green]Loaded {len(self.models)} models[/green]")

        except Exception as e:
            status_widget = self.query_one("#status", Static)
            status_widget.remove_class("loading-text")
            status_widget.add_class("error-text")
            status_widget.update(f"[red]Error loading models: {str(e)}[/red]")

    async def populate_model_list(self) -> None:
        """Populate the model list with filtered models."""
        model_list = self.query_one("#model-list", ListView)
        await model_list.clear()
        self.model_index_map.clear()

        for index, model in enumerate(self.filtered_models):
            model_id = model.get('id', 'Unknown')
            model_name = model.get('name', model_id)

            # Create a display name that fits well in the list
            display_name = model_id
            if model_name and model_name != model_id:
                # For list display, keep it concise but show in details
                if len(model_name) <= 50:
                    display_name += f"\n{model_name}"
                else:
                    display_name += f"\n{model_name[:47]}..."

            list_item = ListItem(Label(display_name), classes="model-item")
            self.model_index_map[index] = model
            await model_list.append(list_item)

    async def on_input_changed(self, event: Input.Changed) -> None:
        """Handle filter input changes."""
        if event.input.id == "model-filter":
            filter_text = event.value.lower()

            if not filter_text:
                self.filtered_models = self.models.copy()
            else:
                self.filtered_models = [
                    model for model in self.models
                    if filter_text in model.get('id', '').lower() or
                       filter_text in model.get('name', '').lower()
                ]

            await self.populate_model_list()

            # Update status
            status_widget = self.query_one("#status", Static)
            if self.filtered_models:
                status_widget.update(f"[cyan]Showing {len(self.filtered_models)} of {len(self.models)} models[/cyan]")
                status_widget.remove_class("error-text")
                status_widget.add_class("success-text")
            else:
                status_widget.update("[yellow]No models match your filter[/yellow]")
                status_widget.remove_class("success-text")
                status_widget.add_class("error-text")

    async def on_list_view_selected(self, _event: ListView.Selected) -> None:
        """Handle model selection."""
        model_list = self.query_one("#model-list", ListView)
        if model_list.highlighted_child:
            # Get the index of the highlighted item
            selected_index = model_list.index

            # Get the model data from our mapping
            model_data = self.model_index_map.get(selected_index)
            if model_data:
                self.selected_model = model_data
                await self.display_model_details()

    async def display_model_details(self) -> None:
        """Display detailed information about the selected model."""
        if not self.selected_model:
            return

        model = self.selected_model

        # Format model details with professional styling
        details = f"[bold cyan]{model.get('id', 'Unknown Model')}[/bold cyan]\n\n"

        if model.get('name'):
            details += f"[bold]Display Name:[/bold]\n{model['name']}\n\n"

        if model.get('description'):
            # Format description for better display in RichLog
            description = model['description']
            # Rich will handle text wrapping automatically with wrap=True
            details += f"[bold]Description:[/bold]\n{description}\n\n"

        # Context length
        if model.get('context_length'):
            context = model['context_length']
            details += f"[bold]Context Length:[/bold] [green]{context:,} tokens[/green]\n\n"

        # Pricing information
        if model.get('pricing'):
            pricing = model['pricing']
            details += "[bold cyan]Pricing Information:[/bold cyan]\n"
            if pricing.get('prompt'):
                details += f"  Prompt: [yellow]${pricing['prompt']}[/yellow] per 1K tokens\n"
            if pricing.get('completion'):
                details += f"  Completion: [yellow]${pricing['completion']}[/yellow] per 1K tokens\n"
            details += "\n"

        # Top provider
        if model.get('top_provider'):
            provider = model['top_provider']
            details += "[bold cyan]Top Provider:[/bold cyan]\n"
            if provider.get('name'):
                details += f"  Name: [white]{provider['name']}[/white]\n"
            if provider.get('max_completion_tokens'):
                details += f"  Max Completion: [green]{provider['max_completion_tokens']:,} tokens[/green]\n"
            details += "\n"

        # Architecture info
        if model.get('architecture'):
            arch = model['architecture']
            details += "[bold cyan]Architecture:[/bold cyan]\n"
            if arch.get('modality'):
                details += f"  Modality: [white]{arch['modality']}[/white]\n"
            if arch.get('tokenizer'):
                details += f"  Tokenizer: [white]{arch['tokenizer']}[/white]\n"
            if arch.get('instruct_type'):
                details += f"  Instruct Type: [white]{arch['instruct_type']}[/white]\n"
            details += "\n"

        details += "[dim]Information from OpenRouter API[/dim]"

        details_widget = self.query_one("#model-details", RichLog)
        details_widget.clear()
        details_widget.write(details)

    async def on_button_pressed(self, event) -> None:
        """Handle button presses."""
        if event.button.id == "refresh-models":
            await self.action_refresh()
        elif event.button.id == "back-button":
            await self.action_back()

    def get_help_text(self) -> str:
        """Get help text for model browser screen."""
        return """
Model Browser Help:
• / - Focus search filter
• R or Ctrl+R - Refresh model list
• Enter - Select highlighted model
• ↑↓ - Navigate model list
• Escape - Go back to main interface
• Ctrl+Q - Quit application
• F1 - Show this help

Filter by typing model names (gpt, claude, llama, etc.)
Select models to view detailed pricing and specifications.
        """.strip()
