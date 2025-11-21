"""
Swagger/OpenAPI configuration for the AskAI API.
"""

# API Documentation Configuration
API_CONFIG = {
    'title': 'AskAI API',
    'version': '1.0.0',
    'description': """
    REST API for AskAI CLI functionality.

    This API provides programmatic access to AskAI's question processing capabilities,
    including pattern-based AI interactions, file processing, and response formatting.

    ## Features

    - **Question Processing**: Submit questions and get AI-powered responses
    - **Pattern Management**: Access and use predefined AI interaction patterns
    - **File Processing**: Include files and URLs in your questions
    - **Multiple Formats**: Get responses in text, JSON, or Markdown format
    - **Health Monitoring**: Check service status and readiness

    ## Authentication

    Currently, the API uses the same configuration as the CLI tool.
    Make sure your AskAI configuration is properly set up.

    ## Rate Limiting

    API calls are subject to the same rate limits as configured for your AI provider.
    """,
    'contact': {
        'name': 'AskAI Team',
        'url': 'https://github.com/ngroegli/askai-cli',
    },
    'license': {
        'name': 'MIT',
        'url': 'https://opensource.org/licenses/MIT',
    },
    'servers': [
        {
            'url': 'http://localhost:8080/api/v1',
            'description': 'Development server'
        }
    ]
}

# Swagger UI Configuration
SWAGGER_CONFIG = {
    'headers': [],
    'specs': [
        {
            'endpoint': 'apispec',
            'route': '/apispec.json',
            'rule_filter': lambda rule: True,
            'model_filter': lambda tag: True,
        }
    ],
    'static_url_path': '/flasgger_static',
    'swagger_ui': True,
    'specs_route': '/docs/',
    'openapi': '3.0.0',
    'uiversion': 3,
    'ui_params': {
        'displayOperationId': True,
        'defaultModelsExpandDepth': 2,
        'defaultModelExpandDepth': 2,
        'displayRequestDuration': True,
        'docExpansion': 'none',
        'filter': True,
        'showExtensions': True,
        'showCommonExtensions': True,
        'tryItOutEnabled': True
    }
}

# API Tags for organization
API_TAGS = [
    {
        'name': 'health',
        'description': 'Health check and monitoring endpoints'
    },
    {
        'name': 'questions',
        'description': 'Question processing and AI interaction endpoints'
    },
    {
        'name': 'patterns',
        'description': 'Pattern management and discovery endpoints'
    }
]
