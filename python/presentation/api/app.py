"""
Flask application factory and main entry point for AskAI API.
"""
import os
import sys
import logging
from flask import Flask, redirect, jsonify
from flask_restx import Api
from flask_cors import CORS

# Add project paths for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "python"))

from shared.config.loader import load_config
from shared.logging.setup import setup_logger
from .routes.questions import questions_ns
from .routes.health import health_ns
from .routes.patterns import patterns_ns


def get_logger():
    """Get the CLI logger instance for the current Flask app.

    Returns:
        logging.Logger: CLI logger if available, otherwise Flask app logger
    """
    from flask import current_app
    return current_app.config.get('CLI_LOGGER') or current_app.logger


def create_app(config=None):
    """Create and configure the Flask application.

    Args:
        config: Optional configuration dictionary

    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__)

    # Enable CORS for web UI integration
    CORS(app)

    # Basic configuration
    app.config.update({
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key'),
        'DEBUG': os.environ.get('FLASK_DEBUG', 'False').lower() == 'true',
        'TESTING': os.environ.get('FLASK_TESTING', 'False').lower() == 'true',
    })

    # Override with provided config
    if config:
        app.config.update(config)

    # Configure CLI logger for consistency with CLI application
    try:
        askai_config = load_config()
        if askai_config:
            cli_logger = setup_logger(askai_config, debug=app.config.get('DEBUG', False))
            # Store the CLI logger in app config for use in error handlers
            app.config['CLI_LOGGER'] = cli_logger
        else:
            # Fallback to basic Flask logging if config fails
            if not app.config['TESTING']:
                logging.basicConfig(level=logging.INFO)
            app.config['CLI_LOGGER'] = None
    except Exception as e:
        # Fallback to basic Flask logging if CLI logger setup fails
        if not app.config['TESTING']:
            logging.basicConfig(level=logging.INFO)
        app.logger.warning("Failed to setup CLI logger, using Flask logger: %s", e)
        app.config['CLI_LOGGER'] = None

    # Initialize Flask-RESTX API with Swagger documentation
    api = Api(
        app,
        doc='/docs/',
        title='AskAI API',
        version='1.0.0',
        description='REST API for AskAI CLI functionality',
        contact='AskAI Team',
        license='MIT',
        prefix='/api/v1'
    )

    # Register API namespaces
    api.add_namespace(health_ns)
    api.add_namespace(questions_ns)
    api.add_namespace(patterns_ns)

    # Add custom root endpoints as regular Flask routes
    @app.route('/', endpoint='api_root')
    def api_root():
        """Root endpoint - redirect to documentation."""
        return redirect('/docs/', code=302)

    @app.route('/api', endpoint='api_info_endpoint')
    def api_info():
        """API information endpoint."""
        return jsonify({
            'name': 'AskAI API',
            'version': '1.0.0',
            'description': (
                'REST API for AskAI CLI functionality - '
                'AI-powered question processing and pattern management'
            ),
            'endpoints': {
                'health': '/api/v1/health/',
                'questions': '/api/v1/questions/',
                'patterns': '/api/v1/patterns/',
                'documentation': '/docs/',
                'api_spec': '/api/v1/swagger.json'
            },
            'documentation': '/docs/'
        })

    # Note: /api/v1 is handled by Flask-RESTX automatically

    @app.route('/favicon.ico', endpoint='favicon_endpoint')
    def favicon():
        """Simple favicon handler to prevent 404s."""
        return '', 204

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors with helpful information."""
        # Use CLI logger if available, otherwise Flask logger
        logger = app.config.get('CLI_LOGGER') or app.logger
        logger.warning(f"404 Not Found: {error}")
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested endpoint was not found.',
            'available_endpoints': {
                'root': '/ (redirects to /docs/)',
                'api_info': '/api',
                'api_v1_info': '/api/v1',
                'documentation': '/docs/',
                'health': '/api/v1/health/',
                'questions': '/api/v1/questions/',
                'patterns': '/api/v1/patterns/'
            },
            'suggestion': 'Visit /docs/ for interactive API documentation'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        # Use CLI logger if available, otherwise Flask logger
        logger = app.config.get('CLI_LOGGER') or app.logger
        logger.error(f"Internal Server Error: {error}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred.',
            'suggestion': 'Check the server logs for more details'
        }), 500

    return app


def main():
    """Main entry point for running the Flask development server."""
    app = create_app()

    # Get configuration from environment
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 8080))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
