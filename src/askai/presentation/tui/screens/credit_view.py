"""Credit balance view screen for the TUI."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Container
from textual.widgets import Header, Footer, Button, Static

from askai.core.ai.openrouter import OpenRouterClient
from askai.presentation.tui.screens.base_screen import BaseScreen
from askai.presentation.tui.styles import StyledStatic


class CreditViewScreen(BaseScreen):
    """Screen for displaying OpenRouter credit balance and usage details."""

    BINDINGS = BaseScreen.BINDINGS + [
        Binding("r", "refresh", "Refresh", show=True),
    ]

    CSS = """
        .credit-view-container {
            height: 1fr;
            padding: 2;
        }

        .content-panel {
            border: round #00FFFF;
            padding: 2;
            background: $surface;
            height: 1fr;
            margin-bottom: 2;
        }

        .loading-text {
            color: $accent;
            text-style: italic;
            text-align: center;
        }

        .success-text {
            color: $success;
        }

        .error-text {
            color: $error;
        }

        .button-container {
            height: auto;
            padding: 1;
        }

        /* Uniform button styling */
        Button.primary {
            background: $primary;
            color: $text;
            border: none;
            text-style: bold;
            width: 12;
            height: 3;
            margin: 1;
        }

        Button.primary:hover {
            background: $primary 80%;
        }

        Button.primary:focus {
            border: thick #00FFFF;
        }
    """

    def __init__(self):
        super().__init__()
        self.credit_data = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)

        with Container(classes="credit-view-container"):
            yield StyledStatic(
                "Loading credit information...",
                id="credit-content",
                classes="content-panel loading-text"
            )

            with Horizontal(classes="button-container"):
                yield Button("Refresh", id="refresh-credits", variant="primary")
                yield Button("Back", id="back-button", variant="primary")

        yield Footer()

    async def on_mount(self) -> None:
        """Called when screen is mounted."""
        await self.load_credit_data()

    async def action_refresh(self) -> None:
        """Refresh credit data."""
        await self.load_credit_data()

    async def load_credit_data(self) -> None:
        """Load credit balance data from OpenRouter."""
        try:
            content_widget = self.query_one("#credit-content", Static)
            content_widget.update("[cyan]Loading credit information...[/cyan]")
            content_widget.remove_class("error-text")
            content_widget.add_class("loading-text")

            # Create OpenRouter client
            client = OpenRouterClient()
            self.credit_data = client.get_credit_balance()

            # Format the credit information
            await self.display_credit_info()

        except Exception as e:
            content_widget = self.query_one("#credit-content", Static)
            content_widget.update(f"[red]Error loading credit data:[/red]\n\n{str(e)}")
            content_widget.remove_class("loading-text")
            content_widget.add_class("error-text")

    async def display_credit_info(self) -> None:
        """Display formatted credit information."""
        if not self.credit_data:
            return

        total_credits = self.credit_data.get('total_credits', 0)
        total_usage = self.credit_data.get('total_usage', 0)
        remaining_credits = total_credits - total_usage
        usage_percentage = (total_usage / total_credits * 100) if total_credits > 0 else 0

        # Create a progress bar representation
        bar_length = 40
        filled_length = int(bar_length * usage_percentage / 100)
        progress_bar = "█" * filled_length + "░" * (bar_length - filled_length)

        # Create detailed credit display with better formatting
        credit_display = f"""
[bold cyan]OpenRouter Account Information[/bold cyan]

[green]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/green]

[bold yellow]� Account Balance[/bold yellow]
  Total Credits:     [bold green]${total_credits:.4f}[/bold green]
  Total Usage:       [bold red]${total_usage:.4f}[/bold red]
  Remaining Credits: [bold blue]${remaining_credits:.4f}[/bold blue]

[bold cyan]Usage Overview[/bold cyan]
  Usage Percentage:  [bold]{usage_percentage:.1f}%[/bold]

  Progress: [{progress_bar}] {usage_percentage:.1f}%

  Credits Used:      {total_usage:.4f} / {total_credits:.4f}

[bold cyan]Account Details[/bold cyan]
  • Credit value is in USD
  • Usage includes all API calls to OpenRouter models
  • Real-time balance updated on refresh
  • Rate limits apply based on your account tier

[green]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/green]

[dim]Last updated: Just now[/dim]
        """.strip()

        content_widget = self.query_one("#credit-content", Static)
        content_widget.remove_class("loading-text")
        content_widget.remove_class("error-text")
        content_widget.update(credit_display)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "refresh-credits":
            await self.action_refresh()
        elif event.button.id == "back-button":
            await self.action_back()

    def get_help_text(self) -> str:
        """Get help text for credit view screen."""
        return """
Credit View Help:
• R or Ctrl+R - Refresh credit balance
• Escape - Go back to main interface
• Ctrl+Q - Quit application
• F1 - Show this help

This screen shows your OpenRouter account balance,
usage statistics, and remaining credits.
        """.strip()
