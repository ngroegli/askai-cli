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
    messages, resolved_pattern_id = message_builder.build_messages(
        question=args.question,
        file_input=args.file_input,
        pattern_id=args.use_pattern,
        pattern_input=args.pattern_input,
        format=args.format,
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
            
    # Special handling for Linux CLI command generation pattern
    is_linux_cli_pattern = (resolved_pattern_id == "linux_cli_command_generation")
    if is_linux_cli_pattern:
        logger.debug("Linux CLI command pattern detected early")
        
        # Make sure we have a response in the expected format
        if isinstance(response, dict) and "content" in response:
            try:
                content_text = response["content"]
                import re
                
                # Try to parse the content as JSON
                json_match = re.search(r'\{[\s\S]*?"result":\s*"([^"]+)"[\s\S]*?"visual_output":\s*"([\s\S]*?)"[\s\S]*?\}', content_text)
                
                if json_match:
                    command = json_match.group(1)
                    visual_output = json_match.group(2).replace('\\n', '\n').replace('\\"', '"')
                    
                    # Create a clean response
                    response = {
                        "result": command,
                        "visual_output": visual_output
                    }
                    logger.debug("Successfully restructured response for Linux CLI pattern")
            except Exception as e:
                logger.debug(f"Error restructuring response: {str(e)}")

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
    has_output_arg = hasattr(args, 'output') and args.output is not None
    
    # Initialize output configuration
    output_config = {}
        
    # Add format to output_config so the handler knows what format to use
    output_config['format'] = args.format
    
    # Special handling for Linux CLI command generation pattern
    if resolved_pattern_id == "linux_cli_command_generation":
        # Check if the response has the expected format
        if isinstance(response, dict) and "result" in response and "visual_output" in response:
            command = response["result"]
            visual_output = response["visual_output"]
            
            # Print the visual output
            print("\n" + "=" * 80)
            print("LINUX COMMAND GENERATED")
            print("=" * 80)
            print(f"\nCommand: {command}")
            print("\nEXPLANATION:")
            print("-" * 50)
            print(visual_output)
            print("-" * 50)
            
            # Prompt for execution
            from patterns.pattern_outputs import PatternOutput
            PatternOutput.execute_command(command, "result")
            
            # Exit successfully
            sys.exit(0)
    
    # Don't override file_output if it was already set by pattern outputs
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
        
    # For pattern output files, if no directory specified, use interactive prompt
    
    formatted_output, created_files = output_handler.process_output(
        output=response,
        output_config=output_config,
        console_output=console_output,
        file_output=file_output,
        pattern_outputs=pattern_outputs
    )
    
    # For Linux CLI command pattern, let's handle the output specially
    if resolved_pattern_id == "linux_cli_command_generation":
        logger.debug("Linux CLI command pattern detected")
        
        # Extract the actual content from the response
        command = None
        visual_output = None
        
        # Case 1: Response is already the expected dict format with result field
        if isinstance(response, dict) and "result" in response:
            command = response["result"]
            visual_output = response.get("visual_output", "")
            logger.debug("Found result directly in response")
            
        # Case 2: Response is a dict with content field containing formatted output
        elif isinstance(response, dict) and "content" in response:
            content = response["content"]
            logger.debug(f"Content from response: {content[:100]}...")
            
            # Try to extract using simple pattern matching
            import re
            
            # Look for "result": "command"
            result_match = re.search(r'"result":\s*"([^"]+)"', content)
            if result_match:
                command = result_match.group(1)
                logger.debug("Extracted command using regex")
                
            # Look for "visual_output": "markdown content"
            visual_match = re.search(r'"visual_output":\s*"(.*?)(?:"\s*\}|"\s*,)', content, re.DOTALL)
            if visual_match:
                visual_output = visual_match.group(1)
                # Unescape the content
                visual_output = visual_output.replace('\\n', '\n').replace('\\"', '"')
                logger.debug("Extracted visual output using regex")
                
        # FALLBACK: If we couldn't extract the command, try plain text extraction
        if command is None and isinstance(response, dict) and "content" in response:
            content = response["content"]
            # Look for anything that looks like a Linux command in the content
            command_patterns = [
                r'find\s+[.]\s+-type\s+f\s+-size',
                r'ls\s+-[la]+h\s+',
                r'grep\s+-[r]+',
                r'ps\s+aux'
            ]
            
            for pattern in command_patterns:
                command_match = re.search(pattern, content)
                if command_match:
                    # Extract a reasonable command length
                    start = command_match.start()
                    end = min(start + 100, len(content))
                    command_line = content[start:end].split('\n')[0]
                    command = command_line.strip().strip('"')
                    logger.debug("Extracted command using fallback pattern")
                    break
                
        # Process the command if found
        if command:
            logger.debug(f"Command found with visual_output present: {visual_output is not None}")
            
            # First display the visual output explanation
            if visual_output:
                print("\n" + "=" * 80)
                print(f"COMMAND: {command}")
                print("EXPLANATION:")
                print("=" * 80 + "\n")
                print(visual_output)
            
            # Then prompt for execution
            from patterns.pattern_outputs import PatternOutput
            PatternOutput.execute_command(command, "result")
        else:
            logger.warning("Failed to parse command from response")
            # For other patterns, print the formatted output normally
            print(formatted_output)
    else:
        # For other patterns, print the formatted output normally
        print(formatted_output)
    
    # Log created files
    if created_files:
        print(f"\nCreated output files: {', '.join(created_files)}")
        if logger:
            logger.info(f"Created output files: {', '.join(created_files)}")
if __name__ == "__main__":
    main()
