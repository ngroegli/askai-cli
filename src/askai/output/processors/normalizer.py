"""Response normalization and cleaning.

This module handles normalizing AI responses from different formats
and cleaning content for processing.
"""

import json
import logging
from typing import Union, Dict, Optional, Any

logger = logging.getLogger(__name__)

class ResponseNormalizer:
    """Normalizes and cleans AI responses."""

    def normalize_response(self, response: Union[str, Dict]) -> str:
        """Normalize response to a consistent string format.

        Args:
            response: Raw response from AI service

        Returns:
            Normalized string response
        """
        if isinstance(response, dict):
            return self._normalize_dict_response(response)

        # String-like objects
        if hasattr(response, 'replace'):
            return response

        # Handle other types
        return self._to_json_or_str(response)

    def _normalize_dict_response(self, response: Dict) -> str:
        """Normalize dictionary response to string."""
        # Try various response formats in order
        content = (
            self._extract_from_choices(response) or
            self._extract_direct_content(response) or
            self._extract_result(response) or
            self._extract_from_message(response) or
            self._to_json_or_str(response)
        )
        return content

    def _extract_from_choices(self, response: Dict) -> Optional[str]:
        """Extract content from choices format."""
        if 'choices' in response and response['choices']:
            choice = response['choices'][0]
            if 'message' in choice and 'content' in choice['message']:
                return choice['message']['content']
            if 'text' in choice:
                return choice['text']
        return None

    def _extract_direct_content(self, response: Dict) -> Optional[str]:
        """Extract direct content field."""
        return response.get('content')

    def _extract_result(self, response: Dict) -> Optional[str]:
        """Extract and format result field."""
        if 'result' in response:
            result = response['result']
            if isinstance(result, str):
                return result
            return json.dumps(result, indent=2)
        return None

    def _extract_from_message(self, response: Dict) -> Optional[str]:
        """Extract content from nested message."""
        if 'message' in response and isinstance(response['message'], dict):
            return response['message'].get('content')
        return None

    def _to_json_or_str(self, obj: Any) -> str:
        """Convert object to JSON string or fallback to str()."""
        try:
            return json.dumps(obj, indent=2)
        except (TypeError, ValueError):
            return str(obj)

    def clean_content(self, content: str) -> str:
        """Clean and format content.

        Args:
            content: Content to clean

        Returns:
            Cleaned content
        """
        if not content:
            return content

        # Remove excessive whitespace
        content = content.strip()

        # Normalize line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')

        # Remove trailing whitespace from lines
        lines = content.split('\n')
        lines = [line.rstrip() for line in lines]
        content = '\n'.join(lines)

        return content
