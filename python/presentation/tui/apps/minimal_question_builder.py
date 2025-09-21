"""
Minimal Question Builder TUI for testing input functionality.
"""

import os
from typing import Optional, Dict, Any

try:
    from textual.app import App
    from textual.containers import Vertical
    from textual.widgets import Header, Footer, Static, Button, Input, TextArea
    from textual.binding import Binding
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False


if TEXTUAL_AVAILABLE:
    class MinimalQuestionBuilder(App):
        """Minimal Question Builder for testing."""

        BINDINGS = [
            Binding("ctrl+q", "quit", "Quit"),
            Binding("ctrl+r", "execute", "Execute"),
        ]

        def __init__(self, question_processor, **kwargs):
            super().__init__(**kwargs)
            self.question_processor = question_processor
            self.question_text = ""

        def compose(self):
            """Compose the minimal question builder interface."""
            yield Header(show_clock=True)

            with Vertical():
                yield Static("🤔 Minimal Question Builder")
                yield Static("Type your question below:")
                yield TextArea(
                    text="",
                    placeholder="Enter your question here...",
                    id="question-input"
                )
                yield Static("", id="status")
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
                await self.action_quit()

        async def action_execute(self) -> None:
            """Execute the question."""
            if not self.question_text.strip():
                status = self.query_one("#status", Static)
                status.update("❌ Please enter a question first")
                return

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

                mock_args = MockArgs(self.question_text)
                response = self.question_processor.process_question(mock_args)

                # Show result
                status.update(f"✅ Executed! Response: {len(response.content)} chars")

            except Exception as e:
                status.update(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()  # Debug info


def run_minimal_question_builder(question_processor) -> Optional[Dict[str, Any]]:
    """Run the minimal question builder."""
    if not TEXTUAL_AVAILABLE:
        return None

    try:
        app = MinimalQuestionBuilder(question_processor)
        result = app.run()
        return result
    except Exception:
        return None


__all__ = ['MinimalQuestionBuilder', 'run_minimal_question_builder']
