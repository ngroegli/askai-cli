"""
Main entry point for the AskAI CLI application.
Orchestrates the different components to provide AI assistance via command line.
"""

# Standard library imports
import json
import os
import sys1234

# Local application imports
from python.ai import AIService
from python.chat import ChatManager
from python.cli import CommandHandler
from python.logger import setup_logger
from python.message_builder import MessageBuilder
from python.output.output_handler import OutputHandler
from python.config import load_config
from python.patterns import PatternManager
from python.cli.cli_parser import CLIParser
from python.utils import print_error_or_warnings

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
            pattern_manager = PatternManager(base_path)

        if args.list_chats or args.view_chat is not None:
            chat_manager = ChatManager(config, logger)

        # Create the command handler with only what's needed
        command_handler = CommandHandler(pattern_manager, chat_manager, logger)
    else:
        # Full command execution requires all components
        pattern_manager = PatternManager(base_path)
        chat_manager = ChatManager(config, logger)
        command_handler = CommandHandler(pattern_manager, chat_manager, logger)
        message_builder = MessageBuilder(pattern_manager, logger)
        ai_service = AIService(logger)

    # Initialize output handler
    output_handler = OutputHandler()

    # Check for incompatible combinations of pattern and chat commands
    using_pattern = args.use_pattern is not None

    # Handle commands in priority order - patterns first
    if command_handler.handle_pattern_commands(args):
        sys.exit(0)
    if command_handler.handle_chat_commands(args):
        sys.exit(0)
    if command_handler.handle_openrouter_commands(args):
        sys.exit(0)

    # Validate arguments
    cli_parser.validate_arguments(args, logger)

    # Determine which mode we're operating in: pattern mode or chat/question mode
    using_pattern = args.use_pattern is not None

    # Check if chat functionality is being used
    using_chat = args.persistent_chat is not None or args.view_chat is not None

    # Warn if trying to use both pattern and chat functionality together
    if using_pattern and using_chat:
        logger.warning(json.dumps({
            "log_message": "User attempted to use chat functionality with patterns"
        }))
        print_error_or_warnings(
            "Chat functionality is not compatible with patterns. Chat options will be ignored.", 
            warning_only=True
        )
        # Force chat features to be disabled
        args.persistent_chat = None
        args.view_chat = None
        # No chat functionality with patterns
        chat_id = None

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
        chat_id = None

    else:
        # === CHAT/QUESTION MODE ===
        # Make sure we have the required components
        if pattern_manager is None:
            pattern_manager = PatternManager(base_path)
        if message_builder is None:
            message_builder = MessageBuilder(pattern_manager, logger)
        if chat_manager is None:
            chat_manager = ChatManager(config, logger)
        if ai_service is None:
            ai_service = AIService(logger)

        # Build messages for chat/question
        messages, resolved_pattern_id = message_builder.build_messages(
            question=args.question,
            file_input=args.file_input,
            pattern_id=None,  # No pattern in chat mode
            pattern_input=None,
            response_format=args.format,
            url=args.url,
            image=args.image if hasattr(args, 'image') else None,
            pdf=args.pdf if hasattr(args, 'pdf') else None,
            image_url=args.image_url if hasattr(args, 'image_url') else None,
            pdf_url=args.pdf_url if hasattr(args, 'pdf_url') else None
        )

        # Check if message building was cancelled
        if messages is None:
            sys.exit(0)

        # Handle persistent chat setup and context loading
        chat_id, messages = chat_manager.handle_persistent_chat(args, messages)

        # Debug log the final messages
        logger.debug(json.dumps({"log_message": "Chat messages content", "messages": messages}))

        # Determine if web search should be enabled for URL analysis
        enable_url_search = args.url is not None

        # Get AI response for chat/question
        response = ai_service.get_ai_response(
            messages=messages,
            model_name=args.model,
            pattern_id=None,  # No pattern in chat mode
            debug=args.debug,
            pattern_manager=None,  # No pattern manager needed
            enable_url_search=enable_url_search
        )

        # Store chat history if using persistent chat (only in chat/question mode)
        # Make sure we're not using pattern mode before storing chat
        if chat_id and not using_pattern:
            chat_manager.store_chat_conversation(
                chat_id, messages, response, None, None  # No pattern data in chat mode
            )

    # Get pattern outputs for auto-execution handling
    pattern_outputs = None
    if resolved_pattern_id:
        # Make sure pattern_manager is initialized
        if pattern_manager is None:
            pattern_manager = PatternManager(base_path)

        pattern_data = pattern_manager.get_pattern_content(resolved_pattern_id)
        if pattern_data:
            pattern_outputs = pattern_data.get('outputs', [])

    # Handle output
    console_output = True  # Default to showing console output
    file_output = args.save if hasattr(args, 'save') else False

    # Enable file output if we have pattern outputs with write_to_file
    pattern_has_file_output = False
    if pattern_outputs:
        for output in pattern_outputs:
            if output.should_write_to_file():
                file_output = True
                pattern_has_file_output = True
                break

    # Process output
    # Check if user specified an output file via args.output
    has_output_arg = hasattr(args, 'output') and args.output is not None and not using_pattern

    # Initialize output configuration
    output_config = {}

    # Add format to output_config so the handler knows what format to use
    # But only use the user's format if not using a pattern
    output_config['format'] = "rawtext" if using_pattern else args.format

    # Don't override file_output if it was already set by pattern outputs
    # And don't use args.output if we're using a pattern
    if has_output_arg and not pattern_has_file_output:
        file_output = True

        # Use the format specified with -f to determine the output file type
        output_path = args.output

        # Simple approach: Just set the format and filename based on user's format choice
        if args.format == 'json':
            output_config['json_filename'] = os.path.basename(output_path)
        elif args.format == 'md':
            output_config['markdown_filename'] = os.path.basename(output_path)
        else:
            # Default to markdown for text output (most versatile format)
            output_config['markdown_filename'] = os.path.basename(output_path)

        # Set output directory to parent directory of output file
        output_dir = os.path.dirname(os.path.abspath(output_path))
        output_handler.output_dir = output_dir

    # Use the pattern manager to handle the response if we have a pattern
    if resolved_pattern_id:
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

    else:
        # Default output handling for non-pattern responses
        formatted_output, created_files = output_handler.process_output(
            response=response,
            output_config=output_config,
            console_output=console_output,
            file_output=file_output
        )
        print(formatted_output)

    # Log created files
    if created_files:
        print(f"\nCreated output files: {', '.join(created_files)}")
        logger.info("Created output files: %s", ', '.join(created_files))


if __name__ == "__main__":
    main()
