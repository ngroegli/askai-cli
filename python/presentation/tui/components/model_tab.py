"""
Model Browser Tab Component.
Handles AI model browsing and selection.
"""

from typing import TYPE_CHECKING
from .base_tab import BaseTabComponent

from ..common import (
    Static, Button, ListView, ListItem, Label, Input,
    Vertical, Horizontal, VerticalScroll, Message, StatusMixin
)

try:
    from modules.ai import OpenRouterClient
except ImportError:
    if not TYPE_CHECKING:
        OpenRouterClient = object

if TYPE_CHECKING:
    from textual.widgets import Static, Button, ListView, ListItem, Label, Input
    from textual.containers import Vertical, Horizontal, VerticalScroll
    from textual.message import Message
    from modules.ai import OpenRouterClient


class ModelTab(BaseTabComponent, StatusMixin):
    """Model Browser tab component."""

    class ModelSelected(Message):
        """Message sent when a model is selected."""
        def __init__(self, model_data: dict) -> None:
            self.model_data = model_data
            super().__init__()

    def __init__(self, *args, **kwargs):
        """Initialize the model tab."""
        super().__init__("Model Browser", *args, **kwargs)
        self.models = []
        self.models_data = []  # Store the full model data from OpenRouter
        self.selected_model = None
        self.filter_text = ""
        self.openrouter_client = None
        self._initialize_openrouter_client()

    def compose(self):
        """Compose the model browser interface."""
        yield Static("Model Browser", classes="panel-title")

        with Horizontal(classes="model-browser-container"):
            # Left panel - Model list
            with Vertical(classes="model-list-panel"):
                yield Static("Available Models", classes="panel-subtitle")

                # Search input
                yield Static("Search:")
                yield Input(placeholder="Search models...", id="model-search")

                # Scrollable model list container with border
                with VerticalScroll(id="model-list-scroll", classes="pattern-list-box"):
                    yield ListView(id="model-list")

                # Action buttons
                with Horizontal(classes="button-row"):
                    yield Button("Refresh", variant="default", id="refresh-models-button")

            # Right panel - Model details
            with Vertical(classes="model-details-panel"):
                yield Static("Model Details", classes="panel-subtitle")

                # Scrollable model details container with border
                with VerticalScroll(id="model-details-scroll", classes="pattern-details-box"):
                    yield Static("Select a model to view details", id="model-info")

                # Status
                yield Static("✅ Ready to browse models", id="status-display", classes="status-text")

    async def initialize(self):
        """Initialize the model browser."""
        # Use call_after_refresh to ensure widgets are properly mounted
        self.call_after_refresh(self._load_models)

    def _initialize_openrouter_client(self):
        """Initialize the OpenRouter client with configuration."""
        try:
            # Use the same pattern as CLI - let OpenRouterClient load its own config
            self.openrouter_client = OpenRouterClient()
        except Exception:
            self.openrouter_client = None
            # We'll handle this in the UI by showing an error message

    def _load_models(self):
        """Load models into the list."""
        try:
            # Query for the widgets using their IDs
            status_display = self.query_one("#status-display", Static)

            status_display.update("🔄 Loading models from OpenRouter...")

            if not self.openrouter_client:
                status_display.update("❌ OpenRouter client not configured")
                return

            # Load models from OpenRouter API
            try:
                models_data = self.openrouter_client.get_available_models()
                if models_data:
                    self.models_data = models_data
                    self._update_model_list(models_data)
                    status_display.update(f"✅ Loaded {len(models_data)} models from OpenRouter")
                else:
                    status_display.update("❌ No models available from OpenRouter")
            except Exception as api_error:
                status_display.update(f"❌ Error loading from OpenRouter: {str(api_error)}")
                # Fall back to sample models for now
                self._load_fallback_models(status_display)
        except Exception:
            try:
                status_display = self.query_one("#status-display", Static)
                status_display.update("❌ Error loading models: Widget not available")
            except Exception:
                pass  # Widget not available yet

    def _load_fallback_models(self, status_display):
        """Load fallback models when API is not available."""
        fallback_models = [
            {
                'id': 'openai/gpt-4o',
                'name': 'GPT-4o',
                'description': 'OpenAI GPT-4 Optimized',
                'context_length': 128000,
                'pricing': {'prompt': 0.005, 'completion': 0.015}
            },
            {
                'id': 'anthropic/claude-3-opus',
                'name': 'Claude 3 Opus',
                'description': 'Anthropic Claude 3 Opus',
                'context_length': 200000,
                'pricing': {'prompt': 0.015, 'completion': 0.075}
            },
            {
                'id': 'google/gemma-3-27b-it',
                'name': 'Gemma 3 27B IT',
                'description': 'Google Gemma 3 27B Instruction Tuned',
                'context_length': 8192,
                'pricing': {'prompt': 0.0001, 'completion': 0.0001}
            },
            {
                'id': 'meta-llama/llama-3.1-405b-instruct',
                'name': 'Llama 3.1 405B',
                'description': 'Meta Llama 3.1 405B Instruct',
                'context_length': 131072,
                'pricing': {'prompt': 0.003, 'completion': 0.003}
            }
        ]

        self.models_data = fallback_models
        self._update_model_list(fallback_models)
        status_display.update(f"⚠️ Using fallback models ({len(fallback_models)} available)")

    def _update_model_list(self, models):
        """Update the model list display."""
        try:
            model_list = self.query_one("#model-list", ListView)
            model_list.clear()

            for model in models:
                model_id = model.get('id', 'unknown')
                name = model.get('name', 'Unknown')
                context = model.get('context_length', 0)

                # Format context length nicely
                if context >= 1000:
                    context_str = f"{context//1000}K"
                else:
                    context_str = str(context)

                label = f"🤖 {name} ({context_str} ctx)"
                list_item = ListItem(Label(label), name=model_id)
                model_list.append(list_item)
        except Exception:
            pass  # Widget not available yet

    async def on_input_changed(self, event) -> None:
        """Handle search input changes."""
        if event.input.id == "model-search":
            search_term = event.value.lower()
            if search_term:
                filtered_models = [
                    model for model in self.models_data
                    if search_term in model.get('name', '').lower() or
                       search_term in model.get('id', '').lower() or
                       search_term in model.get('description', '').lower()
                ]
            else:
                filtered_models = self.models_data

            self._update_model_list(filtered_models)

    async def on_list_view_selected(self, event) -> None:
        """Handle model selection."""
        if event.list_view.id == "model-list" and event.item:
            model_id = event.item.name
            await self._display_model_info(model_id)

    async def _display_model_info(self, model_id: str):
        """Display information about the selected model."""
        try:
            model_info = self.query_one("#model-info", Static)
        except Exception:
            return  # Widget not available yet

        # Find the selected model
        selected_model = next((m for m in self.models_data if m.get('id') == model_id), None)

        if selected_model:
            self.selected_model = selected_model

            name = selected_model.get('name', 'Unknown')
            model_id = selected_model.get('id', 'unknown')
            description = selected_model.get('description', 'No description available')
            context_length = selected_model.get('context_length', 0)
            pricing = selected_model.get('pricing', {})

            info_text = f"**{name}**\n\n"
            info_text += f"🆔 ID: {model_id}\n"
            info_text += f"📄 Description: {description}\n"
            info_text += f"📏 Context Length: {context_length:,} tokens\n"

            if pricing:
                prompt_price = pricing.get('prompt', 0)
                completion_price = pricing.get('completion', 0)

                # Convert string prices to float for formatting
                try:
                    prompt_price_float = float(prompt_price) if prompt_price else 0.0
                    completion_price_float = float(completion_price) if completion_price else 0.0
                except (ValueError, TypeError):
                    prompt_price_float = 0.0
                    completion_price_float = 0.0

                info_text += "\n💰 Pricing:\n"
                info_text += f"  📥 Prompt: ${prompt_price_float:.6f} per 1K tokens\n"
                info_text += f"  📤 Completion: ${completion_price_float:.6f} per 1K tokens\n"

            model_info.update(info_text)
        else:
            model_info.update("❌ Model not found")

    async def on_button_pressed(self, event) -> None:
        """Handle button presses."""
        if event.button.id == "refresh-models-button":
            self._load_models()

    def update_status(self, message: str) -> None:
        """Update the status display."""
        # Use the inherited method from StatusMixin
        super().update_status(message)
