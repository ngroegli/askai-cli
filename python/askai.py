import os
import argparse
import sys
import json
import threading
from banner_argument_parser import BannerArgumentParser
from openrouter_api import ask_openrouter
from config import load_config
from logger import setup_logger
from utils import (
    write_to_file,
    tqdm_spinner,
    get_piped_input,
    get_file_input,
    build_format_instruction,
    render_markdown,
    print_error_or_warnings
)
from system_manager import SystemManager
from chat_manager import ChatManager


def setup_argument_parser():
    """Setup and configure the argument parser for the CLI."""
    parser = BannerArgumentParser(description="AskAI - AI assistant for your terminal")
    
    # Input options
    parser.add_argument('-q', '--question', help='Your question for the AI')
    parser.add_argument('-fi', '--file-input', help='Input file to include as context')
    
    # Output options
    parser.add_argument('-o', '--output', help='Output file to save result')
    parser.add_argument('-f', '--format', 
                       default="rawtext", 
                       choices=["rawtext", "json", "md"], 
                       help='Instruct AI to respond in rawtext (default), json, or md format')
    parser.add_argument('--plain-md', 
                       action='store_true', 
                       help='If used with -f md, outputs raw markdown as plain text instead of rendering')
    
    # Model options
    parser.add_argument('-m', '--model', help='Override default AI model')
    
    # System options
    system_group = parser.add_argument_group('System logic')
    system_group.add_argument('-us', '--use-system',
                       nargs='?',
                       const='new',  # When -s is used without value
                       metavar='SYSTEM_ID',
                       help='Add system-specific context. Use without ID to select from available systems')
    system_group.add_argument('-ls', '--list-systems', 
                       action='store_true', 
                       help='List all available system files')
    system_group.add_argument('-vs', '--view-system',
                       nargs='?',
                       const='',  # When -vs is used without value
                       help='View system content. Use without ID to select from available systems')
    system_group.add_argument('-si', '--system-input',
                       type=json.loads,
                       help='Provide system inputs as JSON object')
    
    # Debug options
    parser.add_argument('--debug', 
                       action='store_true', 
                       help='Enable debug logging for this session')
    
    # Chat persistence options
    chat_group = parser.add_argument_group('Chat persistence')
    chat_group.add_argument('-pc', '--persistent-chat',
                        nargs='?', 
                        const='new',
                        metavar='CHAT_ID',
                        help='Enable persistent chat. Use without value to create new chat, '
                             'or provide chat ID to continue existing chat')
    chat_group.add_argument('-lc', '--list-chats',
                        action='store_true',
                        help='List all available chat files')
    chat_group.add_argument('-vc', '--view-chat',
                        nargs='?',
                        const='',  # When -vc is used without value
                        metavar='CHAT_ID',
                        help='View chat history. Use without ID to select from available chats')
    
    return parser


def parse_arguments():
    """Parse and validate command line arguments."""
    parser = setup_argument_parser()
    
    # Show help if no arguments provided
    if len(sys.argv) == 1:
        sys.argv.append('--help')
        
    return parser.parse_args()


def build_messages(args, system_manager, logger):
    """Builds the message list for OpenRouter.
    
    Args:
        args: Parsed command line arguments
        system_manager: SystemManager instance
        logger: Logger instance for recording operations
        
    Returns:
        list: List of message dictionaries for the AI model
    """
    messages = []

    # Handle piped input from terminal
    if context := get_piped_input():
        logger.info(json.dumps({"log_message": "Piped input received"}))
        messages.append({
            "role": "system", 
            "content": f"Previous terminal output:\n{context}"
        })

    # Handle input file content
    if args.file_input and (file_content := get_file_input(args.file_input)):
        logger.info(json.dumps({
            "log_message": "Input file read successfully", 
            "file_path": args.file_input
        }))
        messages.append({
            "role": "system", 
            "content": f"The file content of {args.file_input} to work with:\n{file_content}"
        })

    # Add system-specific context if specified
    if args.use_system is not None:  # -s was used
        system_id = None
        if args.use_system == 'new':  # No specific system ID was provided
            system_id = system_manager.select_system()
            if system_id is None:
                print("System selection cancelled.")
                sys.exit(0)
        else:  # Specific system ID was provided
            system_id = args.use_system
            
        logger.info(json.dumps({
            "log_message": "System used", 
            "system": system_id
        }))
        
        system_data = system_manager.get_system_content(system_id)
        if system_data is None:
            print(f"Error: System '{system_id}' does not exist")
            sys.exit(1)
            
        # Process system inputs
        system_inputs = system_manager.process_system_inputs(
            system_id=system_id,
            input_values=args.system_input
        )
        
        if system_inputs is None:
            sys.exit(1)
            
        # Combine system content with processed inputs
        system_context = system_data['content']
        if system_inputs:
            system_context += "\n\nSystem Inputs:\n" + json.dumps(system_inputs, indent=2)
            
        messages.append({
            "role": "system", 
            "content": system_context
        })

    # Add format instructions
    messages.append({
        "role": "system", 
        "content": build_format_instruction(args.format)
    })

    # Add user question if provided
    if args.question:
        messages.append({
            "role": "user", 
            "content": args.question
        })

    return messages


def handle_system_commands(args, system_manager, logger):
    """Handle system-related commands."""
    if args.list_systems:
        logger.info(json.dumps({"log_message": "User requested to list all available system files"}))
        systems = system_manager.list_systems()
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
        system_id = args.view_system or system_manager.select_system()
        
        if system_id is None:
            print("System selection cancelled.")
            return True
            
        logger.info(json.dumps({
            "log_message": "User requested to view system file",
            "system": system_id
        }))
        try:
            system_manager.display_system(system_id)
        except ValueError as e:
            print(f"Error: {str(e)}")
        return True

    return False


def handle_chat_commands(args, chat_manager, logger):
    """Handle chat-related commands."""
    if args.list_chats:
        logger.info(json.dumps({"log_message": "User requested to list all available chats"}))
        chats = chat_manager.list_chats()
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
        chat_id = args.view_chat or chat_manager.select_chat(allow_new=False)
        
        if chat_id is None:
            print("Chat selection cancelled.")
            return True
            
        logger.info(json.dumps({
            "log_message": "User requested to view chat history",
            "chat_id": chat_id
        }))
        try:
            chat_manager.display_chat(chat_id)
        except ValueError as e:
            print(f"Error: {str(e)}")
        return True

    return False


def validate_arguments(args, logger):
    """Validate command line arguments and log warnings/errors."""
    if not args.question and not args.use_system:
        logger.error(json.dumps({
            "log_message": "User did not provide a question with -q or a dedicated system with -s"
        }))
        print_error_or_warnings(
            text="ERROR: Provide a question with -q or a dedicated system with -s"
        )
        sys.exit(1)

    if args.plain_md and args.format != "md":
        logger.warning(json.dumps({
            "log_message": "User used --plain-md without -f md"
        }))
        print_error_or_warnings(
            text="WARN: --plain-md can only be used with -f md. The parameter --plain-md will be ignored.",
            warning_only=True
        )


def get_ai_response(messages, args, logger):
    """Get response from AI model with progress spinner."""
    stop_spinner = threading.Event()
    spinner = threading.Thread(target=tqdm_spinner, args=(stop_spinner,))
    spinner.start()

    try:
        logger.info(json.dumps({"log_message": "Messages sending to ai"}))
        response = ask_openrouter(messages=messages, model=args.model, debug=args.debug)
        logger.debug(json.dumps({
            "log_message": "Response from ai", 
            "response": str(response)
        }))
        logger.info(json.dumps({"log_message": "Response received from ai"}))
        return response
    finally:
        stop_spinner.set()
        spinner.join()


def handle_output(response, args, logger):
    """Handle the output of the AI response based on arguments."""
    if args.output:
        logger.info(json.dumps({
            "log_message": "Writing response to output file", 
            "output_file": args.output
        }))
        write_to_file(args.output, response)
        print(f"Response written to {args.output}")
        return True

    if args.format == "md" and not args.plain_md:
        logger.info(json.dumps({"log_message": "Rendering response as markdown"}))
        render_markdown(response)
        return True

    logger.info(json.dumps({"log_message": "Printing response as raw text"}))
    print(response)
    return False


def main():
    """Main entry point for the AskAI CLI application."""
    config = load_config()
    args = parse_arguments()
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logger = setup_logger(config, args.debug)
    chat_manager = ChatManager(config)
    system_manager = SystemManager(base_path)

    logger.info(json.dumps({"log_message": "AskAI started and arguments parsed"}))

    # Handle chat and system commands
    if handle_chat_commands(args, chat_manager, logger):
        sys.exit(0)
    if handle_system_commands(args, system_manager, logger):
        sys.exit(0)

    # Validate arguments
    validate_arguments(args, logger)

    # Build and send messages to AI
    messages = build_messages(args, system_manager, logger)

    # Handle persistent chat
    chat_id = None
    if args.persistent_chat is not None:  # Check if -pc was used at all
        if args.persistent_chat == 'n':  # Explicit request for new chat
            chat_id = chat_manager.create_chat()
            print(f"\nCreated new chat with ID: {chat_id}")
        elif args.persistent_chat == 'new':  # No chat ID provided, show selection
            selected_chat = chat_manager.select_chat(allow_new=True)
            
            if selected_chat is None:
                print("Chat selection cancelled.")
                sys.exit(0)
            elif selected_chat == 'new':
                chat_id = chat_manager.create_chat()
                print(f"\nCreated new chat with ID: {chat_id}")
            else:
                chat_id = selected_chat
        else:  # Specific chat ID provided
            chat_id = args.persistent_chat
            
        # If we have a chat_id, load its context
        if chat_id:
            try:
                # Add context from chat history
                context_messages = chat_manager.build_context_messages(chat_id)
                # Insert context messages before the system messages
                system_messages = [msg for msg in messages if msg['role'] == 'system']
                user_messages = [msg for msg in messages if msg['role'] == 'user']
                messages = system_messages + context_messages + user_messages
                print(f"\nContinuing chat: {chat_id}")
            except ValueError as e:
                print(f"Error: {str(e)}")
                sys.exit(1)

    logger.debug(json.dumps({"log_message": "Messages content", "messages": messages}))
    
    # Get AI response
    response = get_ai_response(messages, args, logger)

    # Store chat history if using persistent chat
    if chat_id:
        chat_manager.add_conversation(chat_id, messages, response)

    # Handle output and exit if needed
    if handle_output(response, args, logger):
        sys.exit(0)


if __name__ == "__main__":
    main()
