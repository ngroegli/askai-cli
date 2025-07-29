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


def build_messages(question=None, file_input=None, system_id=None, system_input=None, 
                format="rawtext", system_manager=None, logger=None):
    """Builds the message list for OpenRouter.
    
    Args:
        question: Optional user question
        file_input: Optional path to input file
        system_id: Optional system ID to use
        system_input: Optional system inputs as dict
        format: Response format (rawtext, json, or md)
        system_manager: SystemManager instance
        logger: Logger instance for recording operations
        
    Returns:
        tuple: (messages, resolved_system_id)
    """
    messages = []
    resolved_system_id = system_id

    # Handle piped input from terminal
    if context := get_piped_input():
        logger.info(json.dumps({"log_message": "Piped input received"}))
        messages.append({
            "role": "system", 
            "content": f"Previous terminal output:\n{context}"
        })

    # Handle input file content
    if file_input and (file_content := get_file_input(file_input)):
        logger.info(json.dumps({
            "log_message": "Input file read successfully", 
            "file_path": file_input
        }))
        messages.append({
            "role": "system", 
            "content": f"The file content of {file_input} to work with:\n{file_content}"
        })

    # Add system-specific context if specified
    if system_id is not None:
        # Handle system selection if no specific ID was provided
        if system_id == 'new':
            resolved_system_id = system_manager.select_system()
            if resolved_system_id is None:
                print("System selection cancelled.")
                sys.exit(0)
        else:
            resolved_system_id = system_id
        logger.info(json.dumps({
            "log_message": "System used", 
            "system": resolved_system_id
        }))
        system_data = system_manager.get_system_content(resolved_system_id)
        if system_data is None:
            print(f"Error: System '{resolved_system_id}' does not exist")
            sys.exit(1)
        # Get and validate system data
        system_inputs = system_manager.process_system_inputs(
            system_id=resolved_system_id,
            input_values=system_input
        )
        if system_inputs is None:
            sys.exit(1)
        # Add system prompt content (purpose and functionality only)
        system_prompt = system_data['prompt_content']
        messages.append({
            "role": "system", 
            "content": system_prompt
        })
        # If there are inputs, provide them in a structured way
        if system_inputs:
            messages.append({
                "role": "system",
                "content": "Available inputs:\n" + json.dumps(system_inputs, indent=2)
            })
        # If there are output definitions, provide them to help the AI structure its response
        if system_outputs := system_data.get('outputs'):
            output_spec = {
                output.name: {
                    "description": output.description,
                    "type": output.output_type.value,
                    "required": output.required,
                    "schema": output.schema if hasattr(output, 'schema') else None
                } for output in system_outputs
            }
            messages.append({
                "role": "system",
                "content": "Required output format:\n" + json.dumps(output_spec, indent=2)
            })

    # Add format instructions
    messages.append({
        "role": "system", 
        "content": build_format_instruction(format)
    })

    # Add user question if provided
    if question:
        messages.append({
            "role": "user", 
            "content": question
        })

    return messages, resolved_system_id

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


def get_model_configuration(model_name, config, logger, system_data=None):
    """Get model configuration based on priority: CLI > System config > Global config.
    
    Args:
        model_name: Optional model name from CLI
        config: Global configuration
        logger: Logger instance
        system_data: Optional system data containing system-specific configuration
        
    Returns:
        ModelConfiguration: The model configuration to use
    """
    from system_configuration import ModelConfiguration, ModelProvider
    
    # Priority 1: Explicit model name
    if model_name:
        logger.info(json.dumps({
            "log_message": "Using explicit model configuration",
            "model": model_name
        }))
        return ModelConfiguration(
            provider=ModelProvider.OPENROUTER,
            model_name=model_name
        )
    
    # Priority 2: System configuration
    if system_data and isinstance(system_data, dict):
        # Configuration is nested under the 'configuration' key
        system_config = system_data.get('configuration')
        
        if system_config:          
            if hasattr(system_config, 'model') and system_config.model:
                # Direct access to ModelConfiguration object from SystemConfiguration
                model_config = system_config.model
                logger.info(json.dumps({
                    "log_message": "Using model configuration from system",
                    "model_name": model_config.model_name,
                    "provider": model_config.provider.value if model_config.provider else 'openrouter'
                }))
                return model_config
            elif isinstance(system_config, dict) and 'model' in system_config:
                # Handle dictionary format
                logger.info(f"Creating model configuration from dict: {system_config}")
                try:
                    model_data = system_config['model']
                    return ModelConfiguration(
                        provider=model_data.get('provider', 'openrouter'),
                        model_name=model_data.get('model_name'),
                        temperature=model_data.get('temperature', 0.7),
                        max_tokens=model_data.get('max_tokens'),
                        stop_sequences=model_data.get('stop_sequences'),
                        custom_parameters=model_data.get('custom_parameters')
                    )
                except Exception as e:
                    logger.error(f"Error creating model configuration from dict: {e}")
    
    # Priority 3: Global configuration
    logger.info(json.dumps({
        "log_message": "Using global default model configuration",
        "model": config["default_model"]
    }))
    return ModelConfiguration(
        provider=ModelProvider.OPENROUTER,
        model_name=config["default_model"]
    )

def get_ai_response(messages, model_name=None, system_id=None, debug=False, logger=None, system_manager=None):
    """Get response from AI model with progress spinner.
    
    Args:
        messages: List of message dictionaries
        model_name: Optional model name to override default
        system_id: Optional system ID to get system-specific configuration
        debug: Whether to enable debug mode
        logger: Logger instance
        system_manager: SystemManager instance for accessing system data
    """
    stop_spinner = threading.Event()
    spinner = threading.Thread(target=tqdm_spinner, args=(stop_spinner,))
    spinner.start()

    try:
        logger.info(json.dumps({"log_message": "Messages sending to ai"}))
        
        # Get configuration from the proper source
        config = load_config()
        system_data = None
        if system_id:
            system_data = system_manager.get_system_content(system_id)

        model_config = get_model_configuration(model_name, config, logger, system_data)
            
        response = ask_openrouter(
            messages=messages, 
            model_config=model_config,
            debug=debug
        )
        
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

    # Build messages and get the resolved system_id (after selection)
    messages, resolved_system_id = build_messages(
        question=args.question,
        file_input=args.file_input,
        system_id=args.use_system,
        system_input=args.system_input,
        format=args.format,
        system_manager=system_manager,
        logger=logger
    )

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
    
    # Get AI response with explicit parameters, using the resolved system_id
    response = get_ai_response(
        messages=messages,
        model_name=args.model,
        system_id=resolved_system_id,
        debug=args.debug,
        logger=logger,
        system_manager=system_manager
    )

    # Store chat history if using persistent chat
    if chat_id:
        # Parse outputs if we have output specifications
        structured_outputs = None
        system_outputs = None
        system_config = None
        
        if resolved_system_id:
            system_data = system_manager.get_system_content(resolved_system_id)
            if system_data:
                system_outputs = system_data.get('outputs', [])
                system_config = system_data.get('configuration')
                
                if system_outputs:
                    # Try to parse structured outputs from response
                    try:
                        import re
                        outputs = []
                        for output_def in system_outputs:
                            # Try to find content matching the output type pattern
                            if output_def.output_type.value == 'json':
                                matches = re.findall(r'\{[\s\S]*?\}', response)
                                if matches:
                                    outputs.append({
                                        'name': output_def.name,
                                        'type': output_def.output_type.value,
                                        'value': json.loads(matches[0])
                                    })
                            elif output_def.output_type.value == 'markdown':
                                # Look for markdown sections
                                matches = re.findall(r'##[\s\S]*?(?=##|\Z)', response)
                                if matches:
                                    outputs.append({
                                        'name': output_def.name,
                                        'type': output_def.output_type.value,
                                        'value': matches[0].strip()
                                    })
                        if outputs:
                            structured_outputs = outputs
                    except Exception as e:
                        logger.warning(f"Could not parse structured outputs: {str(e)}")
        
        chat_manager.add_conversation(
            chat_id=chat_id,
            messages=messages,
            response=response,
            outputs=structured_outputs,
            system_outputs=system_outputs,
            system_config=system_config
        )

    # Handle output and exit if needed
    if handle_output(response, args, logger):
        sys.exit(0)


if __name__ == "__main__":
    main()
