"""
Pattern Browser Tab Component.
Handles pattern browsing, selection, and execution.
"""

from typing import Optional, TYPE_CHECKING
from .base_tab import BaseTabComponent

from ..common import (
    Static, Button, ListView, ListItem, Label, TextArea, Input,
    Vertical, Horizontal, VerticalScroll, Message, StatusMixin
)

if TYPE_CHECKING:
    from textual.widgets import Static, Button, ListView, ListItem, Label, TextArea, Input
    from textual.containers import Vertical, Horizontal, VerticalScroll
    from textual.message import Message


class PatternTab(BaseTabComponent, StatusMixin):
    """Pattern Browser tab component."""

    class PatternSelected(Message):
        """Message sent when a pattern is selected for execution."""
        def __init__(self, pattern_data: dict, pattern_input: Optional[dict] = None) -> None:
            self.pattern_data = pattern_data
            self.pattern_input = pattern_input or {}
            super().__init__()

    def __init__(self, *args, pattern_manager=None, **kwargs):
        super().__init__("Pattern Browser", *args, **kwargs)
        self.pattern_manager = pattern_manager
        self.selected_pattern = None
        self.patterns_data = {}  # Store pattern data by pattern_id

    def compose(self):
        """Compose the pattern browser interface."""
        yield Static("Pattern Browser", classes="panel-title")

        with Horizontal(classes="pattern-browser-container"):
            # Left panel - Pattern list
            with Vertical(classes="pattern-list-panel"):
                yield Static("Available Patterns", classes="panel-subtitle")

                # Scrollable pattern list container with border
                with VerticalScroll(id="pattern-list-scroll", classes="pattern-list-box"):
                    yield ListView(id="pattern-list")

                # Action buttons
                with Horizontal(classes="button-row"):
                    yield Button("Execute Pattern", variant="primary", id="execute-pattern-button")
                    yield Button("Refresh", variant="default", id="refresh-button")

            # Right panel - Pattern details and execution
            with Vertical(classes="pattern-details-panel"):
                yield Static("Pattern Details", classes="panel-subtitle")

                # Scrollable pattern details container with border
                with VerticalScroll(id="pattern-details-scroll", classes="pattern-details-box"):
                    yield Static("Select a pattern to view details", id="pattern-info")

                    # Dynamic input fields container
                    yield Static("Pattern Inputs:", id="inputs-label", classes="hidden")
                    yield Vertical(id="pattern-inputs-container")

                # Status
                yield Static("✅ Ready to browse patterns", id="status-display", classes="status-text")

    async def initialize(self):
        """Initialize the pattern browser."""
        # Use call_after_refresh to ensure widgets are properly mounted
        self.call_after_refresh(self._load_patterns)

    def _load_patterns(self):
        """Load patterns into the list."""
        if not self.pattern_manager:
            return

        try:
            # Query for the widgets using their IDs
            pattern_list = self.query_one("#pattern-list", ListView)
            status_display = self.query_one("#status-display", Static)

            patterns = self.pattern_manager.list_patterns()
            pattern_list.clear()

            for pattern in patterns:
                name = pattern.get('name', 'Unknown')
                pattern_id = pattern.get('pattern_id', name)
                is_private = pattern.get('is_private', False)

                # Create display label
                source_indicator = "🔒" if is_private else "📦"
                label = f"{source_indicator} {name}"

                list_item = ListItem(Label(label), name=pattern_id)
                # Store pattern data in our mapping
                self.patterns_data[pattern_id] = pattern
                pattern_list.append(list_item)

            status_display.update(f"✅ Loaded {len(patterns)} patterns")

        except Exception as e:
            try:
                status_display = self.query_one("#status-display", Static)
                status_display.update(f"❌ Error loading patterns: {e}")
            except Exception:
                pass  # Widget not available yet

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle pattern selection."""
        try:
            # Get the pattern data from our mapping using the ListItem's name
            item_name = getattr(event.item, 'name', None)
            pattern_data = self.patterns_data.get(item_name)

            if pattern_data:
                self.selected_pattern = pattern_data
                await self._display_pattern_info()
            else:
                try:
                    pattern_info = self.query_one("#pattern-info", Static)
                    pattern_info.update("Pattern details not available.")
                except Exception:
                    pass

        except Exception as e:
            try:
                pattern_info = self.query_one("#pattern-info", Static)
                pattern_info.update(f"Error displaying pattern: {str(e)}")
            except Exception:
                pass

    async def _display_pattern_info(self):
        """Display information about the selected pattern."""
        if not self.selected_pattern:
            return

        try:
            pattern_info = self.query_one("#pattern-info", Static)
            inputs_container = self.query_one("#pattern-inputs-container", Vertical)
            inputs_label = self.query_one("#inputs-label", Static)
        except Exception:
            return  # Widget not available yet

        pattern = self.selected_pattern
        name = pattern.get('name', 'Unknown')
        source = pattern.get('source', 'built-in')
        is_private = pattern.get('is_private', False)

        # Get full pattern content for more details
        pattern_id = pattern.get('pattern_id', name)
        try:
            if self.pattern_manager:
                pattern_content = self.pattern_manager.get_pattern_content(pattern_id)
                if pattern_content:
                    # Get description from pattern content first, fallback to pattern metadata
                    description = pattern_content.get(
                        'description',
                        pattern.get('description', 'No description available')
                    )
                    inputs = pattern_content.get('inputs', [])
                    outputs = pattern_content.get('outputs', [])

                    info_text = f"**{name}**\n\n"
                    info_text += f"📄 Description: {description}\n"
                    info_text += f"🏷️ Source: {source}\n"
                    info_text += f"🔒 Private: {'Yes' if is_private else 'No'}\n"

                    if inputs:
                        info_text += "\n📥 Inputs:\n"
                        for inp in inputs:
                            # Handle both dict and object inputs
                            if isinstance(inp, dict):
                                inp_name = inp.get('name', 'unknown')
                                inp_desc = inp.get('description', 'No description')
                                inp_required = inp.get('required', False)
                            else:
                                # Handle object inputs
                                inp_name = getattr(inp, 'name', 'unknown')
                                inp_desc = getattr(inp, 'description', 'No description')
                                inp_required = getattr(inp, 'required', False)

                            req_indicator = "✅" if inp_required else "⚪"
                            info_text += f"  {req_indicator} {inp_name}: {inp_desc}\n"

                    if outputs:
                        info_text += "\n📤 Outputs:\n"
                        for out in outputs:
                            # Handle both dict and object outputs
                            if isinstance(out, dict):
                                out_type = out.get('type', out.get('name', 'text'))
                                out_desc = out.get('description', 'No description')
                            else:
                                # Handle object outputs
                                out_type = getattr(out, 'type', getattr(out, 'name', 'text'))
                                out_desc = getattr(out, 'description', 'No description')

                            info_text += f"  📄 {out_type}: {out_desc}\n"

                    pattern_info.update(info_text)

                    # Create dynamic input fields
                    await self._create_input_fields(inputs, inputs_container, inputs_label)
                else:
                    pattern_info.update("❌ Could not load pattern details")
                    inputs_label.add_class("hidden")
        except Exception as e:
            pattern_info.update(f"❌ Error loading pattern details: {e}")
            inputs_label.add_class("hidden")

    async def _create_input_fields(self, inputs, inputs_container, inputs_label):
        """Create dynamic input fields based on pattern inputs."""
        # Clear existing input fields
        await inputs_container.remove_children()

        if not inputs:
            inputs_label.add_class("hidden")
            return

        # Show inputs section
        inputs_label.remove_class("hidden")

        for inp in inputs:
            # Handle both dict and object inputs
            if isinstance(inp, dict):
                inp_name = inp.get('name', 'unknown')
                inp_desc = inp.get('description', 'No description')
                inp_required = inp.get('required', False)
                inp_type = inp.get('type', 'text')
            else:
                # Handle object inputs
                inp_name = getattr(inp, 'name', 'unknown')
                inp_desc = getattr(inp, 'description', 'No description')
                inp_required = getattr(inp, 'required', False)
                inp_type = getattr(inp, 'type', 'text')

            # Create label with requirement indicator
            req_indicator = "* " if inp_required else ""
            label_text = f"{req_indicator}{inp_name}"
            if inp_desc and inp_desc != 'No description':
                label_text += f" - {inp_desc}"

            # Create input field
            if inp_type in ['text', 'string']:
                input_widget = Input(placeholder=f"Enter {inp_name}", id=f"input-{inp_name}")
            elif inp_type in ['textarea', 'multiline']:
                input_widget = TextArea(placeholder=f"Enter {inp_name}", id=f"input-{inp_name}")
            else:
                # Default to text input
                input_widget = Input(placeholder=f"Enter {inp_name}", id=f"input-{inp_name}")

            # Add to container
            await inputs_container.mount(Static(label_text, classes="input-label"))
            await inputs_container.mount(input_widget)

    async def on_button_pressed(self, event) -> None:
        """Handle button presses."""
        if event.button.id == "execute-pattern-button":
            await self._execute_pattern()
        elif event.button.id == "refresh-button":
            self._load_patterns()

    async def _execute_pattern(self) -> None:
        """Execute the selected pattern with collected input values."""
        if not self.selected_pattern:
            try:
                status_display = self.query_one("#status-display", Static)
                status_display.update("❌ Please select a pattern first")
            except Exception:
                pass
            return

        try:
            status_display = self.query_one("#status-display", Static)
            status_display.update("🔄 Collecting inputs...")
        except Exception:
            pass

        # Collect input values from dynamic fields
        pattern_inputs = {}
        try:
            # Get pattern content to know what inputs we expect
            pattern_id = self.selected_pattern.get('pattern_id', self.selected_pattern.get('name', ''))
            if self.pattern_manager:
                pattern_content = self.pattern_manager.get_pattern_content(pattern_id)
                if pattern_content:
                    expected_inputs = pattern_content.get('inputs', [])

                    for inp in expected_inputs:
                        # Handle both dict and object inputs
                        if isinstance(inp, dict):
                            inp_name = inp.get('name', 'unknown')
                            inp_required = inp.get('required', False)
                        else:
                            inp_name = getattr(inp, 'name', 'unknown')
                            inp_required = getattr(inp, 'required', False)

                        # Try to find the input widget
                        try:
                            input_widget = self.query_one(f"#input-{inp_name}")
                            value = ""

                            # Handle different widget types
                            if isinstance(input_widget, Input):
                                value = input_widget.value.strip()
                            elif isinstance(input_widget, TextArea):
                                value = input_widget.text.strip()
                            else:
                                # Fallback - try both attributes safely
                                value = getattr(input_widget, 'value', getattr(input_widget, 'text', '')).strip()

                            if inp_required and not value:
                                status_display.update(f"❌ Required field '{inp_name}' is empty")
                                return

                            if value:  # Only include non-empty values
                                pattern_inputs[inp_name] = value

                        except Exception:
                            if inp_required:
                                status_display.update(f"❌ Could not read required field '{inp_name}'")
                                return
        except Exception:
            pass

        try:
            status_display.update("🔄 Executing pattern...")
        except Exception:
            pass

        # Emit message to parent for actual execution
        self.post_message(self.PatternSelected(self.selected_pattern, pattern_inputs))

    async def _use_pattern(self) -> None:
        """Legacy method - redirect to new execution method."""
        await self._execute_pattern()

