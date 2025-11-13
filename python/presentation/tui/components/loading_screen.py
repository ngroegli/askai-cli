"""
Shared loading screen component for TUI applications.
"""

from typing import Optional, TYPE_CHECKING

try:
    from textual.containers import Center, Middle, Vertical, Horizontal, ScrollableContainer
    from textual.widgets import Static, ProgressBar, TextArea, Button, Header, Footer
    from textual.screen import ModalScreen, Screen
    from textual import work
    import asyncio
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    if not TYPE_CHECKING:
        Center = object
        Middle = object
        Vertical = object
        Static = object
        ProgressBar = object
        ModalScreen = object
        Screen = object

        def work(x):
            """Simple fallback for work decorator."""
            return x
    import asyncio

# Type imports for static analysis
if TYPE_CHECKING:
    from textual.containers import Center, Middle, Vertical
    from textual.widgets import Static, ProgressBar
    from textual.screen import ModalScreen, Screen
    from textual import work


if TEXTUAL_AVAILABLE:
    class LoadingScreen(ModalScreen):
        """Modal loading screen with animated progress and status messages."""

        def __init__(self, title: str = "Processing", message: str = "Please wait...", **kwargs):
            super().__init__(**kwargs)
            self.title: str = title or "Processing"
            self.message: str = message or "Please wait..."
            self.is_loading = True

        def compose(self):
            """Compose the loading screen."""
            with Center():
                with Middle():
                    with Vertical(id="loading-container"):
                        yield Static(self.title, id="loading-title")
                        yield Static(self.message, id="loading-message")
                        yield ProgressBar(show_eta=False, show_percentage=False, id="loading-progress")
                        yield Static("⏳ Working...", id="loading-status")

        def on_mount(self) -> None:
            """Start the loading animation when mounted."""
            self.animate_loading()

        @work(exclusive=True)
        async def animate_loading(self):
            """Animate the loading screen with rotating status."""
            progress_bar = self.query_one("#loading-progress", ProgressBar)
            status = self.query_one("#loading-status", Static)

            # Start indeterminate progress
            progress_bar.advance(0)

            animation_chars = ["⏳", "⌛", "🔄", "⚡"]
            messages = [
                "Processing your request...",
                "Analyzing content...",
                "Generating response...",
                "Almost ready..."
            ]

            counter = 0
            while self.is_loading:
                char = animation_chars[counter % len(animation_chars)]
                message = messages[counter % len(messages)]
                status.update(f"{char} {message}")

                # Animate progress bar
                progress_bar.advance(10)

                counter += 1
                await asyncio.sleep(0.5)

        def update_message(self, message: str) -> None:
            """Update the loading message."""
            message_widget = self.query_one("#loading-message", Static)
            message_widget.update(message)

        def update_status(self, status: str) -> None:
            """Update the status message."""
            status_widget = self.query_one("#loading-status", Static)
            status_widget.update(status)

        def stop_loading(self) -> None:
            """Stop the loading animation."""
            self.is_loading = False

        def safe_dismiss(self) -> None:
            """Safely dismiss the loading screen."""
            try:
                self.stop_loading()
                self.dismiss()
            except Exception:
                # Ignore dismissal errors
                pass

        CSS = """
        #loading-container {
            width: 60%;
            height: 20%;
            background: $surface;
            border: thick #00FFFF;
            padding: 3;
        }

        #loading-title {
            text-style: bold;
            color: $primary;
            text-align: center;
            margin-bottom: 1;
        }

        #loading-message {
            color: $text;
            text-align: center;
            margin-bottom: 2;
        }

        #loading-progress {
            margin: 1 0;
        }

        #loading-status {
            color: $text-muted;
            text-align: center;
            text-style: italic;
        }
        """


    class ResponseViewerScreen(ModalScreen):
        """Modal screen for displaying AI responses."""

        def __init__(self, response_content: str, title: str = "AI Response", **kwargs):
            super().__init__(**kwargs)
            self.response_content = response_content
            self.title = title or "AI Response"

        def compose(self):
            """Compose the response viewer."""
            with Vertical(id="response-container"):
                yield Static(self.title or "AI Response", id="response-title")
                yield Static(f"Response ({len(self.response_content)} characters)", id="response-info")

                # Create scrollable response area
                yield TextArea(
                    text=self.response_content,
                    read_only=True,
                    id="response-content"
                )

                yield Button("Close", id="close-response", variant="primary")

        async def on_button_pressed(self, event) -> None:
            """Handle button presses."""
            if event.button.id == "close-response":
                self.dismiss()

        def on_key(self, event) -> None:
            """Handle key presses."""
            if event.key == "escape":
                self.dismiss()

        DEFAULT_CSS = """
        ResponseViewerScreen {
            align: center middle;
        }

        #response-container {
            background: $surface;
            border: thick #00FFFF;
            width: 80%;
            height: 80%;
            padding: 1;
        }

        #response-title {
            text-align: center;
            background: $primary;
            color: $text;
            padding: 0 1;
            margin-bottom: 1;
        }

        #response-info {
            text-align: center;
            color: $accent;
            margin-bottom: 1;
        }

        #response-content {
            height: 30;
            border: solid #87CEEB;
            margin-bottom: 1;
        }

        #close-response {
            width: 20;
            margin: 0 20;
        }
        """


    class QuestionResponseScreen:
        """Dedicated screen for displaying question responses with navigation options."""

        def __init__(self, response_content: str, title: str = "Question Response", app_instance=None):
            self.response_content = response_content
            self.title = title or "Question Response"
            self.app_instance = app_instance

        def create_screen_class(self):
            """Create the screen class dynamically."""
            response_content = self.response_content
            title = self.title
            app_instance = self.app_instance

            class ResponseScreen(Screen):
                """Screen for displaying AI response with navigation options."""

                BINDINGS = [
                    ("ctrl+b", "back_to_main", "Back"),
                    ("ctrl+q", "quit_app", "Quit"),
                    ("f1", "help", "Help"),
                    ("ctrl+n", "ask_another", "Ask Another"),
                    ("escape", "back_to_main", "Back"),
                ]

                def compose(self):
                    """Compose the response screen."""
                    yield Header(show_clock=True)

                    with Vertical():
                        yield Static(f"📋 {title}", classes="response-title")
                        yield Static(f"Response Length: {len(response_content)} characters", classes="response-info")

                        # Scrollable response area
                        with ScrollableContainer(id="response-scroll"):
                            yield TextArea(
                                text=response_content,
                                read_only=True,
                                id="response-content",
                                language="markdown"
                            )

                        # Action buttons
                        with Horizontal(classes="button-row"):
                            yield Button("Ask Another Question", id="ask-another", variant="primary")
                            yield Button("Back to Main Menu", id="back-main", variant="success")

                    yield Footer()

                async def on_button_pressed(self, event: Button.Pressed) -> None:
                    """Handle button presses."""
                    if event.button.id == "ask-another":
                        await self.action_ask_another()
                    elif event.button.id == "back-main":
                        await self.action_back_to_main()

                async def action_ask_another(self) -> None:
                    """Go back to question builder to ask another question."""
                    if app_instance and hasattr(app_instance, 'switch_to_question_builder'):
                        await app_instance.switch_to_question_builder()
                    else:
                        # Fallback: pop current screen
                        self.app.pop_screen()

                async def action_back_to_main(self) -> None:
                    """Return to main menu."""
                    # First, try the app_instance which should be the question builder
                    if app_instance and hasattr(app_instance, 'unified_app'):
                        unified_app = app_instance.unified_app
                        if unified_app and hasattr(unified_app, 'return_to_main_menu'):
                            await unified_app.return_to_main_menu()
                            return

                    # If that fails, try to find the unified app in the app chain
                    current_app = self.app
                    if hasattr(current_app, 'return_to_main_menu'):
                        return_method = getattr(current_app, 'return_to_main_menu', None)
                        if return_method:
                            await return_method()
                            return

                    # Fallback: Pop all screens to get back to main (should not happen in unified app)
                    while len(self.app.screen_stack) > 1:
                        self.app.pop_screen()

                async def action_quit_app(self) -> None:
                    """Quit the entire application."""
                    self.app.exit()

                async def action_help(self) -> None:
                    """Show help information."""
                    help_text = """
                    Response Viewer Help:

                    Navigation:
                    • Ask Another Question: Return to question builder with cleared form
                    • Back to Main Menu: Return to main workflow selection

                    Global Shortcuts:
                    • Ctrl+B / Esc: Back to main menu
                    • Ctrl+Q: Quit application
                    • Ctrl+N: Ask another question
                    • F1: This help
                    """
                    self.notify(help_text, severity="information")

                CSS = """
                .response-title {
                    text-style: bold;
                    color: $primary;
                    text-align: center;
                    margin: 1 0;
                    background: $surface;
                    border: solid #87CEEB;
                    padding: 1;
                }

                .response-info {
                    text-align: center;
                    color: $accent;
                    text-style: italic;
                    margin-bottom: 1;
                }

                #response-scroll {
                    height: 25;
                    border: thick #00FFFF;
                    margin: 1 0;
                }

                #response-content {
                    background: $surface;
                    border: none;
                    min-height: 100%;
                }

                .button-row {
                    align: center middle;
                    height: auto;
                    margin: 1 0;
                }

                .button-row Button {
                    width: 40%;
                    margin: 0 2;
                }
                """

            return ResponseScreen


def create_loading_screen(title: str = "Processing", message: str = "Please wait...") -> Optional['LoadingScreen']:
    """Create a loading screen instance."""
    if not TEXTUAL_AVAILABLE:
        return None

    # Access class from module globals to avoid self-import
    loading_screen_class = globals().get('LoadingScreen')
    if loading_screen_class:
        return loading_screen_class(title, message)
    return None


def create_response_viewer_screen(data: dict) -> Optional['ResponseViewerScreen']:
    """Create a response viewer screen instance."""
    if not TEXTUAL_AVAILABLE:
        return None

    # Access class from module globals to avoid self-import
    response_viewer_class = globals().get('ResponseViewerScreen')
    if response_viewer_class:
        # Extract content from the data dict - handle different possible keys
        content = data.get('content', data.get('response', data.get('text', str(data))))
        title = data.get('title', 'AI Response')
        return response_viewer_class(content, title)
    return None


def create_pattern_response_screen(response_content: str, title: str = "Pattern Response", app_instance=None):
    """Create a dedicated pattern response screen."""
    if not TEXTUAL_AVAILABLE:
        return None

    # Access class from module globals to avoid self-import
    question_response_class = globals().get('QuestionResponseScreen')
    if question_response_class:
        response_screen_builder = question_response_class(response_content, title, app_instance)
        return response_screen_builder.create_screen_class()
    return None


def create_question_response_screen(question: str, response: str) -> Optional['QuestionResponseScreen']:
    """Create a question response screen instance."""
    if not TEXTUAL_AVAILABLE:
        return None

    # Access class from module globals to avoid self-import
    question_response_class = globals().get('QuestionResponseScreen')
    if question_response_class:
        return question_response_class(question, response)
    return None
__all__ = [
    'LoadingScreen', 'ResponseViewerScreen', 'QuestionResponseScreen',
    'create_loading_screen', 'create_response_viewer_screen', 'create_question_response_screen',
    'create_pattern_response_screen'
]
