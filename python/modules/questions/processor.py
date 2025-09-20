"""
Question processor for the AskAI CLI.
Handles standalone question processing separate from patterns.
"""

import json
import os
import sys
from typing import Tuple

from modules.ai import AIService
from modules.chat import ChatManager
from modules.messaging import MessageBuilder
from modules.patterns import PatternManager
from infrastructure.output.output_coordinator import OutputCoordinator
from .models import QuestionContext, QuestionResponse


class QuestionProcessor:
    """Processes standalone questions without patterns."""

    def __init__(self, config: dict, logger, base_path: str):
        """Initialize the question processor.

        Args:
            config: Configuration dictionary
            logger: Logger instance
            base_path: Base path for the application
        """
        self.config = config
        self.logger = logger
        self.base_path = base_path

        # Initialize required components
        self.pattern_manager = PatternManager(base_path, config)
        self.message_builder = MessageBuilder(self.pattern_manager, logger)
        self.chat_manager = ChatManager(config, logger)
        self.ai_service = AIService(logger)
        self.output_coordinator = OutputCoordinator()

    def process_question(self, args) -> QuestionResponse:
        """Process a standalone question.

        Args:
            args: CLI arguments namespace

        Returns:
            QuestionResponse: The processed response
        """
        # Create question context from args
        context = self._create_question_context(args)

        # Build messages for the question
        messages, _ = self.message_builder.build_messages(
            question=context.question,
            file_input=context.file_input,
            pattern_id=None,  # No pattern in question mode
            pattern_input=None,
            response_format=context.response_format,
            url=context.url,
            image=context.image,
            pdf=context.pdf,
            image_url=context.image_url,
            pdf_url=context.pdf_url
        )

        # Check if message building was cancelled
        if messages is None:
            sys.exit(0)

        # Handle persistent chat setup and context loading
        chat_id, messages = self.chat_manager.handle_persistent_chat(args, messages)

        # Debug log the messages
        self.logger.debug(json.dumps({
            "log_message": "Question messages content",
            "messages": messages
        }))

        # Determine if web search should be enabled for URL analysis
        enable_url_search = context.url is not None

        # Get AI response
        response = self.ai_service.get_ai_response(
            messages=messages,
            model_name=context.model,
            pattern_id=None,  # No pattern in question mode
            debug=getattr(args, 'debug', False),
            pattern_manager=None,  # No pattern manager needed
            enable_url_search=enable_url_search
        )

        # Store chat history if using persistent chat
        if chat_id:
            self.chat_manager.store_chat_conversation(
                chat_id, messages, response, None, None  # No pattern data in question mode
            )

        # Process the output
        formatted_output, created_files = self._process_output(
            response, context, args
        )

        return QuestionResponse(
            content=formatted_output,
            created_files=created_files,
            chat_id=chat_id
        )

    def _create_question_context(self, args) -> QuestionContext:
        """Create question context from CLI arguments.

        Args:
            args: CLI arguments namespace

        Returns:
            QuestionContext: Question processing context
        """
        return QuestionContext(
            question=getattr(args, 'question', None),
            file_input=getattr(args, 'file_input', None),
            url=getattr(args, 'url', None),
            image=getattr(args, 'image', None) if hasattr(args, 'image') else None,
            pdf=getattr(args, 'pdf', None) if hasattr(args, 'pdf') else None,
            image_url=getattr(args, 'image_url', None) if hasattr(args, 'image_url') else None,
            pdf_url=getattr(args, 'pdf_url', None) if hasattr(args, 'pdf_url') else None,
            response_format=getattr(args, 'format', 'rawtext'),
            model=getattr(args, 'model', None)
        )

    def _process_output(self, response, context: QuestionContext, args) -> Tuple[str, list]:
        """Process the AI response output.

        Args:
            response: AI response
            context: Question context
            args: CLI arguments

        Returns:
            Tuple[str, list]: Formatted output and list of created files
        """
        # Initialize output configuration
        output_config = {
            'format': context.response_format
        }

        # Add plain_md flag if it's set and we're using markdown format
        if hasattr(args, 'plain_md') and args.plain_md and context.response_format == 'md':
            output_config['plain_md'] = 'true'

        # Handle output file if specified
        console_output = True
        file_output = getattr(args, 'save', False) if hasattr(args, 'save') else False

        # Check if user specified an output file via args.output
        has_output_arg = hasattr(args, 'output') and args.output is not None

        if has_output_arg:
            file_output = True
            output_path = args.output

            # Set format-specific filename based on user's format choice
            if context.response_format == 'json':
                output_config['json_filename'] = os.path.basename(output_path)
            elif context.response_format == 'md':
                output_config['markdown_filename'] = os.path.basename(output_path)
            else:
                # Default to markdown for text output
                output_config['markdown_filename'] = os.path.basename(output_path)

            # Set output directory
            output_dir = os.path.dirname(os.path.abspath(output_path))
            self.output_coordinator.output_dir = output_dir

        # Process the output
        formatted_output, created_files = self.output_coordinator.process_output(
            response=response,
            output_config=output_config,
            console_output=console_output,
            file_output=file_output
        )

        return formatted_output, created_files
