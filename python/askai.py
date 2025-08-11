"""
Main entry point for the AskAI CLI application.
Orchestrates the different components to provide AI assistance via command line.
"""

import os
import sys
import json
import re
from config import load_config
from logger import setup_logger
from patterns import PatternManager
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
    pattern_manager = PatternManager(base_path)
    command_handler = CommandHandler(pattern_manager, chat_manager, logger)
    message_builder = MessageBuilder(pattern_manager, logger)
    ai_service = AIService(logger)

    # Initialize output handler
    output_handler = OutputHandler()

    # Handle chat and pattern commands (these exit if executed)
    if command_handler.handle_chat_commands(args):
        sys.exit(0)
    if command_handler.handle_pattern_commands(args):
        sys.exit(0)
    if command_handler.handle_openrouter_commands(args):
        sys.exit(0)

    # Validate arguments
    cli_parser.validate_arguments(args, logger)

    # Build messages and get the resolved pattern_id (after selection)
    # When using a pattern, ignore all question logic parameters
    using_pattern = args.use_pattern is not None
    messages, resolved_pattern_id = message_builder.build_messages(
        question=None if using_pattern else args.question,
        file_input=None if using_pattern else args.file_input,
        pattern_id=args.use_pattern,
        pattern_input=args.pattern_input,
        format="rawtext" if using_pattern else args.format,  # Use default format with patterns
        url=None if using_pattern else args.url,
        image=None if using_pattern else (args.image if hasattr(args, 'image') else None),
        pdf=None if using_pattern else (args.pdf if hasattr(args, 'pdf') else None),
        image_url=None if using_pattern else (args.image_url if hasattr(args, 'image_url') else None),
        pdf_url=None if using_pattern else (args.pdf_url if hasattr(args, 'pdf_url') else None)
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
        pattern_id=resolved_pattern_id,
        debug=args.debug,
        pattern_manager=pattern_manager,
        enable_url_search=enable_url_search
    )

    # Store chat history if using persistent chat
    chat_manager.store_chat_conversation(
        chat_id, messages, response, resolved_pattern_id, pattern_manager
    )

    # Get pattern outputs for auto-execution handling
    pattern_outputs = None
    if resolved_pattern_id:
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
        except Exception as e:
            logger.debug(f"Error checking for direct JSON: {str(e)}")
        
        logger.debug(f"Using pattern manager to handle response for {resolved_pattern_id}")
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
        logger.info(f"Created output files: {', '.join(created_files)}")


if __name__ == "__main__":
    main()
