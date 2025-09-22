"""
Command handlers for system and chat related operations.
Handles all CLI commands like listing, viewing systems and chats.
"""

import json
import os
from modules.ai import OpenRouterClient
from modules.questions.processor import QuestionProcessor
from shared.config.loader import load_config
from shared.utils import print_error_or_warnings
from shared.config import (
    ASKAI_DIR, CONFIG_PATH, CHATS_DIR, LOGS_DIR, TEST_DIR,
    TEST_CHATS_DIR, TEST_CONFIG_PATH, TEST_LOGS_DIR,
    get_config_path, is_test_environment, create_test_config_from_production
)

# TUI imports with fallback
try:
    from presentation.tui import is_tui_available
    from presentation.tui.apps.pattern_selector import run_pattern_selector
    from presentation.tui.apps.chat_selector import run_chat_selector
    from presentation.tui.apps.tabbed_tui_app import run_tabbed_tui
    from presentation.tui.apps.question_builder import run_question_builder
    TUI_IMPORTS_AVAILABLE = True
except ImportError:
    TUI_IMPORTS_AVAILABLE = False
    def is_tui_available() -> bool:
        """
        Fallback function when TUI imports are not available.

        Returns:
            bool: Always False when TUI dependencies are missing
        """
        return False



class CommandHandler:
    """Handles various CLI commands for patterns and chats."""

    def __init__(self, pattern_manager, chat_manager, logger, question_processor=None):
        self.pattern_manager = pattern_manager
        self.chat_manager = chat_manager
        self.logger = logger
        self.question_processor = question_processor

    def determine_interface_mode(self, args, config=None):
        """
        Determine which interface mode to use based on arguments and configuration.

        Args:
            args: Parsed command line arguments
            config: Optional config dict (loaded automatically if not provided)

        Returns:
            str: 'tui' or 'cli'
        """
        # Load config if not provided
        if config is None:
            try:
                config = load_config()
            except Exception:
                config = {}

        # Check explicit override arguments (highest priority)
        if getattr(args, 'cli', False) or getattr(args, 'no_tui', False):
            return 'cli'
        if getattr(args, 'tui', False):
            return 'tui'

        # Check if TUI functionality is available
        if not TUI_IMPORTS_AVAILABLE or not is_tui_available():
            return 'cli'

        # Check configuration default
        interface_config = config.get('interface', {})
        tui_features = interface_config.get('tui_features', {})

        # If TUI is disabled in config
        if not tui_features.get('enabled', True):
            return 'cli'

        # Get default mode from config
        default_mode = interface_config.get('default_mode', 'cli')

        # Override for specific operations if requested
        if getattr(args, 'interactive', False):
            return 'tui'
        if getattr(args, 'tui_patterns', False) or getattr(args, 'tui_chats', False):
            return 'tui'  # For specific TUI operations

        return default_mode

    def handle_interactive_mode(self, args):
        """
        Handle full interactive TUI mode.

        Args:
            args: Parsed command line arguments

        Returns:
            bool: True if interactive mode was handled
        """
        if not getattr(args, 'interactive', False):
            return False

        if not TUI_IMPORTS_AVAILABLE or not is_tui_available():
            print("Interactive TUI mode is not available. Falling back to CLI.")
            return False

        try:
            self.logger.info(json.dumps({"log_message": "Launching interactive TUI mode"}))

            # Ensure we have a question processor for the unified TUI
            question_processor = self.question_processor
            if question_processor is None:
                # Create a question processor on-demand
                config = load_config()
                base_path = os.path.abspath('.')
                question_processor = QuestionProcessor(config, self.logger, base_path)
                self.logger.info(json.dumps({"log_message": "Created question processor for TUI mode"}))

            # Use the new tabbed TUI interface instead of unified TUI
            result = run_tabbed_tui(
                pattern_manager=self.pattern_manager,
                chat_manager=self.chat_manager,
                question_processor=question_processor
            )

            if result and isinstance(result, dict):
                result_type = result.get('type')
                result_data = result.get('data')

                if result_type == 'pattern' and result_data:
                    # Check if this is a workflow selection or an actual pattern
                    if result_data.get('workflow') == 'pattern_browser':
                        # Launch the pattern browser
                        print("\n🔍 Launching Pattern Browser...")
                        try:
                            pattern_result = run_pattern_selector(self.pattern_manager)
                            if pattern_result:
                                print(f"\nSelected pattern: {pattern_result.get('name', 'Unknown')}")
                                pattern_id = pattern_result.get('pattern_id', pattern_result.get('name'))
                                if pattern_id:
                                    self.pattern_manager.display_pattern(pattern_id)
                            else:
                                print("Pattern browser cancelled.")
                        except Exception as e:
                            print(f"Pattern browser failed: {e}")
                    else:
                        # Handle direct pattern selection (legacy behavior)
                        print(f"\nSelected pattern: {result_data.get('name', 'Unknown')}")
                        pattern_id = result_data.get('pattern_id', result_data.get('name'))
                        if pattern_id:
                            self.pattern_manager.display_pattern(pattern_id)

                elif result_type == 'question' and result_data:
                    # Handle question workflow selection
                    if result_data.get('workflow') == 'question_builder':
                        print("\n🤔 Launching Question Builder...")
                        try:
                            if self.question_processor:
                                question_result = run_question_builder(self.question_processor)
                                if question_result:
                                    print("Question builder completed successfully")
                                else:
                                    print("Question builder cancelled.")
                            else:
                                print("Question processor not available. Creating one now...")
                                # Create a temporary question processor for TUI mode
                                config = load_config()
                                base_path = os.path.abspath('.')
                                temp_question_processor = QuestionProcessor(config, self.logger, base_path)
                                question_result = run_question_builder(temp_question_processor)
                                if question_result:
                                    print("Question builder completed successfully")
                                else:
                                    print("Question builder cancelled.")
                        except Exception as e:
                            print(f"Question builder failed: {e}")
                            self.logger.error(f"Question builder error: {e}")
                    else:
                        print(f"\nQuestion workflow result: {result_data}")

                elif result_type == 'internals' and result_data:
                    # Handle internals workflow selection
                    if result_data.get('workflow') == 'internals_management':
                        print("\n⚙️ Internals Management Workflow")
                        print("This would launch the internals management interface.")
                        print("For now, use CLI options like --openrouter, --list-patterns, --list-chats.")
                    else:
                        print(f"\nInternals workflow result: {result_data}")

                elif result_type == 'chat' and result_data:
                    print(f"\nSelected chat: {result_data.get('chat_id', 'Unknown')}")
                    if not result_data.get('corrupted', False):
                        print(f"Created: {result_data.get('created_at', 'Unknown')}")
                        print(f"Messages: {result_data.get('conversation_count', 0)}")
                    else:
                        print("This chat file is corrupted and cannot be displayed.")

                elif result_type == 'model' and result_data:
                    print(f"\nSelected model: {result_data}")

                elif result_type == 'new_chat':
                    print("\nStarting new chat session...")
                    # This would trigger chat creation logic

                elif result_type == 'delete_chat' and result_data:
                    chat_id = result_data.get('chat_id', 'Unknown')
                    confirm = input(f"Are you sure you want to delete chat '{chat_id}'? (y/n): ").lower()
                    if confirm == 'y':
                        if self.chat_manager.delete_chat(chat_id):
                            print(f"Successfully deleted chat: {chat_id}")
                        else:
                            print(f"Failed to delete chat: {chat_id}")
                    else:
                        print("Deletion cancelled.")
            else:
                # Unified TUI app exited normally (user chose to quit)
                print("Interactive session ended.")

            return True

        except Exception as e:
            self.logger.error(json.dumps({
                "log_message": f"Interactive TUI mode failed: {e}"
            }))
            print(f"Interactive mode failed: {e}")
            return False

    def handle_pattern_commands(self, args):
        """Handle pattern-related commands."""
        # Check if interactive TUI mode should be used
        if self.handle_interactive_mode(args):
            return True

        # Determine interface mode for this operation
        interface_mode = self.determine_interface_mode(args)

        # Check if TUI should be used for pattern operations
        should_use_tui = (
            interface_mode == 'tui' and
            TUI_IMPORTS_AVAILABLE and
            is_tui_available() and
            (getattr(args, 'tui_patterns', False) or
             getattr(args, 'list_patterns', False) or
             getattr(args, 'view_pattern', None) is not None)
        )

        if args.list_patterns:
            self.logger.info(json.dumps({"log_message": "User requested to list all available pattern files"}))

            # Use TUI if requested and available
            if should_use_tui:
                try:
                    # Add timeout and better error handling for TUI
                    self.logger.info(json.dumps({"log_message": "Launching TUI pattern browser"}))
                    selected_pattern = run_pattern_selector(self.pattern_manager)
                    if selected_pattern:
                        print(f"Selected pattern: {selected_pattern.get('name', 'Unknown')}")
                        # Show the selected pattern content
                        pattern_id = selected_pattern.get('pattern_id', selected_pattern.get('name'))
                        if pattern_id:
                            self.pattern_manager.display_pattern(pattern_id)
                    else:
                        print("Pattern browser closed.")
                    return True
                except Exception as e:
                    self.logger.warning(json.dumps({
                        "log_message": f"TUI pattern browser failed, falling back to CLI: {e}"
                    }))
                    print(f"TUI not available ({str(e)}), using traditional interface...")
                    # Fall through to traditional CLI listing

            # Traditional CLI listing
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
            if args.view_pattern == '' and should_use_tui:
                # Use TUI for pattern selection
                try:
                    selected_pattern = run_pattern_selector(self.pattern_manager)
                    if selected_pattern:
                        pattern_id = selected_pattern.get('pattern_id', selected_pattern.get('name'))
                    else:
                        print("Pattern selection cancelled.")
                        return True
                except Exception as e:
                    self.logger.warning(json.dumps({
                        "log_message": f"TUI pattern browser failed, falling back to CLI: {e}"
                    }))
                    pattern_id = self.pattern_manager.select_pattern()
            else:
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
        # Check if interactive TUI mode should be used
        if self.handle_interactive_mode(args):
            return True

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

        # Determine interface mode for this operation
        interface_mode = self.determine_interface_mode(args)

        # Check if TUI should be used for chat operations
        should_use_tui = (
            interface_mode == 'tui' and
            TUI_IMPORTS_AVAILABLE and
            is_tui_available() and
            (getattr(args, 'tui_chats', False) or
             getattr(args, 'list_chats', False) or
             getattr(args, 'view_chat', None) is not None)
        )

        if args.list_chats:
            self.logger.info(json.dumps({"log_message": "User requested to list all available chats"}))

            # Use TUI if requested and available
            if should_use_tui:
                try:
                    selected_chat = run_chat_selector(self.chat_manager)
                    if selected_chat:
                        print(f"Selected chat: {selected_chat.get('chat_id', 'Unknown')}")
                        if not selected_chat.get('corrupted', False):
                            # Show basic chat info
                            print(f"Created: {selected_chat.get('created_at', 'Unknown')}")
                            print(f"Messages: {selected_chat.get('conversation_count', 0)}")
                        else:
                            print("This chat file is corrupted and cannot be displayed.")
                    else:
                        print("Chat browser closed.")
                    return True
                except Exception as e:
                    self.logger.warning(json.dumps({
                        "log_message": f"TUI chat manager failed, falling back to CLI: {e}"
                    }))
                    print(f"TUI not available ({str(e)}), using traditional interface...")
                    # Fall through to traditional CLI listing

            # Traditional CLI listing
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
