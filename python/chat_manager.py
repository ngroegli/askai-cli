import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from system_outputs import SystemOutput
from system_configuration import SystemConfiguration

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
                        response: str, outputs: Optional[List[Dict[str, Any]]] = None,
                        system_outputs: Optional[List[SystemOutput]] = None,
                        system_config: Optional[SystemConfiguration] = None) -> None:
        """Add a new conversation to the chat history.
        
        Args:
            chat_id: The chat identifier
            messages: List of message dictionaries sent to the AI
            response: The AI's response
            outputs: Optional structured outputs from the AI
            system_outputs: Optional system output definitions for validation
            system_config: Optional system configuration used
        """
        chat_file = self._get_chat_file_path(chat_id)
        if not os.path.exists(chat_file):
            raise ValueError(f"Chat {chat_id} does not exist")

        # Validate outputs if provided
        if outputs and system_outputs:
            valid, error = self.validate_outputs(outputs, system_outputs)
            if not valid:
                raise ValueError(f"Invalid outputs: {error}")

        # Validate configuration if provided
        if system_config:
            valid, error = self.validate_configuration(system_config)
            if not valid:
                raise ValueError(f"Invalid configuration: {error}")

        with open(chat_file, 'r') as f:
            chat_data = json.load(f)

        # Extract only the new messages (not from history)
        current_messages = []
        
        # Add system messages if present
        system_messages = [msg for msg in messages if msg['role'] == 'system']
        if system_messages:
            current_messages.extend(system_messages)
        
        # Add only the last user message
        user_messages = [msg for msg in messages if msg['role'] == 'user']
        if user_messages:
            current_messages.append(user_messages[-1])  # Only keep the latest user message

        conversation = {
            "timestamp": datetime.now().isoformat(),
            "messages": current_messages,
            "response": response,
        }
        
        # Add structured outputs if provided
        if outputs:
            conversation["outputs"] = outputs
            
        # Add system configuration if provided
        if system_config:
            conversation["system_config"] = {
                "model": system_config.model.__dict__,
                "format_instructions": system_config.format_instructions
            }

        chat_data['conversations'].append(conversation)

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

    def select_chat(self, allow_new: bool = True) -> Optional[str]:
        """Display an interactive chat selection menu.
        
        Args:
            allow_new: Whether to show the option to create a new chat
            
        Returns:
            Optional[str]: Selected chat ID, 'new' for new chat, or None if selection cancelled
        """
        chats = self.list_chats()
        
        if not chats:
            print("No existing chats found.")
            if allow_new:
                print("Use -pc to create a new chat.")
            return None
            
        print("\nAvailable chats:")
        print("-" * 60)
        
        # Display chats with index
        for i, chat in enumerate(chats, 1):
            print(f"{i}. Chat ID: {chat['chat_id']}")
            print(f"   Created: {chat['created_at']}")
            print(f"   Messages: {chat['conversation_count']}")
            print("-" * 60)
        
        print("\nOptions:")
        if allow_new:
            print("0. Create new chat")
        print("1-{0}. Select existing chat".format(len(chats)))
        print("q. Quit")
        
        while True:
            max_choice = len(chats)
            min_choice = 0 if allow_new else 1
            choice = input(f"\nEnter your choice ({min_choice}-{max_choice} or q): ").lower()
            
            if choice == 'q':
                return None
            
            try:
                choice_num = int(choice)
                if allow_new and choice_num == 0:
                    return 'new'
                elif 1 <= choice_num <= len(chats):
                    return chats[choice_num - 1]['chat_id']
                else:
                    print(f"Please enter a number between {min_choice} and {max_choice}")
            except ValueError:
                print("Please enter a valid number or 'q' to quit")

    def validate_outputs(self, outputs: List[Dict[str, Any]], 
                        system_outputs: List[SystemOutput]) -> tuple[bool, Optional[str]]:
        """Validate AI outputs against the system's output definitions.
        
        Args:
            outputs: The outputs to validate
            system_outputs: The system's output definitions
            
        Returns:
            tuple[bool, Optional[str]]: Success flag and error message if validation fails
        """
        required_outputs = {output.name: output for output in system_outputs if output.required}
        
        # Check all required outputs are present
        for name, output_def in required_outputs.items():
            if not any(o['name'] == name for o in outputs):
                return False, f"Missing required output '{name}'"
                
        # Validate each provided output
        for output in outputs:
            output_def = next((o for o in system_outputs if o.name == output['name']), None)
            if not output_def:
                return False, f"Unknown output '{output['name']}'"
                
            valid, error = output_def.validate_value(output['value'])
            if not valid:
                return False, f"Invalid output '{output['name']}': {error}"
                
        return True, None

    def validate_configuration(self, config: SystemConfiguration) -> tuple[bool, Optional[str]]:
        """Validate a system's model configuration.
        
        Args:
            config: The system configuration to validate
            
        Returns:
            tuple[bool, Optional[str]]: Success flag and error message if validation fails
        """
        if not config.model:
            return False, "Missing model configuration"
            
        if not config.model.model_name:
            return False, "Missing model name in configuration"
            
        if not config.model.provider:
            return False, "Missing model provider in configuration"
            
        return True, None

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
            # Only include the user question and AI response for context
            # Find the last user message in the conversation
            user_message = None
            for msg in conv['messages']:
                if msg['role'] == 'user':
                    user_message = msg
            
            if user_message:
                context_messages.append(user_message)
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
            
            # Print conversations
            for msg in conv['messages']:
                if msg['role'] == 'user':
                    print(f"\nUser: {msg['content']}")

                if msg['role'] == 'assistant':
                    print(f"\nAssistant: {msg['content']}")
                    print("-" * 25) # Print line after eacht answer
                    
            # Print AI response
            print(f"\nAssistant: {conv['response']}\n")
            print("=" * 50)
