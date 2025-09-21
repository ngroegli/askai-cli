"""
Main entry point for the AskAI CLI application.
Orchestrates the different components to provide AI assistance via command line.
"""

# Standard library imports
import json
import os
import sys

# Local application imports - grouped by package
from infrastructure.output.output_coordinator import OutputCoordinator

from modules.ai import AIService
from modules.chat import ChatManager
from modules.messaging import MessageBuilder
from modules.patterns import PatternManager
from modules.questions import QuestionProcessor

from presentation.cli import CommandHandler
from presentation.cli.cli_parser import CLIParser

from shared.config import load_config
from shared.logging import setup_logger
from shared.utils import print_error_or_warnings

# Add the parent directory to Python path to enable local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def display_help_fast():
    """
    Display help information with minimal imports.
    This function is optimized to avoid unnecessary imports when only help is needed.
    """
    cli_parser = CLIParser()
    cli_parser.parse_arguments()  # This will display help and exit

def main():
    """Main entry point for the AskAI CLI application."""
    # Check if this is a help request (before any heavy initialization)
    # Use most efficient path for help commands
    if '-h' in sys.argv or '--help' in sys.argv or len(sys.argv) == 1:
        display_help_fast()
        return  # Exit after displaying help

    # For non-help commands, initialize CLI parser first
    cli_parser = CLIParser()
    args = cli_parser.parse_arguments()

    # Now load configuration (needed for most commands)
    config = load_config()
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Setup logging
    logger = setup_logger(config, args.debug)
    logger.info(json.dumps({"log_message": "AskAI started and arguments parsed"}))

    # Initialize services based on what's needed
    # Start with just the minimal components
    chat_manager = None
    pattern_manager = None
    message_builder = None
    ai_service = None

    # Initialize only the components we need based on the command
    # Check for simple command options that don't need all managers
    simple_commands = (
        args.list_patterns or args.view_pattern is not None or
        args.list_chats or args.view_chat is not None or
        args.openrouter is not None
    )

    if simple_commands:
        # For simple commands, we only need specific managers
        if args.list_patterns or args.view_pattern is not None:
            pattern_manager = PatternManager(base_path, config)

        if args.list_chats or args.view_chat is not None:
            chat_manager = ChatManager(config, logger)

        # Create the command handler with only what's needed
        # Note: question_processor will be created on-demand in the handler if needed for TUI
        command_handler = CommandHandler(pattern_manager, chat_manager, logger)
    else:
        # Full command execution requires all components
        pattern_manager = PatternManager(base_path, config)
        chat_manager = ChatManager(config, logger)
        # Note: question_processor will be created on-demand in the handler if needed for TUI
        command_handler = CommandHandler(pattern_manager, chat_manager, logger)
        message_builder = MessageBuilder(pattern_manager, logger)
        ai_service = AIService(logger)

    # Initialize output handler
    output_handler = OutputCoordinator()

    # Check for incompatible combinations of pattern and chat commands
    using_pattern = args.use_pattern is not None

    # Handle commands in priority order - patterns first
    if command_handler.handle_pattern_commands(args):
        sys.exit(0)
    if command_handler.handle_chat_commands(args):
        sys.exit(0)
    if command_handler.handle_openrouter_commands(args):
        sys.exit(0)
    if command_handler.handle_config_commands(args):
        sys.exit(0)

    # Validate arguments
    cli_parser.validate_arguments(args, logger)

    # Determine which mode we're operating in: pattern mode or chat/question mode
    using_pattern = args.use_pattern is not None

    # Check if chat functionality is being used
    using_chat = args.persistent_chat is not None or args.view_chat is not None

    # Initialize output variables for both processing paths
    formatted_output = ""
    created_files = []

    # Warn if trying to use both pattern and chat functionality together
    if using_pattern and using_chat:
        logger.warning(json.dumps({
            "log_message": "User attempted to use chat functionality with patterns"
        }))
        print_error_or_warnings(
            "Patterns and chat features are not compatible. Chat options (-pc, -vc) will be ignored.",
            warning_only=True
        )
        # Force chat features to be disabled
        args.persistent_chat = None
        args.view_chat = None
        # No chat functionality with patterns

    # Create separate flows for pattern vs. chat processing
    if using_pattern:
        # === PATTERN MODE ===
        # Make sure we have the required components
        if pattern_manager is None:
            pattern_manager = PatternManager(base_path)
        if message_builder is None:
            message_builder = MessageBuilder(pattern_manager, logger)
        if ai_service is None:
            ai_service = AIService(logger)

        # Build messages for pattern and get the resolved pattern_id (after selection)
        messages, resolved_pattern_id = message_builder.build_messages(
            question=None,
            file_input=None,
            pattern_id=args.use_pattern,
            pattern_input=args.pattern_input,
            response_format="rawtext",  # Use default format with patterns
            url=None,
            image=None,
            pdf=None,
            image_url=None,
            pdf_url=None
        )

        # Check if message building was cancelled
        if messages is None:
            sys.exit(0)

        # Debug log the final messages
        logger.debug(json.dumps({"log_message": "Pattern messages content", "messages": messages}))

        # Get AI response for pattern
        response = ai_service.get_ai_response(
            messages=messages,
            model_name=None,  # Don't override model for patterns
            pattern_id=resolved_pattern_id,
            debug=args.debug,
            pattern_manager=pattern_manager,
            enable_url_search=False
        )

        # No chat history for patterns

    else:
        # === CHAT/QUESTION MODE ===
        # Use the dedicated question processor
        question_processor = QuestionProcessor(config, logger, base_path)
        response_obj = question_processor.process_question(args)

        # The question processor returns a QuestionResponse object
        formatted_output = response_obj.content
        created_files = response_obj.created_files

    # Process output based on mode
    if using_pattern:
        # Get pattern outputs for auto-execution handling
        if resolved_pattern_id:
            # Make sure pattern_manager is initialized
            if pattern_manager is None:
                pattern_manager = PatternManager(base_path, config)

            pattern_data = pattern_manager.get_pattern_content(resolved_pattern_id)
            if pattern_data:
                _ = pattern_data.get('outputs', [])

        # Check if the response is already a properly formatted JSON with a 'results' field
        try:
            if isinstance(response, dict) and 'content' in response:
                content = response['content']
                if isinstance(content, str) and content.strip().startswith('{'):
                    # Try to parse the content as JSON
                    try:
                        parsed_json = json.loads(content)
                        if isinstance(parsed_json, dict) and 'results' in parsed_json:
                            # We have proper JSON with results, modify the response directly
                            logger.debug("Found direct JSON with results in content")
                            # Create a new response object with the parsed content
                            response = parsed_json
                    except json.JSONDecodeError:
                        logger.debug("Content is not valid JSON")
        except (ValueError, TypeError, KeyError, AttributeError) as e:
            logger.debug("Error checking for direct JSON: %s", str(e))

        logger.debug("Using pattern manager to handle response for %s", resolved_pattern_id)
        # Make sure pattern_manager is initialized
        if pattern_manager is None:
            pattern_manager = PatternManager(base_path)

        formatted_output, created_files = pattern_manager.process_pattern_response(
            resolved_pattern_id,
            response,
            output_handler
        )
    # For question mode, the output is already processed by QuestionProcessor
    # No additional processing needed

    # Print the formatted output for both pattern and non-pattern responses
    print(formatted_output)

    # Execute any pending operations (commands and files) after display is shown
    # Only for pattern mode - question mode already handles its own output
    if using_pattern:
        additional_files = output_handler.execute_pending_operations()
        # Combine created files from both output processing and pending operations
        all_created_files = (created_files or []) + additional_files
    else:
        # For question mode, files are already handled by QuestionProcessor
        all_created_files = created_files or []

    # Log created files
    if all_created_files:
        print(f"\nCreated output files: {', '.join(all_created_files)}")
        logger.info("Created output files: %s", ', '.join(all_created_files))


if __name__ == "__main__":
    main()
