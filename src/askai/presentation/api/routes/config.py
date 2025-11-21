"""
Configuration management endpoints for the AskAI API.
"""
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
                'configured': configured and not issues,
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
                'valid': not issues,
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
