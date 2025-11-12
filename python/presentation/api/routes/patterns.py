"""
Pattern management endpoints for the AskAI API.
"""
import logging
import os
import sys
import traceback
from flask import current_app, request
from flask_restx import Namespace, Resource, fields

# Add project paths for imports
project_root = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "..", ".."
))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "python"))

# pylint: disable=wrong-import-position
from modules.ai.ai_service import AIService
from modules.messaging.builder import MessageBuilder
from modules.patterns.pattern_manager import PatternManager
from shared.config.loader import load_config

# Create namespace
patterns_ns = Namespace('patterns', description='Pattern management operations')

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
    """Execute a pattern with provided inputs."""

    @patterns_ns.doc('execute_pattern')
    @patterns_ns.expect(pattern_execution_request, validate=True)
    @patterns_ns.marshal_with(pattern_execution_response)
    def post(self):
        """Execute a pattern with provided input values.

        Executes the specified pattern with the provided input values
        and returns the AI response along with any generated outputs.
        """
        try:
            # Get request data
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

            # Process pattern inputs (non-interactive mode)
            processed_inputs = pattern_manager.process_pattern_inputs(
                pattern_id=pattern_id,
                input_values=inputs,
                interactive=False  # API execution is non-interactive
            )

            if processed_inputs is None:
                return {
                    'error': 'Failed to process pattern inputs - validation failed',
                    'success': False,
                    'pattern_id': pattern_id
                }, 400

            # Build messages using message builder approach
            # Initialize message builder with logging
            logger = logging.getLogger(__name__)
            message_builder = MessageBuilder(pattern_manager, logger)

            # Build messages for the pattern
            messages, resolved_pattern_id = message_builder.build_messages(
                question=None,
                file_input=None,
                pattern_id=pattern_id,
                pattern_input=processed_inputs,
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
                return {
                    'error': 'No response received from AI service',
                    'success': False,
                    'pattern_id': pattern_id
                }, 500

            # Process the response using pattern manager
            # For API execution, we'll provide a simplified output processing
            # since the complex OutputCoordinator has many dependencies
            formatted_output = str(ai_response)
            created_files = []

            # Basic response processing - in a real implementation this would
            # use the full output processing pipeline
            if isinstance(ai_response, dict):
                formatted_output = ai_response.get('content', str(ai_response))
            elif isinstance(ai_response, str):
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
            current_app.logger.error(f"Error executing pattern: {e}")
            current_app.logger.debug(
                f"Pattern execution error details: {traceback.format_exc()}"
            )

            return {
                'error': 'Failed to execute pattern',
                'details': str(e),
                'success': False,
                'pattern_id': (
                    data.get('pattern_id', 'unknown')
                    if 'data' in locals() else 'unknown'
                )
            }, 500


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
                            template[input_name] = "<path_to_file>"
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
