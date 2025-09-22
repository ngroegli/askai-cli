"""
Main TUI Application for AskAI CLI.
Refactored to use modular styling system.
Comprehensive terminal interface that routes between Question Logic,
Pattern Logic, and Internals Management workflows.
"""

from typing import Optional, Dict, Any, TYPE_CHECKING

try:
    from textual.app import App
    from textual.containers import Horizontal, Vertical, Container
    from textual.widgets import Header, Footer, Static, Button
    from textual.binding import Binding
    from textual.screen import ModalScreen
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    if not TYPE_CHECKING:
        App = object
        Horizontal = object
        Vertical = object
        Container = object
        Header = object
        Footer = object
        Static = object
        Button = object
        Binding = object
        BindingType = object
        ModalScreen = object

# Type imports for static analysis
if TYPE_CHECKING:
    from textual.app import App
    from textual.containers import Horizontal, Vertical, Container
    from textual.widgets import Header, Footer, Static, Button
    from textual.binding import Binding, BindingType
    from textual.screen import ModalScreen

# Import the modular styling system
try:
    from ..styles import DEFAULT_THEME
    from ..styles.styled_components import (
        TitleText, CaptionText, PrimaryButton, DangerButton, ButtonGroup
    )
    STYLES_AVAILABLE = True
except ImportError:
    STYLES_AVAILABLE = False
    if not TYPE_CHECKING:
        DEFAULT_THEME = None
        TitleText = object
        CaptionText = object
        PrimaryButton = object
        DangerButton = object
        ButtonGroup = object


if TEXTUAL_AVAILABLE:
    class WorkflowSelectionModal(ModalScreen):
        """Modal for selecting the main workflow using styled components."""

        def compose(self):
            """Compose the workflow selection modal."""
            with Container(id="workflow-dialog", classes="modal-container"):
                yield TitleText("Select AskAI Workflow")
                yield CaptionText("Choose the type of operation you want to perform:")

                with Vertical(classes="workflow-options"):
                    yield PrimaryButton("Ask Question", id="question-workflow", classes="workflow-btn")
                    yield CaptionText("Interactive question builder with context files, URLs, images, and PDFs")

                    yield PrimaryButton("Use Pattern", id="pattern-workflow", classes="workflow-btn")
                    yield CaptionText("Browse patterns, preview content, configure inputs, and execute")

                    yield PrimaryButton("System Management", id="internals-workflow", classes="workflow-btn")
                    yield CaptionText("OpenRouter management, configuration, and system operations")

                with ButtonGroup(classes="modal-actions"):
                    yield DangerButton("Cancel", id="cancel")

        def on_button_pressed(self, event: Button.Pressed) -> None:
            """Handle workflow selection."""
            if event.button.id == "question-workflow":
                self.dismiss("question")
            elif event.button.id == "pattern-workflow":
                self.dismiss("pattern")
            elif event.button.id == "internals-workflow":
                self.dismiss("internals")
            elif event.button.id == "cancel":
                self.dismiss(None)

        # Use modular CSS system for the modal
        CSS = DEFAULT_THEME.get_component_only_css("modals", "buttons") if DEFAULT_THEME else """
        #workflow-dialog {
            width: 80%;
            height: 70%;
            background: $surface;
            border: thick #00FFFF;
            padding: 2;
        }

        .modal-title {
            text-style: bold;
            color: $primary;
            text-align: center;
            margin-bottom: 1;
        }

        .modal-description {
            color: $text-muted;
            text-align: center;
            margin-bottom: 2;
        }

        .workflow-options {
            margin: 2 0;
        }

        .workflow-btn {
            width: 100%;
            margin: 1 0;
        }

        .workflow-desc {
            color: $text-muted;
            text-style: italic;
            margin-bottom: 2;
            text-align: center;
        }

        .modal-actions {
            margin-top: 2;
            text-align: center;
        }
        """


    class MainTUIApp(App):
        """Main AskAI TUI Application with workflow routing and modular styling."""

        # Use centralized CSS instead of scattered inline styles
        CSS = DEFAULT_THEME.get_complete_css() if DEFAULT_THEME else """
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

        # BINDINGS is a list of Binding
        BINDINGS = [
            Binding("q", "quit", "Quit"),
            Binding("ctrl+c", "quit", "Quit"),
            Binding("escape", "quit", "Quit"),
            Binding("1", "question_workflow", "Question"),
            Binding("2", "pattern_workflow", "Pattern"),
            Binding("3", "internals_workflow", "Internals"),
            Binding("f1", "help", "Help"),
        ]

        def __init__(self, pattern_manager, chat_manager, **kwargs):
            super().__init__(**kwargs)
            self.pattern_manager = pattern_manager
            self.chat_manager = chat_manager
            self.workflow_result = None

        def compose(self):
            """Compose the main application layout."""
            yield Header(show_clock=True)

            # Welcome section
            yield Static("🤖 AskAI Interactive Terminal", classes="welcome-title")
            yield Static("Choose your workflow to get started", classes="welcome-subtitle")

            # Workflow cards
            yield Static("🤔 Question Logic", classes="workflow-title")
            yield Static("Build interactive AI queries with context files, URLs, images, and PDFs", classes="workflow-description")
            yield Button("Start Question Builder", id="start-question", variant="primary")

            yield Static("📋 Pattern Logic", classes="workflow-title")
            yield Static("Browse patterns, preview markdown content, and execute with custom inputs", classes="workflow-description")
            yield Button("Browse Patterns", id="start-pattern", variant="primary")

            yield Static("⚙️ System Management", classes="workflow-title")
            yield Static("Manage OpenRouter account, configuration, and system operations", classes="workflow-description")
            yield Button("Open Internals", id="start-internals", variant="primary")

            # Action buttons
            with Horizontal():
                yield Button("Quick Workflow Select", id="quick-select", variant="success")
                yield Button("Exit", id="exit", variant="error")

            yield Footer()

        async def on_button_pressed(self, event: Button.Pressed) -> None:
            """Handle button presses."""
            if event.button.id == "start-question":
                await self.action_question_workflow()
            elif event.button.id == "start-pattern":
                await self.action_pattern_workflow()
            elif event.button.id == "start-internals":
                await self.action_internals_workflow()
            elif event.button.id == "quick-select":
                await self.action_quick_select()
            elif event.button.id == "exit":
                await self.action_quit()

        async def action_question_workflow(self) -> None:
            """Launch the question logic workflow."""
            try:
                self.notify("Starting Question Builder...", severity="information")
                # Exit with a signal that question mode was requested
                self.workflow_result = {
                    'type': 'question',
                    'data': {'workflow': 'question_builder'}
                }
                self.exit(self.workflow_result)

            except Exception as e:
                self.notify(f"Failed to start question workflow: {e}", severity="error")

        async def action_pattern_workflow(self) -> None:
            """Launch the pattern logic workflow."""
            try:
                # Use the simple pattern browser for now
                self.notify("Starting Pattern Logic workflow...", severity="information")

                # Exit the main app and let the command handler show the pattern browser
                self.workflow_result = {
                    'type': 'pattern',
                    'data': {'workflow': 'pattern_browser'}
                }
                self.exit(self.workflow_result)

            except Exception as e:
                self.notify(f"Failed to start pattern workflow: {e}", severity="error")
                self.exit(None)

        async def action_internals_workflow(self) -> None:
            """Launch the internals management workflow."""
            try:
                self.notify("Internals Management workflow available - exiting to CLI mode", severity="information")
                # For now, exit with a signal that internals mode was requested
                self.workflow_result = {
                    'type': 'internals',
                    'data': {'workflow': 'internals_management'}
                }
                self.exit(self.workflow_result)

            except Exception as e:
                self.notify(f"Failed to start internals workflow: {e}", severity="error")
                self.exit(None)

        async def action_quick_select(self) -> None:
            """Show quick workflow selection modal."""
            def handle_workflow_selection(workflow_type: Optional[str]) -> None:
                if workflow_type == "question":
                    self.call_later(self.action_question_workflow)
                elif workflow_type == "pattern":
                    self.call_later(self.action_pattern_workflow)
                elif workflow_type == "internals":
                    self.call_later(self.action_internals_workflow)

            self.push_screen(WorkflowSelectionModal(), handle_workflow_selection)

        async def action_help(self) -> None:
            """Show help information."""
            help_text = """
            AskAI Interactive Terminal Help:

            Workflows:
            1. Question Logic (1): Interactive question builder with context
            2. Pattern Logic (2): Template-based AI interactions
            3. System Management (3): Internal operations

            Navigation:
            • Use number keys (1-3) for quick workflow selection
            • Click buttons or use Quick Select for modal
            • Each workflow is a complete standalone interface

            Shortcuts:
            • 1: Question Logic
            • 2: Pattern Logic
            • 3: System Management
            • Q/Esc: Exit
            • F1: This help
            """
            self.notify(help_text, severity="information")

        async def action_quit(self) -> None:
            """Quit the application."""
            self.exit(None)


def run_main_tui_app(pattern_manager, chat_manager) -> Optional[Dict[str, Any]]:
    """
    Run the main TUI application with workflow routing.

    Args:
        pattern_manager: Pattern manager instance
        chat_manager: Chat manager instance

    Returns:
        Dict with workflow type and execution data, or None if cancelled
    """
    if not TEXTUAL_AVAILABLE:
        return None

    try:
        app = MainTUIApp(pattern_manager, chat_manager)
        result = app.run()
        # Return the result, ensuring it's in the expected format
        if isinstance(result, dict):
            return result
        return None
    except Exception:
        # If TUI fails, return None to trigger fallback
        return None


__all__ = ['MainTUIApp', 'run_main_tui_app']
