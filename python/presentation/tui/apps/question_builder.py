"""
Question Builder TUI for interactive question creation and execution.
"""

from typing import Optional

try:
    from textual.app import App
    from textual.screen import Screen
    from textual.containers import Vertical, Horizontal
    from textual.widgets import Header, Footer, Static, Button, TextArea
    from textual import work
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False


if TEXTUAL_AVAILABLE:
    class QuestionBuilder(Screen):
        """Interactive Question Builder TUI Screen."""

        BINDINGS = [
            ("ctrl+b", "back_to_main", "Back"),
            ("ctrl+q", "quit_app", "Quit"),
            ("f1", "help", "Help"),
            ("ctrl+r", "execute", "Execute"),
        ]

        CSS = """
        Static {
            text-align: center;
            margin: 1 0;
        }

        #question-input {
            height: 10;
            margin: 1 0;
        }

        #status {
            color: $accent;
            text-style: italic;
            height: 3;
            text-align: center;
        }

        Button {
            width: 30%;
            margin: 1;
        }

        .title {
            text-style: bold;
            color: $primary;
            text-align: center;
        }
        """

        def __init__(self, question_processor, **kwargs):
            super().__init__(**kwargs)
            self.question_processor = question_processor
            self.question_text = ""
            self.loading_active = False

        def compose(self):
            """Compose the question builder interface."""
            yield Header(show_clock=True)

            with Vertical():
                yield Static("🤔 Question Builder", classes="title")
                yield Static("Type your question below:")
                yield TextArea(
                    text="",
                    placeholder="Enter your question here...",
                    id="question-input"
                )
                yield Static("", id="status")

                with Horizontal():
                    yield Button("Execute Question", id="execute", variant="success")
                    yield Button("Quit", id="quit", variant="error")

            yield Footer()

        def on_mount(self):
            """Called when mounted."""
            self.call_after_refresh(self.focus_input)

        def focus_input(self):
            """Focus the input after UI is ready."""
            try:
                question_input = self.query_one("#question-input", TextArea)
                question_input.focus()
                status = self.query_one("#status", Static)
                status.update("✅ Input focused - you can type now!")
            except Exception as e:
                status = self.query_one("#status", Static)
                status.update(f"❌ Focus failed: {e}")

        async def on_text_area_changed(self, event: TextArea.Changed) -> None:
            """Handle text area changes."""
            if event.text_area.id == "question-input":
                self.question_text = event.text_area.text
                status = self.query_one("#status", Static)
                status.update(f"Question updated: {len(self.question_text)} chars")

        async def on_button_pressed(self, event: Button.Pressed) -> None:
            """Handle button presses."""
            if event.button.id == "execute":
                await self.action_execute()
            elif event.button.id == "quit":
                await self.action_quit_app()

        async def action_execute(self) -> None:
            """Execute the question with loading indication and response display."""
            if not self.question_text.strip():
                status = self.query_one("#status", Static)
                status.update("❌ Please enter a question first")
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
                            await self.app.push_screen(response_screen)
                    except Exception as screen_error:
                        # Fallback: show in status if screen fails
                        status.update(f"✅ Response ready! Length: {len(response.content)} chars (Screen unavailable)")
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

        async def switch_to_question_builder(self):
            """Clear the form for a new question."""
            # Clear the current question
            question_input = self.query_one("#question-input", TextArea)
            question_input.text = ""
            self.question_text = ""

            # Update status
            status = self.query_one("#status", Static)
            status.update("💡 Ready for your next question!")

            # Focus input
            question_input.focus()

            # Pop the response screen to return to this screen
            self.app.pop_screen()

        async def switch_to_main_menu(self):
            """Exit to main menu or quit app."""
            # If we have a unified app, call its method
            unified_app = getattr(self.app, 'unified_app', None) or getattr(self, 'unified_app', None)
            if unified_app and hasattr(unified_app, 'return_to_main_menu'):
                await unified_app.return_to_main_menu()
            else:
                # Fallback: pop current screen or exit
                try:
                    self.app.pop_screen()
                except Exception:
                    self.app.exit()

        async def action_back_to_main(self):
            """Return to main menu."""
            await self.switch_to_main_menu()

        async def action_quit_app(self):
            """Quit the entire application."""
            self.app.exit()

        async def action_help(self):
            """Show help information."""
            help_text = """
            Question Builder Help:

            Usage:
            • Type your question in the text area
            • Press Execute button or Ctrl+R to process
            • Loading animation shows progress
            • Response opens in dedicated viewer

            Global Shortcuts:
            • Ctrl+B: Back to main menu
            • Ctrl+Q: Quit application
            • Ctrl+R: Execute question
            • F1: This help

            Tips:
            • You can enter multi-line questions
            • Questions are processed with AI analysis
            • Responses include markdown formatting
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
                    def __init__(self, question):
                        self.question = question
                        self.file_input = None
                        self.url = None
                        self.image = None
                        self.pdf = None
                        self.image_url = None
                        self.pdf_url = None
                        self.format = 'rawtext'
                        self.model = None
                        self.debug = False
                        self.save = False
                        self.output = None
                        self.persistent_chat = None
                        self.use_pattern = None
                        self.plain_md = False

                mock_args = MockArgs(self.question_text)
                return self.question_processor.process_question(mock_args)

            # Run in thread pool to avoid blocking the UI
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, process_sync)

        async def action_execute_fallback(self) -> None:
            """Fallback execute method without loading screen."""
            status = self.query_one("#status", Static)
            status.update(f"🔄 Executing: {self.question_text[:50]}...")

            try:
                # Create mock args
                class MockArgs:
                    def __init__(self, question):
                        self.question = question
                        self.file_input = None
                        self.url = None
                        self.image = None
                        self.pdf = None
                        self.image_url = None
                        self.pdf_url = None
                        self.format = 'rawtext'
                        self.model = None
                        self.debug = False
                        self.save = False
                        self.output = None
                        self.persistent_chat = None
                        self.use_pattern = None
                        self.plain_md = False

                mock_args = MockArgs(self.question_text)
                response = self.question_processor.process_question(mock_args)

                # Show result
                status.update(f"✅ Executed! Response: {len(response.content)} chars")

            except Exception as e:
                status.update(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()  # Debug info


def run_question_builder(question_processor) -> Optional[bool]:
    """Run the question builder as a standalone app."""
    if not TEXTUAL_AVAILABLE:
        return None

    try:
        # Create a simple app wrapper for standalone usage
        class QuestionBuilderApp(App):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.question_processor = question_processor

            def compose(self):
                question_screen = QuestionBuilder(question_processor)
                return question_screen.compose()

            async def on_mount(self):
                question_screen = QuestionBuilder(question_processor)
                self.push_screen(question_screen)

        app = QuestionBuilderApp()
        result = app.run()
        return True if result else False
    except Exception:
        return False


__all__ = ['QuestionBuilder', 'run_question_builder']
