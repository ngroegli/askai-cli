"""
DEPRECATED: This file is a concatenation of route modules.
Use the individual modules in the routes/ directory instead:
- routes/health.py
- routes/questions.py
- routes/patterns.py
- routes/openrouter.py
- routes/config.py

This file should be deleted but is kept temporarily for reference.
"""
# pylint: skip-file

"""
Health check and status endpoints for the AskAI API.
"""
from flask import current_app
from flask_restx import Namespace, Resource, fields

# Create namespace
health_ns = Namespace('health', description='Health check and status operations')

# Response models
health_response = health_ns.model('HealthResponse', {
    'status': fields.String(required=True, description='Service status', example='healthy'),
    'version': fields.String(required=True, description='API version', example='1.0.0'),
    'timestamp': fields.DateTime(required=True, description='Current timestamp'),
    'uptime': fields.Float(description='Service uptime in seconds'),
})

status_response = health_ns.model('StatusResponse', {
    'api': fields.String(required=True, description='API status', example='running'),
    'database': fields.String(description='Database status', example='connected'),
    'dependencies': fields.Raw(description='Dependency status'),
})


@health_ns.route('/health')
class Health(Resource):
    """Health check endpoint."""

    @health_ns.doc('health_check')
    @health_ns.marshal_with(health_response)
    def get(self):
        """Get service health status.

        Returns basic health information about the service.
        """
        import datetime
        import time

        # Get app start time (simplified for now)
        start_time = getattr(current_app, 'start_time', time.time())
        uptime = time.time() - start_time

        return {
            'status': 'healthy',
            'version': '1.0.0',
            'timestamp': datetime.datetime.utcnow(),
            'uptime': uptime
        }


@health_ns.route('/status')
class Status(Resource):
    """Detailed status endpoint."""

    @health_ns.doc('service_status')
    @health_ns.marshal_with(status_response)
    def get(self):
        """Get detailed service status.

        Returns detailed status information including dependencies.
        """
        try:
            # Check core components (simplified for now)
            dependencies = {
                'patterns': 'available',
                'ai_service': 'available',
                'config': 'loaded'
            }

            return {
                'api': 'running',
                'database': 'not_applicable',
                'dependencies': dependencies
            }
        except Exception as e:
            current_app.logger.error(f"Status check failed: {e}")
            return {
                'api': 'degraded',
                'database': 'not_applicable',
                'dependencies': {'error': str(e)}
            }, 503


@health_ns.route('/ready')
class Readiness(Resource):
    """Readiness probe endpoint."""

    @health_ns.doc('readiness_check')
    def get(self):
        """Check if service is ready to serve requests.

        Returns 200 if ready, 503 if not ready.
        """
        try:
            # Perform readiness checks
            # For now, just return ready
            return {'ready': True}, 200
        except Exception as e:
            current_app.logger.error(f"Readiness check failed: {e}")
            return {'ready': False, 'error': str(e)}, 503


@health_ns.route('/live')
class Liveness(Resource):
    """Liveness probe endpoint."""

    @health_ns.doc('liveness_check')
    def get(self):
        """Check if service is alive.

        Returns 200 if alive, 503 if dead.
        """
        return {'alive': True}, 200


"""
Question processing endpoints for the AskAI API.
"""
# pylint: disable=wrong-import-position
import os
import sys
from flask import request, current_app
from flask_restx import Namespace, Resource, fields

# Add project paths for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

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
    'persistent_chat': fields.String(description='Chat ID for persistent conversation (optional, use "new" for new chat)')
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
            class MockArgs:
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
            is_valid = len(errors) == 0

            return {
                'valid': is_valid,
                'errors': errors,
                'warnings': warnings
            }, 200

        except Exception as e:
            current_app.logger.error(f"Error validating question: {e}")
            return {'error': 'Validation failed', 'details': str(e)}, 500


"""
Configuration management endpoints for the AskAI API.
"""
# pylint: disable=wrong-import-position
import os
import sys
from flask import current_app
from flask_restx import Namespace, Resource, fields

# Add project paths for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

# pylint: disable=wrong-import-position
from askai.utils.config import load_config, CONFIG_PATH, ASKAI_DIR

# Create namespace
config_ns = Namespace('config', description='Configuration management operations')

# Response models
config_info = config_ns.model('ConfigInfo', {
    'api_key': fields.String(description='OpenRouter API key (masked)'),
    'base_url': fields.String(description='OpenRouter base URL'),
    'default_model': fields.String(description='Default AI model'),
    'default_vision_model': fields.String(description='Default vision model'),
    'default_pdf_model': fields.String(description='Default PDF model'),
    'log_path': fields.String(description='Log file path'),
    'private_patterns_path': fields.String(description='Private patterns directory'),
    'chat': fields.Raw(description='Chat configuration'),
    'web_search': fields.Raw(description='Web search configuration'),
    'logging': fields.Raw(description='Logging configuration'),
    'patterns': fields.Raw(description='Pattern configuration')
})

config_status = config_ns.model('ConfigStatus', {
    'configured': fields.Boolean(required=True, description='Configuration status'),
    'config_file_exists': fields.Boolean(description='Config file existence'),
    'config_path': fields.String(description='Configuration file path'),
    'askai_dir_exists': fields.Boolean(description='AskAI directory existence'),
    'askai_dir_path': fields.String(description='AskAI directory path'),
    'issues': fields.List(fields.String, description='Configuration issues'),
    'suggestions': fields.List(fields.String, description='Configuration suggestions')
})

config_validation = config_ns.model('ConfigValidation', {
    'valid': fields.Boolean(required=True, description='Validation status'),
    'issues': fields.List(fields.String, description='Validation issues'),
    'warnings': fields.List(fields.String, description='Validation warnings'),
    'suggestions': fields.List(fields.String, description='Improvement suggestions')
})

# Note: Configuration updates are not supported via API for security reasons
# Use the CLI setup wizard or edit configuration files directly


def mask_api_key(api_key):
    """Mask API key for safe display."""
    if not api_key:
        return None
    if len(api_key) <= 8:
        return '*' * len(api_key)
    return api_key[:4] + '*' * (len(api_key) - 8) + api_key[-4:]


@config_ns.route('/')
class Configuration(Resource):
    """Get current configuration."""

    @config_ns.doc('get_config')
    @config_ns.marshal_with(config_info)
    def get(self):
        """Get current AskAI configuration.

        Returns the current configuration with sensitive information masked.
        """
        try:
            # Load configuration
            config = load_config()

            if not config:
                return {'error': 'Failed to load configuration'}, 500

            # Mask sensitive information
            safe_config = config.copy()
            if 'api_key' in safe_config:
                safe_config['api_key'] = mask_api_key(safe_config['api_key'])

            return safe_config

        except Exception as e:
            current_app.logger.error(f"Error getting configuration: {e}")
            return {'error': 'Failed to get configuration', 'details': str(e)}, 500


@config_ns.route('/status')
class ConfigurationStatus(Resource):
    """Get configuration status."""

    @config_ns.doc('get_config_status')
    @config_ns.marshal_with(config_status)
    def get(self):
        """Get AskAI configuration status.

        Returns detailed status information about the configuration setup.
        """
        try:
            issues = []
            suggestions = []

            # Check if AskAI directory exists
            askai_dir_exists = os.path.exists(ASKAI_DIR)
            if not askai_dir_exists:
                issues.append(f"AskAI directory does not exist: {ASKAI_DIR}")
                suggestions.append("Run setup to create AskAI directory structure")

            # Check if config file exists
            config_file_exists = os.path.exists(CONFIG_PATH)
            if not config_file_exists:
                issues.append(f"Configuration file does not exist: {CONFIG_PATH}")
                suggestions.append("Run setup wizard to create configuration file")

            # Try to load configuration
            configured = True
            config = None
            try:
                config = load_config()
                if not config:
                    configured = False
                    issues.append("Configuration file is empty or invalid")
            except Exception as e:
                configured = False
                issues.append(f"Failed to load configuration: {e}")

            # Validate configuration if loaded
            if config:
                if not config.get('api_key'):
                    issues.append("OpenRouter API key not configured")
                    suggestions.append("Set your OpenRouter API key in configuration")

                if not config.get('base_url'):
                    issues.append("OpenRouter base URL not configured")
                    suggestions.append("Configure OpenRouter base URL")

                if not config.get('default_model'):
                    issues.append("Default model not configured")
                    suggestions.append("Set a default AI model")

            return {
                'configured': configured and len(issues) == 0,
                'config_file_exists': config_file_exists,
                'config_path': CONFIG_PATH,
                'askai_dir_exists': askai_dir_exists,
                'askai_dir_path': ASKAI_DIR,
                'issues': issues,
                'suggestions': suggestions
            }

        except Exception as e:
            current_app.logger.error(f"Error getting configuration status: {e}")
            return {'error': 'Failed to get configuration status', 'details': str(e)}, 500


@config_ns.route('/validate')
class ConfigurationValidation(Resource):
    """Validate configuration."""

    @config_ns.doc('validate_config')
    @config_ns.marshal_with(config_validation)
    def get(self):
        """Validate current AskAI configuration.

        Performs comprehensive validation of the current configuration.
        """
        try:
            issues = []
            warnings = []
            suggestions = []

            # Load configuration
            config = load_config()

            if not config:
                issues.append("Configuration could not be loaded")
                return {
                    'valid': False,
                    'issues': issues,
                    'warnings': warnings,
                    'suggestions': ['Run setup to create valid configuration']
                }

            # Validate required fields
            if not config.get('api_key'):
                issues.append("API key is missing - api_key must be set")

            if not config.get('base_url'):
                issues.append("Base URL is missing")

            if not config.get('default_model'):
                warnings.append("Default model not configured - may cause issues with some requests")

            # Validate API key format (basic check)
            api_key = config.get('api_key', '')
            if api_key and (len(api_key) < 10 or not api_key.startswith('sk-')):
                warnings.append("API key format may be invalid (should start with 'sk-' and be longer)")
                suggestions.append("Verify your OpenRouter API key format")

            # Validate base URL
            base_url = config.get('base_url', '')
            if base_url and not base_url.startswith('http'):
                issues.append("Base URL should start with 'http' or 'https'")

            # Check optional configurations
            patterns_config = config.get('patterns', {})
            if not patterns_config.get('private_patterns_path'):
                suggestions.append("Consider setting a private patterns path for custom patterns")

            if not config.get('chat', {}).get('storage_path'):
                warnings.append("Chat storage path not configured - chat functionality may be limited")

            # Check logging configuration
            log_level = config.get('log_level')
            if log_level and log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
                warnings.append("Invalid logging level - should be DEBUG, INFO, WARNING, or ERROR")

            return {
                'valid': len(issues) == 0,
                'issues': issues,
                'warnings': warnings,
                'suggestions': suggestions
            }

        except Exception as e:
            current_app.logger.error(f"Error validating configuration: {e}")
            return {
                'valid': False,
                'issues': [f'Configuration validation failed: {e}'],
                'warnings': [],
                'suggestions': ['Check server logs for details']
            }, 500
"""
Pattern management endpoints for the AskAI API.
"""
import json
import os
import sys
import tempfile
import traceback
from flask import current_app, request
from flask_restx import Namespace, Resource, fields
from werkzeug.datastructures import FileStorage

# Add project paths for imports
project_root = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "..", ".."
))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

# pylint: disable=wrong-import-position
from askai.core.ai import AIService
from askai.core.messaging import MessageBuilder
from askai.core.patterns import PatternManager
from askai.utils import load_config, get_logger

# Create namespace
patterns_ns = Namespace('patterns', description='Pattern management operations')


def _save_uploaded_file(uploaded_file: FileStorage, prefix: str = "uploaded") -> str:
    """Save an uploaded file to a temporary location and return the path.

    Args:
        uploaded_file: Flask FileStorage object from file upload
        prefix: Prefix for the temporary filename

    Returns:
        str: Path to the saved temporary file

    Raises:
        ValueError: If file is invalid or cannot be saved
    """
    if not uploaded_file or not uploaded_file.filename:
        raise ValueError("Invalid file upload")

    # Get file extension for proper handling
    filename = uploaded_file.filename
    _, ext = os.path.splitext(filename)

    # Create temporary file with proper extension
    fd, temp_path = tempfile.mkstemp(prefix=f"{prefix}_", suffix=ext)

    try:
        # Save uploaded file to temporary location
        with os.fdopen(fd, 'wb') as tmp_file:
            uploaded_file.save(tmp_file)

        # Use shared application logger
        logger = get_logger()
        logger.info("Saved uploaded file '%s' (%s bytes) to %s", filename, uploaded_file.content_length, temp_path)
        return temp_path

    except Exception as e:
        # Clean up on error
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        raise ValueError(f"Failed to save uploaded file: {e}") from e
def _cleanup_temp_file(file_path: str) -> None:
    """Clean up a temporary file.

    Args:
        file_path: Path to the file to delete
    """
    try:
        if file_path and os.path.exists(file_path):
            os.unlink(file_path)
            # Use shared application logger
            logger = get_logger()
            logger.debug("Cleaned up temporary file: %s", file_path)
    except OSError as e:
        logger = get_logger()
        logger.warning("Failed to cleanup temporary file %s: %s", file_path, e)
def _process_file_inputs(pattern_inputs: list, form_data: dict, files: dict) -> tuple[dict, list]:
    """Process file inputs by mapping uploaded files to temporary paths.

    Args:
        pattern_inputs: List of pattern input definitions
        form_data: Form data from request
        files: Files from request

    Returns:
        tuple: A tuple containing (processed_inputs_dict, temp_files_list)
            - processed_inputs_dict: Processed inputs with file paths mapped to temporary files
            - temp_files_list: List of temporary file paths created

    Raises:
        ValueError: If required files are missing or invalid
    """
    processed = form_data.copy()
    temp_files_created = []

    try:
        for input_obj in pattern_inputs:
            if not hasattr(input_obj, 'input_type'):
                continue

            input_name = input_obj.name
            input_type = (
                input_obj.input_type.value
                if hasattr(input_obj.input_type, 'value')
                else str(input_obj.input_type)
            )

            # Handle different file input types
            if input_type in ['file', 'image_file', 'pdf_file']:
                if input_name in files:
                    uploaded_file = files[input_name]
                    if uploaded_file and uploaded_file.filename:
                        # Save file to temporary location
                        temp_path = _save_uploaded_file(uploaded_file, f"{input_type}_{input_name}")
                        temp_files_created.append(temp_path)
                        processed[input_name] = temp_path
                        current_app.logger.info(
                            f"Mapped {input_type} input '{input_name}' to temporary file: {temp_path}"
                        )
                elif input_obj.required and input_name not in processed:
                    raise ValueError(f"Required file input '{input_name}' not provided")

        return processed, temp_files_created

    except Exception as e:
        # Clean up any files we created before the error
        for temp_file in temp_files_created:
            _cleanup_temp_file(temp_file)
        raise e

# Response models
pattern_info = patterns_ns.model('PatternInfo', {
    'id': fields.String(required=True, description='Pattern ID'),
    'name': fields.String(required=True, description='Pattern name'),
    'description': fields.String(description='Pattern description'),
    'category': fields.String(description='Pattern category'),
    'inputs': fields.List(fields.Raw, description='Pattern input requirements'),
    'outputs': fields.List(fields.Raw, description='Pattern output specifications')
})

patterns_list = patterns_ns.model('PatternsList', {
    'patterns': fields.List(fields.Nested(pattern_info), description='List of available patterns'),
    'count': fields.Integer(description='Total number of patterns')
})

# Input models for pattern execution
pattern_input_values = patterns_ns.model('PatternInputValues', {
    # This is a dynamic model - any field can be added
    '*': fields.Raw(description='Pattern input values as key-value pairs')
})

pattern_execution_request = patterns_ns.model('PatternExecutionRequest', {
    'pattern_id': fields.String(required=True, description='ID of the pattern to execute'),
    'inputs': fields.Nested(pattern_input_values, required=True, description='Input values for the pattern'),
    'debug': fields.Boolean(default=False, description='Enable debug mode for execution'),
    'model_name': fields.String(description='Override model name for this execution')
})

# File upload models
pattern_file_execution_request = patterns_ns.model('PatternFileExecutionRequest', {
    'pattern_id': fields.String(required=True, description='ID of the pattern to execute'),
    'inputs': fields.Raw(required=True, description='Non-file input values as JSON object'),
    'debug': fields.Boolean(default=False, description='Enable debug mode for execution'),
    'model_name': fields.String(description='Override model name for this execution')
})

# Response models for pattern execution
pattern_execution_response = patterns_ns.model('PatternExecutionResponse', {
    'success': fields.Boolean(required=True, description='Whether execution was successful'),
    'pattern_id': fields.String(required=True, description='ID of the executed pattern'),
    'response': fields.Raw(description='AI response content'),
    'formatted_output': fields.String(description='Formatted output text'),
    'created_files': fields.List(fields.String, description='List of files created during execution'),
    'error': fields.String(description='Error message if execution failed'),
    'details': fields.String(description='Additional error details')
})

# Template models
pattern_template = patterns_ns.model('PatternTemplate', {
    'pattern_id': fields.String(required=True, description='Pattern ID'),
    'template': fields.Raw(required=True, description='JSON template with default/example values for pattern inputs')
})


@patterns_ns.route('/')
class PatternsList(Resource):
    """List available patterns."""

    @patterns_ns.doc('list_patterns')
    @patterns_ns.marshal_with(patterns_list)
    def get(self):
        """Get list of all available patterns.

        Returns a list of all patterns available in the system.
        """
        try:
            # Load configuration
            config = load_config()

            if not config:
                return {'error': 'Failed to load configuration'}, 500

            # Initialize pattern manager
            pattern_manager = PatternManager(project_root, config)

            # Get all patterns
            available_patterns = pattern_manager.list_patterns()
            patterns = []

            for pattern_data in available_patterns:
                try:
                    pattern_id = pattern_data.get('pattern_id', '')
                    pattern_content = pattern_manager.get_pattern_content(pattern_id)

                    if pattern_content:
                        # Convert PatternInput objects to dictionaries for JSON serialization
                        inputs = []
                        for input_obj in pattern_content.get('inputs', []):
                            if hasattr(input_obj, 'name'):  # It's a PatternInput object
                                input_type_value = (
                                    input_obj.input_type.value
                                    if hasattr(input_obj.input_type, 'value')
                                    else str(input_obj.input_type)
                                )
                                input_dict = {
                                    'name': input_obj.name,
                                    'description': input_obj.description,
                                    'type': input_type_value,
                                    'required': input_obj.required,
                                    'default': input_obj.default,
                                    'options': input_obj.options,
                                    'min_value': input_obj.min_value,
                                    'max_value': input_obj.max_value,
                                    'group': input_obj.group
                                }
                                inputs.append(input_dict)
                            else:  # It's already a dictionary
                                inputs.append(input_obj)

                        # Convert PatternOutput objects to dictionaries for JSON serialization
                        outputs = []
                        for output_obj in pattern_content.get('outputs', []):
                            if hasattr(output_obj, 'name'):  # It's a PatternOutput object
                                output_type_value = (
                                    output_obj.output_type.value
                                    if hasattr(output_obj.output_type, 'value')
                                    else str(output_obj.output_type)
                                )
                                action_value = (
                                    output_obj.action.value
                                    if hasattr(output_obj.action, 'value')
                                    else str(output_obj.action)
                                )
                                output_dict = {
                                    'name': output_obj.name,
                                    'description': output_obj.description,
                                    'type': output_type_value,
                                    'required': output_obj.required,
                                    'example': output_obj.example,
                                    'action': action_value,
                                    'write_to_file': output_obj.write_to_file,
                                    'group': output_obj.group
                                }
                                outputs.append(output_dict)
                            else:  # It's already a dictionary
                                outputs.append(output_obj)

                        patterns.append({
                            'id': pattern_id,
                            'name': pattern_data.get('name', pattern_id),
                            'description': pattern_data.get('description', ''),
                            'category': pattern_data.get('category', 'general'),
                            'inputs': inputs,
                            'outputs': outputs
                        })
                except Exception as e:
                    current_app.logger.warning(f"Failed to load pattern {pattern_data}: {e}")
                    continue

            return {
                'patterns': patterns,
                'count': len(patterns)
            }

        except Exception as e:
            current_app.logger.error(f"Error listing patterns: {e}")
            return {'error': 'Failed to list patterns', 'details': str(e)}, 500


@patterns_ns.route('/<string:pattern_id>')
class PatternDetail(Resource):
    """Get pattern details."""

    @patterns_ns.doc('get_pattern')
    @patterns_ns.marshal_with(pattern_info)
    def get(self, pattern_id):
        """Get detailed information about a specific pattern.

        Args:
            pattern_id: The ID of the pattern to retrieve
        """
        try:
            # Load configuration
            config = load_config()

            if not config:
                return {'error': 'Failed to load configuration'}, 500

            # Initialize pattern manager
            pattern_manager = PatternManager(project_root, config)

            # Load specific pattern
            pattern_content = pattern_manager.get_pattern_content(pattern_id)

            if not pattern_content:
                return {'error': f'Pattern not found: {pattern_id}'}, 404

            # Convert PatternInput objects to dictionaries for JSON serialization
            inputs = []
            for input_obj in pattern_content.get('inputs', []):
                if hasattr(input_obj, 'name'):  # It's a PatternInput object
                    input_type_value = (
                        input_obj.input_type.value
                        if hasattr(input_obj.input_type, 'value')
                        else str(input_obj.input_type)
                    )
                    input_dict = {
                        'name': input_obj.name,
                        'description': input_obj.description,
                        'type': input_type_value,
                        'required': input_obj.required,
                        'default': input_obj.default,
                        'options': input_obj.options,
                        'min_value': input_obj.min_value,
                        'max_value': input_obj.max_value,
                        'group': input_obj.group
                    }
                    inputs.append(input_dict)
                else:  # It's already a dictionary
                    inputs.append(input_obj)

            # Convert PatternOutput objects to dictionaries for JSON serialization
            outputs = []
            for output_obj in pattern_content.get('outputs', []):
                if hasattr(output_obj, 'name'):  # It's a PatternOutput object
                    output_type_value = (
                        output_obj.output_type.value
                        if hasattr(output_obj.output_type, 'value')
                        else str(output_obj.output_type)
                    )
                    action_value = (
                        output_obj.action.value
                        if hasattr(output_obj.action, 'value')
                        else str(output_obj.action)
                    )
                    output_dict = {
                        'name': output_obj.name,
                        'description': output_obj.description,
                        'type': output_type_value,
                        'required': output_obj.required,
                        'example': output_obj.example,
                        'action': action_value,
                        'write_to_file': output_obj.write_to_file,
                        'group': output_obj.group
                    }
                    outputs.append(output_dict)
                else:  # It's already a dictionary
                    outputs.append(output_obj)

            return {
                'id': pattern_id,
                'name': pattern_content.get('name', pattern_id),
                'description': pattern_content.get('description', ''),
                'category': pattern_content.get('category', 'general'),
                'inputs': inputs,
                'outputs': outputs
            }

        except Exception as e:
            current_app.logger.error(f"Error getting pattern {pattern_id}: {e}")
            return {'error': 'Failed to get pattern', 'details': str(e)}, 500


@patterns_ns.route('/categories')
class PatternCategories(Resource):
    """Get pattern categories."""

    @patterns_ns.doc('get_categories')
    def get(self):
        """Get list of pattern categories.

        Returns all available pattern categories.
        """
        try:
            # Load configuration
            config = load_config()

            if not config:
                return {'error': 'Failed to load configuration'}, 500

            # Initialize pattern manager
            pattern_manager = PatternManager(project_root, config)

            # Get all patterns and extract categories
            available_patterns = pattern_manager.list_patterns()
            categories = set()

            for pattern_data in available_patterns:
                try:
                    pattern_id = pattern_data.get('pattern_id', '')
                    pattern_content = pattern_manager.get_pattern_content(pattern_id)

                    if pattern_content:
                        category = pattern_content.get('category', 'general')
                        categories.add(category)
                except Exception:
                    continue

            return {
                'categories': sorted(list(categories)),
                'count': len(categories)
            }

        except Exception as e:
            current_app.logger.error(f"Error getting categories: {e}")
            return {'error': 'Failed to get categories', 'details': str(e)}, 500


@patterns_ns.route('/execute')
class PatternExecution(Resource):
    """Execute a pattern with text inputs only (no files)."""

    @patterns_ns.doc('execute_pattern')
    @patterns_ns.expect(pattern_execution_request, validate=True)
    @patterns_ns.marshal_with(pattern_execution_response)
    def post(self):
        """Execute a pattern with provided input values (text/numbers only).

        This endpoint handles patterns that don't require file inputs.
        For patterns that need files, use the /patterns/execute/files endpoint.
        """
        try:
            # Get JSON data only
            data = request.get_json()
            if not data:
                return {'error': 'Request body must be valid JSON', 'success': False}, 400

            pattern_id = data.get('pattern_id')
            inputs = data.get('inputs', {})
            debug_mode = data.get('debug', False)
            model_name = data.get('model_name')

            if not pattern_id:
                return {'error': 'pattern_id is required', 'success': False}, 400

            # Load configuration
            config = load_config()
            if not config:
                return {'error': 'Failed to load configuration', 'success': False}, 500

            # Initialize pattern manager
            pattern_manager = PatternManager(project_root, config)

            # Validate pattern exists
            pattern_content = pattern_manager.get_pattern_content(pattern_id)
            if not pattern_content:
                return {
                    'error': f'Pattern not found: {pattern_id}',
                    'success': False,
                    'pattern_id': pattern_id
                }, 404

            # Check if pattern requires files
            pattern_inputs = pattern_content.get('inputs', [])
            file_inputs = []
            for input_obj in pattern_inputs:
                if hasattr(input_obj, 'input_type'):
                    input_type = (
                        input_obj.input_type.value
                        if hasattr(input_obj.input_type, 'value')
                        else str(input_obj.input_type)
                    )
                    if input_type in ['file', 'image_file', 'pdf_file']:
                        file_inputs.append(input_obj.name)

            if file_inputs:
                return {
                    'error': (f'Pattern requires file inputs: {file_inputs}. '
                             'Use /patterns/execute/files endpoint instead.'),
                    'success': False,
                    'pattern_id': pattern_id,
                    'required_file_inputs': file_inputs
                }, 400

            # Process pattern inputs (non-interactive mode)
            validated_inputs = pattern_manager.process_pattern_inputs(
                pattern_id=pattern_id,
                input_values=inputs,
                interactive=False
            )

            if validated_inputs is None:
                return {
                    'error': 'Failed to process pattern inputs - validation failed',
                    'success': False,
                    'pattern_id': pattern_id
                }, 400

            # Execute pattern
            result = self._execute_pattern(
                pattern_manager, pattern_id, validated_inputs, debug_mode, model_name
            )
            return result

        except Exception as e:
            current_app.logger.error(f"Error executing pattern: {e}")
            current_app.logger.debug(f"Pattern execution error details: {traceback.format_exc()}")

            return {
                'error': 'Failed to execute pattern',
                'details': str(e),
                'success': False,
                'pattern_id': data.get('pattern_id', 'unknown') if 'data' in locals() else 'unknown'
            }, 500

    def _execute_pattern(self, pattern_manager, pattern_id, inputs, debug_mode, model_name):
        """Common pattern execution logic."""
        logger = get_logger()
        logger.info("Executing pattern '%s'", pattern_id)

        message_builder = MessageBuilder(pattern_manager, logger)        # Build messages for the pattern
        messages, resolved_pattern_id = message_builder.build_messages(
            question=None,
            file_input=None,
            pattern_id=pattern_id,
            pattern_input=inputs,
            response_format="rawtext",
            url=None,
            image=None,
            pdf=None,
            image_url=None,
            pdf_url=None
        )

        if not messages:
            return {
                'error': 'Failed to build messages for pattern execution',
                'success': False,
                'pattern_id': pattern_id
            }, 500

        logger.info("Built %d messages for pattern '%s'", len(messages), pattern_id)

        # Initialize AI service
        ai_service = AIService(logger)

        # Execute pattern through AI service
        ai_response = ai_service.get_ai_response(
            messages=messages,
            model_name=model_name,
            pattern_id=resolved_pattern_id,
            debug=debug_mode,
            pattern_manager=pattern_manager,
            enable_url_search=False
        )

        if not ai_response:
            logger.error("No response received from AI service for pattern '%s'", pattern_id)
            return {
                'error': 'No response received from AI service',
                'success': False,
                'pattern_id': pattern_id
            }, 500

        logger.info("Successfully executed pattern '%s'", pattern_id)

        # Process response
        if isinstance(ai_response, dict):  # type: ignore[reportUnnecessaryIsInstance]
            formatted_output = ai_response.get('content', str(ai_response))
        else:
            formatted_output = str(ai_response)

        return {
            'success': True,
            'pattern_id': pattern_id,
            'response': ai_response,
            'formatted_output': formatted_output,
            'created_files': []
        }


@patterns_ns.route('/execute/files')
class PatternFileExecution(Resource):
    """Execute a pattern with file uploads via multipart form data."""

    @patterns_ns.doc('execute_pattern_with_files')
    @patterns_ns.expect(pattern_file_execution_request, validate=False)
    @patterns_ns.marshal_with(pattern_execution_response)
    def post(self):
        """Execute a pattern with file uploads.

        Use multipart/form-data with:
        - pattern_id: Pattern ID (form field)
        - inputs: JSON string of non-file inputs (form field)
        - debug: true/false (form field, optional)
        - model_name: Model override (form field, optional)
        - file inputs: Upload files using the pattern's input field names

        Example:
        curl -X POST "/api/v1/patterns/execute/files" \\
          -F "pattern_id=image_analysis" \\
          -F "inputs={\"description\":\"Analyze this image\"}" \\
          -F "image_input=@/path/to/image.jpg" \\
          -F "debug=false"
        """
        temp_files_to_cleanup = []

        try:
            # Ensure this is multipart data
            if not request.content_type or not request.content_type.startswith('multipart/form-data'):
                return {
                    'error': (
                        'This endpoint requires multipart/form-data. '
                        'Use /patterns/execute for JSON-only patterns.'
                    ),
                    'success': False
                }, 400

            form = request.form
            files = request.files

            pattern_id = form.get('pattern_id')
            debug_mode = form.get('debug', '').lower() in ('true', '1', 'yes')
            model_name = form.get('model_name')

            if not pattern_id:
                return {'error': 'pattern_id is required', 'success': False}, 400

            # Parse JSON inputs
            try:
                inputs_json = form.get('inputs', '{}')
                inputs = json.loads(inputs_json) if inputs_json else {}
            except json.JSONDecodeError as e:
                return {
                    'error': f'Invalid JSON in inputs field: {e}',
                    'success': False,
                    'pattern_id': pattern_id
                }, 400

            current_app.logger.info(
                f"File upload request - Pattern: {pattern_id}, Inputs: {list(inputs.keys())}, "
                f"Files: {list(files.keys())}"
            )

            # Load configuration
            config = load_config()
            if not config:
                return {'error': 'Failed to load configuration', 'success': False}, 500

            # Initialize pattern manager
            pattern_manager = PatternManager(project_root, config)

            # Validate pattern exists
            pattern_content = pattern_manager.get_pattern_content(pattern_id)
            if not pattern_content:
                return {
                    'error': f'Pattern not found: {pattern_id}',
                    'success': False,
                    'pattern_id': pattern_id
                }, 404

            # Process file inputs
            pattern_inputs = pattern_content.get('inputs', [])
            processed_inputs, temp_files_to_cleanup = _process_file_inputs(
                pattern_inputs, inputs, files
            )

            # Process pattern inputs
            validated_inputs = pattern_manager.process_pattern_inputs(
                pattern_id=pattern_id,
                input_values=processed_inputs,
                interactive=False
            )

            if validated_inputs is None:
                return {
                    'error': 'Failed to process pattern inputs - validation failed',
                    'success': False,
                    'pattern_id': pattern_id
                }, 400

            # Use shared application logger instead of creating new one
            logger = get_logger()
            logger.info("Executing pattern '%s' with file uploads: %s", pattern_id, list(files.keys()))

            # Extract file paths for MessageBuilder - it expects specific parameter names
            file_input = None
            image = None
            pdf = None

            # Map uploaded files to MessageBuilder parameters based on input types
            for input_obj in pattern_inputs:
                if hasattr(input_obj, 'input_type') and input_obj.name in processed_inputs:
                    input_type = (
                        input_obj.input_type.value
                        if hasattr(input_obj.input_type, 'value')
                        else str(input_obj.input_type)
                    )
                    file_path = processed_inputs[input_obj.name]

                    if input_type == 'file':
                        file_input = file_path
                        logger.info("Mapped file input '%s' -> file_input: %s", input_obj.name, file_path)
                    elif input_type == 'image_file':
                        image = file_path
                        logger.info("Mapped image input '%s' -> image: %s", input_obj.name, file_path)
                    elif input_type == 'pdf_file':
                        pdf = file_path
                        logger.info("Mapped PDF input '%s' -> pdf: %s", input_obj.name, file_path)

            # Build messages using message builder with proper file parameters
            message_builder = MessageBuilder(pattern_manager, logger)

            # Build messages for the pattern with file support
            messages, resolved_pattern_id = message_builder.build_messages(
                question=None,
                file_input=file_input,  # This will read and include file content
                pattern_id=pattern_id,
                pattern_input=validated_inputs,
                response_format="rawtext",
                url=None,
                image=image,  # This will process image files
                pdf=pdf,  # This will process PDF files
                image_url=None,
                pdf_url=None
            )

            if not messages:
                return {
                    'error': 'Failed to build messages for pattern execution',
                    'success': False,
                    'pattern_id': pattern_id
                }, 500

            logger.info("Built %d messages for pattern '%s'", len(messages), pattern_id)

            # Initialize AI service with application logger
            ai_service = AIService(logger)

            # Execute pattern through AI service
            ai_response = ai_service.get_ai_response(
                messages=messages,
                model_name=model_name,
                pattern_id=resolved_pattern_id,
                debug=debug_mode,
                pattern_manager=pattern_manager,
                enable_url_search=False
            )

            if not ai_response:
                logger.error("No response received from AI service for pattern '%s'", pattern_id)
                return {
                    'error': 'No response received from AI service',
                    'success': False,
                    'pattern_id': pattern_id
                }, 500

            logger.info("Successfully executed pattern '%s' with file uploads", pattern_id)

            # Process the response
            formatted_output = str(ai_response)
            created_files = []

            if isinstance(ai_response, dict):  # type: ignore[reportUnnecessaryIsInstance]
                formatted_output = ai_response.get('content', str(ai_response))
            elif isinstance(ai_response, str):  # type: ignore[reportUnnecessaryIsInstance]
                formatted_output = ai_response
            else:
                formatted_output = str(ai_response)

            # Return successful response
            return {
                'success': True,
                'pattern_id': pattern_id,
                'response': ai_response,
                'formatted_output': formatted_output,
                'created_files': created_files or []
            }

        except Exception as e:
            current_app.logger.error(f"Error executing pattern with files: {e}")
            current_app.logger.debug(f"Pattern file execution error details: {traceback.format_exc()}")

            error_pattern_id = pattern_id if 'pattern_id' in locals() else 'unknown'
            return {
                'error': 'Failed to execute pattern with files',
                'details': str(e),
                'success': False,
                'pattern_id': error_pattern_id
            }, 500

        finally:
            # Always clean up temporary files
            for temp_file in temp_files_to_cleanup:
                _cleanup_temp_file(temp_file)


@patterns_ns.route('/<string:pattern_id>/template')
class PatternTemplate(Resource):
    """Get JSON template for pattern inputs."""

    @patterns_ns.doc('get_pattern_template')
    @patterns_ns.marshal_with(pattern_template)
    def get(self, pattern_id):
        """Get a JSON template with default/example values for pattern inputs.

        Returns a template that can be used as a starting point for
        pattern execution requests.

        Args:
            pattern_id: The ID of the pattern to get template for
        """
        try:
            # Load configuration
            config = load_config()
            if not config:
                return {'error': 'Failed to load configuration'}, 500

            # Initialize pattern manager
            pattern_manager = PatternManager(project_root, config)

            # Load specific pattern
            pattern_content = pattern_manager.get_pattern_content(pattern_id)
            if not pattern_content:
                return {'error': f'Pattern not found: {pattern_id}'}, 404

            # Generate template from pattern inputs
            inputs = pattern_content.get('inputs', [])
            template = {}

            for input_obj in inputs:
                if hasattr(input_obj, 'name'):  # It's a PatternInput object
                    input_name = input_obj.name

                    # Use default value if available
                    if input_obj.default is not None:
                        template[input_name] = input_obj.default
                    # Use first option if available
                    elif input_obj.options:
                        template[input_name] = input_obj.options[0]
                    # Generate example based on type
                    else:
                        input_type = (
                            input_obj.input_type.value
                            if hasattr(input_obj.input_type, 'value')
                            else str(input_obj.input_type)
                        )

                        if input_type == 'text':
                            template[input_name] = (
                                f"<{input_obj.description}>"
                                if input_obj.description
                                else "<text_value>"
                            )
                        elif input_type == 'file':
                            template[input_name] = {
                                "_note": "For API execution, upload this as a file in multipart/form-data request",
                                "_example": "Use the field name as the file upload parameter"
                            }
                        elif input_type == 'image_file':
                            template[input_name] = {
                                "_note": "For API execution, upload image file in multipart/form-data request",
                                "_supported_formats": ["jpg", "jpeg", "png", "gif", "webp"],
                                "_example": "Use the field name as the file upload parameter"
                            }
                        elif input_type == 'pdf_file':
                            template[input_name] = {
                                "_note": "For API execution, upload PDF file in multipart/form-data request",
                                "_supported_formats": ["pdf"],
                                "_example": "Use the field name as the file upload parameter"
                            }
                        elif input_type == 'number':
                            if input_obj.min_value is not None:
                                template[input_name] = input_obj.min_value
                            else:
                                template[input_name] = 0
                        elif input_type == 'boolean':
                            template[input_name] = input_obj.required
                        else:
                            template[input_name] = f"<{input_type}_value>"

                else:  # It's already a dictionary (backwards compatibility)
                    input_name = input_obj.get('name', 'unknown')
                    template[input_name] = input_obj.get(
                        'default',
                        f"<{input_name}_value>"
                    )

            return {
                'pattern_id': pattern_id,
                'template': template
            }

        except Exception as e:
            current_app.logger.error(f"Error getting pattern template {pattern_id}: {e}")
            return {'error': 'Failed to get pattern template', 'details': str(e)}, 500
"""
OpenRouter API management endpoints for the AskAI API.
"""
import os
import sys
from flask import current_app
from flask_restx import Namespace, Resource, fields

# Add project paths for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

from askai.core.ai import OpenRouterClient
from askai.utils import load_config

# Create namespace
openrouter_ns = Namespace('openrouter', description='OpenRouter API management operations')

# Response models
model_info = openrouter_ns.model('ModelInfo', {
    'id': fields.String(required=True, description='Model ID'),
    'name': fields.String(description='Model name'),
    'description': fields.String(description='Model description'),
    'context_length': fields.Integer(description='Maximum context length'),
    'pricing': fields.Raw(description='Pricing information'),
    'top_provider': fields.Raw(description='Top provider information')
})

models_response = openrouter_ns.model('ModelsResponse', {
    'models': fields.List(fields.Nested(model_info), description='List of available models'),
    'count': fields.Integer(description='Total number of models')
})

credits_response = openrouter_ns.model('CreditsResponse', {
    'credits': fields.Float(description='Total credits'),
    'limit': fields.Float(description='Credit limit (same as total credits)'),
    'usage': fields.Float(description='Credits used'),
    'remaining': fields.Float(description='Remaining credits available'),
    'label': fields.String(description='API key label')
})

api_test_response = openrouter_ns.model('ApiTestResponse', {
    'success': fields.Boolean(required=True, description='Test success status'),
    'message': fields.String(description='Test result message'),
    'api_accessible': fields.Boolean(description='API accessibility status'),
    'credits_available': fields.Float(description='Available credits'),
    'models_count': fields.Integer(description='Number of available models')
})


@openrouter_ns.route('/models')
class OpenRouterModels(Resource):
    """Get available OpenRouter models."""

    @openrouter_ns.doc('get_models')
    @openrouter_ns.marshal_with(models_response)
    def get(self):
        """Get list of all available OpenRouter models.

        Returns a list of all AI models available through OpenRouter API.
        """
        try:
            # Load configuration
            config = load_config()

            if not config:
                return {'error': 'Failed to load configuration'}, 500

            # Check API key
            if not config.get('api_key'):
                return {'error': 'OpenRouter API key not configured'}, 400

            # Initialize OpenRouter client
            logger = current_app.config.get('CLI_LOGGER') or current_app.logger
            client = OpenRouterClient(config, logger)

            # Get models
            models = client.get_available_models(debug=False)

            if models is None:
                return {'error': 'Failed to fetch models from OpenRouter'}, 500

            # Format models for API response
            formatted_models = []
            for model in models:
                formatted_models.append({
                    'id': model.get('id', ''),
                    'name': model.get('name', ''),
                    'description': model.get('description', ''),
                    'context_length': model.get('context_length', 0),
                    'pricing': model.get('pricing', {}),
                    'top_provider': model.get('top_provider', {})
                })

            return {
                'models': formatted_models,
                'count': len(formatted_models)
            }

        except Exception as e:
            current_app.logger.error(f"Error getting OpenRouter models: {e}")
            return {'error': 'Failed to get models', 'details': str(e)}, 500


@openrouter_ns.route('/credits')
class OpenRouterCredits(Resource):
    """Get OpenRouter credit balance."""

    @openrouter_ns.doc('get_credits')
    @openrouter_ns.marshal_with(credits_response)
    def get(self):
        """Get current OpenRouter credit balance.

        Returns the current credit balance and usage information.
        """
        try:
            # Load configuration
            config = load_config()

            if not config:
                return {'error': 'Failed to load configuration'}, 500

            # Check API key
            if not config.get('api_key'):
                return {'error': 'OpenRouter API key not configured'}, 400

            # Initialize OpenRouter client
            logger = current_app.config.get('CLI_LOGGER') or current_app.logger
            client = OpenRouterClient(config, logger)

            # Get credit balance
            credits_info = client.get_credit_balance()

            if credits_info is None:
                return {'error': 'Failed to fetch credits from OpenRouter'}, 500

            total_credits = credits_info.get('total_credits', 0.0)
            total_usage = credits_info.get('total_usage', 0.0)

            return {
                'credits': total_credits,
                'limit': total_credits,  # Total credits available
                'usage': total_usage,
                'remaining': total_credits - total_usage,
                'label': credits_info.get('label', 'Unknown')
            }

        except Exception as e:
            current_app.logger.error(f"Error getting OpenRouter credits: {e}")
            return {'error': 'Failed to get credits', 'details': str(e)}, 500


@openrouter_ns.route('/test')
class OpenRouterTest(Resource):
    """Test OpenRouter API connectivity."""

    @openrouter_ns.doc('test_api')
    @openrouter_ns.marshal_with(api_test_response)
    def get(self):
        """Test OpenRouter API connectivity and functionality.

        Performs a comprehensive test of OpenRouter API access including
        API key validation, credit balance check, and model availability.
        """
        try:
            # Load configuration
            config = load_config()

            if not config:
                return {
                    'success': False,
                    'message': 'Failed to load configuration',
                    'api_accessible': False,
                    'credits_available': 0.0,
                    'models_count': 0
                }, 500

            # Check API key
            if not config.get('api_key'):
                return {
                    'success': False,
                    'message': 'OpenRouter API key not configured',
                    'api_accessible': False,
                    'credits_available': 0.0,
                    'models_count': 0
                }, 400

            # Initialize OpenRouter client
            logger = current_app.config.get('CLI_LOGGER') or current_app.logger
            client = OpenRouterClient(config, logger)

            test_results = {
                'success': True,
                'message': 'OpenRouter API test successful',
                'api_accessible': True,
                'credits_available': 0.0,
                'models_count': 0
            }

            # Test credit balance
            try:
                credits_info = client.get_credit_balance()
                if credits_info:
                    total_credits = credits_info.get('total_credits', 0.0)
                    total_usage = credits_info.get('total_usage', 0.0)
                    test_results['credits_available'] = total_credits - total_usage
            except Exception as e:
                test_results['success'] = False
                test_results['message'] = f'Credit balance check failed: {e}'
                test_results['api_accessible'] = False

            # Test model availability
            try:
                models = client.get_available_models(debug=False)
                if models:
                    test_results['models_count'] = len(models)
                else:
                    test_results['success'] = False
                    test_results['message'] = 'No models available'
            except Exception as e:
                test_results['success'] = False
                test_results['message'] = f'Model availability check failed: {e}'
                test_results['api_accessible'] = False

            return test_results

        except Exception as e:
            current_app.logger.error(f"Error testing OpenRouter API: {e}")
            return {
                'success': False,
                'message': f'API test failed: {str(e)}',
                'api_accessible': False,
                'credits_available': 0.0,
                'models_count': 0
            }, 500