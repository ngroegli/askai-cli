#!/usr/bin/env python3
"""
Unified TUI Application that integrates all workflows with proper navigation.
"""

from typing import Optional

try:
    from textual.app import App
    from textual.containers import Vertical, Horizontal
    from textual.widgets import Header, Footer, Static, Button
    from textual.binding import Binding
    from textual.screen import Screen
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False

if TEXTUAL_AVAILABLE:
    class UnifiedTUIApp(App):
        """Unified TUI application with proper navigation between workflows."""

        BINDINGS = [
            ("ctrl+b", "back_to_main", "Back"),
            ("ctrl+q", "quit", "Quit"),
            ("f1", "help", "Help"),
        ]

        def __init__(self, pattern_manager=None, chat_manager=None, question_processor=None, **kwargs):
            super().__init__(**kwargs)
            self.pattern_manager = pattern_manager
            self.chat_manager = chat_manager
            self.question_processor = question_processor
            self.current_workflow = None

        def compose(self):
            """Compose the main menu."""
            yield Header(show_clock=True)

            with Vertical():
                yield Static("🤖 AskAI Interactive Terminal", classes="welcome-title")
                yield Static("Choose your workflow to get started", classes="welcome-subtitle")

                # Workflow options
                yield Static("🤔 Question Logic", classes="workflow-title")
                yield Static("Build interactive AI queries with context files, URLs, images, and PDFs", classes="workflow-description")
                yield Button("Start Question Builder", id="start-question", variant="primary")

                yield Static("📋 Pattern Logic", classes="workflow-title")
                yield Static("Browse patterns, preview markdown content, and execute with custom inputs", classes="workflow-description")
                yield Button("Browse Patterns", id="start-pattern", variant="primary")

                yield Static("⚙️ System Management", classes="workflow-title")
                yield Static("Manage OpenRouter account, configuration, and system operations", classes="workflow-description")
                yield Button("Open Internals", id="start-internals", variant="primary")

                with Horizontal():
                    yield Button("Exit", id="exit", variant="error")

            yield Footer()

        async def on_button_pressed(self, event: Button.Pressed) -> None:
            """Handle button presses."""
            if event.button.id == "start-question":
                await self.start_question_workflow()
            elif event.button.id == "start-pattern":
                await self.start_pattern_workflow()
            elif event.button.id == "start-internals":
                await self.start_internals_workflow()
            elif event.button.id == "exit":
                self.exit()

        async def start_question_workflow(self):
            """Start the question builder workflow."""
            if not self.question_processor:
                self.notify("Question processor not available", severity="error")
                return

            try:
                from .question_builder import QuestionBuilder
                question_screen = QuestionBuilder(self.question_processor)
                question_screen.unified_app = self  # Reference to return to main menu
                await self.push_screen(question_screen)
                self.current_workflow = "question"
            except Exception as e:
                self.notify(f"Failed to start question workflow: {e}", severity="error")

        async def start_pattern_workflow(self):
            """Start the pattern workflow."""
            self.notify("Pattern workflow available - returning to CLI mode", severity="information")
            self.exit({"type": "pattern", "data": {"workflow": "pattern_browser"}})

        async def start_internals_workflow(self):
            """Start the internals workflow."""
            self.notify("Internals workflow available - returning to CLI mode", severity="information")
            self.exit({"type": "internals", "data": {"workflow": "internals_management"}})

        async def return_to_main_menu(self):
            """Return to the main menu from any workflow."""
            # Pop all screens except the main one
            while len(self.screen_stack) > 1:
                self.pop_screen()
            self.current_workflow = None

        async def action_back_to_main(self):
            """Global back to main menu action."""
            await self.return_to_main_menu()

        async def action_help(self):
            """Show global help information."""
            if self.current_workflow == "question":
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
                • F1: This help
                """
            else:
                help_text = """
                AskAI Interactive Terminal Help:

                Workflows:
                1. Question Logic: Interactive question builder with context
                2. Pattern Logic: Template-based AI interactions
                3. System Management: Internal operations

                Global Shortcuts:
                • Ctrl+B: Back to main menu
                • Ctrl+Q: Quit application
                • F1: This help

                Navigation:
                • Use buttons to select workflows
                • Each workflow has its own interface
                • Global shortcuts work from any screen
                """

            self.notify(help_text, severity="information")

        CSS = """
        .welcome-title {
            text-style: bold;
            color: $primary;
            text-align: center;
            padding: 1;
        }

        .welcome-subtitle {
            color: $text-muted;
            text-align: center;
            margin-bottom: 2;
        }

        .workflow-title {
            text-style: bold;
            color: $primary;
            margin: 1 0;
        }

        .workflow-description {
            color: $text-muted;
            margin-bottom: 1;
        }

        Button {
            margin: 1 0;
        }
        """


def run_unified_tui(pattern_manager=None, chat_manager=None, question_processor=None):
    """Run the unified TUI application."""
    if not TEXTUAL_AVAILABLE:
        return None

    try:
        app = UnifiedTUIApp(pattern_manager, chat_manager, question_processor)
        result = app.run()
        return result
    except Exception as e:
        print(f"TUI failed: {e}")
        return None


__all__ = ['UnifiedTUIApp', 'run_unified_tui']
