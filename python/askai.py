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
from output.output_handler import OutputHandler


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

    # Initialize output handler
    output_handler = OutputHandler()

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
        url=args.url,
        image=args.image if hasattr(args, 'image') else None,
        pdf=args.pdf if hasattr(args, 'pdf') else None
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
    console_output = True  # Default to showing console output
    file_output = args.save if hasattr(args, 'save') else False
    
    # Enable file output if we have system outputs with write_to_file
    system_has_file_output = False
    if system_outputs:
        for output in system_outputs:
            if output.should_write_to_file():
                file_output = True
                system_has_file_output = True
                break
    
    # Process output
    # Check if user specified an output file via args.output
    has_output_arg = hasattr(args, 'output') and args.output is not None
    
    # Initialize output configuration
    output_config = {}
        
    # Add format to output_config so the handler knows what format to use
    output_config['format'] = args.format
    
    # Don't override file_output if it was already set by system outputs
    if has_output_arg and not system_has_file_output:
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
        
    # For system output files, if no directory specified, use interactive prompt
    
    formatted_output, created_files = output_handler.process_output(
        output=response,
        output_config=output_config,
        console_output=console_output,
        file_output=file_output,
        system_outputs=system_outputs
    )
    
    # Print the formatted output
    print(formatted_output)
    
    # Log created files
    if created_files:
        print(f"\nCreated output files: {', '.join(created_files)}")
        if logger:
            logger.info(f"Created output files: {', '.join(created_files)}")
if __name__ == "__main__":
    main()
