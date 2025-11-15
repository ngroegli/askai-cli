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

from modules.ai.openrouter_client import OpenRouterClient
from shared.config.loader import load_config

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