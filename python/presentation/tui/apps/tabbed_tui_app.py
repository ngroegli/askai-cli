#!/usr/bin/env python3
"""
Tabbed TUI Application that integrates all workflows in a single tabbed interface.
Starts directly with question builder and provides tab navigation.
"""

from typing import Optional, TYPE_CHECKING

try:
    from textual.app import App
    from textual.containers import Vertical, Horizontal
    from textual.widgets import Header, Footer, Static, Button, TextArea, Select, TabbedContent, TabPane, ListView, ListItem, Label, Input
    from textual.binding import Binding
    from textual import work
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    if not TYPE_CHECKING:
        App = object
        Vertical = object
        Horizontal = object
        Header = object
        Footer = object
        Static = object
        Button = object
        TextArea = object
        Select = object
        TabbedContent = object
        TabPane = object
        ListView = object
        ListItem = object
        Label = object
        Binding = object
        work = lambda x: x

# Type imports for static analysis
if TYPE_CHECKING:
    from textual.app import App
    from textual.containers import Vertical, Horizontal
    from textual.widgets import Header, Footer, Static, Button, TextArea, Select, TabbedContent, TabPane, ListView, ListItem, Label
    from textual.binding import Binding
    from textual import work


if TEXTUAL_AVAILABLE:
    class TabbedTUIApp(App):
        """Tabbed TUI application with integrated workflows."""

        BINDINGS = [
            ("ctrl+q", "quit", "Quit"),
            ("f1", "help", "Help"),
            ("ctrl+r", "execute_question", "Execute"),
            ("ctrl+1", "focus_tab_1", "Question"),
            ("ctrl+2", "focus_tab_2", "Patterns"),
            ("ctrl+3", "focus_tab_3", "Chat"),
            ("ctrl+4", "focus_tab_4", "Settings"),
            ("/", "focus_pattern_filter", "Filter"),
        ]

        CSS = """
        TabbedContent {
            background: $surface;
        }

        TabPane {
            padding: 1;
        }

        #question-input {
            height: 8;
            margin: 1 0;
        }

        #format-select {
            width: 60%;
            margin: 1;
        }

        #status {
            color: $accent;
            text-style: italic;
            height: 2;
            text-align: center;
        }

        Button {
            margin: 1;
        }

        .title {
            text-style: bold;
            color: $primary;
            text-align: center;
            margin: 1;
        }

        .center-content {
            text-align: center;
            color: $text-muted;
            margin: 2;
        }

        /* Pattern Browser Styles */
        #pattern-list-container {
            width: 50%;
            border-right: thick $surface;
            padding: 1;
        }

        #pattern-details-container {
            width: 50%;
            padding: 1;
        }

        .pattern-list {
            height: 1fr;
            border: solid #87CEEB;
            margin-bottom: 1;
            background: $background;
        }

        .pattern-browser-container {
            height: 1fr;
            padding: 2;
        }

        .pattern-list-panel {
            width: 1fr;
            border: round #00FFFF;
            padding: 2;
            margin-right: 2;
            background: $surface;
        }

        .pattern-details-panel {
            width: 2fr;
            border: round #00FFFF;
            padding: 2;
            background: $surface;
        }

                .model-details-content {
            height: 1fr;
            padding: 2;
            background: $background;
            overflow-y: auto;
            border: solid #87CEEB;
        }

        #pattern-info {
            height: 1fr;
            margin: 0;
            padding: 2;
            background: $background;
            overflow-y: auto;
            border: solid #87CEEB;
        }

        #pattern-actions {
            height: auto;
        }

        /* Additional styles for pattern screens */
        .subtitle {
            text-style: bold;
            margin: 1 0;
        }

        .input-desc {
            color: $text-muted;
            margin-bottom: 1;
        }

        Input {
            margin: 1 0;
        }

        #execution-status {
            color: $accent;
            text-style: italic;
            height: 2;
            text-align: center;
            margin: 1;
        }

        /* Pattern Filter Styles */
        .filter-input {
            margin: 1 0;
            height: 3;
        }

        .status-text {
            color: $text-muted;
            text-align: center;
            margin: 1 0;
        }

        .loading-text {
            color: $accent;
            text-style: italic;
        }

        .success-text {
            color: $success;
        }

        .error-text {
            color: $error;
        }
        """

        def __init__(self, pattern_manager=None, chat_manager=None, question_processor=None, **kwargs):
            super().__init__(**kwargs)
            self.pattern_manager = pattern_manager
            self.chat_manager = chat_manager
            self.question_processor = question_processor
            self.question_text = ""
            self.selected_format = "md"
            self.loading_active = False

            # Pattern browser state
            self.patterns = []
            self.filtered_patterns = []
            self.selected_pattern = None
            self.selected_pattern_data = None

        def compose(self):
            """Compose the tabbed interface."""
            yield Header(show_clock=True)

            with TabbedContent(initial="question-tab"):
                # Question Builder Tab
                with TabPane("🤔 Question Builder", id="question-tab"):
                    yield Static("Ask questions with AI assistance", classes="title")
                    yield Static("Type your question below:")
                    yield TextArea(
                        text="",
                        placeholder="Enter your question here...",
                        id="question-input"
                    )

                    yield Static("Select output format:")
                    yield Select(
                        options=[
                            ("md", "Markdown (default)"),
                            ("rawtext", "Raw Text"),
                            ("json", "JSON")
                        ],
                        id="format-select"
                    )

                    yield Static("", id="status")

                    with Horizontal():
                        yield Button("Execute Question", id="execute", variant="success")
                        yield Button("Clear", id="clear", variant="warning")

                # Pattern Browser Tab
                with TabPane("📋 Pattern Browser", id="pattern-tab"):
                    with Horizontal(classes="pattern-browser-container"):
                        # Left side - Pattern List with Filter
                        with Vertical(classes="pattern-list-panel"):
                            yield Static("📋 Available Patterns", classes="panel-title")
                            yield Input(
                                placeholder="🔍 Filter patterns (e.g., log, data, analysis)...",
                                id="pattern-filter",
                                classes="filter-input"
                            )
                            yield ListView(id="pattern-list", classes="pattern-list")
                            yield Static("Loading patterns...", id="pattern-status", classes="status-text")

                        # Right side - Pattern Details/Actions
                        with Vertical(classes="pattern-details-panel"):
                            yield Static("📖 Pattern Details", classes="panel-title")
                            yield Static(
                                "💡 Select a pattern from the list to view detailed information.\n\n"
                                "Use the filter box to search by pattern name or description.\n"
                                "Press '/' to focus the search box quickly.",
                                id="pattern-info",
                                classes="pattern-details-content"
                            )

                            with Horizontal(classes="button-container"):
                                yield Button("View", id="view-pattern", variant="primary", disabled=True)
                                yield Button("Execute", id="execute-pattern", variant="success", disabled=True)

                # Chat Manager Tab
                with TabPane("💬 Chat Manager", id="chat-tab"):
                    yield Static("Manage your chat history", classes="title")
                    yield Static("Chat management interface will be integrated here", classes="center-content")
                    yield Button("Browse Chats", id="browse-chats", variant="primary")

                # Settings Tab
                with TabPane("⚙️ Settings", id="settings-tab"):
                    yield Static("Application configuration", classes="title")
                    yield Static("Settings and system management", classes="center-content")
                    yield Button("Open Settings", id="open-settings", variant="primary")

                # Admin/System Tab
                with TabPane("🔧 System", id="system-tab"):
                    yield Static("System Information & Management", classes="title")
                    with Horizontal():
                        with Vertical():
                            yield Static("🤖 AI Models", classes="subtitle")
                            yield Button("Browse Available Models", id="browse-models", variant="primary")
                            yield Static("View all OpenRouter models and their capabilities", classes="center-content")
                        with Vertical():
                            yield Static("💳 Account", classes="subtitle")
                            yield Button("Check Credit Balance", id="check-credits", variant="success")
                            yield Static("View your OpenRouter account balance and usage", classes="center-content")

            yield Footer()

        def on_mount(self):
            """Called when mounted."""
            self.call_after_refresh(self.setup_defaults)
            self.call_after_refresh(self.load_patterns)

        def setup_defaults(self):
            """Set up default values and focus after UI is ready."""
            try:
                # Focus the input first
                question_input = self.query_one("#question-input", TextArea)
                question_input.focus()

                # Set default format selection with a small delay
                self.call_later(self.set_default_format)

                status = self.query_one("#status", Static)
                status.update("✅ Ready! Format: Markdown (default)")
            except Exception as e:
                status = self.query_one("#status", Static)
                status.update(f"❌ Setup failed: {e}")

        def set_default_format(self):
            """Set the default format selection."""
            try:
                format_select = self.query_one("#format-select", Select)
                format_select.value = "md"
            except Exception:
                # Silently fail if widget isn't ready yet
                pass

        def load_patterns(self):
            """Load patterns into the pattern browser."""
            if not self.pattern_manager:
                return

            try:
                # Get patterns from pattern manager
                pattern_data = self.pattern_manager.list_patterns()
                self.patterns = pattern_data
                self.filtered_patterns = self.patterns.copy()

                # Update status
                try:
                    status_widget = self.query_one("#pattern-status", Static)
                    status_widget.update(f"✅ {len(self.patterns)} patterns loaded")
                    status_widget.remove_class("loading-text")
                except Exception:
                    pass  # Status widget might not exist yet

                # Populate the ListView
                self.populate_pattern_list()

            except Exception as e:
                # Handle gracefully if pattern loading fails
                print(f"Error loading patterns: {e}")
                try:
                    status_widget = self.query_one("#pattern-status", Static)
                    status_widget.update(f"❌ Error loading patterns: {e}")
                except Exception:
                    pass

        def populate_pattern_list(self):
            """Populate the pattern list with current filtered patterns."""
            try:
                pattern_list = self.query_one("#pattern-list", ListView)
                pattern_list.clear()

                for pattern in self.filtered_patterns:
                    name = pattern.get('name', 'Unknown')
                    description = pattern.get('description', '')

                    # Add icons based on pattern type/name
                    if 'log' in name.lower() or 'log' in description.lower():
                        icon = "📋"
                    elif 'data' in name.lower() or 'visualization' in name.lower():
                        icon = "📊"
                    elif 'analysis' in name.lower() or 'interpret' in name.lower():
                        icon = "�"
                    elif 'generation' in name.lower() or 'create' in name.lower():
                        icon = "⚡"
                    elif 'summary' in name.lower() or 'summarize' in name.lower():
                        icon = "📝"
                    elif 'query' in name.lower() or 'kql' in name.lower() or 'spl' in name.lower():
                        icon = "🔎"
                    elif 'website' in name.lower() or 'content' in name.lower():
                        icon = "🌐"
                    elif 'image' in name.lower():
                        icon = "🖼️"
                    elif 'market' in name.lower() or 'solution' in name.lower():
                        icon = "💼"
                    else:
                        icon = "�🔒" if pattern.get('is_private', False) else "📦"

                    # Create enhanced label with description if available
                    label = f"{icon} {name}"
                    if description:
                        # Truncate description for list view
                        desc = description[:50] + "..." if len(description) > 50 else description
                        label += f"\n   {desc}"

                    list_item = ListItem(Label(label), name=pattern.get('pattern_id', name), classes="pattern-item")
                    pattern_list.append(list_item)

            except Exception as e:
                print(f"Error populating pattern list: {e}")

        def filter_patterns(self, filter_text: str):
            """Filter patterns based on search text."""
            if not filter_text.strip():
                self.filtered_patterns = self.patterns.copy()
            else:
                filter_lower = filter_text.lower()
                self.filtered_patterns = [
                    pattern for pattern in self.patterns
                    if (filter_lower in pattern.get('name', '').lower() or
                        filter_lower in pattern.get('description', '').lower())
                ]

            # Update the list display
            self.populate_pattern_list()

            # Update status with enhanced feedback
            try:
                status_widget = self.query_one("#pattern-status", Static)
                if filter_text.strip():
                    if self.filtered_patterns:
                        status_widget.update(f"� Showing {len(self.filtered_patterns)} of {len(self.patterns)} patterns")
                        status_widget.remove_class("error-text")
                        status_widget.add_class("success-text")
                    else:
                        status_widget.update("❌ No patterns match your filter")
                        status_widget.remove_class("success-text")
                        status_widget.add_class("error-text")
                else:
                    status_widget.update(f"✅ {len(self.patterns)} patterns loaded")
                    status_widget.remove_class("error-text")
                    status_widget.add_class("success-text")
            except Exception:
                pass

        async def on_list_view_selected(self, event: ListView.Selected) -> None:
            """Handle pattern selection."""
            if event.list_view.id == "pattern-list" and self.filtered_patterns and self.pattern_manager:
                try:
                    # Find the selected pattern from filtered list
                    selected_index = event.list_view.index
                    if selected_index is not None and selected_index < len(self.filtered_patterns):
                        self.selected_pattern = self.filtered_patterns[selected_index]
                        pattern_id = self.selected_pattern.get('pattern_id')

                        if pattern_id:
                            # Load pattern details
                            self.selected_pattern_data = self.pattern_manager.get_pattern_content(pattern_id)
                            await self.update_pattern_info()

                            # Enable action buttons
                            view_btn = self.query_one("#view-pattern", Button)
                            execute_btn = self.query_one("#execute-pattern", Button)
                            view_btn.disabled = False
                            execute_btn.disabled = False

                except Exception as e:
                    print(f"Error selecting pattern: {e}")

        async def update_pattern_info(self):
            """Update the pattern information display."""
            if not self.selected_pattern_data or not self.selected_pattern:
                return

            try:
                pattern_info = self.query_one("#pattern-info", Static)

                # Build info display
                name = self.selected_pattern.get('name', 'Unknown')
                source = self.selected_pattern.get('source', 'built-in')

                info_text = f"📋 Pattern: {name}\n"
                info_text += f"📁 Source: {source}\n"

                if 'configuration' in self.selected_pattern_data:
                    config = self.selected_pattern_data['configuration']
                    if config and hasattr(config, 'purpose'):
                        purpose = config.purpose
                        if hasattr(purpose, 'description'):
                            info_text += f"📝 Purpose: {purpose.description[:100]}...\n"

                # Show input requirements
                inputs = self.selected_pattern_data.get('inputs', [])
                if inputs:
                    required_inputs = [inp for inp in inputs if inp.required]
                    optional_inputs = [inp for inp in inputs if not inp.required]

                    info_text += f"\n📥 Inputs:\n"
                    info_text += f"  Required: {len(required_inputs)}\n"
                    info_text += f"  Optional: {len(optional_inputs)}\n"

                pattern_info.update(info_text)

            except Exception as e:
                print(f"Error updating pattern info: {e}")

        async def on_text_area_changed(self, event: TextArea.Changed) -> None:
            """Handle text area changes."""
            if event.text_area.id == "question-input":
                self.question_text = event.text_area.text
                status = self.query_one("#status", Static)
                status.update(f"Question updated: {len(self.question_text)} chars")

        async def on_select_changed(self, event: Select.Changed) -> None:
            """Handle format selection changes."""
            if event.select.id == "format-select":
                self.selected_format = str(event.value)
                status = self.query_one("#status", Static)
                format_names = {"md": "Markdown", "rawtext": "Raw Text", "json": "JSON"}
                format_name = format_names.get(self.selected_format, self.selected_format)
                status.update(f"📝 Format selected: {format_name}")

        async def on_button_pressed(self, event: Button.Pressed) -> None:
            """Handle button presses."""
            if event.button.id == "execute":
                await self.execute_question_action()
            elif event.button.id == "clear":
                await self.action_clear_question()
            elif event.button.id == "view-pattern":
                await self.action_view_pattern()
            elif event.button.id == "execute-pattern":
                await self.action_execute_pattern()
            elif event.button.id == "browse-chats":
                await self.action_browse_chats()
            elif event.button.id == "open-settings":
                await self.action_open_settings()
            elif event.button.id == "browse-models":
                await self.action_browse_models()
            elif event.button.id == "check-credits":
                await self.action_check_credits()

        async def on_input_changed(self, event: Input.Changed) -> None:
            """Handle input changes for filtering."""
            if event.input.id == "pattern-filter":
                # Filter patterns as user types
                self.filter_patterns(event.value)

        async def execute_question_action(self) -> None:
            """Execute the question with loading indication."""
            if not self.question_text.strip():
                status = self.query_one("#status", Static)
                status.update("❌ Please enter a question first")
                return

            if not self.question_processor:
                status = self.query_one("#status", Static)
                status.update("❌ Question processor not available")
                return

            # Start the loading animation
            self.start_loading_animation()

            # Disable the execute button during processing
            execute_btn = self.query_one("#execute", Button)
            execute_btn.disabled = True

            try:
                # Execute the question processing
                response = await self.process_question_async()

                # Stop loading animation
                self.stop_loading_animation()

                # Re-enable the execute button
                execute_btn.disabled = False

                # Show response in dedicated screen
                if response and hasattr(response, 'content'):
                    # Update status first
                    status = self.query_one("#status", Static)
                    status.update("✅ Question executed! Switching to response view...")

                    # Switch to dedicated response screen
                    try:
                        from ..components.loading_screen import create_question_response_screen
                        response_screen_class = create_question_response_screen(
                            response_content=response.content,
                            title="Question Response",
                            app_instance=self
                        )
                        if response_screen_class:
                            # Switch to the response screen
                            response_screen = response_screen_class()
                            await self.push_screen(response_screen)
                    except Exception as screen_error:
                        # Fallback: show in status if screen fails
                        status.update(f"✅ Response ready! Length: {len(response.content)} chars")
                        print(f"Screen error: {screen_error}")
                else:
                    status = self.query_one("#status", Static)
                    status.update("❌ No response received")

            except Exception as e:
                # Stop loading animation
                self.stop_loading_animation()

                # Re-enable the execute button
                execute_btn.disabled = False

                # Show error
                status = self.query_one("#status", Static)
                status.update(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()

        async def action_clear_question(self) -> None:
            """Clear the question input."""
            question_input = self.query_one("#question-input", TextArea)
            question_input.text = ""
            self.question_text = ""

            status = self.query_one("#status", Static)
            status.update("🗑️ Question cleared")

            question_input.focus()

        async def action_view_pattern(self) -> None:
            """View the selected pattern in markdown format."""
            if not self.selected_pattern_data:
                self.notify("No pattern selected", severity="error")
                return

            try:
                # Get the pattern file content
                file_path = self.selected_pattern_data.get('file_path')
                if file_path:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Create a screen to display the pattern content
                    from textual.screen import Screen
                    from textual.widgets import Markdown
                    from textual.containers import ScrollableContainer

                    class PatternViewScreen(Screen):
                        BINDINGS = [
                            ("escape", "go_back", "Back"),
                            ("q", "go_back", "Back"),
                            ("ctrl+e", "execute_pattern", "Execute"),
                        ]

                        def __init__(self, pattern_data, pattern_id, pattern_manager, app_instance):
                            super().__init__()
                            self.pattern_data = pattern_data
                            self.pattern_id = pattern_id
                            self.pattern_manager = pattern_manager
                            self.app_instance = app_instance

                        def compose(self):
                            yield Header()

                            with Vertical():
                                # Pattern title
                                pattern_name = self.pattern_data.get('name', self.pattern_id)
                                yield Static(f"📋 Pattern: {pattern_name}", classes="title")

                                # Action buttons
                                with Horizontal():
                                    yield Button("Back", id="back-btn", variant="default")
                                    yield Button("Execute", id="execute-btn", variant="success")

                                # Pattern content
                                with ScrollableContainer():
                                    yield Markdown(content)

                            yield Footer()

                        async def on_button_pressed(self, event: Button.Pressed):
                            if event.button.id == "back-btn":
                                await self.action_go_back()
                            elif event.button.id == "execute-btn":
                                await self.action_execute_pattern()

                        async def action_go_back(self):
                            """Go back to pattern browser."""
                            self.app.pop_screen()

                        async def action_execute_pattern(self):
                            """Execute the pattern from view screen."""
                            # Close this screen first
                            self.app.pop_screen()
                            # Then trigger pattern execution on the main app
                            await self.app_instance.action_execute_pattern()

                        def on_key(self, event):
                            if event.key == 'escape' or event.key == 'q':
                                self.app.pop_screen()

                    pattern_screen = PatternViewScreen(
                        self.selected_pattern_data,
                        self.selected_pattern.get('pattern_id') if self.selected_pattern else None,
                        self.pattern_manager,
                        self
                    )
                    await self.push_screen(pattern_screen)
                else:
                    self.notify("Pattern file not found", severity="error")

            except Exception as e:
                self.notify(f"Error viewing pattern: {e}", severity="error")

        async def action_execute_pattern(self) -> None:
            """Execute the selected pattern with input form."""
            if not self.selected_pattern_data or not self.selected_pattern:
                self.notify("No pattern selected", severity="error")
                return

            try:
                # Create pattern execution screen
                from textual.screen import Screen
                from textual.widgets import Input

                inputs = self.selected_pattern_data.get('inputs', [])
                pattern_id = self.selected_pattern.get('pattern_id')

                class PatternExecuteScreen(Screen):
                    BINDINGS = [
                        ("escape", "cancel_execute", "Cancel"),
                        ("ctrl+e", "execute_now", "Execute"),
                    ]

                    def __init__(self, pattern_data, pattern_id, pattern_manager, app_instance):
                        super().__init__()
                        self.pattern_data = pattern_data
                        self.pattern_id = pattern_id
                        self.pattern_manager = pattern_manager
                        self.app_instance = app_instance
                        self.input_values = {}
                        self.loading_active = False

                    def compose(self):
                        yield Header()

                        with Vertical():
                            name = self.pattern_data.get('name', self.pattern_id)
                            yield Static(f"Execute Pattern: {name}", classes="title")

                            # Show inputs
                            inputs = self.pattern_data.get('inputs', [])
                            if inputs:
                                yield Static("Pattern Inputs:", classes="subtitle")

                                for inp in inputs:
                                    label = inp.name
                                    if inp.required:
                                        label += " (required)"
                                    else:
                                        label += " (optional)"

                                    yield Static(label)
                                    yield Static(inp.description, classes="input-desc")

                                    placeholder = f"Enter {inp.name}..."
                                    if hasattr(inp, 'default') and inp.default:
                                        placeholder += f" (default: {inp.default})"

                                    yield Input(
                                        placeholder=placeholder,
                                        id=f"input-{inp.name}"
                                    )
                            else:
                                yield Static("This pattern requires no inputs.")

                            # Status for loading animation
                            yield Static("", id="execution-status")

                            with Horizontal():
                                yield Button("Execute", id="execute-now", variant="success")
                                yield Button("Cancel", id="cancel-execute", variant="error")

                        yield Footer()

                    async def on_button_pressed(self, event: Button.Pressed):
                        if event.button.id == "execute-now":
                            await self.action_execute_now()
                        elif event.button.id == "cancel-execute":
                            await self.action_cancel_execute()

                    async def action_execute_now(self):
                        """Execute the pattern with collected inputs."""
                        # Collect input values
                        inputs = self.pattern_data.get('inputs', [])
                        input_values = {}

                        for inp in inputs:
                            try:
                                input_widget = self.query_one(f"#input-{inp.name}", Input)
                                value = input_widget.value.strip()

                                if value:
                                    input_values[inp.name] = value
                                elif inp.required:
                                    self.notify(f"Required field '{inp.name}' is missing", severity="error")
                                    return
                            except Exception:
                                pass

                        # Start loading animation
                        await self.start_pattern_execution(input_values)

                    async def action_cancel_execute(self):
                        """Cancel pattern execution."""
                        self.app.pop_screen()

                    async def start_pattern_execution(self, input_values):
                        """Start pattern execution with loading animation."""
                        # Disable execute button and show loading
                        execute_btn = self.query_one("#execute-now", Button)
                        execute_btn.disabled = True

                        status = self.query_one("#execution-status", Static)

                        # Start loading animation
                        self.loading_active = True
                        self.animate_execution_status()

                        try:
                            # Execute pattern asynchronously
                            response = await self.execute_pattern_async(input_values)

                            # Stop loading animation
                            self.loading_active = False

                            # Show response screen
                            if response:
                                # Handle different response formats
                                if hasattr(response, 'content'):
                                    response_content = response.content
                                elif isinstance(response, dict) and 'content' in response:
                                    response_content = response['content']
                                elif isinstance(response, str):
                                    response_content = response
                                else:
                                    response_content = str(response)

                                status.update("✅ Pattern executed! Showing response...")

                                # Switch to response screen
                                try:
                                    from ..components.loading_screen import create_pattern_response_screen
                                    response_screen_class = create_pattern_response_screen(
                                        response_content=response_content,
                                        title=f"Pattern Response: {self.pattern_data.get('name', self.pattern_id)}",
                                        app_instance=self.app_instance
                                    )
                                    if response_screen_class:
                                        response_screen = response_screen_class()
                                        # Pop this screen and push response screen
                                        self.app.pop_screen()
                                        await self.app.push_screen(response_screen)
                                except Exception as screen_error:
                                    # Fallback: show simple response
                                    status.update(f"✅ Response ready! Length: {len(response_content)} chars")
                                    self.notify(f"Pattern executed successfully. Response length: {len(response_content)} chars", severity="information")
                            else:
                                status.update("❌ No response received")
                                self.notify("Pattern executed but no response received", severity="warning")

                        except Exception as e:
                            # Stop loading animation
                            self.loading_active = False

                            # Show error
                            status.update(f"❌ Execution failed: {str(e)}")
                            self.notify(f"Pattern execution failed: {e}", severity="error")

                        finally:
                            # Re-enable execute button
                            execute_btn.disabled = False

                    @work(exclusive=True)
                    async def animate_execution_status(self):
                        """Animate the execution status during loading."""
                        import asyncio
                        status = self.query_one("#execution-status", Static)
                        animation_chars = ["⏳", "⌛", "🔄", "⚡"]
                        messages = [
                            "Preparing pattern execution...",
                            "Processing inputs...",
                            "Executing pattern...",
                            "Generating response...",
                            "Almost ready..."
                        ]

                        counter = 0
                        while getattr(self, 'loading_active', False):
                            char = animation_chars[counter % len(animation_chars)]
                            message = messages[counter % len(messages)]
                            status.update(f"{char} {message}")
                            counter += 1
                            await asyncio.sleep(0.6)

                    async def execute_pattern_async(self, input_values):
                        """Execute the pattern asynchronously with real AI processing."""
                        import asyncio
                        import json
                        import sys
                        from modules.ai import AIService
                        from modules.messaging import MessageBuilder

                        def execute_sync():
                            try:
                                # Get components from app or initialize with defaults
                                ai_service = getattr(self.app_instance.app, 'ai_service', None)
                                message_builder = getattr(self.app_instance.app, 'message_builder', None)
                                app_logger = getattr(self.app_instance.app, 'logger', None)
                                config = getattr(self.app_instance.app, 'config', {})

                                # Ensure we always have a valid logger
                                if app_logger is not None:
                                    logger = app_logger
                                else:
                                    import logging
                                    # Create a proper logger with console output
                                    logger = logging.getLogger('tui_pattern_execution')
                                    logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all messages

                                    # Only add handler if not already present
                                    if not logger.handlers:
                                        console_handler = logging.StreamHandler()
                                        console_handler.setLevel(logging.INFO)
                                        formatter = logging.Formatter('%(levelname)s: %(message)s')
                                        console_handler.setFormatter(formatter)
                                        logger.addHandler(console_handler)
                                        logger.info("TUI Pattern Execution Logger initialized")

                                # Now logger is guaranteed to be a valid Logger instance

                                # Initialize if not available
                                if not ai_service:
                                    ai_service = AIService(logger)
                                if not message_builder:
                                    message_builder = MessageBuilder(self.pattern_manager, logger)

                                # Build messages for pattern execution
                                messages, pattern_data = message_builder.build_messages(
                                    question=None,  # No question in pattern mode
                                    file_input=None,
                                    pattern_id=self.pattern_id,
                                    pattern_input=input_values,
                                    response_format='md',  # Default to markdown
                                    url=None,
                                    image=None,
                                    pdf=None,
                                    image_url=None,
                                    pdf_url=None
                                )

                                if messages is None:
                                    class MessageErrorResponse:
                                        def __init__(self, content):
                                            self.content = content
                                    return MessageErrorResponse("❌ Error: Failed to build messages for pattern execution")

                                # Debug log the messages (logger is guaranteed to be valid now)
                                logger.debug(json.dumps({
                                    "log_message": "Pattern execution messages",
                                    "pattern_id": self.pattern_id,
                                    "input_values": input_values,
                                    "messages": messages
                                }))

                                # Validate that we have required components
                                if not ai_service:
                                    raise ValueError("AIService could not be initialized")
                                if not self.pattern_manager:
                                    raise ValueError("Pattern manager is not available")

                                # Get AI response
                                logger.info(f"Executing pattern '{self.pattern_id}' with AI service")
                                response = ai_service.get_ai_response(
                                    messages=messages,
                                    model_name=None,  # Use default model
                                    pattern_id=self.pattern_id,
                                    debug=False,
                                    pattern_manager=self.pattern_manager,
                                    enable_url_search=False
                                )

                                logger.info("AI response received successfully")
                                return response

                            except Exception as e:
                                # Return error response with proper logging
                                class PatternErrorResponse:
                                    def __init__(self, content):
                                        self.content = content

                                error_msg = f"❌ Pattern execution failed: {str(e)}"
                                logger.error("Pattern execution error: %s", str(e))

                                # Log full traceback for debugging
                                import traceback
                                logger.debug("Full traceback: %s", traceback.format_exc())

                                return PatternErrorResponse(error_msg)

                        # Run in thread pool to avoid blocking the UI
                        loop = asyncio.get_event_loop()
                        return await loop.run_in_executor(None, execute_sync)

                pattern_screen = PatternExecuteScreen(
                    self.selected_pattern_data,
                    pattern_id,
                    self.pattern_manager,
                    self
                )
                await self.push_screen(pattern_screen)

            except Exception as e:
                self.notify(f"Error executing pattern: {e}", severity="error")

        async def action_browse_chats(self) -> None:
            """Launch chat browser."""
            self.notify("Chat browser will be integrated in future version", severity="information")
            if self.chat_manager:
                # For now, exit to CLI chat browser
                self.exit({"type": "chat", "data": {"workflow": "chat_browser"}})

        async def action_open_settings(self) -> None:
            """Open settings."""
            self.notify("Settings interface will be added in future version", severity="information")

        async def action_browse_models(self) -> None:
            """Browse available OpenRouter models."""
            from python.presentation.tui.screens.model_browser import ModelBrowserScreen
            self.push_screen(ModelBrowserScreen())

        async def action_check_credits(self) -> None:
            """Check OpenRouter credit balance."""
            from python.presentation.tui.screens.credit_view import CreditViewScreen
            self.push_screen(CreditViewScreen())

        async def action_focus_tab_1(self) -> None:
            """Focus question builder tab."""
            tabbed_content = self.query_one(TabbedContent)
            tabbed_content.active = "question-tab"

        async def action_focus_tab_2(self) -> None:
            """Focus pattern browser tab."""
            tabbed_content = self.query_one(TabbedContent)
            tabbed_content.active = "pattern-tab"

        async def action_focus_tab_3(self) -> None:
            """Focus chat manager tab."""
            tabbed_content = self.query_one(TabbedContent)
            tabbed_content.active = "chat-tab"

        async def action_focus_tab_4(self) -> None:
            """Focus settings tab."""
            tabbed_content = self.query_one(TabbedContent)
            tabbed_content.active = "settings-tab"

        async def action_execute_question(self) -> None:
            """Global execute question action."""
            await self.execute_question_action()

        async def action_focus_pattern_filter(self) -> None:
            """Focus the pattern filter input."""
            try:
                # Only focus filter if we're on the pattern tab
                tabbed_content = self.query_one(TabbedContent)
                if tabbed_content.active == "pattern-tab":
                    pattern_filter = self.query_one("#pattern-filter", Input)
                    pattern_filter.focus()
            except Exception:
                pass  # Filter might not exist or be visible

        async def action_help(self) -> None:
            """Show help information."""
            help_text = """
            AskAI Tabbed Interface Help:

            Tabs:
            • Question Builder: Ask AI questions with context
            • Pattern Browser: Browse and use AI patterns
            • Chat Manager: Manage chat history
            • Settings: Application configuration

            Question Builder:
            • Type your question in the text area
            • Select output format: Markdown, Raw Text, or JSON
            • Press Execute or Ctrl+R to process
            • Use Clear to reset the question

            Global Shortcuts:
            • Ctrl+1-4: Switch between tabs
            • Ctrl+R: Execute question (from any tab)
            • Ctrl+Q: Quit application
            • F1: This help

            Tips:
            • Start typing your question immediately
            • Use tabs to organize different workflows
            • All features are integrated in one interface
            """
            self.notify(help_text, severity="information")

        def start_loading_animation(self):
            """Start animated loading status."""
            self.loading_active = True
            self.animate_status()

        def stop_loading_animation(self):
            """Stop the loading animation."""
            self.loading_active = False

        @work(exclusive=True)
        async def animate_status(self):
            """Animate the status during loading."""
            import asyncio
            status = self.query_one("#status", Static)
            animation_chars = ["⏳", "⌛", "🔄", "⚡"]
            messages = [
                "Processing your question...",
                "Analyzing content...",
                "Generating response...",
                "Almost ready..."
            ]

            counter = 0
            while getattr(self, 'loading_active', False):
                char = animation_chars[counter % len(animation_chars)]
                message = messages[counter % len(messages)]
                status.update(f"{char} {message}")
                counter += 1
                await asyncio.sleep(0.5)

        async def process_question_async(self):
            """Process the question asynchronously."""
            import asyncio

            def process_sync():
                # Create mock args
                class MockArgs:
                    def __init__(self, question, format_type):
                        self.question = question
                        self.file_input = None
                        self.url = None
                        self.image = None
                        self.pdf = None
                        self.image_url = None
                        self.pdf_url = None
                        self.format = format_type
                        self.model = None
                        self.debug = False
                        self.save = False
                        self.output = None
                        self.persistent_chat = None
                        self.use_pattern = None
                        self.plain_md = False

                mock_args = MockArgs(self.question_text, self.selected_format)
                if self.question_processor:
                    return self.question_processor.process_question(mock_args)
                else:
                    # Return a mock response if no processor
                    class MockResponse:
                        def __init__(self, content):
                            self.content = content

                    return MockResponse(f"Mock response for: {self.question_text}")

            # Run in thread pool to avoid blocking the UI
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, process_sync)


def run_tabbed_tui(pattern_manager=None, chat_manager=None, question_processor=None):
    """Run the tabbed TUI application."""
    if not TEXTUAL_AVAILABLE:
        return None

    try:
        app = TabbedTUIApp(pattern_manager, chat_manager, question_processor)
        result = app.run()
        return result
    except Exception as e:
        print(f"TUI failed: {e}")
        return None


__all__ = ['TabbedTUIApp', 'run_tabbed_tui']
