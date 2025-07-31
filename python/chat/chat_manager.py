"""
Unified chat management and persistence.
Handles chat history and context building in a simple logbook format.
Includes functionality for chat repair and management.
"""

import os
import json
import uuid
import re
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional


class ChatManager:
    """Unified chat manager handling chat persistence and context building in a simple logbook format."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        """Initialize the chat manager.
        
        Args:
            config: Application configuration dictionary
            logger: Optional logger instance
        """
        chat_config = config.get('chat', {})
        self.storage_path = os.path.expanduser(
            chat_config.get('storage_path', '~/.askai/chats')
        )
        self.max_history = chat_config.get('max_history', 10)
        self.logger = logger
        os.makedirs(self.storage_path, exist_ok=True)

    def _generate_chat_id(self) -> str:
        """Generate a short unique chat ID."""
        return str(uuid.uuid4())[:8]

    def _get_chat_file_path(self, chat_id: str) -> str:
        """Get the full path for a chat file."""
        return os.path.join(self.storage_path, f"{chat_id}.json")

    def create_chat(self) -> str:
        """Create a new chat file with a unique ID."""
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
                        system_outputs: Optional[List] = None,
                        system_config: Optional[Any] = None) -> None:
        """Add a new conversation to the chat history."""
        chat_file = self._get_chat_file_path(chat_id)
        if not os.path.exists(chat_file):
            raise ValueError(f"Chat {chat_id} does not exist")

        # Validate outputs if provided
        if outputs and system_outputs:
            valid, error = self._validate_outputs(outputs, system_outputs)
            if not valid:
                raise ValueError(f"Invalid outputs: {error}")

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
            current_messages.append(user_messages[-1])

        conversation = {
            "timestamp": datetime.now().isoformat(),
            "messages": current_messages,
            "response": response,
        }
        
        # Add structured outputs if provided
        if outputs:
            conversation["outputs"] = outputs
            
        # Add system configuration if provided (proper JSON serialization)
        if system_config:
            try:
                # Handle SystemConfiguration object and its nested objects
                def make_json_serializable(obj):
                    if hasattr(obj, '__dict__'):
                        result = {}
                        for key, value in obj.__dict__.items():
                            result[key] = make_json_serializable(value)
                        return result
                    elif isinstance(obj, list):
                        return [make_json_serializable(item) for item in obj]
                    elif isinstance(obj, dict):
                        return {k: make_json_serializable(v) for k, v in obj.items()}
                    elif hasattr(obj, 'value'):  # Handle Enum objects
                        return obj.value
                    else:
                        return obj
                        
                conversation["system_config"] = make_json_serializable(system_config)
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Could not serialize system config: {e}")

        chat_data['conversations'].append(conversation)

        with open(chat_file, 'w') as f:
            json.dump(chat_data, f, indent=2)

    def get_chat_history(self, chat_id: str, 
                        max_conversations: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get the conversation history for a chat."""
        chat_file = self._get_chat_file_path(chat_id)
        if not os.path.exists(chat_file):
            raise ValueError(f"Chat {chat_id} does not exist")

        try:
            with open(chat_file, 'r') as f:
                try:
                    chat_data = json.load(f)
                except json.JSONDecodeError as e:
                    error_msg = f"Chat file {chat_id} is corrupted: {str(e)}"
                    if self.logger:
                        self.logger.error(error_msg)
                    raise ValueError(error_msg)

            conversations = chat_data['conversations']
            if max_conversations:
                conversations = conversations[-max_conversations:]

            return conversations
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error reading chat history for {chat_id}: {str(e)}")
            raise ValueError(f"Failed to read chat history: {str(e)}")
            
    def repair_chat_file(self, chat_id: str) -> bool:
        """Attempt to repair a corrupted chat file.
        
        Args:
            chat_id: The ID of the chat to repair
            
        Returns:
            bool: True if repair was successful, False otherwise
        """
        chat_file = self._get_chat_file_path(chat_id)
        if not os.path.exists(chat_file):
            return False
            
        try:
            # First, make a backup
            backup_file = f"{chat_file}.bak"
            with open(chat_file, 'r') as f:
                content = f.read()
                
            with open(backup_file, 'w') as f:
                f.write(content)
                
            # Try to parse and fix JSON content
            try:
                with open(chat_file, 'r') as f:
                    lines = f.readlines()
                
                # Find last valid JSON object
                valid_content = "{\n"
                valid_content += '  "chat_id": "' + chat_id + '",\n'
                valid_content += '  "created_at": "' + datetime.now().isoformat() + '",\n'
                valid_content += '  "conversations": []\n'
                valid_content += "}\n"
                
                # Create new file with valid JSON
                with open(chat_file, 'w') as f:
                    f.write(valid_content)
                    
                # Verify it's valid
                with open(chat_file, 'r') as f:
                    json.load(f)
                    
                if self.logger:
                    self.logger.info(f"Successfully repaired chat file {chat_id}")
                return True
                
            except Exception as e:
                # Restore backup if repair failed
                with open(backup_file, 'r') as f:
                    content = f.read()
                    
                with open(chat_file, 'w') as f:
                    f.write(content)
                    
                if self.logger:
                    self.logger.error(f"Failed to repair chat file {chat_id}: {str(e)}")
                return False
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during chat file repair for {chat_id}: {str(e)}")
            return False

    def list_chats(self) -> List[Dict[str, Any]]:
        """List all available chat files."""
        chats = []
        corrupted_files = []
        
        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                file_path = os.path.join(self.storage_path, filename)
                try:
                    with open(file_path, 'r') as f:
                        try:
                            chat_data = json.load(f)
                            chats.append({
                                'chat_id': chat_data['chat_id'],
                                'created_at': chat_data['created_at'],
                                'conversation_count': len(chat_data['conversations'])
                            })
                        except json.JSONDecodeError as e:
                            corrupted_files.append((filename, str(e)))
                            if self.logger:
                                self.logger.error(f"Corrupted chat file {filename}: {str(e)}")
                            continue
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Error reading chat file {filename}: {str(e)}")
                    continue
                    
        # Report corrupted files if any
        if corrupted_files and self.logger:
            self.logger.warning(f"Found {len(corrupted_files)} corrupted chat files")
            
        return sorted(chats, key=lambda x: x['created_at'], reverse=True)

    def select_chat(self, allow_new: bool = True) -> Optional[str]:
        """Display an interactive chat selection menu."""
        chats = self.list_chats()
        
        if not chats:
            print("\nNo valid chat files found.")
            
            # Check if there might be corrupted files
            try:
                all_files = [f for f in os.listdir(self.storage_path) if f.endswith('.json')]
                if all_files and len(all_files) > len(chats):
                    print(f"WARNING: Found {len(all_files) - len(chats)} potentially corrupted chat files.")
                    print("You may need to manually fix or delete these files in:")
                    print(f"  {self.storage_path}")
            except Exception:
                pass
                
            if allow_new:
                print("\nUse -pc to create a new chat.")
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

    def build_context_messages(self, chat_id: str) -> List[Dict[str, str]]:
        """Build context messages from chat history."""
        context_messages = []
        conversations = self.get_chat_history(chat_id, self.max_history)
        
        for conv in conversations:
            # Only include the user question and AI response for context
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
        """Display chat history in a readable format."""
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
                    print("-" * 25)
                    
            # Print AI response
            print(f"\nAssistant: {conv['response']}\n")
            print("=" * 50)

    # Service-level methods (from chat_service.py)
    def handle_persistent_chat(self, args, messages):
        """Handle persistent chat setup and context loading."""
        chat_id = None
        
        if args.persistent_chat is not None:
            if args.persistent_chat == 'n':
                chat_id = self.create_chat()
                print(f"\nCreated new chat with ID: {chat_id}")
            elif args.persistent_chat == 'new':
                selected_chat = self.select_chat(allow_new=True)
                
                if selected_chat is None:
                    print("Chat selection cancelled.")
                    sys.exit(0)
                elif selected_chat == 'new':
                    chat_id = self.create_chat()
                    print(f"\nCreated new chat with ID: {chat_id}")
                else:
                    chat_id = selected_chat
            else:
                chat_id = args.persistent_chat
                
            # If we have a chat_id, load its context
            if chat_id:
                try:
                    context_messages = self.build_context_messages(chat_id)
                    system_messages = [msg for msg in messages if msg['role'] == 'system']
                    user_messages = [msg for msg in messages if msg['role'] == 'user']
                    messages = system_messages + context_messages + user_messages
                    print(f"\nContinuing chat: {chat_id}")
                except ValueError as e:
                    print(f"Error: {str(e)}")
                    sys.exit(1)
        
        return chat_id, messages

    def store_chat_conversation(self, chat_id, messages, response, resolved_system_id, system_manager):
        """Store conversation in chat history as a simple logbook."""
        if not chat_id:
            return
            
        # Extract content from response (handle both string and dict formats)
        response_content = response
        if isinstance(response, dict):
            response_content = response.get("content", str(response))
            
        # Store system metadata without parsing content
        system_outputs = None
        system_config = None
        structured_outputs = None
        
        if resolved_system_id:
            system_data = system_manager.get_system_content(resolved_system_id)
            if system_data:
                system_outputs = system_data.get('outputs', [])
                system_config = system_data.get('configuration')
                
                # Just record output metadata without parsing response
                if system_outputs:
                    structured_outputs = self._parse_structured_outputs(response_content, system_outputs)
        
        self.add_conversation(
            chat_id=chat_id,
            messages=messages,
            response=response_content,
            outputs=structured_outputs,
            system_outputs=system_outputs,
            system_config=system_config
        )


    
    def _parse_structured_outputs(self, response, system_outputs):
        """Store basic output metadata without complex parsing.
        
        This simplified version just records the output definitions without 
        attempting to parse content from the response.
        """
        try:
            outputs = []
            for output_def in system_outputs:
                if not hasattr(output_def, 'output_type'):
                    continue
                    
                # Just record basic metadata about outputs
                outputs.append({
                    'name': output_def.name,
                    'type': output_def.output_type.value,
                    'definition': output_def.description if hasattr(output_def, 'description') else None,
                })
                        
            return outputs if outputs else None
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Could not record output metadata: {str(e)}")
            return None
            


    def _validate_outputs(self, outputs: List[Dict[str, Any]], 
                         system_outputs: List) -> tuple[bool, Optional[str]]:
        """Validate AI outputs against the system's output definitions."""
        try:
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
                    
                if hasattr(output_def, 'validate_value'):
                    valid, error = output_def.validate_value(output['value'])
                    if not valid:
                        return False, f"Invalid output '{output['name']}': {error}"
                        
            return True, None
        except Exception as e:
            return False, f"Validation error: {str(e)}"
            
    def scan_corrupted_chat_files(self) -> List[str]:
        """Scan for corrupted chat files.
        
        Returns:
            List[str]: List of corrupted chat file IDs
        """
        corrupted_files = []
        
        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                chat_id = filename[:-5]  # Remove .json extension
                file_path = os.path.join(self.storage_path, filename)
                try:
                    with open(file_path, 'r') as f:
                        try:
                            json.load(f)
                        except json.JSONDecodeError:
                            corrupted_files.append(chat_id)
                except Exception:
                    corrupted_files.append(chat_id)
                    
        return corrupted_files
        
    def delete_chat(self, chat_id: str) -> bool:
        """Delete a chat file.
        
        Args:
            chat_id: The ID of the chat to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        chat_file = self._get_chat_file_path(chat_id)
        if not os.path.exists(chat_file):
            return False
            
        try:
            os.remove(chat_file)
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to delete chat file {chat_id}: {str(e)}")
            return False
