#!/usr/bin/env python3
"""
Simplified Tabbed TUI Application using component-based architecture.
Each tab is now a separate, reusable component.
"""

from typing import TYPE_CHECKING

# Import our components and common styles
from ..common import COMMON_STYLES
from ..components import QuestionTab, PatternTab, ChatTab, ModelTab, CreditsTab

try:
    from textual.app import App
    from textual.widgets import Header, Footer, TabbedContent, TabPane
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
        TabbedContent = object
        TabPane = object
        Binding = object

# Type imports for static analysis
if TYPE_CHECKING:
    from textual.app import App
    from textual.containers import Vertical, Horizontal
    from textual.widgets import Header, Footer, Static, TabbedContent, TabPane
    from textual.binding import Binding


if TEXTUAL_AVAILABLE:
    class TabbedTUIApp(App):
        """Simplified tabbed TUI application using components."""

        BINDINGS = [
            ("ctrl+q", "quit", "Quit"),
            ("f1", "help", "Help"),
            ("f2", "focus_question", "Question"),
            ("f3", "focus_patterns", "Patterns"),
            ("f4", "focus_chats", "Chats"),
            ("f5", "focus_models", "Models"),
            ("f6", "focus_credits", "Credits"),
        ]

        CSS = f"""
        /* Main Application Styles */
        Screen {{
            background: #0f172a;
        }}

        Header {{
            background: #1e293b;
            color: #00FFFF;
            dock: top;
            height: 3;
        }}

        Footer {{
            background: #1e293b;
            color: #87CEEB;
            dock: bottom;
            height: 3;
        }}

        /* Tab Content Styles */
        TabbedContent {{
            background: #0f172a;
            margin: 1;
        }}

        TabPane {{
            background: #0f172a;
            padding: 1;
        }}

        {COMMON_STYLES}

        /* Additional app-specific styles */
        .question-input {{
            height: 4;
            max-height: 4;
        }}

        .question-form {{
            margin: 1;
        }}

        .question-main-layout {{
            height: 100%;
        }}

        .question-form-panel {{
            width: 1fr;
            margin-right: 1;
        }}

        .answer-panel {{
            width: 1fr;
            margin-left: 1;
        }}

        .input-row, .select-row {{
            height: auto;
            margin: 0;
        }}

        .input-column, .select-column {{
            margin: 0 1;
        }}

        .pattern-browser-container,
        .chat-browser-container,
        .model-browser-container {{
            height: 100%;
        }}

        .pattern-list-panel,
        .chat-list-panel,
        .model-list-panel {{
            width: 1fr;
            margin-right: 1;
        }}

        .pattern-details-panel,
        .chat-details-panel,
        .model-details-panel {{
            width: 2fr;
        }}

        .hidden {{
            display: none;
        }}

        /* Pattern Details Box */
        .pattern-details-box {{
            background: #1e293b;
            border: solid #00FFFF;
            height: 1fr;
            padding: 1;
        }}

        /* Pattern List Box */
        .pattern-list-box {{
            background: #1e293b;
            border: solid #00FFFF;
            height: 1fr;
        }}

        /* Remove border from ListView when inside ScrollableContainer */
        .pattern-list-box ListView {{
            border: none;
            background: transparent;
        }}
        """

        def __init__(self, pattern_manager=None, chat_manager=None, question_processor=None):
            super().__init__()
            self.pattern_manager = pattern_manager
            self.chat_manager = chat_manager
            self.question_processor = question_processor

            # Component instances
            self.question_tab = None
            self.pattern_tab = None
            self.chat_tab = None
            self.model_tab = None
            self.credits_tab = None

        def compose(self):
            """Compose the main application layout."""
            yield Header()

            with TabbedContent(initial="question-tab"):
                # Question Builder Tab
                with TabPane("Question Builder", id="question-tab"):
                    self.question_tab = QuestionTab(
                        question_processor=self.question_processor,
                        id="question-component"
                    )
                    yield self.question_tab

                # Pattern Browser Tab
                with TabPane("Pattern Browser", id="pattern-tab"):
                    self.pattern_tab = PatternTab(
                        pattern_manager=self.pattern_manager,
                        id="pattern-component"
                    )
                    yield self.pattern_tab

                # Chat Browser Tab
                with TabPane("Chat Browser", id="chat-tab"):
                    self.chat_tab = ChatTab(
                        chat_manager=self.chat_manager,
                        id="chat-component"
                    )
                    yield self.chat_tab

                # Model Browser Tab
                with TabPane("Model Browser", id="model-tab"):
                    self.model_tab = ModelTab(id="model-component")
                    yield self.model_tab

                # Credits Tab
                with TabPane("Credits", id="credits-tab"):
                    self.credits_tab = CreditsTab(id="credits-component")
                    yield self.credits_tab

            yield Footer()

        async def on_mount(self) -> None:
            """Called when the app mounts."""
            self.title = "AskAI - Interactive Terminal UI"
            self.sub_title = "Question Builder | Pattern Browser | Chat Manager | Model Browser | Credits"

            # Initialize all component tabs
            if hasattr(self, 'question_tab') and self.question_tab:
                await self.question_tab.initialize()
            if hasattr(self, 'pattern_tab') and self.pattern_tab:
                await self.pattern_tab.initialize()
            if hasattr(self, 'chat_tab') and self.chat_tab:
                await self.chat_tab.initialize()
            if hasattr(self, 'model_tab') and self.model_tab:
                await self.model_tab.initialize()
            if hasattr(self, 'credits_tab') and self.credits_tab:
                await self.credits_tab.initialize()

        # Message handlers for component interactions
        async def on_question_tab_question_submitted(self, event) -> None:
            """Handle question submission from QuestionTab."""
            question_data = event.question_data

            # Update status
            if self.question_tab:
                self.question_tab.update_status("🔄 Processing question...")

            try:
                if not self.question_processor:
                    if self.question_tab:
                        self.question_tab.update_status("❌ Question processor not available")
                    return

                # Create a simple args object from question_data
                class SimpleArgs:
                    """Simple arguments container for question processing."""

                    def __init__(self, question_data):
                        self.question = question_data['question']
                        self.file_input = question_data['file_input'] if question_data['file_input'] else None
                        self.url = question_data['url'] if question_data['url'] else None
                        self.format = question_data['format']
                        self.model = question_data['model'] if question_data['model'] else None
                        self.output = None
                        self.debug = False
                        # These are not supported in TUI yet, but needed for compatibility
                        self.image = None
                        self.pdf = None
                        self.image_url = None
                        self.pdf_url = None
                        self.persistent_chat = None

                args = SimpleArgs(question_data)

                # Process the question
                response = self.question_processor.process_question(args)

                if response and response.content:
                    # Display the answer
                    if self.question_tab:
                        self.question_tab.display_answer(response.content)
                        self.question_tab.update_status("✅ Question processed successfully!")
                else:
                    if self.question_tab:
                        self.question_tab.update_status("❌ No response received")

            except Exception as e:
                if self.question_tab:
                    self.question_tab.update_status(f"❌ Error processing question: {str(e)}")
                    self.question_tab.display_answer(f"Error: {str(e)}")

        async def on_pattern_tab_pattern_selected(self, event) -> None:
            """Handle pattern selection from PatternTab."""
            pattern_data = event.pattern_data
            pattern_input = event.pattern_input

            # Update status
            if self.pattern_tab:
                self.pattern_tab.update_status("🔄 Executing pattern...")

            try:
                # For now, just validate the pattern and inputs
                pattern_id = pattern_data.get('pattern_id', pattern_data.get('name', ''))

                if self.pattern_manager:
                    # Validate that we have the pattern
                    pattern_content = self.pattern_manager.get_pattern_content(pattern_id)
                    if pattern_content:
                        input_summary = ""
                        if pattern_input:
                            input_summary = f" with {len(pattern_input)} inputs"

                        if self.pattern_tab:
                            status_msg = f"✅ Pattern '{pattern_id}' ready for execution{input_summary}"
                            self.pattern_tab.update_status(status_msg)
                    else:
                        if self.pattern_tab:
                            self.pattern_tab.update_status(f"❌ Pattern '{pattern_id}' not found")
                else:
                    if self.pattern_tab:
                        self.pattern_tab.update_status("❌ Pattern manager not available")

            except Exception as e:
                if self.pattern_tab:
                    self.pattern_tab.update_status(f"❌ Pattern execution failed: {str(e)}")

        async def on_chat_tab_chat_selected(self, event) -> None:
            """Handle chat selection from ChatTab."""
            chat_data = event.chat_data

            # Update status
            if self.chat_tab:
                self.chat_tab.update_status(f"✅ Selected chat: {chat_data.get('chat_id', 'Unknown')}")

        async def on_chat_tab_chat_action(self, event) -> None:
            """Handle chat actions from ChatTab."""
            action = event.action
            chat_data = event.chat_data

            if action == "new_chat":
                # Handle new chat creation
                if self.chat_tab:
                    self.chat_tab.update_status("✅ New chat created!")
            elif action == "delete_chat" and chat_data:
                # Handle chat deletion
                chat_id = chat_data.get('chat_id', 'Unknown')
                if self.chat_tab:
                    self.chat_tab.update_status(f"✅ Deleted chat: {chat_id}")

        async def on_model_tab_model_selected(self, event) -> None:
            """Handle model selection from ModelTab."""
            model_data = event.model_data

            # Update status
            if self.model_tab:
                self.model_tab.update_status(f"✅ Selected model: {model_data.get('name', 'Unknown')}")

        # Key binding actions
        def action_focus_question(self) -> None:
            """Focus the question tab."""
            tabs = self.query_one(TabbedContent)
            tabs.active = "question-tab"

        def action_focus_patterns(self) -> None:
            """Focus the patterns tab."""
            tabs = self.query_one(TabbedContent)
            tabs.active = "pattern-tab"

        def action_focus_chats(self) -> None:
            """Focus the chats tab."""
            tabs = self.query_one(TabbedContent)
            tabs.active = "chat-tab"

        def action_focus_models(self) -> None:
            """Focus the models tab."""
            tabs = self.query_one(TabbedContent)
            tabs.active = "model-tab"

        def action_focus_credits(self) -> None:
            """Focus the credits tab."""
            tabs = self.query_one(TabbedContent)
            tabs.active = "credits-tab"

        def action_help(self) -> None:
            """Show help information."""
            help_text = """
**AskAI Interactive TUI Help**

**Navigation:**
• F1: Show this help
• F2: Switch to Question Builder
• F3: Switch to Pattern Browser
• F4: Switch to Chat Browser
• F5: Switch to Model Browser
• F6: Switch to Credits
• Ctrl+Q: Quit application

**Tabs:**
• Question Builder: Create and submit questions to AI
• Pattern Browser: Browse and use AI patterns
• Chat Browser: Manage chat history
• Model Browser: Browse and select AI models
• Credits: Monitor OpenRouter credit balance and usage

**Question Builder:**
• Enter your question in the main text area
• Optionally add file input, URL, or specify format
• Click "Ask AI" to submit your question
• Use "Clear" to reset the form

**Pattern Browser:**
• Browse available patterns in the left panel
• Select a pattern to view details in the right panel
• Provide JSON input if the pattern requires it
• Click "Use Pattern" to execute

**Chat Browser:**
• View all your chat sessions
• Create new chats or delete existing ones
• Select a chat to view details

**Model Browser:**
• Browse available AI models
• Search for specific models
• View model details, pricing, and capabilities
• Check your OpenRouter credits
"""

            # For now, just log the help - in a real implementation you'd create a help screen
            self.log(help_text)
def run_tabbed_tui(pattern_manager=None, chat_manager=None, question_processor=None):
    """
    Run the tabbed TUI application.

    Args:
        pattern_manager: Pattern manager instance
        chat_manager: Chat manager instance
        question_processor: Question processor instance

    Returns:
        Any result from the TUI interaction
    """
    if not TEXTUAL_AVAILABLE:
        print("Textual TUI library is not available. Please install it with: pip install textual")
        return None

    try:
        app = TabbedTUIApp(
            pattern_manager=pattern_manager,
            chat_manager=chat_manager,
            question_processor=question_processor
        )
        return app.run()
    except Exception as e:
        print(f"TUI application failed: {e}")
        return None
    except KeyboardInterrupt:
        print("\nTUI application interrupted by user")
        return None


# Fallback function for when TUI is not available
def tabbed_tui_fallback(pattern_manager=None, chat_manager=None, question_processor=None):
    """Fallback when TUI is not available."""
    # Acknowledge parameters to satisfy linter (they maintain API compatibility)
    _ = pattern_manager, chat_manager, question_processor

    print("Tabbed TUI interface is not available.")
    print("This could be due to:")
    print("1. Missing textual package (install with: pip install textual)")
    print("2. Incompatible terminal environment")
    print("3. System configuration issues")
    print("\nPlease use the CLI interface instead.")


if not TEXTUAL_AVAILABLE:
    run_tabbed_tui = tabbed_tui_fallback
