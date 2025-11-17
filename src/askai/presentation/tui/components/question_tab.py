"""
Question Builder Tab Component.
Handles the question creation interface with inputs, format selection, and execution.
"""

from typing import TYPE_CHECKING
from .base_tab import BaseTabComponent

from ..common import (
    Static, Button, TextArea, Select, Input,
    Vertical, Horizontal, VerticalScroll, Message, StatusMixin
)

if TYPE_CHECKING:
    from textual.widgets import Static, Button, TextArea, Select, Input
    from textual.containers import Vertical, Horizontal, VerticalScroll
    from textual.message import Message


class QuestionTab(BaseTabComponent, StatusMixin):
    """Question Builder tab component."""

    class QuestionSubmitted(Message):
        """Message sent when a question is submitted."""
        def __init__(self, question_data: dict) -> None:
            self.question_data = question_data
            super().__init__()

    def __init__(self, *args, question_processor=None, **kwargs):
        super().__init__("Question Builder", *args, **kwargs)
        self.question_processor = question_processor

    def compose(self):
        """Compose the question builder interface."""
        yield Static("Question Builder", classes="panel-title")

        with Horizontal(classes="question-main-layout"):
            # Left panel - Simplified question form
            with Vertical(classes="question-form-panel"):
                # Question input - main element
                yield Static("Question:")
                yield TextArea(
                    placeholder="Enter your question here...",
                    id="question-input",
                    classes="question-input"
                )

                # Action buttons - prominently placed right after question
                with Horizontal(classes="button-row"):
                    yield Button("Ask AI", variant="primary", id="ask-button")
                    yield Button("Clear", variant="default", id="clear-button")

                # Optional inputs - compact row
                with Horizontal(classes="input-row"):
                    with Vertical(classes="input-column"):
                        yield Static("File:")
                        yield Input(placeholder="file path", id="file-input")

                    with Vertical(classes="input-column"):
                        yield Static("URL:")
                        yield Input(placeholder="https://...", id="url-input")

                # Format selection - compact
                with Horizontal(classes="select-row"):
                    yield Static("Format:")
                    yield Select([
                        ("Text", "rawtext"),
                        ("Markdown", "md"),
                        ("JSON", "json")
                    ], value="rawtext", id="format-select")

                # Status display
                yield Static("✅ Ready to ask your question!", id="status-display", classes="status-text")

            # Right panel - Answer display
            with Vertical(classes="answer-panel"):
                yield Static("Answer", classes="panel-subtitle")

                # Scrollable answer container with border
                with VerticalScroll(id="answer-scroll", classes="pattern-details-box"):
                    yield Static("Ask a question to see the AI response here.", id="answer-display")

    async def initialize(self):
        """Initialize the question builder."""
        status_display = self.query_one("#status-display", Static)
        status_display.update("✅ Ready to ask your question!")

    async def on_button_pressed(self, event) -> None:
        """Handle button presses."""
        if event.button.id == "ask-button":
            await self._submit_question()
        elif event.button.id == "clear-button":
            await self._clear_form()

    async def _submit_question(self) -> None:
        """Submit the question for processing."""
        question_input = self.query_one("#question-input", TextArea)
        status_display = self.query_one("#status-display", Static)

        if not question_input.text.strip():
            status_display.update("❌ Please enter a question")
            return

        file_input = self.query_one("#file-input", Input)
        url_input = self.query_one("#url-input", Input)
        format_select = self.query_one("#format-select", Select)

        question_data = {
            'question': question_input.text.strip(),
            'file_input': file_input.value,
            'url': url_input.value,
            'format': format_select.value,
            'model': '',  # Default model
        }

        status_display.update("🔄 Processing question...")

        # Emit message to parent
        self.post_message(self.QuestionSubmitted(question_data))

    async def _clear_form(self) -> None:
        """Clear all form inputs."""
        question_input = self.query_one("#question-input", TextArea)
        file_input = self.query_one("#file-input", Input)
        url_input = self.query_one("#url-input", Input)
        format_select = self.query_one("#format-select", Select)
        status_display = self.query_one("#status-display", Static)

        question_input.text = ""
        file_input.value = ""
        url_input.value = ""
        format_select.value = "rawtext"
        status_display.update("✅ Form cleared, ready for new question!")


    def display_answer(self, answer: str) -> None:
        """Display the AI answer in the answer panel."""
        try:
            answer_display = self.query_one("#answer-display", Static)
            answer_display.update(answer)
        except Exception:
            pass
