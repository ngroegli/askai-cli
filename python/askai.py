"""
Main entry point for the AskAI CLI application.
Orchestrates the different components to provide AI assistance via command line.
"""

import os
import sys
import json
from config import load_config
from logger import setup_logger
from systems import SystemManager
from chat import ChatManager
from cli import CLIParser, CommandHandler
from message_builder import MessageBuilder
from ai import AIService
from output_handler import OutputHandler


def main():
    """Main entry point for the AskAI CLI application."""
    # Initialize configuration and base components
    config = load_config()
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Initialize CLI parser and parse arguments
    cli_parser = CLIParser()
    args = cli_parser.parse_arguments()
    
    # Setup logging
    logger = setup_logger(config, args.debug)
    logger.info(json.dumps({"log_message": "AskAI started and arguments parsed"}))
    
    # Initialize managers and services
    chat_manager = ChatManager(config, logger)
    system_manager = SystemManager(base_path)
    command_handler = CommandHandler(system_manager, chat_manager, logger)
    message_builder = MessageBuilder(system_manager, logger)
    ai_service = AIService(logger)
    output_handler = OutputHandler(logger)

    # Handle chat and system commands (these exit if executed)
    if command_handler.handle_chat_commands(args):
        sys.exit(0)
    if command_handler.handle_system_commands(args):
        sys.exit(0)
    if command_handler.handle_openrouter_commands(args):
        sys.exit(0)

    # Validate arguments
    cli_parser.validate_arguments(args, logger)

    # Build messages and get the resolved system_id (after selection)
    messages, resolved_system_id = message_builder.build_messages(
        question=args.question,
        file_input=args.file_input,
        system_id=args.use_system,
        system_input=args.system_input,
        format=args.format,
        url=args.url
    )
    
    # Check if message building was cancelled
    if messages is None:
        sys.exit(0)

    # Handle persistent chat setup and context loading
    chat_id, messages = chat_manager.handle_persistent_chat(args, messages)

    # Debug log the final messages
    logger.debug(json.dumps({"log_message": "Messages content", "messages": messages}))
    
    # Determine if web search should be enabled for URL analysis
    enable_url_search = args.url is not None
    
    # Get AI response
    response = ai_service.get_ai_response(
        messages=messages,
        model_name=args.model,
        system_id=resolved_system_id,
        debug=args.debug,
        system_manager=system_manager,
        enable_url_search=enable_url_search
    )

    # Store chat history if using persistent chat
    chat_manager.store_chat_conversation(
        chat_id, messages, response, resolved_system_id, system_manager
    )

    # Get system outputs for auto-execution handling
    system_outputs = None
    if resolved_system_id:
        system_data = system_manager.get_system_content(resolved_system_id)
        if system_data:
            system_outputs = system_data.get('outputs', [])

    # Handle output
    output_handler.handle_output(response, args, system_outputs)


if __name__ == "__main__":
    main()
