"""
CLI argument parsing and validation module.
Handles all command-line argument setup, parsing, and validation logic.
"""

import argparse
import sys
import json
from .banner_argument_parser import BannerArgumentParser
from utils import print_error_or_warnings


class CLIParser:
    """Handles command-line argument parsing and validation."""
    
    def __init__(self):
        self.parser = self._setup_argument_parser()
    
    def _setup_argument_parser(self):
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
        
        # Provider-specific options
        provider_group = parser.add_argument_group('Provider internals')
        provider_group.add_argument('-or', '--openrouter',
                            nargs='+',
                            metavar='COMMAND',
                            help='OpenRouter API commands: check-credits, list-models [FILTER...]')
        # Future provider example:
        # provider_group.add_argument('-az', '--azure',
        #                     nargs='+',
        #                     metavar='COMMAND',
        #                     help='Azure OpenAI API commands: check-quota, list-deployments [FILTER...]')
        
        return parser

    def parse_arguments(self):
        """Parse and validate command line arguments."""
        # Show help if no arguments provided
        if len(sys.argv) == 1:
            sys.argv.append('--help')
            
        return self.parser.parse_args()

    def validate_arguments(self, args, logger):
        """Validate command line arguments and log warnings/errors."""
        # Check if user is using any command that doesn't require a question
        has_command = (args.list_systems or args.view_system is not None or 
                      args.list_chats or args.view_chat is not None or 
                      args.openrouter is not None)
        
        if not args.question and not args.use_system and not has_command:
            logger.error(json.dumps({
                "log_message": "User did not provide a question with -q or a dedicated system with -s"
            }))
            print_error_or_warnings(
                text="ERROR: Provide a question with -q or a dedicated system with -s"
            )
            sys.exit(1)

        # Validate OpenRouter commands
        if args.openrouter is not None:
            if len(args.openrouter) == 0:
                logger.error(json.dumps({
                    "log_message": "User provided --openrouter without any command"
                }))
                print_error_or_warnings(
                    text="ERROR: --openrouter requires a command (check-credits, list-models)"
                )
                sys.exit(1)
            
            valid_commands = ['check-credits', 'list-models']
            command = args.openrouter[0]
            if command not in valid_commands:
                logger.error(json.dumps({
                    "log_message": f"User provided invalid OpenRouter command: {command}"
                }))
                print_error_or_warnings(
                    text=f"ERROR: Invalid OpenRouter command '{command}'. Valid commands: {', '.join(valid_commands)}"
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
