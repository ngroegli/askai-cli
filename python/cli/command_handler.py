"""
Command handlers for system and chat related operations.
Handles all CLI commands like listing, viewing systems and chats.
"""

import json
import os
from ai import OpenRouterClient
from utils import print_error_or_warnings
from config import (
    ASKAI_DIR, CONFIG_PATH, CHATS_DIR, LOGS_DIR, TEST_DIR,
    TEST_CHATS_DIR, TEST_CONFIG_PATH, TEST_LOGS_DIR,
    get_config_path, is_test_environment, create_test_config_from_production
)



class CommandHandler:
    """Handles various CLI commands for patterns and chats."""

    def __init__(self, pattern_manager, chat_manager, logger):
        self.pattern_manager = pattern_manager
        self.chat_manager = chat_manager
        self.logger = logger

    def handle_pattern_commands(self, args):
        """Handle pattern-related commands."""
        if args.list_patterns:
            self.logger.info(json.dumps({"log_message": "User requested to list all available pattern files"}))
            patterns = self.pattern_manager.list_patterns()
            if not patterns:
                print("No pattern files found.")
            else:
                print("\nAvailable patterns:")
                print("-" * 70)
                for pattern in patterns:
                    source_indicator = "🔒" if pattern.get('is_private', False) else "📦"
                    print(f"ID: {pattern['pattern_id']} {source_indicator}")
                    print(f"Name: {pattern['name']}")
                    print(f"Source: {pattern.get('source', 'built-in')}")
                    print("-" * 70)
                print("\n🔒 = Private pattern, 📦 = Built-in pattern")
            return True

        if args.view_pattern is not None:  # -vp was used
            # If no specific pattern ID was provided, show selection
            pattern_id = args.view_pattern or self.pattern_manager.select_pattern()

            if pattern_id is None:
                print("Pattern selection cancelled.")
                return True

            self.logger.info(json.dumps({
                "log_message": "User requested to view pattern file",
                "pattern": pattern_id
            }))
            try:
                self.pattern_manager.display_pattern(pattern_id)
            except ValueError as e:
                print_error_or_warnings(str(e))
            return True

        return False

    def handle_chat_commands(self, args):
        """Handle chat-related commands."""
        # Check for incompatible combinations
        using_pattern = args.use_pattern is not None
        using_pattern_commands = args.list_patterns or args.view_pattern is not None or using_pattern
        using_chat = (args.persistent_chat is not None or args.list_chats or
                     args.view_chat is not None or args.manage_chats)

        # If pattern commands are present, they always take precedence over chat commands
        if using_pattern_commands and using_chat:
            # Only log the issue, don't print a warning (main warning will be in askai.py)
            self.logger.warning(json.dumps({"log_message": "User attempted to use chat functionality with patterns"}))
            return False

        if args.list_chats:
            self.logger.info(json.dumps({"log_message": "User requested to list all available chats"}))
            chats = self.chat_manager.list_chats()

            # Also check for corrupted files
            corrupted_files = self.chat_manager.scan_corrupted_chat_files()

            if not chats and not corrupted_files:
                print("No chat history found.")
            else:
                if chats:
                    print("\nAvailable chats:")
                    print("-" * 60)
                    for chat in chats:
                        print(f"ID: {chat['chat_id']}")
                        print(f"Created: {chat['created_at']}")
                        print(f"Messages: {chat['conversation_count']}")
                        print("-" * 60)

                if corrupted_files:
                    print_error_or_warnings(f"Found {len(corrupted_files)} corrupted chat files:", warning_only=True)
                    for chat_id in corrupted_files:
                        print(f"- {chat_id}")
                    print("\nUse --manage-chats to repair or delete these files")
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
                print_error_or_warnings(str(e))
            return True

        if hasattr(args, 'manage_chats') and args.manage_chats:
            self.logger.info(json.dumps({"log_message": "User requested to manage chat files"}))
            self._handle_chat_management()
            return True

        return False

    def _handle_chat_management(self):
        """Handle chat file management, including repair and deletion of corrupted files."""
        # Scan for corrupted files
        corrupted_files = self.chat_manager.scan_corrupted_chat_files()

        if not corrupted_files:
            print("No corrupted chat files found.")
            return

        print(f"\nFound {len(corrupted_files)} corrupted chat files:")
        for i, chat_id in enumerate(corrupted_files, 1):
            print(f"{i}. {chat_id}")

        print("\nOptions:")
        print("1. Try to repair all files")
        print("2. Delete all corrupted files")
        print("3. Select individual files to manage")
        print("q. Quit")

        choice = input("\nEnter your choice (1-3 or q): ").lower()

        if choice == 'q':
            return

        if choice == '1':
            # Try to repair all files
            success_count = 0
            for chat_id in corrupted_files:
                if self.chat_manager.repair_chat_file(chat_id):
                    success_count += 1
                    print(f"Repaired: {chat_id}")
                else:
                    print_error_or_warnings(f"Failed to repair: {chat_id}", warning_only=True)

            print(f"\nRepaired {success_count} out of {len(corrupted_files)} files.")

        elif choice == '2':
            # Confirm deletion
            confirm = input(
                f"Are you sure you want to delete all {len(corrupted_files)} corrupted chat files? (y/n): "
            ).lower()
            if confirm != 'y':
                print("Deletion cancelled.")
                return

            # Delete all files
            success_count = 0
            for chat_id in corrupted_files:
                if self.chat_manager.delete_chat(chat_id):
                    success_count += 1
                    print(f"Deleted: {chat_id}")
                else:
                    print_error_or_warnings(f"Failed to delete: {chat_id}", warning_only=True)

            print(f"\nDeleted {success_count} out of {len(corrupted_files)} files.")

        elif choice == '3':
            # Handle individual files
            while True:
                print("\nSelect a file to manage:")
                for i, chat_id in enumerate(corrupted_files, 1):
                    print(f"{i}. {chat_id}")
                print("b. Back to main menu")

                file_choice = input(f"\nEnter file number (1-{len(corrupted_files)} or b): ").lower()

                if file_choice == 'b':
                    break

                try:
                    file_idx = int(file_choice) - 1
                    if 0 <= file_idx < len(corrupted_files):
                        selected_chat_id = corrupted_files[file_idx]

                        print(f"\nManaging file: {selected_chat_id}")
                        print("1. Try to repair")
                        print("2. Delete file")
                        print("b. Back to file selection")

                        action = input("Enter choice (1-2 or b): ").lower()

                        if action == 'b':
                            continue

                        if action == '1':
                            if self.chat_manager.repair_chat_file(selected_chat_id):
                                print(f"Successfully repaired: {selected_chat_id}")
                                # Remove from the list
                                corrupted_files.pop(file_idx)
                                if not corrupted_files:
                                    print("No more corrupted files to manage.")
                                    break
                            else:
                                print_error_or_warnings(f"Failed to repair: {selected_chat_id}", warning_only=True)

                        elif action == '2':
                            confirm = input(f"Are you sure you want to delete {selected_chat_id}? (y/n): ").lower()
                            if confirm == 'y':
                                if self.chat_manager.delete_chat(selected_chat_id):
                                    print(f"Successfully deleted: {selected_chat_id}")
                                    # Remove from the list
                                    corrupted_files.pop(file_idx)
                                    if not corrupted_files:
                                        print("No more corrupted files to manage.")
                                        break
                                else:
                                    print_error_or_warnings(f"Failed to delete: {selected_chat_id}", warning_only=True)
                    else:
                        print_error_or_warnings("Invalid file number.", warning_only=True)
                except ValueError:
                    print_error_or_warnings("Please enter a valid number.", warning_only=True)
        else:
            print_error_or_warnings("Invalid choice.", warning_only=True)

    def handle_openrouter_commands(self, args):
        """Handle OpenRouter-related commands."""
        if args.openrouter is None:
            return False

        command = args.openrouter[0]
        command_args = args.openrouter[1:] if len(args.openrouter) > 1 else []

        if command == 'check-credits':
            self.logger.info(json.dumps({"log_message": "User requested OpenRouter credit balance"}))
            try:
                client = OpenRouterClient(logger=self.logger)
                credit_data = client.get_credit_balance(debug=getattr(args, 'debug', False))

                total_credits = credit_data.get('total_credits', 0)
                total_usage = credit_data.get('total_usage', 0)
                remaining_credits = total_credits - total_usage

                print("\nOpenRouter Credit Balance:")
                print("-" * 40)
                print(f"Total Credits:     ${total_credits:.4f}")
                print(f"Total Usage:       ${total_usage:.4f}")
                print(f"Remaining Credits: ${remaining_credits:.4f}")
                print("-" * 40)

            except Exception as e:
                print_error_or_warnings(f"Error retrieving credit balance: {str(e)}")
            return True

        if command == 'list-models':
            self.logger.info(json.dumps({"log_message": "User requested OpenRouter available models"}))
            try:
                client = OpenRouterClient(logger=self.logger)
                models = client.get_available_models(debug=getattr(args, 'debug', False))

                if not models:
                    print("No models found.")
                else:
                    # Apply filtering if search terms are provided
                    filtered_models = models
                    if command_args:  # If there are filter terms
                        filtered_models = []
                        search_terms = [term.lower() for term in command_args]

                        for model in models:
                            model_id = model.get('id', '').lower()
                            name = model.get('name', '').lower()

                            # Check if any search term matches ID or name
                            if any(term in model_id or term in name for term in search_terms):
                                filtered_models.append(model)

                    if not filtered_models:
                        if command_args:
                            print(f"No models found matching filter(s): {', '.join(command_args)}")
                        else:
                            print("No models found.")
                        return True

                    # Display header with filter info
                    if command_args:
                        print(
                            f"\nFiltered OpenRouter Models ({len(filtered_models)} of {len(models)} total, " +
                            f"filter: {', '.join(command_args)}):"
                        )
                    else:
                        print(f"\nAvailable OpenRouter Models ({len(filtered_models)} total):")
                    print("=" * 100)

                    for model in filtered_models:
                        model_id = model.get('id', 'N/A')
                        name = model.get('name', 'N/A')
                        description = model.get('description', 'No description available')

                        # Get context length info
                        context_length = model.get('context_length', 'N/A')
                        top_provider = model.get('top_provider', {})
                        max_completion_tokens = top_provider.get('max_completion_tokens', 'N/A')

                        # Get pricing info
                        pricing = model.get('pricing', {})
                        prompt_price = pricing.get('prompt', 'N/A')
                        completion_price = pricing.get('completion', 'N/A')

                        # Format pricing display
                        if prompt_price != 'N/A' and completion_price != 'N/A':
                            try:
                                prompt_float = float(prompt_price)
                                completion_float = float(completion_price)
                                pricing_display = (
                                    f"${prompt_float:.8f}/token (prompt), "
                                    f"${completion_float:.8f}/token (completion)"
                                )
                            except (ValueError, TypeError):
                                pricing_display = (
                                    f"${prompt_price}/token (prompt), "
                                    f"${completion_price}/token (completion)"
                                )
                        else:
                            pricing_display = (
                                f"${prompt_price}/token (prompt), "
                                f"${completion_price}/token (completion)"
                            )

                        print(f"ID: {model_id}")
                        print(f"Name: {name}")

                        # Display description with intelligent truncation
                        if len(description) > 200:
                            # Try to truncate at a sentence boundary
                            truncated = description[:200]
                            last_period = truncated.rfind('.')
                            last_space = truncated.rfind(' ')

                            if last_period > 150:  # If there's a sentence ending reasonably close
                                description_display = description[:last_period + 1] + "..."
                            elif last_space > 150:  # Otherwise truncate at word boundary
                                description_display = description[:last_space] + "..."
                            else:  # Last resort: hard truncate
                                description_display = description[:200] + "..."
                        else:
                            description_display = description

                        print(f"Description: {description_display}")
                        print(
                            f"Context Length: {context_length:,}"
                            if isinstance(context_length, int)
                            else f"Context Length: {context_length}"
                        )
                        print(
                            f"Max Completion Tokens: {max_completion_tokens:,}"
                            if isinstance(max_completion_tokens, int)
                            else f"Max Completion Tokens: {max_completion_tokens}"
                        )
                        print(f"Pricing: {pricing_display}")
                        print("-" * 100)

            except Exception as e:
                print_error_or_warnings(f"Error retrieving available models: {str(e)}")
            return True

        return False

    def handle_config_commands(self, args):
        """Handle configuration-related commands."""
        if args.config is None:
            return False

        if not args.config:  # Empty list means --config was used without arguments
            print("Available configuration commands:")
            print("  create-test-config  - Create or recreate test configuration file")
            print("  show-config-path    - Show which configuration file is being used")
            print("  show-structure      - Show the ~/.askai directory structure")
            return True

        command = args.config[0]

        if command == 'create-test-config':
            self.logger.info(json.dumps({"log_message": "User requested to create test configuration"}))

            if create_test_config_from_production():
                print(f"\nTest configuration successfully created at {TEST_CONFIG_PATH}")
                print("\nThis configuration will be used automatically when ASKAI_TESTING=true")
                print("You can edit this file to customize test settings without affecting production.")
            else:
                print_error_or_warnings("Failed to create test configuration")
            return True

        if command == 'show-config-path':
            self.logger.info(json.dumps({"log_message": "User requested to show config path"}))

            config_path = get_config_path()
            env_type = "test" if is_test_environment() else "production"
            print(f"\nCurrently using {env_type} configuration:")
            print(f"  {config_path}")

            if is_test_environment():
                print("\nTest environment detected (ASKAI_TESTING=true)")
            else:
                print("\nProduction environment")
            return True

        if command == 'show-structure':
            self.logger.info(json.dumps({"log_message": "User requested to show directory structure"}))

            print("\nAskAI Directory Structure:")
            print(f"  {ASKAI_DIR}/")
            print(f"  ├── config.yml {'✓' if os.path.exists(CONFIG_PATH) else '✗'}")
            print(f"  ├── chats/ {'✓' if os.path.exists(CHATS_DIR) else '✗'}")
            print(f"  ├── logs/ {'✓' if os.path.exists(LOGS_DIR) else '✗'}")
            print(f"  └── test/ {'✓' if os.path.exists(TEST_DIR) else '✗'}")
            if os.path.exists(TEST_DIR):
                print(f"      ├── config.yml {'✓' if os.path.exists(TEST_CONFIG_PATH) else '✗'}")
                print(f"      ├── chats/ {'✓' if os.path.exists(TEST_CHATS_DIR) else '✗'}")
                print(f"      └── logs/ {'✓' if os.path.exists(TEST_LOGS_DIR) else '✗'}")

            print("\n✓ = exists, ✗ = missing")
            return True

        print_error_or_warnings(f"Unknown configuration command: {command}")
        print("Available commands: create-test-config, show-config-path, show-structure")
        return True
