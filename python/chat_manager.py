import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

class ChatManager:
    def __init__(self, config: Dict[str, Any]):
        """Initialize the chat manager.
        
        Args:
            config: Application configuration dictionary
        """
        chat_config = config.get('chat', {})
        self.storage_path = os.path.expanduser(
            chat_config.get('storage_path', '~/.askai/chats')
        )
        self.max_history = chat_config.get('max_history', 10)
        os.makedirs(self.storage_path, exist_ok=True)

    def _generate_chat_id(self) -> str:
        """Generate a short unique chat ID."""
        return str(uuid.uuid4())[:8]

    def _get_chat_file_path(self, chat_id: str) -> str:
        """Get the full path for a chat file.
        
        Args:
            chat_id: The unique chat identifier
            
        Returns:
            str: Full path to the chat file
        """
        return os.path.join(self.storage_path, f"{chat_id}.json")

    def create_chat(self) -> str:
        """Create a new chat file with a unique ID.
        
        Returns:
            str: The generated chat ID
        """
        chat_id = self._generate_chat_id()
        chat_file = self._get_chat_file_path(chat_id)
        
        chat_data = {
            "chat_id": chat_id,
            "created_at": datetime.now().isoformat(),
            "conversations": []
        }
        
        with open(chat_file, 'w') as f:
            json.dump(chat_data, f, indent=2)
            
        return chat_id

    def add_conversation(self, chat_id: str, messages: List[Dict[str, str]], 
                        response: str) -> None:
        """Add a new conversation to the chat history.
        
        Args:
            chat_id: The chat identifier
            messages: List of message dictionaries sent to the AI
            response: The AI's response
        """
        chat_file = self._get_chat_file_path(chat_id)
        if not os.path.exists(chat_file):
            raise ValueError(f"Chat {chat_id} does not exist")

        with open(chat_file, 'r') as f:
            chat_data = json.load(f)

        chat_data['conversations'].append({
            "timestamp": datetime.now().isoformat(),
            "messages": messages,
            "response": response
        })

        with open(chat_file, 'w') as f:
            json.dump(chat_data, f, indent=2)

    def get_chat_history(self, chat_id: str, 
                        max_conversations: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get the conversation history for a chat.
        
        Args:
            chat_id: The chat identifier
            max_conversations: Maximum number of past conversations to return
            
        Returns:
            List[Dict[str, Any]]: List of conversation records
        """
        chat_file = self._get_chat_file_path(chat_id)
        if not os.path.exists(chat_file):
            raise ValueError(f"Chat {chat_id} does not exist")

        with open(chat_file, 'r') as f:
            chat_data = json.load(f)

        conversations = chat_data['conversations']
        if max_conversations:
            conversations = conversations[-max_conversations:]

        return conversations

    def list_chats(self) -> List[Dict[str, Any]]:
        """List all available chat files.
        
        Returns:
            List[Dict[str, Any]]: List of chat metadata
        """
        chats = []
        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                file_path = os.path.join(self.storage_path, filename)
                with open(file_path, 'r') as f:
                    chat_data = json.load(f)
                    chats.append({
                        'chat_id': chat_data['chat_id'],
                        'created_at': chat_data['created_at'],
                        'conversation_count': len(chat_data['conversations'])
                    })
        return sorted(chats, key=lambda x: x['created_at'], reverse=True)

    def build_context_messages(self, chat_id: str) -> List[Dict[str, str]]:
        """Build context messages from chat history.
        
        Args:
            chat_id: The chat identifier
            
        Returns:
            List[Dict[str, str]]: List of message dictionaries for context
        """
        context_messages = []
        conversations = self.get_chat_history(chat_id, self.max_history)
        
        for conv in conversations:
            for msg in conv['messages']:
                if msg['role'] != 'system':  # Don't include system messages from history
                    context_messages.append(msg)
            context_messages.append({
                "role": "assistant",
                "content": conv['response']
            })
            
        return context_messages

    def display_chat(self, chat_id: str) -> None:
        """Display chat history in a readable format.
        
        Args:
            chat_id: The chat identifier
        """
        chat_file = self._get_chat_file_path(chat_id)
        if not os.path.exists(chat_file):
            raise ValueError(f"Chat {chat_id} does not exist")

        with open(chat_file, 'r') as f:
            chat_data = json.load(f)

        print(f"\nChat ID: {chat_data['chat_id']}")
        print(f"Created: {chat_data['created_at']}\n")
        
        for i, conv in enumerate(chat_data['conversations'], 1):
            print(f"\nConversation {i} - {conv['timestamp']}")
            print("-" * 50)
            
            # Print user messages
            for msg in conv['messages']:
                if msg['role'] == 'user':
                    print(f"\nUser: {msg['content']}")
                    
            # Print AI response
            print(f"\nAssistant: {conv['response']}\n")
            print("=" * 50)
