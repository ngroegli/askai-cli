"""
CLI argument parsing and validation module.
Handles all command-line argument setup, parsing, and validation logic.
"""

import sys
import json
from askai.shared.utils import print_error_or_warnings
from askai import __version__, get_full_version
from .banner_argument_parser import BannerArgumentParser


class CLIParser:
    """Handles command-line argument parsing and validation."""

    def __init__(self):
        self.parser = self._setup_argument_parser()

    def _setup_argument_parser(self):
        """Setup and configure the argument parser for the CLI."""
        parser = BannerArgumentParser(description="AskAI - AI assistant for your terminal")

        # Add version argument
        parser.add_argument('--version', action='version',
                          version=f'AskAI CLI {get_full_version()}')

        # Question-related options (grouped together)
        question_group = parser.add_argument_group('Question logic (ignored when using patterns)')
        question_group.add_argument('-q', '--question', help='Your question for the AI')
        question_group.add_argument('-fi', '--file-input', help='Input file to include as context')
        question_group.add_argument('-url', '--url', help='URL to analyze/summarize along with your question')
        question_group.add_argument('-img', '--image',
                           help='Image file to analyze along with your question (JPG, PNG, WebP, etc)')
        question_group.add_argument('-img-url', '--image-url',
                           help='Image URL to analyze along with your question')
        question_group.add_argument('-pdf', '--pdf',
                           help='PDF file to analyze along with your question (must have .pdf extension)')
        question_group.add_argument('-pdf-url', '--pdf-url', help='PDF URL to analyze along with your question')
        question_group.add_argument('-o', '--output', help='Output file to save result')
        question_group.add_argument('-f', '--format',
                           default="rawtext",
                           choices=["rawtext", "json", "md"],
                           help='Instruct AI to respond in rawtext (default), json, or md format')
        question_group.add_argument('--plain-md',
                           action='store_true',
                           help='If used with -f md, outputs raw markdown as plain text instead of rendering')
        question_group.add_argument('-m', '--model', help='Override default AI model')

        # Chat persistence options as a subgroup under Question logic
        chat_group = parser.add_argument_group(
            '  Chat persistence (subgroup of Question logic, not compatible with patterns)'
        )
        chat_group.add_argument('-pc', '--persistent-chat',
                            nargs='?',
                            const='new',
                            metavar='CHAT_ID',
                            help='Enable persistent chat. Use without value to create new chat, '
                                 'or provide chat ID to continue existing chat (incompatible with patterns)')
        chat_group.add_argument('-lc', '--list-chats',
                            action='store_true',
                            help='List all available chat files (can be used with patterns, but chat will be ignored)')
        chat_group.add_argument(
            '-vc', '--view-chat',
            nargs='?',
            const='',  # When -vc is used without value
            metavar='CHAT_ID',
            help='View chat history. Use without ID to select from available chats (incompatible with patterns)'
        )
        chat_group.add_argument('--manage-chats',
                            action='store_true',
                            help='Manage chat files (repair or delete corrupted files) (incompatible with patterns)')

        # Pattern options
        pattern_group = parser.add_argument_group('Pattern logic (not compatible with chat persistence)')
        pattern_group.add_argument(
            '-up', '--use-pattern',
            nargs='?',
            const='new',  # When -p is used without value
            metavar='PATTERN_ID',
            help='Use a predefined pattern. Without ID, select from available patterns (incompatible with chat)'
        )
        pattern_group.add_argument('-lp', '--list-patterns',
                           action='store_true',
                           help='List all available pattern files')
        pattern_group.add_argument('-vp', '--view-pattern',
                           nargs='?',
                           const='',  # When -vp is used without value
                           help='View pattern content. Use without ID to select from available patterns')
        pattern_group.add_argument('-pi', '--pattern-input',
                           type=json.loads,
                           help='Provide pattern inputs as JSON object (used with --use-pattern)')

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

        # Configuration management
        config_group = parser.add_argument_group('Configuration management')
        config_group.add_argument('--config',
                           nargs='*',
                           metavar='ACTION',
                           help='Configuration management commands: create-test-config, show-config-path')

        # Debug options (moved to the end)
        debug_group = parser.add_argument_group('Debug options')
        debug_group.add_argument('--debug',
                           action='store_true',
                           help='Enable debug logging for this session')

        # TUI (Terminal User Interface) options
        tui_group = parser.add_argument_group('Interface mode')
        tui_group.add_argument('--interactive', '-i',
                          action='store_true',
                          help='Launch interactive terminal interface')

        return parser

    def parse_arguments(self):
        """Parse and validate command line arguments."""
        # Show help if no arguments provided
        if len(sys.argv) == 1:
            sys.argv.append('--help')

        # Parse arguments - argparse will automatically handle help flags
        return self.parser.parse_args()

    def validate_arguments(self, args, logger):
        """Validate command line arguments and log warnings/errors."""
        # Function already imported at the top of the file

        # Check if user is using any command that doesn't require a question
        has_command = (args.list_patterns or args.view_pattern is not None or
                      args.list_chats or args.view_chat is not None or
                      args.openrouter is not None)

        # Allow URL, image, or PDF without question (for simple analysis)
        has_url = args.url is not None
        has_image = args.image is not None
        has_image_url = args.image_url is not None
        has_pdf = args.pdf is not None
        has_pdf_url = args.pdf_url is not None

        # Check if pattern is being used
        using_pattern = args.use_pattern is not None

        # Check if chat persistence is being used
        using_chat = args.persistent_chat is not None or args.view_chat is not None

        # Check for incompatible combinations of pattern and chat
        if using_pattern and using_chat:
            # Only log the issue, don't print a warning (main warning will be in askai.py)
            logger.warning(json.dumps({
                "log_message": "User attempting to use chat persistence features with pattern; these are incompatible"
            }))

        # Check if question-related parameters are used with a pattern
        if using_pattern and any([
            args.question, has_url, has_image, has_image_url,
            has_pdf, has_pdf_url, args.file_input, args.output,
            args.format != "rawtext", args.plain_md, args.model
        ]):
            logger.warning(json.dumps({
                "log_message": "User provided question logic parameters with a pattern; these will be ignored"
            }))
            print_error_or_warnings(
                text=(
                    "Question logic parameters (-q, -url, -img, -img-url, -pdf, -pdf-url, "
                    "-fi, -o, -f, --plain-md, -m) are ignored when using a pattern (-up). "
                    "Pattern inputs should be provided using -pi."
                ),
                warning_only=True
            )

        if not (args.question or args.use_pattern or has_command or
                has_url or has_image or has_pdf or has_image_url or has_pdf_url):
            logger.error(json.dumps({
                "log_message": (
                    "User did not provide a question with -q, URL with -url, "
                    "image with -img/--image-url, PDF with -pdf/--pdf-url, "
                    "or a dedicated pattern with -up"
                )
            }))
            print_error_or_warnings(
                text=(
                    "Provide a question with -q, URL with -url, image with -img/--image-url, "
                    "PDF with -pdf/--pdf-url, or a dedicated pattern with -up"
                )
            )
            sys.exit(1)

        # Validate OpenRouter commands
        if args.openrouter is not None:
            if not args.openrouter:  # Empty sequence evaluates to False in boolean context
                logger.error(json.dumps({
                    "log_message": "User provided --openrouter without any command"
                }))
                print_error_or_warnings(
                    text="--openrouter requires a command (check-credits, list-models)"
                )
                sys.exit(1)

            valid_commands = ['check-credits', 'list-models']
            command = args.openrouter[0]
            if command not in valid_commands:
                logger.error(json.dumps({
                    "log_message": f"User provided invalid OpenRouter command: {command}"
                }))
                print_error_or_warnings(
                    text=f"Invalid OpenRouter command '{command}'. Valid commands: {', '.join(valid_commands)}"
                )
                sys.exit(1)

        if args.plain_md and args.format != "md":
            logger.warning(json.dumps({
                "log_message": "User used --plain-md without -f md"
            }))
            print_error_or_warnings(
                text="--plain-md can only be used with -f md. The parameter --plain-md will be ignored.",
                warning_only=True
            )
