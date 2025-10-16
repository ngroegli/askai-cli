"""
Pattern management endpoints for the AskAI API.
"""
import os
import sys
from flask import current_app
from flask_restx import Namespace, Resource, fields

# Add project paths for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "python"))

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
            patterns_dir = os.path.join(project_root, "patterns")
            pattern_manager = PatternManager(patterns_dir, config)

            # Get all patterns
            available_patterns = pattern_manager.list_patterns()
            patterns = []

            for pattern_data in available_patterns:
                try:
                    pattern_id = pattern_data.get('id', '')
                    pattern_content = pattern_manager.get_pattern_content(pattern_id)

                    if pattern_content:
                        patterns.append({
                            'id': pattern_id,
                            'name': pattern_data.get('name', pattern_id),
                            'description': pattern_data.get('description', ''),
                            'category': pattern_data.get('category', 'general'),
                            'inputs': pattern_content.get('inputs', []),
                            'outputs': pattern_content.get('outputs', [])
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
            patterns_dir = os.path.join(project_root, "patterns")
            pattern_manager = PatternManager(patterns_dir, config)

            # Load specific pattern
            pattern_content = pattern_manager.get_pattern_content(pattern_id)

            if not pattern_content:
                return {'error': f'Pattern not found: {pattern_id}'}, 404

            return {
                'id': pattern_id,
                'name': pattern_content.get('name', pattern_id),
                'description': pattern_content.get('description', ''),
                'category': pattern_content.get('category', 'general'),
                'inputs': pattern_content.get('inputs', []),
                'outputs': pattern_content.get('outputs', [])
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
            patterns_dir = os.path.join(project_root, "patterns")
            pattern_manager = PatternManager(patterns_dir, config)

            # Get all patterns and extract categories
            available_patterns = pattern_manager.list_patterns()
            categories = set()

            for pattern_data in available_patterns:
                try:
                    pattern_id = pattern_data.get('id', '')
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