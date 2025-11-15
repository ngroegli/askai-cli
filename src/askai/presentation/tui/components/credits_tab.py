"""
Credits Tab Component.
Displays OpenRouter credit balance and usage information.
"""

from typing import TYPE_CHECKING
from datetime import datetime
from .base_tab import BaseTabComponent

from ..common import (
    Static, Button, ProgressBar, Vertical, Horizontal,
    VerticalScroll, StatusMixin
)

try:
    from askai.modules.ai import OpenRouterClient
except ImportError:
    if not TYPE_CHECKING:
        OpenRouterClient = object

        def load_config():
            """Fallback config loader."""
            return {}

if TYPE_CHECKING:
    from textual.widgets import Static, Button, ProgressBar
    from textual.containers import Vertical, Horizontal, VerticalScroll
    from askai.modules.ai import OpenRouterClient


class CreditsTab(BaseTabComponent, StatusMixin):
    """Credits monitoring tab component."""

    def __init__(self, *args, **kwargs):
        """Initialize the credits tab."""
        super().__init__("Credits", *args, **kwargs)
        self.openrouter_client = None
        self.credit_data = None
        self._initialize_openrouter_client()

    def _initialize_openrouter_client(self):
        """Initialize the OpenRouter client with configuration."""
        try:
            # Use the same pattern as CLI - let OpenRouterClient load its own config
            self.openrouter_client = OpenRouterClient()
        except Exception:
            self.openrouter_client = None

    def compose(self):
        """Compose the credits interface."""
        yield Static("Credits & Usage", classes="panel-title")

        with VerticalScroll(classes="credits-container"):
            # Credit Balance Section
            with Vertical(classes="credits-section"):
                yield Static("💰 Credit Balance", classes="section-title")

                with Vertical(id="balance-info", classes="info-box"):
                    yield Static("Loading credit information...", id="balance-display")
                    yield Static("", id="usage-display")
                    yield Static("", id="limit-display")

            # Usage Progress Section
            with Vertical(classes="credits-section"):
                yield Static("📊 Usage Overview", classes="section-title")

                with Vertical(id="usage-info", classes="info-box"):
                    yield Static("", id="usage-percentage")
                    yield ProgressBar(total=100, show_eta=False, id="usage-progress")
                    yield Static("", id="usage-details")

            # Recent Activity Section
            with Vertical(classes="credits-section"):
                yield Static("📈 Account Status", classes="section-title")

                with Vertical(id="activity-info", classes="info-box"):
                    yield Static("", id="account-status")
                    yield Static("", id="last-updated")

            # Action Buttons
            with Horizontal(classes="button-row"):
                yield Button("Refresh Credits", variant="primary", id="refresh-credits-button")
                yield Button("View Usage History", variant="default", id="usage-history-button")

        # Status
        yield Static("✅ Ready to check credits", id="status-display", classes="status-text")

    async def initialize(self):
        """Initialize the credits tab."""
        self.call_after_refresh(self._load_credits)

    def _load_credits(self):
        """Load credit information from OpenRouter API."""
        try:
            status_display = self.query_one("#status-display", Static)
            status_display.update("🔄 Loading credit information...")

            if not self.openrouter_client:
                status_display.update("❌ OpenRouter client not configured")
                self._show_error_state()
                return

            try:
                # Load credit data from OpenRouter API
                self.credit_data = self.openrouter_client.get_credit_balance()

                if self.credit_data and ('total_credits' in self.credit_data or 'data' in self.credit_data):
                    self._update_credit_display()
                    status_display.update("✅ Credit information loaded")
                else:
                    status_display.update("❌ No credit data available")
                    self._show_error_state()

            except Exception as api_error:
                status_display.update(f"❌ Error loading credits: {str(api_error)}")
                self._show_error_state()

        except Exception as e:
            status_display = self.query_one("#status-display", Static)
            status_display.update(f"❌ Error: {e}")

    def _update_credit_display(self):
        """Update the credit display with real data."""
        if not self.credit_data:
            return

        # Handle both data formats: direct or wrapped in 'data' key
        if 'data' in self.credit_data:
            data = self.credit_data['data']
            balance = data.get('balance', 0)
            usage = data.get('usage', 0)
            limit = data.get('limit', 0)
        else:
            # Direct format from OpenRouter API
            total_credits = self.credit_data.get('total_credits', 0)
            usage = self.credit_data.get('total_usage', 0)
            balance = total_credits - usage  # Calculate remaining balance
            limit = 0  # No limit information in direct format

        try:
            # Update balance information
            balance_display = self.query_one("#balance-display", Static)
            balance_display.update(f"💰 Current Balance: ${balance:.4f}")

            usage_display = self.query_one("#usage-display", Static)
            usage_display.update(f"📊 Total Usage: ${usage:.4f}")

            limit_display = self.query_one("#limit-display", Static)
            if limit > 0:
                remaining = limit - usage
                limit_display.update(f"🏦 Credit Limit: ${limit:.4f} (${remaining:.4f} remaining)")
            else:
                # Show total credits instead of limit for direct format
                total_credits = self.credit_data.get('total_credits', 0)
                limit_display.update(f"🏦 Total Credits: ${total_credits:.4f}")

            # Update usage progress
            if limit > 0:
                usage_percentage = (usage / limit) * 100
            else:
                # Use total credits for percentage calculation
                total_credits = self.credit_data.get('total_credits', 0)
                usage_percentage = (usage / total_credits * 100) if total_credits > 0 else 0

            usage_percent_display = self.query_one("#usage-percentage", Static)
            if limit > 0:
                usage_percent_display.update(f"Usage: {usage_percentage:.1f}% of limit")
            else:
                usage_percent_display.update(f"Usage: {usage_percentage:.1f}% of total credits")

            progress_bar = self.query_one("#usage-progress", ProgressBar)
            progress_bar.update(progress=min(usage_percentage, 100))

            # Color coding based on usage
            if usage_percentage > 90:
                color_status = "🔴 High usage - consider adding credits"
            elif usage_percentage > 75:
                color_status = "🟡 Moderate usage"
            else:
                color_status = "🟢 Good credit availability"

            usage_details = self.query_one("#usage-details", Static)
            usage_details.update(color_status)

            # Update account status
            account_status = self.query_one("#account-status", Static)
            if balance > 0:
                account_status.update("✅ Account Active - Credits Available")
            else:
                account_status.update("⚠️  Low Balance - Add Credits Soon")

            last_updated = self.query_one("#last-updated", Static)
            last_updated.update(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        except Exception:
            pass  # Widget not available yet

    def _show_error_state(self):
        """Show error state when credit data cannot be loaded."""
        try:
            balance_display = self.query_one("#balance-display", Static)
            balance_display.update("❌ Unable to load credit information")

            usage_display = self.query_one("#usage-display", Static)
            usage_display.update("Check your OpenRouter configuration")

            limit_display = self.query_one("#limit-display", Static)
            limit_display.update("")

            account_status = self.query_one("#account-status", Static)
            account_status.update("❌ Connection Error")

        except Exception:
            pass

    async def on_button_pressed(self, event) -> None:
        """Handle button presses."""
        if event.button.id == "refresh-credits-button":
            self._load_credits()
        elif event.button.id == "usage-history-button":
            # Placeholder for future usage history functionality
            status_display = self.query_one("#status-display", Static)
            status_display.update("📈 Usage history feature coming soon...")
