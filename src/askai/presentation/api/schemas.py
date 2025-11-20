"""
Response schema definitions for the AskAI API.
"""
from marshmallow import Schema, fields, validate


class QuestionResponseSchema(Schema):
    """Schema for question processing responses."""

    content = fields.String(
        required=True,
        metadata={'description': 'The AI response content'}
    )

    created_files = fields.List(
        fields.String(),
        metadata={'description': 'List of created files'}
    )

    chat_id = fields.String(
        allow_none=True,
        metadata={'description': 'Chat session ID'}
    )

    model_used = fields.String(
        allow_none=True,
        metadata={'description': 'AI model that was used'}
    )

    token_usage = fields.Dict(
        allow_none=True,
        metadata={'description': 'Token usage information'}
    )


class PatternInfoSchema(Schema):
    """Schema for pattern information."""

    id = fields.String(
        required=True,
        metadata={'description': 'Pattern ID'}
    )

    name = fields.String(
        required=True,
        metadata={'description': 'Pattern name'}
    )

    description = fields.String(
        allow_none=True,
        metadata={'description': 'Pattern description'}
    )

    category = fields.String(
        allow_none=True,
        metadata={'description': 'Pattern category'}
    )

    inputs = fields.List(
        fields.Dict(),
        metadata={'description': 'Pattern input requirements'}
    )

    outputs = fields.List(
        fields.Dict(),
        metadata={'description': 'Pattern output specifications'}
    )


class PatternsListSchema(Schema):
    """Schema for patterns list response."""

    patterns = fields.List(
        fields.Nested(PatternInfoSchema),
        metadata={'description': 'List of available patterns'}
    )

    count = fields.Integer(
        metadata={'description': 'Total number of patterns'}
    )


class HealthResponseSchema(Schema):
    """Schema for health check responses."""

    status = fields.String(
        required=True,
        metadata={'description': 'Service status'}
    )

    version = fields.String(
        required=True,
        metadata={'description': 'API version'}
    )

    timestamp = fields.DateTime(
        required=True,
        metadata={'description': 'Current timestamp'}
    )

    uptime = fields.Float(
        allow_none=True,
        metadata={'description': 'Service uptime in seconds'}
    )


class ErrorResponseSchema(Schema):
    """Schema for error responses."""

    error = fields.String(
        required=True,
        metadata={'description': 'Error message'}
    )

    details = fields.String(
        allow_none=True,
        metadata={'description': 'Detailed error information'}
    )

    code = fields.String(
        allow_none=True,
        metadata={'description': 'Error code'}
    )


class ValidationResponseSchema(Schema):
    """Schema for validation responses."""

    valid = fields.Boolean(
        required=True,
        metadata={'description': 'Whether the request is valid'}
    )

    errors = fields.List(
        fields.String(),
        metadata={'description': 'List of validation errors'}
    )

    warnings = fields.List(
        fields.String(),
        metadata={'description': 'List of validation warnings'}
    )


class QuestionRequestSchema(Schema):
    """Schema for question processing requests."""

    question = fields.String(
        required=True,
        validate=validate.Length(min=1, max=10000),
        metadata={'description': 'The question to ask'}
    )

    file_input = fields.String(
        allow_none=True,
        metadata={'description': 'Path to input file (optional)'}
    )

    url = fields.String(
        allow_none=True,
        validate=validate.URL(),
        metadata={'description': 'URL to process (optional)'}
    )

    response_format = fields.String(
        validate=validate.OneOf(['rawtext', 'json', 'md']),
        load_default='rawtext',
        metadata={'description': 'Response format'}
    )

    model = fields.String(
        allow_none=True,
        metadata={'description': 'AI model to use (optional)'}
    )

    pattern_id = fields.String(
        allow_none=True,
        metadata={'description': 'Pattern ID to use (optional)'}
    )


class PatternRequestSchema(Schema):
    """Schema for pattern-related requests."""

    category = fields.String(
        allow_none=True,
        metadata={'description': 'Filter by category (optional)'}
    )

    limit = fields.Integer(
        validate=validate.Range(min=1, max=100),
        load_default=50,
        metadata={'description': 'Maximum number of results'}
    )

    offset = fields.Integer(
        validate=validate.Range(min=0),
        load_default=0,
        metadata={'description': 'Offset for pagination'}
    )
