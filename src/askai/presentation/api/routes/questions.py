"""
Question processing endpoints for the AskAI API.
"""
import os
import sys
from flask import request, current_app
from flask_restx import Namespace, Resource, fields

# Add project paths for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

# pylint: disable=wrong-import-position
from askai.core.questions.processor import QuestionProcessor
from askai.utils import load_config, setup_logger

# Create namespace
questions_ns = Namespace('questions', description='Question processing operations')

# Request models
question_request = questions_ns.model('QuestionRequest', {
    'question': fields.String(required=True, description='The question to ask', example='What is machine learning?'),
    'file_input': fields.String(description='Path to input file (optional)'),
    'url': fields.String(description='URL to process (optional)'),
    'response_format': fields.String(description='Response format', enum=['rawtext', 'json', 'md'], default='rawtext'),
    'model': fields.String(description='AI model to use (optional)'),
    'pattern_id': fields.String(description='Pattern ID to use (optional)'),
    'persistent_chat': fields.String(
        description='Chat ID for persistent conversation (optional, use "new" for new chat)'
    )
})

# Response models
question_response = questions_ns.model('QuestionResponse', {
    'content': fields.String(required=True, description='The AI response content'),
    'created_files': fields.List(fields.String, description='List of created files'),
    'chat_id': fields.String(description='Chat session ID'),
    'model_used': fields.String(description='AI model that was used'),
    'token_usage': fields.Raw(description='Token usage information')
})

error_response = questions_ns.model('ErrorResponse', {
    'error': fields.String(required=True, description='Error message'),
    'details': fields.String(description='Detailed error information'),
    'code': fields.String(description='Error code')
})


@questions_ns.route('/ask')
class AskQuestion(Resource):
    """Process a question using AskAI."""

    @questions_ns.doc('ask_question')
    @questions_ns.expect(question_request)
    @questions_ns.marshal_with(question_response)
    def post(self):
        """Process a question and return AI response.

        Accepts a question and optional parameters, processes it through AskAI,
        and returns the AI response.
        """
        try:
            data = request.get_json()

            # Validate required fields
            if not data or not data.get('question'):
                return {'error': 'Question is required', 'code': 'MISSING_QUESTION'}, 400

            # Load configuration
            config = load_config()

            if not config:
                return {'error': 'Failed to load configuration', 'code': 'CONFIG_ERROR'}, 500

            # Initialize logger
            logger = setup_logger(config)

            # Create question processor
            base_path = os.path.join(project_root)
            processor = QuestionProcessor(config, logger, base_path)

            # Create mock args object for compatibility
            class MockArgs:  # pylint: disable=missing-class-docstring,too-few-public-methods,too-many-instance-attributes
                def __init__(self, data):
                    self.question = data.get('question')
                    self.file_input = data.get('file_input')
                    self.url = data.get('url')
                    self.format = data.get('response_format', 'rawtext')  # Use 'format' not 'response_format'
                    self.response_format = data.get('response_format', 'rawtext')  # Keep both for compatibility
                    self.model = data.get('model')
                    self.pattern_id = data.get('pattern_id')
                    self.output_file = None
                    self.output = None  # Output file path
                    self.plain_md = False  # Plain markdown flag
                    self.save = False  # Save to file flag
                    self.verbose = False
                    self.debug = False
                    # Image and PDF attributes
                    self.image = None
                    self.pdf = None
                    self.image_url = None
                    self.pdf_url = None
                    # Chat-related attributes
                    self.persistent_chat = data.get('persistent_chat')  # None, 'new', or chat_id
                    self.list_chats = False
                    self.view_chat = None
                    self.manage_chats = False
                    # Pattern-related attributes
                    self.pattern = None
                    self.use_pattern = None
                    self.list_patterns = False
                    self.view_pattern = None
                    self.pattern_input = None
                    # Other CLI attributes that might be needed
                    self.tui = False
                    self.enable_url_search = data.get('url') is not None
                    self.openrouter = None
                    self.config = None

            args = MockArgs(data)

            # Process the question
            response = processor.process_question(args)

            # Format response
            result = {
                'content': response.content,
                'created_files': response.created_files or [],
                'chat_id': response.chat_id,
                'model_used': getattr(response, 'model_used', None),
                'token_usage': getattr(response, 'token_usage', None)
            }

            return result, 200

        except ValueError as e:
            current_app.logger.error(f"Validation error: {e}")
            return {'error': str(e), 'code': 'VALIDATION_ERROR'}, 400
        except Exception as e:
            current_app.logger.error(f"Error processing question: {e}")
            return {'error': 'Internal server error', 'details': str(e), 'code': 'INTERNAL_ERROR'}, 500


@questions_ns.route('/validate')
class ValidateQuestion(Resource):
    """Validate a question request."""

    @questions_ns.doc('validate_question')
    @questions_ns.expect(question_request)
    def post(self):
        """Validate a question request without processing it.

        Checks if the request is valid and returns validation results.
        """
        try:
            data = request.get_json()

            errors = []
            warnings = []

            # Validate question
            if not data or not data.get('question'):
                errors.append("Question is required")
            elif not data.get('question').strip():
                errors.append("Question cannot be empty")

            # Validate file input if provided
            if data.get('file_input'):
                file_path = data.get('file_input')
                if not os.path.exists(file_path):
                    warnings.append(f"File not found: {file_path}")

            # Validate response format
            valid_formats = ['rawtext', 'json', 'md']
            response_format = data.get('response_format', 'rawtext')
            if response_format not in valid_formats:
                errors.append(f"Invalid response format. Must be one of: {', '.join(valid_formats)}")

            # Return validation results
            is_valid = not errors

            return {
                'valid': is_valid,
                'errors': errors,
                'warnings': warnings
            }, 200

        except Exception as e:
            current_app.logger.error(f"Error validating question: {e}")
            return {'error': 'Validation failed', 'details': str(e)}, 500
