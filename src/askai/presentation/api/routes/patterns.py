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
from askai.utils import load_config
from askai.utils import get_logger

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
    def get(self):  # pylint: disable=too-many-nested-blocks
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
    def post(self):  # pylint: disable=too-many-return-statements
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
    def post(self):  # pylint: disable=too-many-return-statements
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
    def get(self, pattern_id):  # pylint: disable=too-many-nested-blocks
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
