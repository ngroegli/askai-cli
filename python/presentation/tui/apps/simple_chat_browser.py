"""
Simple and robust chat browser for quick listing and selection.
"""

from typing import Optional

try:
    from textual.app import App
    from textual.widgets import Header, Footer, Static, ListView, ListItem, Label
    from textual.binding import Binding
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    App = object


if TEXTUAL_AVAILABLE:
    class SimpleChatBrowser(App):
        """Simple chat browser for listing and quick selection."""

        CSS = """
        ListView {
            height: 1fr;
        }

        .chat-item {
            padding: 1;
        }

        .chat-name {
            text-style: bold;
        }

        .chat-description {
            color: $text-muted;
        }
        """

        BINDINGS = [
            Binding("q", "quit", "Quit"),
            Binding("escape", "quit", "Quit"),
            Binding("enter", "select", "Select"),
        ]

        def __init__(self, chat_manager, **kwargs):
            super().__init__(**kwargs)
            self.chat_manager = chat_manager
            self.chats = []
            self.selected_chat = None

        def compose(self):
            """Compose the application UI."""
            yield Header()
            yield Static("Chat Browser - Use arrow keys to navigate, Enter to select, Q to quit",
                        classes="help-text")

            # Create empty list view - will populate after mounting
            yield ListView(id="chat-list")
            yield Footer()

        def on_mount(self):
            """Called after the widget is mounted."""
            self.load_and_populate_chats()

        def load_and_populate_chats(self):
            """Load chats and populate the list view."""
            # Load chats from the chat manager
            self.load_chats()

            # Get the list view and populate it
            chat_list = self.query_one("#chat-list", ListView)

            if not self.chats:
                chat_list.append(ListItem(Label("No chats found"), name="none"))
                return

            for i, chat in enumerate(self.chats):
                chat_id = chat.get('chat_id', 'Unknown')
                created_at = chat.get('created_at', '')
                message_count = chat.get('conversation_count', 0)

                # Create list item with chat info
                item_text = f"[bold]{chat_id}[/bold]"
                if created_at:
                    item_text += f"\n  Created: {created_at}"
                if message_count:
                    item_text += f" | Messages: {message_count}"

                chat_list.append(ListItem(Label(item_text), name=str(i)))

        def load_chats(self):
            """Load chats from the chat manager."""
            try:
                self.chats = self.chat_manager.list_chats()

                # Also check for corrupted files
                corrupted_files = self.chat_manager.scan_corrupted_chat_files()
                for chat_id in corrupted_files:
                    self.chats.append({
                        'chat_id': f"{chat_id} (CORRUPTED)",
                        'created_at': 'Unknown',
                        'conversation_count': 0,
                        'corrupted': True
                    })

            except Exception as e:
                self.chats = [{'chat_id': f'Error loading chats: {e}', 'created_at': '', 'conversation_count': 0}]

        def on_list_view_selected(self, event: ListView.Selected):
            """Handle chat selection."""
            if event.list_view.id == "chat-list":
                try:
                    if event.item.name and event.item.name != "none":
                        index = int(event.item.name)
                        if 0 <= index < len(self.chats):
                            self.selected_chat = self.chats[index]
                            self.action_select()
                except (ValueError, IndexError):
                    pass

        def action_select(self):
            """Select the current chat and exit."""
            if self.selected_chat and not self.selected_chat.get('chat_id', '').startswith('Error'):
                self.exit(self.selected_chat)
            else:
                self.exit(None)

        def action_quit(self):
            """Quit the application."""
            self.exit(None)


def run_simple_chat_browser(chat_manager) -> Optional[dict]:
    """
    Run the simple chat browser and return the selected chat.
    """
    if not TEXTUAL_AVAILABLE:
        return None

    try:
        app = SimpleChatBrowser(chat_manager)
        result = app.run()
        return result
    except Exception:
        # If TUI fails, return None to trigger fallback
        return None


__all__ = ['SimpleChatBrowser', 'run_simple_chat_browser']
