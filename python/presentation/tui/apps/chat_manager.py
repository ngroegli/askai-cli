"""
Interactive chat manager using Textual TUI framework.

Provides a modern interface for browsing, managing, and viewing chat history
with real-time filtering, sorting, and preview capabilities.
"""

import os
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

# Safe imports with fallbacks
try:
    from textual.app import App
    from textual.containers import Horizontal, Vertical, Container
    from textual.widgets import (
        Header, Footer, Input, Static, DataTable, Button
    )
    from textual.binding import Binding
    TEXTUAL_AVAILABLE = True
except ImportError:
    # Fallback classes for when textual is not available
    TEXTUAL_AVAILABLE = False
    App = object
    Container = object


class ChatItem:
    """Represents a chat with metadata."""

    def __init__(self, chat_id: str, path: str, created_at: str = "",
                 message_count: int = 0, corrupted: bool = False):
        self.chat_id = chat_id
        self.path = path
        self.created_at = created_at
        self.message_count = message_count
        self.corrupted = corrupted
        self.content: Optional[str] = None
        self.last_modified = ""

        # Try to get file stats
        try:
            if os.path.exists(path):
                stat = os.stat(path)
                self.last_modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
        except Exception:
            pass

    def load_content(self) -> str:
        """Load chat content from file."""
        if self.content is None:
            try:
                with open(self.path, 'r', encoding='utf-8') as f:
                    self.content = f.read()
            except Exception as e:
                self.content = f"Error loading chat: {e}"
                self.corrupted = True
        return self.content

    def get_preview(self, max_lines: int = 20) -> str:
        """Get a preview of the chat content."""
        if self.corrupted:
            return "❌ This chat file is corrupted and cannot be displayed."

        try:
            content = self.load_content()
            # Try to parse as JSON and extract messages
            chat_data = json.loads(content)
            messages = chat_data.get('messages', [])

            if not messages:
                return "No messages in this chat."

            preview_lines = []
            for msg in messages[-5:]:  # Show last 5 messages
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                timestamp = msg.get('timestamp', '')

                preview_lines.append(f"[{role.upper()}] {timestamp}")
                preview_lines.append(content[:200] + ("..." if len(content) > 200 else ""))
                preview_lines.append("")

                if len(preview_lines) >= max_lines:
                    break

            return '\n'.join(preview_lines)

        except Exception as e:
            return f"Error reading chat content: {e}"

    def get_summary(self) -> Dict[str, Any]:
        """Get chat summary information."""
        return {
            'id': self.chat_id,
            'created': self.created_at,
            'modified': self.last_modified,
            'messages': self.message_count,
            'corrupted': self.corrupted,
            'path': self.path
        }


if TEXTUAL_AVAILABLE:
    class ChatPreview(Container):
        """Widget for displaying chat content preview."""

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.chat: Optional[ChatItem] = None

        def update_preview(self, chat: Optional[ChatItem]):
            """Update the preview with new chat content."""
            self.chat = chat
            self.remove_children()

            if chat is None:
                self.mount(Static("Select a chat to preview", classes="preview-placeholder"))
            else:
                # Show chat metadata
                summary = chat.get_summary()
                self.mount(Static(f"Chat ID: {summary['id']}", classes="preview-title"))
                self.mount(Static(f"Created: {summary['created']}", classes="preview-meta"))
                self.mount(Static(f"Modified: {summary['modified']}", classes="preview-meta"))
                self.mount(Static(f"Messages: {summary['messages']}", classes="preview-meta"))

                if summary['corrupted']:
                    self.mount(Static("❌ CORRUPTED FILE", classes="preview-error"))

                self.mount(Static("─" * 50, classes="preview-separator"))

                # Show content preview
                content = chat.get_preview(30)
                self.mount(Static(content, classes="preview-content"))


    class ChatTable(DataTable):
        """Custom DataTable for chats with enhanced functionality."""

        def __init__(self, chats: List[ChatItem], **kwargs):
            super().__init__(**kwargs)
            self.all_chats = chats
            self.filtered_chats = chats.copy()
            self.setup_table()
            self.populate_table()

        def setup_table(self):
            """Setup table columns."""
            self.add_columns("ID", "Created", "Messages", "Status", "Modified")
            self.cursor_type = "row"
            self.show_header = True

        def populate_table(self):
            """Populate the table with current filtered chats."""
            self.clear()
            for chat in self.filtered_chats:
                status = "❌ Corrupted" if chat.corrupted else "✓ OK"
                self.add_row(
                    chat.chat_id,
                    chat.created_at,
                    str(chat.message_count),
                    status,
                    chat.last_modified,
                    key=chat.chat_id
                )

        def filter_chats(self, search_term: str):
            """Filter chats based on search term."""
            search_term = search_term.lower().strip()
            if not search_term:
                self.filtered_chats = self.all_chats.copy()
            else:
                self.filtered_chats = [
                    chat for chat in self.all_chats
                    if (search_term in chat.chat_id.lower() or
                        search_term in chat.created_at.lower() or
                        search_term in chat.last_modified.lower())
                ]
            self.populate_table()

        def get_selected_chat(self) -> Optional[ChatItem]:
            """Get the currently selected chat."""
            if not self.cursor_coordinate or self.cursor_coordinate.row >= len(self.filtered_chats):
                return None
            return self.filtered_chats[self.cursor_coordinate.row]

        def sort_chats(self, column: str, reverse: bool = False):
            """Sort chats by the specified column."""
            if column == "Created":
                self.filtered_chats.sort(key=lambda x: x.created_at, reverse=reverse)
            elif column == "Messages":
                self.filtered_chats.sort(key=lambda x: x.message_count, reverse=reverse)
            elif column == "Modified":
                self.filtered_chats.sort(key=lambda x: x.last_modified, reverse=reverse)
            elif column == "Status":
                self.filtered_chats.sort(key=lambda x: x.corrupted, reverse=reverse)
            else:  # ID
                self.filtered_chats.sort(key=lambda x: x.chat_id, reverse=reverse)

            self.populate_table()


    class ChatManager(App):
        """Main application for managing chats."""

        CSS = """
        Screen {
            layout: horizontal;
        }

        #chat-panel {
            width: 60%;
            border-right: thick $surface;
        }

        #preview-panel {
            width: 40%;
            padding: 1;
        }

        #search {
            margin: 1;
        }

        #actions {
            height: 3;
            margin: 1;
        }

        .preview-title {
            text-style: bold;
            color: $primary;
        }

        .preview-meta {
            color: $secondary;
        }

        .preview-error {
            color: $error;
            text-style: bold;
        }

        .preview-separator {
            color: $surface;
            margin-bottom: 1;
        }

        .preview-content {
            margin-top: 1;
        }

        .preview-placeholder {
            color: $secondary;
            text-align: center;
            margin-top: 5;
        }

        .action-buttons {
            layout: horizontal;
        }
        """

        BINDINGS = [
            Binding("ctrl+q", "quit", "Quit"),
            Binding("ctrl+c", "quit", "Quit"),
            Binding("escape", "quit", "Quit"),
            Binding("ctrl+f", "focus_search", "Search"),
            Binding("/", "focus_search", "Search"),
            Binding("enter", "select_chat", "Select"),
            Binding("delete", "delete_chat", "Delete"),
            Binding("ctrl+r", "refresh", "Refresh"),
            Binding("f5", "refresh", "Refresh"),
        ]

        def __init__(self, chat_manager, **kwargs):
            super().__init__(**kwargs)
            self.chat_manager = chat_manager
            self.chats: List[ChatItem] = []
            self.selected_chat: Optional[ChatItem] = None

        def compose(self):
            """Compose the application layout."""
            yield Header(show_clock=True)

            # Load chats
            self.load_chats()

            with Horizontal():
                with Vertical(id="chat-panel"):
                    yield Input(placeholder="Search chats...", id="search")
                    yield ChatTable(self.chats, id="chat-table")

                    with Horizontal(id="actions", classes="action-buttons"):
                        yield Button("View", id="view-btn", variant="primary")
                        yield Button("Delete", id="delete-btn", variant="error")
                        yield Button("Refresh", id="refresh-btn")

                yield ChatPreview(id="preview-panel")

            yield Footer()

        def load_chats(self):
            """Load chats from the chat manager."""
            try:
                # Get chats from the chat manager
                chat_data = self.chat_manager.list_chats()
                corrupted_files = self.chat_manager.scan_corrupted_chat_files()

                # Load regular chats
                for chat_info in chat_data:
                    chat_id = chat_info.get('chat_id', 'Unknown')
                    created_at = chat_info.get('created_at', '')
                    message_count = chat_info.get('conversation_count', 0)
                    path = chat_info.get('path', '')

                    chat = ChatItem(
                        chat_id=chat_id,
                        path=path,
                        created_at=created_at,
                        message_count=message_count,
                        corrupted=False
                    )
                    self.chats.append(chat)

                # Add corrupted chats
                for chat_id in corrupted_files:
                    # Try to construct path (this might need adjustment based on chat_manager implementation)
                    path = os.path.join(self.chat_manager.get_chat_dir(), f"{chat_id}.json")
                    chat = ChatItem(
                        chat_id=chat_id,
                        path=path,
                        created_at="Unknown",
                        message_count=0,
                        corrupted=True
                    )
                    self.chats.append(chat)

            except Exception:
                # Fallback for testing or when chat manager is not available
                self.chats = [
                    ChatItem(
                        chat_id="example_chat_001",
                        path="/tmp/example_chat.json",
                        created_at="2024-01-01 10:00",
                        message_count=5,
                        corrupted=False
                    )
                ]

        def on_mount(self):
            """Called when the app is mounted."""
            search_input = self.query_one("#search", Input)
            search_input.focus()

        def on_input_changed(self, event: Input.Changed):
            """Handle search input changes."""
            if event.input.id == "search":
                chat_table = self.query_one("#chat-table", ChatTable)
                chat_table.filter_chats(event.value)

        def on_data_table_row_selected(self, event: DataTable.RowSelected):
            """Handle chat selection."""
            if event.data_table.id == "chat-table":
                chat_table = self.query_one("#chat-table", ChatTable)
                selected_chat = chat_table.get_selected_chat()

                if selected_chat:
                    self.selected_chat = selected_chat
                    preview = self.query_one("#preview-panel", ChatPreview)
                    preview.update_preview(selected_chat)

        def on_button_pressed(self, event: Button.Pressed):
            """Handle button presses."""
            if event.button.id == "view-btn":
                self.action_select_chat()
            elif event.button.id == "delete-btn":
                self.action_delete_chat()
            elif event.button.id == "refresh-btn":
                self.action_refresh()

        def action_focus_search(self):
            """Focus the search input."""
            search_input = self.query_one("#search", Input)
            search_input.focus()

        def action_select_chat(self):
            """Select the current chat and exit."""
            if self.selected_chat:
                self.exit(self.selected_chat)
            else:
                # If no chat selected, try to select the first one
                chat_table = self.query_one("#chat-table", ChatTable)
                if chat_table.filtered_chats:
                    self.exit(chat_table.filtered_chats[0])

        def action_delete_chat(self):
            """Delete the selected chat."""
            if self.selected_chat:
                # This would need to be implemented with a confirmation dialog
                # For now, just show a message
                self.notify(f"Delete functionality for {self.selected_chat.chat_id} not implemented yet")

        def action_refresh(self):
            """Refresh the chat list."""
            self.chats.clear()
            self.load_chats()
            chat_table = self.query_one("#chat-table", ChatTable)
            chat_table.all_chats = self.chats
            chat_table.filter_chats("")  # Reset filter
            self.notify("Chat list refreshed")

        async def action_quit(self):
            """Quit the application."""
            self.exit(None)


def run_chat_manager(chat_manager) -> Optional[ChatItem]:
    """
    Run the chat manager TUI and return the selected chat.

    Args:
        chat_manager: The chat manager instance

    Returns:
        Selected ChatItem or None if cancelled
    """
    if not TEXTUAL_AVAILABLE:
        return None

    app = ChatManager(chat_manager)
    result = app.run()
    return result


# Fallback function for when Textual is not available
def chat_manager_fallback(chat_manager):
    """Fallback chat manager using simple CLI."""
    print("Textual TUI not available, falling back to simple interface...")
    chats = chat_manager.list_chats()
    corrupted_files = chat_manager.scan_corrupted_chat_files()

    if not chats and not corrupted_files:
        print("No chat history found.")
        return None

    all_items = []

    if chats:
        print("\nAvailable chats:")
        for i, chat in enumerate(chats, 1):
            chat_id = chat.get('chat_id', 'Unknown')
            created_at = chat.get('created_at', '')
            message_count = chat.get('conversation_count', 0)
            print(f"{i}. {chat_id}")
            print(f"   Created: {created_at}, Messages: {message_count}")
            all_items.append(ChatItem(
                chat_id=chat_id,
                path=chat.get('path', ''),
                created_at=created_at,
                message_count=message_count,
                corrupted=False
            ))

    if corrupted_files:
        print(f"\nCorrupted files found ({len(corrupted_files)}):")
        for i, chat_id in enumerate(corrupted_files, len(all_items) + 1):
            print(f"{i}. {chat_id} (CORRUPTED)")
            all_items.append(ChatItem(
                chat_id=chat_id,
                path="",
                created_at="Unknown",
                message_count=0,
                corrupted=True
            ))

    try:
        choice = input(f"\nSelect chat (1-{len(all_items)}) or press Enter to cancel: ").strip()
        if not choice:
            return None

        index = int(choice) - 1
        if 0 <= index < len(all_items):
            return all_items[index]
        else:
            print("Invalid selection.")
            return None
    except (ValueError, KeyboardInterrupt):
        print("\nCancelled.")
        return None


__all__ = ['ChatManager', 'ChatItem', 'run_chat_manager', 'chat_manager_fallback']
