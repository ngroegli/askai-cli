"""
Command handlers for system and chat related operations.
Handles all CLI commands like listing, viewing systems and chats.
"""

import json
import sys


class CommandHandler:
    """Handles various CLI commands for systems and chats."""
    
    def __init__(self, system_manager, chat_manager, logger):
        self.system_manager = system_manager
        self.chat_manager = chat_manager
        self.logger = logger

    def handle_system_commands(self, args):
        """Handle system-related commands."""
        if args.list_systems:
            self.logger.info(json.dumps({"log_message": "User requested to list all available system files"}))
            systems = self.system_manager.list_systems()
            if not systems:
                print("No system files found.")
            else:
                print("\nAvailable systems:")
                print("-" * 60)
                for system in systems:
                    print(f"ID: {system['system_id']}")
                    print(f"Name: {system['name']}")
                    print("-" * 60)
            return True

        if args.view_system is not None:  # -vs was used
            # If no specific system ID was provided, show selection
            system_id = args.view_system or self.system_manager.select_system()
            
            if system_id is None:
                print("System selection cancelled.")
                return True
                
            self.logger.info(json.dumps({
                "log_message": "User requested to view system file",
                "system": system_id
            }))
            try:
                self.system_manager.display_system(system_id)
            except ValueError as e:
                print(f"Error: {str(e)}")
            return True

        return False

    def handle_chat_commands(self, args):
        """Handle chat-related commands."""
        if args.list_chats:
            self.logger.info(json.dumps({"log_message": "User requested to list all available chats"}))
            chats = self.chat_manager.list_chats()
            if not chats:
                print("No chat history found.")
            else:
                print("\nAvailable chats:")
                print("-" * 60)
                for chat in chats:
                    print(f"ID: {chat['chat_id']}")
                    print(f"Created: {chat['created_at']}")
                    print(f"Messages: {chat['conversation_count']}")
                    print("-" * 60)
            return True

        if args.view_chat is not None:  # -vc was used
            # If no specific chat ID was provided, show selection
            chat_id = args.view_chat or self.chat_manager.select_chat(allow_new=False)
            
            if chat_id is None:
                print("Chat selection cancelled.")
                return True
                
            self.logger.info(json.dumps({
                "log_message": "User requested to view chat history",
                "chat_id": chat_id
            }))
            try:
                self.chat_manager.display_chat(chat_id)
            except ValueError as e:
                print(f"Error: {str(e)}")
            return True

        return False
