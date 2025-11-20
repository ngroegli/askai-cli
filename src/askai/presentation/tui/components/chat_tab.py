"""
Chat Browser Tab Component.
Handles chat browsing, viewing, and management.
"""

from typing import Optional, TYPE_CHECKING
from .base_tab import BaseTabComponent

# pylint: disable=import-error
try:
    from textual.widgets import Static, Button, ListView, ListItem, Label
    from textual.containers import Vertical, Horizontal
    from textual.message import Message

    # Import or define status mixin
    try:
        from ..common.utils import StatusMixin
    except ImportError:
        class StatusMixin:
            """Mixin for status functionality."""
            # No implementation needed for fallback
except ImportError:
    # Fallback classes
    class Static:
        """Fallback Static widget."""
    class Button:
        """Fallback Button widget."""
    class ListView:
        """Fallback ListView widget."""
    class ListItem:
        """Fallback ListItem widget."""
    class Label:
        """Fallback Label widget."""
    class Vertical:
        """Fallback Vertical container."""
    class Horizontal:
        """Fallback Horizontal container."""
    class Message:
        """Fallback Message class."""
    class StatusMixin:
        """Fallback StatusMixin."""

if TYPE_CHECKING:
    from textual.widgets import Static, Button, ListView, ListItem, Label
    from textual.containers import Vertical, Horizontal
    from textual.message import Message


class ChatTab(BaseTabComponent, StatusMixin):
    """Chat Browser tab component."""

    class ChatSelected(Message):
        """Message sent when a chat is selected."""
        def __init__(self, chat_data: dict) -> None:
            self.chat_data = chat_data
            super().__init__()

    class ChatAction(Message):
        """Message sent when a chat action is requested."""
        def __init__(self, action: str, chat_data: Optional[dict] = None) -> None:
            self.action = action  # 'new_chat', 'delete_chat', etc.
            self.chat_data = chat_data
            super().__init__()

    def __init__(self, *args, chat_manager=None, **kwargs):
        super().__init__("Chat Browser", *args, **kwargs)
        self.chat_manager = chat_manager
        self.chat_list = None
        self.chat_info = None
        self.selected_chat = None
        self.status_display = None

    def compose(self):
        """Compose the chat browser interface."""
        yield Static("Chat Browser", classes="panel-title")

        with Horizontal(classes="chat-browser-container"):
            # Left panel - Chat list
            with Vertical(classes="chat-list-panel"):
                yield Static("Available Chats", classes="panel-subtitle")
                self.chat_list = ListView(id="chat-list")
                yield self.chat_list

                # Action buttons
                with Horizontal(classes="button-row"):
                    yield Button("New Chat", variant="primary", id="new-chat-button")
                    yield Button("Delete", variant="error", id="delete-chat-button")
                    yield Button("Refresh", variant="default", id="refresh-chats-button")

            # Right panel - Chat details
            with Vertical(classes="chat-details-panel"):
                yield Static("Chat Details", classes="panel-subtitle")
                self.chat_info = Static("Select a chat to view details", id="chat-info")
                yield self.chat_info

                # Status
                self.status_display = Static("✅ Ready to browse chats", classes="status-text")
                yield self.status_display

    async def initialize(self):
        """Initialize the chat browser."""
        await self._load_chats()

    async def _load_chats(self):
        """Load chats into the list."""
        if not self.chat_manager or not self.chat_list:
            return

        try:
            chats = self.chat_manager.list_chats()
            corrupted_files = self.chat_manager.scan_corrupted_chat_files()

            self.chat_list.clear()

            # Add regular chats
            for chat in chats:
                chat_id = chat.get('chat_id', 'Unknown')
                message_count = chat.get('conversation_count', 0)

                label = f"💬 {chat_id} ({message_count} messages)"
                list_item = ListItem(Label(label), name=chat_id)
                # Store chat data in a custom way since we can't assign attributes directly
                self.chat_list.append(list_item)

            # Add corrupted files
            for corrupted in corrupted_files:
                filename = corrupted.get('filename', 'Unknown')
                label = f"🚫 {filename} (corrupted)"
                list_item = ListItem(Label(label), name=f"corrupted_{filename}")
                self.chat_list.append(list_item)

            total_count = len(chats) + len(corrupted_files)
            if self.status_display:
                self.status_display.update(f"✅ Loaded {total_count} chats, {len(corrupted_files)} corrupted")

        except Exception as e:
            if self.status_display:
                self.status_display.update(f"❌ Error loading chats: {e}")

    async def on_list_view_selected(self, event) -> None:
        """Handle chat selection."""
        if event.list_view.id == "chat-list" and event.item:
            chat_name = event.item.name
            if chat_name and not chat_name.startswith("corrupted_"):
                await self._display_chat_info(chat_name)
            else:
                self._display_corrupted_info(chat_name)

    async def _display_chat_info(self, chat_id: str):
        """Display information about the selected chat."""
        if not self.chat_manager or not self.chat_info:
            return

        try:
            # Get chat details
            chats = self.chat_manager.list_chats()
            selected_chat = next((c for c in chats if c.get('chat_id') == chat_id), None)

            if selected_chat:
                self.selected_chat = selected_chat
                chat_id = selected_chat.get('chat_id', 'Unknown')
                created_at = selected_chat.get('created_at', 'Unknown')
                message_count = selected_chat.get('conversation_count', 0)

                info_text = f"**Chat: {chat_id}**\n\n"
                info_text += f"📅 Created: {created_at}\n"
                info_text += f"💬 Messages: {message_count}\n"
                info_text += "📍 Status: Active\n"

                self.chat_info.update(info_text)
            else:
                self.chat_info.update("❌ Chat not found")

        except Exception as e:
            self.chat_info.update(f"❌ Error loading chat details: {e}")

    def _display_corrupted_info(self, corrupted_name: str):
        """Display information about corrupted chat."""
        if not self.chat_info:
            return

        filename = corrupted_name.replace("corrupted_", "")
        info_text = f"**Corrupted Chat: {filename}**\n\n"
        info_text += "🚫 Status: Corrupted\n"
        info_text += "⚠️ This chat file cannot be read\n"
        info_text += "🔧 Use the Delete button to remove it\n"

        self.chat_info.update(info_text)

    async def on_button_pressed(self, event) -> None:
        """Handle button presses."""
        if event.button.id == "new-chat-button":
            await self._new_chat()
        elif event.button.id == "delete-chat-button":
            await self._delete_chat()
        elif event.button.id == "refresh-chats-button":
            await self._load_chats()

    async def _new_chat(self) -> None:
        """Create a new chat."""
        if self.status_display:
            self.status_display.update("🔄 Creating new chat...")

        # Emit message to parent
        self.post_message(self.ChatAction("new_chat"))

    async def _delete_chat(self) -> None:
        """Delete the selected chat."""
        if not self.selected_chat:
            if self.status_display:
                self.status_display.update("❌ Please select a chat first")
            return

        if self.status_display:
            self.status_display.update("🔄 Deleting chat...")

        # Emit message to parent
        self.post_message(self.ChatAction("delete_chat", self.selected_chat))
