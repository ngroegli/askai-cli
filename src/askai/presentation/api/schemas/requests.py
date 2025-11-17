"""
Request schema definitions for the AskAI API.
"""
from marshmallow import Schema, fields, validate


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
